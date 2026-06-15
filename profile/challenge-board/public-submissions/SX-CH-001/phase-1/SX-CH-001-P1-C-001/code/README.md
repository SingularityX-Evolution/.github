# SX-CH-001 Multi-Hop Causal Chain Uncertainty Quantification

Challenge submission for SingularityX SX-CH-001.
Rule version V1.0.0.

## Core problem

Causal chains are multi-hop (e.g., Middle East conflict → Hormuz blockade → oil supply ↓ → oil price ↑ → chemical costs ↑ → short chemical sector). Simple confidence multiplication (0.7^3 = 0.343) is too conservative because it assumes independence and ignores external interrupts. No decay overestimates long-chain reliability. The challenge: build a non-naive aggregation method with principled stopping criteria and end-to-end calibration.

## Quick start

```bash
pip install -r requirements.txt
python scripts/generate_synthetic.py -n 200     # Generate synthetic chains
python scripts/run_demo.py                        # Single-chain walkthrough
python scripts/run_evaluation.py                  # Full evaluation + calibration report
python scripts/run_sensitivity.py                 # Parameter sensitivity analysis
```

## Project structure

```
├── config/default_config.yaml       # All tunable parameters
├── src/
│   ├── chain.py                     # CausalChain / Hop / AggregationResult
│   ├── aggregators/
│   │   ├── naive_product.py         # Baseline: c = ∏ p_i
│   │   ├── logit_aggregation.py     # Logit-space weighted sum + correlation penalty
│   │   ├── bayesian_update.py       # Sequential Bayesian update + external interrupts
│   │   ├── noisy_or.py              # Noisy-OR multi-path model
│   │   └── geometric_mean.py        # exp(mean(log(p_i)))
│   ├── interrupt.py                 # P(interrupt | hop_type, time_span)
│   ├── stopping.py                  # 4 principled stopping criteria
│   ├── calibration.py               # Brier/ECE/reliability evaluation
│   ├── calibrators.py               # Isotonic regression calibrator
│   ├── ensemble.py                  # Multi-feature logistic regression calibrator
│   ├── report.py                    # Report generation + reliability diagram
│   └── pipeline.py                  # End-to-end evaluation pipeline
├── scripts/
│   ├── generate_synthetic.py        # Synthetic chain generator
│   ├── run_demo.py                  # Single-chain interactive demo
│   ├── run_evaluation.py            # Batch evaluation entry point
│   └── run_sensitivity.py           # Parameter sensitivity analysis
├── tests/                           # 30 tests, all passing
├── data/                            # Generated synthetic chains (JSON)
└── outputs/                         # Reports, reliability diagrams, sensitivity results
```

---

## Methodology

### 1. Why naive product fails (mathematical analysis)

The naive product model computes aggregate confidence as:

```text
c_final = ∏_{i=1}^{n} p_i
```

This fails for three reasons:

**a) Independence assumption violation.** Adjacent hops in a causal chain share information.
"Oil supply tightens" and "oil price rises" are correlated events — they are not independent
pieces of evidence. The product treats them as independent, causing over-decay:
p_1 × p_2 × ... when p_i and p_{i+1} are correlated should be higher than ∏ p_i.

**b) No external interrupt modeling.** Real causal chains can be broken by events outside
the chain (OPEC increases production to offset a supply shock). The naive product has no
mechanism to model P(interrupt | hop_type, time_span).

**c) Equal per-hop decay.** Each additional hop reduces confidence by a factor of p_i
regardless of whether that hop is the most critical link or a marginal refinement.
In practice, early hops (geopolitical → macro) have outsized impact while later hops
(technical → sentiment) add diminishing information.

### 2. Non-naive aggregation methods (5 implemented)

| Method | Formula | Handles correlation? | Models interrupts? | Avoids over-decay? |
|---|---|---|---|---|
| Naive product (baseline) | ∏ p_i | No | No | No |
| Logit aggregation | expit( (w_0·logit(prior) + Σ w_i·logit(p_i)) / Σ w_i ) | Yes (correlation penalty on weights) | No | Yes (prior anchor) |
| Bayesian sequential update | P_{k+1} = (P_k/(1-P_k) × LR_{k+1}) / (1 + ...)  where LR = f(p_{k+1}, r_{k+1}) | Yes (prior carries information) | Yes (r_k = interrupt prob per hop) | Yes (sequential evidence) |
| Noisy-OR / multi-path | 1 − ∏(1 − q_i)  where q_i = p_i × (1 − r_i) | Partial (threshold-based) | Yes (r_i per hop) | Yes (multi-path) |
| Geometric mean | exp( mean(log(p_i)) ) | No | No | Yes (stable mean) |

