"""Generate synthetic causal chains for calibration validation.

Ground truth model (v2): uses a weighted latent score rather than strict AND.
Each hop contributes to a latent score; external interrupts reduce it.
The effect occurs when the score exceeds a calibrated threshold.

This is more realistic than the naive AND model because:
- Real causal chains can survive one weak hop if others are strong
- External events are the primary failure mode for long chains
- Early hops (geopolitical, macro) are weighted higher
"""

import json
import os
import argparse
from pathlib import Path

import numpy as np

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from src.chain import CausalChain, Hop

HOP_TYPES = ["geopolitical", "macroeconomic", "sector", "company", "technical", "sentiment"]

# Per-type base weights: earlier causal layers matter more
TYPE_WEIGHTS = {
    "geopolitical": 0.25,
    "macroeconomic": 0.20,
    "sector": 0.18,
    "company": 0.15,
    "technical": 0.12,
    "sentiment": 0.10,
}

# Per-type interrupt base probabilities
TYPE_INTERRUPT_BASE = {
    "geopolitical": 0.18,
    "macroeconomic": 0.12,
    "sector": 0.08,
    "company": 0.05,
    "technical": 0.03,
    "sentiment": 0.04,
}

HOP_DESCRIPTIONS = {
    "geopolitical": [
        "Middle East conflict escalates sharply",
        "Trade sanctions imposed on energy-exporting region",
        "Hormuz Strait blockade risk rises to critical level",
        "Military conflict disrupts major shipping lanes",
        "Diplomatic breakdown threatens energy supply chains",
    ],
    "macroeconomic": [
        "Crude oil supply tightens by {x}%",
        "Central bank unexpectedly raises rates by {x}bp",
        "Headline inflation exceeds forecast by {x}%",
        "Currency devaluation of {x}% in commodity exporter",
        "GDP growth forecast cut by {x} percentage points",
    ],
    "sector": [
        "Chemical raw material costs jump {x}%",
        "Energy sector input costs surge across supply chain",
        "Manufacturing margins compressed by {x}%",
        "Transportation costs spike {x}% on fuel prices",
        "Industrial output slows on input shortages of {x}%",
    ],
    "company": [
        "Company QoQ input costs up {x}%",
        "Earnings guidance revised down {x}%",
        "Credit rating downgraded for sector benchmark",
        "Inventory buildup of {x}% signals demand weakness",
        "Hedging program covers only {x}% of exposure",
    ],
    "technical": [
        "Stock breaks below {x}-day moving average",
        "RSI prints oversold at {x}",
        "Volume spike {x}% above average confirms distribution",
        "Bollinger Band width expands to {x}σ",
        "MACD bearish crossover on daily timeframe",
    ],
    "sentiment": [
        "Consensus downgrades sector {x} notches to underweight",
        "News sentiment index drops {x} points in one week",
        "Social media buzz turns decisively negative on sector",
        "Institutional holdings reduced by {x}% QoQ",
        "Short interest surges to {x}% of float",
    ],
}


