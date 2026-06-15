"""Interactive single-chain demo.

Demonstrates the full pipeline on a single causal chain with detailed output.
Shows intermediate confidences, stopping decisions, and per-hop contributions.
"""

import sys
import json
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.chain import CausalChain, Hop


def demo_builtin_chain():
    """Run demo on the classic Middle East -> Oil -> Chemicals -> Short example."""
    chain = CausalChain(
        chain_id="DEMO-001",
        trigger_event="Middle East conflict escalates",
        hops=[
            Hop(
                hop_id=0,
                description="Hormuz Strait blockade risk increases significantly",
                confidence=0.80,
                hop_type="geopolitical",
                time_span_days=3,
            ),
            Hop(
                hop_id=1,
                description="Crude oil supply tightens by 15%",
                confidence=0.75,
                hop_type="macroeconomic",
                time_span_days=7,
            ),
            Hop(
                hop_id=2,
                description="Oil prices rise 25% in spot market",
                confidence=0.70,
                hop_type="macroeconomic",
                time_span_days=14,
            ),
            Hop(
                hop_id=3,
                description="Chemical raw material costs rise by 20%",
                confidence=0.72,
                hop_type="sector",
                time_span_days=10,
            ),
            Hop(
                hop_id=4,
                description="Chemical sector earnings forecast cut by 15%",
                confidence=0.65,
                hop_type="company",
                time_span_days=7,
            ),
            Hop(
                hop_id=5,
                description="Chemical sector stocks enter downtrend; short signal triggered",
                confidence=0.68,
                hop_type="technical",
                time_span_days=5,
            ),
        ],
        ground_truth=True,
    )

    from src.aggregators import (
        NaiveProductAggregator,
        LogitAggregator,
        BayesianUpdateAggregator,
        NoisyOrAggregator,
    )
    from src.interrupt import InterruptModel
    from src.stopping import StoppingCriteria

    interrupt_model = InterruptModel()
    interrupt_probs = interrupt_model.estimate(chain)

    stopping = StoppingCriteria()

    aggregators = {
        "Naive Product (baseline)": NaiveProductAggregator(),
        "Logit Aggregation": LogitAggregator(),
        "Bayesian Update": BayesianUpdateAggregator(),
        "Noisy-OR": NoisyOrAggregator(),
    }

    print("=" * 70)
    print("SX-CH-001 Single-Chain Demo")
    print("=" * 70)
    print(f"\nChain: {chain.chain_id}")
    print(f"Trigger: {chain.trigger_event}")
    print(f"Ground truth: {chain.ground_truth}")
    print(f"\n{'#':<3} {'Type':<16} {'Conf':>7} {'Interrupt':>9}  Description")
    print("-" * 70)
    for i, (hop, ip) in enumerate(zip(chain.hops, interrupt_probs)):
        print(
            f"{i:<3} {hop.hop_type:<16} {hop.confidence:>7.4f} {ip:>9.4f}  "
            f"{hop.description}"
        )
    print("-" * 70)

    print(f"\nNaive product (baseline): {np.prod(chain.confidences):.4f}")
    print(
        f"(0.80 * 0.75 * 0.70 * 0.72 * 0.65 * 0.68 = "
        f"{0.80*0.75*0.70*0.72*0.65*0.68:.4f})"
    )
    print("This is the naive multiplication that the challenge says is too conservative.\n")

    print("=" * 70)
    print("Method Comparisons")
    print("=" * 70)

    for name, agg in aggregators.items():
        kwargs = {}
        if name in ("Bayesian Update", "Noisy-OR"):
            kwargs["interrupt_probs"] = interrupt_probs.tolist()

        result = agg.aggregate(chain, **kwargs)
        ci_lower, ci_upper = result.confidence_interval

        print(f"\n--- {name} ---")
        print(f"  Final confidence: {result.final_confidence:.4f}")
        print(f"  90% CI: [{ci_lower:.4f}, {ci_upper:.4f}]  (width: {ci_upper - ci_lower:.4f})")
        print(f"  Per-hop contributions: {[f'{c:+.4f}' for c in result.per_hop_contributions]}")
        print(f"  Intermediates: {[f'{c:.4f}' for c in result.intermediate_confidences]}")

        # Stopping evaluation
        for i, conf in enumerate(result.intermediate_confidences):
            ci_width = ci_upper - ci_lower
            next_conf = chain.confidences[i + 1] if i + 1 < chain.n_hops else None
            decision = stopping.evaluate(i + 1, conf, ci_width, next_conf)
            status = "STOP" if decision.should_stop else "continue"
            if decision.should_stop:
                print(f"  Hop {i + 1}: conf={conf:.4f}, ci_width={ci_width:.4f} -> "
                      f"{status} ({decision.reason})")
                break
            else:
                print(f"  Hop {i + 1}: conf={conf:.4f}, ci_width={ci_width:.4f} -> {status}")

    # Naive product failure analysis
    print("\n" + "=" * 70)
    print("Why Naive Product Fails")
    print("=" * 70)
    print("""
Naive product assumes:
  1. Per-hop independence — but causal chain hops are correlated
     (e.g., "oil supply tightens" and "oil prices rise" share information)
  2. No external interrupts — but OPEC can increase production to offset
  3. Equal decay per hop — but later hops may be more certain given earlier ones

For a 6-hop chain with average confidence 0.72:
  Naive product:  0.72^6 ≈ 0.14  (unrealistically low)
  Bayesian update: ~0.45-0.55    (more realistic, accounts for interrupts)

The Bayesian and Noisy-OR models explicitly model:
  - P(interrupt | hop type): geopolitical events have higher interrupt risk
  - Sequential evidence accumulation: each hop informs but doesn't fully multiply
  - Time-dependent decay: longer time spans allow more interrupt opportunity
""")


def main():
    demo_builtin_chain()


if __name__ == "__main__":
    main()