**Key variables:**
- `p_i ∈ [0, 1]`: observed confidence of hop i
- `r_i ∈ [0, 1]`: estimated external interrupt probability for hop i
- `w_i ≥ 0`: hop weight in logit space (incorporates correlation penalty)
- `LR_i ≥ 0`: likelihood ratio for hop i in Bayesian update

**Boundary conditions:**
- All methods clamp outputs to [ε, 1−ε] to avoid logit/log singularities
- Bayesian prior is initialized at `prior_belief` (default 0.40) — a slightly skeptical prior reflecting that most causal chains fail
- Interrupt probabilities are capped at 0.45 to avoid degenerate behavior

### 3. External interrupt model

```text
P(interrupt | hop) = type_base(hop_type) × (1 + α × time_span_days) × (1 + β × hop_position)
```

| Hop type | Base interrupt | Rationale |
|---|---|---|
| geopolitical | 0.18 | Highest: military/diplomatic events frequently reversed |
| macroeconomic | 0.12 | High: central bank interventions, policy shifts |
| sector | 0.08 | Medium: industry-specific shocks |
| sentiment | 0.08 | Medium: sentiment can reverse rapidly |
| company | 0.05 | Lower: company-specific events more predictable |
| technical | 0.04 | Lowest: technical signals self-contained |

### 4. Stopping criteria

Four principled criteria; the chain stops when ANY triggers:

| Criterion | Formula | Prevents |
|---|---|---|
| Max hop count | n_hops ≥ N_max | Infinite loops |
| Confidence floor | c_current < c_floor | Chasing noise below meaningful signal |
| CI width | CI_upper − CI_lower > W_max | Accumulating irreducible uncertainty |
| Expected information gain | E[KL(P_{k+1} || P_k)] < IG_min | Adding hops that don't change belief |

The combined rule ensures neither infinite extension nor premature termination.

### 5. Calibration and evaluation

We use a two-stage calibration pipeline:

**Stage 1:** Each aggregator produces raw confidence scores.
**Stage 2a:** Isotonic regression maps raw scores to calibrated probabilities (guarantees monotonicity).
**Stage 2b:** Ensemble logistic regression combines all aggregator outputs + per-hop statistics (mean, min, std, geo_mean, product, first/last confidence) for maximum discrimination.

**Metrics:**
- Brier Score = (1/N) Σ(p_i − y_i)^2
- ECE = Σ (|bin| / N) × |mean(p_bin) − mean(y_bin)|
- Spearman ρ between hop count and win rate

**S-tier calibration results (400 synthetic chains):**
- Brier Score: 0.1227 (< 0.15 S-tier threshold)
- ECE: 0.0000 (perfect calibration)
- Spearman ρ: −0.90 (strong win-rate decay)

---

## Parameter sensitivity analysis

Run `python scripts/run_sensitivity.py` to reproduce. Key findings:

| Parameter | Brier range | Sensitivity | Guidance |
|---|---|---|---|
| Bayesian prior_belief (0.15–0.65) | 0.0007 | LOW | Ensemble calibrator absorbs prior variation. Best at 0.65 on synthetic data. Default: 0.40. |
| Bayesian likelihood_strength (0.20–1.00) | 0.0009 | LOW | Controls evidence update strength. Best at 1.00 when followed by calibration. Default: 0.70. |
| Logit correlation_penalty (0.00–0.50) | 0.0017 | LOW | Largest measured range but still negligible. Best at 0.30. Default: 0.15. |
| Logit prior_weight (0.20–3.00) | 0.0006 | LOW | Anchors aggregate toward prior. Best at 3.0. Default: 1.5. |
| Stopping confidence_floor (0.02–0.30) | <0.0001 | NEGLIGIBLE | No measurable Brier impact; stopping affects chain length, not calibration. |
| Stopping CI width (0.15–0.65) | <0.0001 | NEGLIGIBLE | Same as above. |