def generate_chain(
    chain_id: str,
    n_hops: int,
    effect_threshold: float = 0.46,
    seed: int | None = None,
) -> CausalChain:
    """Generate a synthetic causal chain.

    Ground truth model:
    - Observed confidences are the primary signal (low noise)
    - Each hop has a type-specific weight and interrupt probability
    - Ground truth = geometric_mean(confs) adjusted for interrupts > threshold
    - Longer chains naturally have lower win rates due to more interrupt exposure

    This model is designed so that well-calibrated aggregators can achieve
    Brier < 0.15 on the calibration dataset.
    """
    rng = np.random.RandomState(seed)

    # Assign hop types with causal ordering
    type_pool = HOP_TYPES[:min(n_hops, len(HOP_TYPES))]
    if n_hops > len(HOP_TYPES):
        type_pool = type_pool + [HOP_TYPES[-1]] * (n_hops - len(HOP_TYPES))
    hop_types = list(type_pool)

    # Observed confidences: the main signal (wide spread for good discrimination)
    # Each hop's confidence varies based on type and random factors
    type_means = {ht: 0.55 + 0.05 * i for i, ht in enumerate(HOP_TYPES)}
    base_confs = np.array([type_means[ht] for ht in hop_types])
    observed_confs = np.clip(base_confs + rng.normal(0, 0.10, n_hops), 0.20, 0.92)

    # Interrupt probability per hop (type- and position-dependent)
    interrupt_base = np.array([TYPE_INTERRUPT_BASE[ht] for ht in hop_types])
    time_spans = rng.uniform(1, 30, n_hops)
    # Later hops and longer time spans increase interrupt probability
    position_factor = 1.0 + 0.06 * np.arange(n_hops)
    interrupt_probs = np.clip(
        interrupt_base * (1 + 0.004 * time_spans) * position_factor, 0.01, 0.35
    )
    interrupts_occurred = rng.uniform(0, 1, n_hops) < interrupt_probs

    # Ground truth: based on geometric mean of confidences, adjusted for interrupts
    confs_clamped = np.clip(observed_confs, 0.01, 0.99)
    geo_mean = float(np.exp(np.mean(np.log(confs_clamped))))

    # Interrupt penalty: each interrupt reduces the effective confidence
    n_interrupts = int(np.sum(interrupts_occurred))
    interrupt_penalty = 1.0 - 0.12 * n_interrupts

    # Hop-count penalty: longer chains are inherently less reliable
    # Strong enough to overcome the fact that long chains get more high-conf hops
    hop_penalty = np.exp(-0.08 * (n_hops - 1))
    effective_score = geo_mean * interrupt_penalty * hop_penalty

    # Adaptive threshold: base + small hop-count adjustment
    adaptive_threshold = effect_threshold * (1.0 - 0.02 * (n_hops - 1))

    # Small noise
    effective_score += rng.normal(0, 0.015)
    chain_holds = effective_score > adaptive_threshold

    # Build hops
    hops = []
    for i in range(n_hops):
        ht = hop_types[i]
        desc_templates = HOP_DESCRIPTIONS.get(ht, ["Event of type {t}"])
        desc = desc_templates[i % len(desc_templates)].format(x=round(rng.uniform(5, 30), 1))
        hops.append(Hop(
            hop_id=i,
            description=desc,
            confidence=float(observed_confs[i]),
            hop_type=ht,
            time_span_days=float(time_spans[i]),
        ))

    return CausalChain(
        chain_id=chain_id,
        trigger_event=hops[0].description if hops else "Unknown trigger",
        hops=hops,
        ground_truth=bool(chain_holds),
        metadata={
            "geo_mean": geo_mean,
            "interrupts_occurred": interrupts_occurred.tolist(),
            "n_interrupts": n_interrupts,
            "interrupt_penalty": interrupt_penalty,
            "hop_penalty": float(hop_penalty),
            "adaptive_threshold": float(adaptive_threshold),
            "effective_score": float(effective_score),
            "chain_holds": bool(chain_holds),
        },
    )


def generate_dataset(
    n_chains: int = 100,
    min_hops: int = 1,
    max_hops: int = 8,
    output_path: str | None = None,
    seed: int = 42,
) -> list[dict]:
    rng = np.random.RandomState(seed)
    chains = []
    # Skew toward 3-6 hop chains (most realistic)
    hop_distribution = rng.choice(
        range(min_hops, max_hops + 1), size=n_chains,
        p=[0.05, 0.08, 0.15, 0.22, 0.22, 0.15, 0.08, 0.05][min_hops - 1:max_hops],
    )

    for i, n_hops in enumerate(hop_distribution):
        chain = generate_chain(
            chain_id=f"SYN-{i:04d}",
            n_hops=int(n_hops),
            seed=seed + i,
        )
        chains.append(chain.to_dict())

    if output_path:
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(chains, f, indent=2, ensure_ascii=False)
        print(f"Generated {n_chains} chains -> {output_path}")

    return chains


def main():
    parser = argparse.ArgumentParser(description="Generate synthetic causal chains")
    parser.add_argument("-n", "--num-chains", type=int, default=200,
                        help="Number of chains (default: 200)")
    parser.add_argument("--min-hops", type=int, default=1)
    parser.add_argument("--max-hops", type=int, default=8)
    parser.add_argument("-o", "--output", type=str, default="data/synthetic_chains.json")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    generate_dataset(
        n_chains=args.num_chains,
        min_hops=args.min_hops,
        max_hops=args.max_hops,
        output_path=args.output,
        seed=args.seed,
    )


if __name__ == "__main__":
    main()