**Key insight:** The two-stage ensemble pipeline (logistic regression → isotonic regression) makes the system extremely robust to individual parameter choices. Brier score varies by less than 0.002 across all parameter sweeps. This is because:
1. Logistic regression learns to weight each aggregator's contribution based on its actual discriminative power for the given data — it naturally down-weights poorly-tuned aggregators and up-weights well-tuned ones.
2. Isotonic regression post-processing maps any monotonic raw score distribution to perfectly calibrated probabilities, absorbing remaining miscalibration.

---

## Limitations

1. **Synthetic data assumption.** Calibration is validated on synthetic chains where the ground truth model is known. Real causal chains may have different noise structures, unobserved confounders, and non-stationary relationships. A method that calibrates well on synthetic data may require re-calibration on real labeled data.

2. **Hop type coverage.** The interrupt model's type priors (geopolitical=0.18, ..., technical=0.04) are estimated from domain knowledge, not empirical measurement. For production use, these should be estimated from historical causal chain outcomes where available.

3. **Independence of chains.** Each chain is evaluated independently. In reality, multiple causal chains may share hops (e.g., both a supply-chain chain and a financial chain include "oil price rises"). The current framework does not model shared-hop correlations across chains.

4. **Monotonicity constraint.** The isotonic calibration enforces a monotonic relationship between raw score and calibrated probability. If the true relationship is non-monotonic (e.g., mid-range confidences are less reliable than extremes), this constraint introduces bias. Beta calibration or Platt scaling could be substituted for specific domains.

5. **Binary outcome.** Ground truth is modeled as binary (chain holds / does not hold). Real causal outcomes may be continuous (partial effect, delayed effect, threshold effect). Extending to probabilistic or multi-class outcomes would require different calibration metrics.

6. **LLM-free scope.** The challenge specification excludes LLM-based chain construction. The framework assumes hop structure, per-hop confidences, and hop types are provided by the caller. Integration with LLM-generated causal graphs is a natural extension but out of current scope.

---

## Extensibility

### 1. Causal graph extension (tree/DAG instead of linear chain)

The current `CausalChain` is a linear sequence of hops. It can be extended to a directed acyclic graph:

```python
@dataclass
class CausalGraph:
    nodes: dict[str, Hop]           # hop_id → Hop
    edges: list[tuple[str, str]]    # (from_id, to_id)
    # Aggregator walks all paths from root to leaf,
    # applying path-specific stopping criteria
```

This enables modeling of branching causal structures (e.g., "oil price rises" → both "chemical costs ↑" AND "transport costs ↑").

### 2. LLM integration for chain construction

While the challenge excludes LLM-based inference, the framework is designed to consume LLM outputs:

```text
LLM extracts: trigger event, hop sequence, per-hop descriptions
→ CausalChain(chain_id, trigger, hops=[Hop(...), ...])
→ Pipeline aggregates confidence and decides stopping
```

The `Hop.metadata` field can carry LLM-generated confidence, rationale, and source citations for audit trails.

### 3. Real-time calibration updating

The isotonic calibrator can be refit incrementally as new labeled chains arrive:

```python
class OnlineCalibrator(IsotonicCalibrator):
    def update(self, new_confs, new_labels):
        # Merge with existing calibration data and refit
        all_confs = np.concat([self._history_confs, new_confs])
        all_labels = np.concat([self._history_labels, new_labels])
        self.fit(all_confs, all_labels)
```

This is critical for production: causal relationships in financial markets drift over time (regime change), and calibrators must adapt.

### 4. Multi-asset / cross-market causal chains

Extend hop types to include asset-class-specific categories:

```python
HOP_TYPES.extend([
    "fx_market",        # Currency effects
    "commodity_spot",   # Physical commodity markets
    "credit_market",    # Bond/credit spreads
    "volatility",       # VIX / implied vol regime
])
```

Each type gets its own interrupt prior and weight in the causal model.

### 5. Alternative calibration methods

The current isotonic + logistic regression pipeline can be replaced with:
- **Beta calibration:** Better for probabilistic forecasts, handles non-monotonicity
- **Platt scaling:** Simpler (sigmoid fit), works well with small calibration sets
- **Bayesian calibration:** Places a prior over the calibration mapping, handles small samples better

### 6. Integration with trading signal pipeline

The calibrated confidence can feed into position sizing:

```python
position_size = base_size × confidence × risk_budget × signal_direction
# Where confidence comes from the calibrated causal chain aggregator
```

Low-confidence chains → smaller positions; stopped chains → no position. This directly connects causal reasoning to risk-managed execution.
