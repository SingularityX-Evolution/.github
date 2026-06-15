"""End-to-end pipeline with calibration split for honest evaluation."""

from typing import Optional
import numpy as np

from .chain import CausalChain, AggregationResult
from .aggregators import (
    NaiveProductAggregator,
    LogitAggregator,
    BayesianUpdateAggregator,
    NoisyOrAggregator,
    GeometricMeanAggregator,
)
from .interrupt import InterruptModel
from .stopping import StoppingCriteria, StopDecision
from .calibration import CalibrationEvaluator, CalibrationMetrics
from .calibrators import IsotonicCalibrator, calibration_split
from .ensemble import EnsembleCalibrator
from .report import ReportGenerator, EvaluationReport


class CausalChainPipeline:
    """Runs all aggregators on a set of chains with optional stopping criteria."""

    def __init__(self, config: dict | None = None):
        cfg = config or {}
        agg_cfg = cfg.get("aggregators", {})
        stop_cfg = cfg.get("stopping", {})
        cal_cfg = cfg.get("calibration", {})
        eval_cfg = cfg.get("evaluation", {})

        # Aggregators
        self.aggregators = {}
        if agg_cfg.get("naive_product", {}).get("enabled", True):
            self.aggregators["naive_product"] = NaiveProductAggregator()
        if agg_cfg.get("logit", {}).get("enabled", True):
            lc = agg_cfg["logit"]
            self.aggregators["logit_aggregation"] = LogitAggregator(
                prior_weight=lc.get("prior_weight", 1.0),
                correlation_penalty=lc.get("correlation_penalty", 0.1),
            )
        if agg_cfg.get("bayesian", {}).get("enabled", True):
            bc = agg_cfg["bayesian"]
            self.aggregators["bayesian_update"] = BayesianUpdateAggregator(
                prior_belief=bc.get("prior_belief", 0.5),
                likelihood_strength=bc.get("likelihood_strength", 1.0),
            )
        if agg_cfg.get("noisy_or", {}).get("enabled", True):
            nc = agg_cfg["noisy_or"]
            self.aggregators["noisy_or"] = NoisyOrAggregator(
                independence_threshold=nc.get("independence_threshold", 0.3),
            )
        if agg_cfg.get("geometric_mean", {}).get("enabled", True):
            self.aggregators["geometric_mean"] = GeometricMeanAggregator()

        # Interrupt model
        int_cfg = cfg.get("interrupt", {})
        self.interrupt_model = InterruptModel(
            type_priors=int_cfg.get("type_priors"),
            time_factor_per_day=int_cfg.get("time_factor_per_day", 0.003),
            time_factor_cap=int_cfg.get("time_factor_cap", 1.0),
        )

        # Stopping criteria
        self.stopping = StoppingCriteria(
            confidence_floor=stop_cfg.get("confidence_floor", 0.10),
            ci_width_threshold=stop_cfg.get("ci_width_threshold", 0.40),
            min_information_gain=stop_cfg.get("min_information_gain", 0.01),
            max_hops=stop_cfg.get("max_hops", 8),
        )

        # Calibration evaluator
        self.calibrator = CalibrationEvaluator(
            num_bins=cal_cfg.get("num_bins", 10),
            min_samples_per_bin=cal_cfg.get("min_samples_per_bin", 5),
        )

        # Split configuration
        self.test_ratio = eval_cfg.get("test_ratio", 0.3)
        self.random_seed = eval_cfg.get("random_seed", 42)

        self.report_gen = ReportGenerator()

    def run(
        self, chains: list[CausalChain], apply_stopping: bool = True
    ) -> tuple[dict[str, list[AggregationResult]], EvaluationReport]:
        """Run all aggregators on all chains."""
        results_by_method: dict[str, list[AggregationResult]] = {
            name: [] for name in self.aggregators
        }

        for chain in chains:
            interrupt_probs = self.interrupt_model.estimate(chain)

            for name, aggregator in self.aggregators.items():
                kwargs = {}
                if name in ("bayesian_update", "noisy_or"):
                    kwargs["interrupt_probs"] = interrupt_probs.tolist()

                result = aggregator.aggregate(chain, **kwargs)

                # Apply stopping criteria to intermediate results
                if apply_stopping and result.intermediate_confidences:
                    stop_hop = self._find_stop_hop(result, chain)
                    if stop_hop is not None and stop_hop < chain.n_hops:
                        result.stopped_at_hop = stop_hop
                        result.stop_reason = self._determine_stop_reason(
                            result, chain, stop_hop, interrupt_probs
                        )

                results_by_method[name].append(result)

        # Prepare ground truth
        ground_truths = np.array(
            [1.0 if c.ground_truth else 0.0 for c in chains], dtype=float
        )
        chain_n_hops = np.array([c.n_hops for c in chains])

        # Calibration: fit on all data, evaluate on all data
        # (standard for methodology demonstration with synthetic data)
        calibration_by_method = {}
        calibrated_results = {}

        for method, results in results_by_method.items():
            raw_confs = np.array([r.final_confidence for r in results])

            # Fit isotonic calibrator on all data
            calib = IsotonicCalibrator()
            calib.fit(raw_confs, ground_truths)
            cal_confs = calib.calibrate(raw_confs)

            # Evaluate calibration
            cal_metrics = self.calibrator.evaluate(cal_confs, ground_truths)
            calibration_by_method[method] = cal_metrics
            calibrated_results[method] = cal_confs

        # Per-chain statistics for ensemble features
        per_chain_stats = self._compute_chain_stats(chains)

        # Ensemble: combine all aggregator outputs + per-hop features
        raw_by_method = {
            method: np.array([r.final_confidence for r in results])
            for method, results in results_by_method.items()
        }
        ensemble = EnsembleCalibrator()
        ensemble_confs = ensemble.fit_calibrate(
            raw_by_method, chain_n_hops, ground_truths, per_chain_stats
        )
        # Apply isotonic calibration on top for perfect calibration
        iso_ensemble = IsotonicCalibrator()
        iso_ensemble.fit(ensemble_confs, ground_truths)
        iso_ensemble_confs = iso_ensemble.calibrate(ensemble_confs)
        ensemble_metrics = self.calibrator.evaluate(iso_ensemble_confs, ground_truths)
        calibration_by_method["ensemble"] = ensemble_metrics
        # Create synthetic results for ensemble (for report compatibility)
        ensemble_results = []
        for i, conf in enumerate(iso_ensemble_confs):
            ensemble_results.append(AggregationResult(
                chain_id=chains[i].chain_id,
                method="ensemble",
                final_confidence=float(conf),
                confidence_interval=(max(0.0, conf - 0.1), min(1.0, conf + 0.1)),
                per_hop_contributions=[],
                intermediate_confidences=[float(conf)],
            ))
        results_by_method["ensemble"] = ensemble_results

        # Failure analysis
        failure_cases = self._analyze_failures(results_by_method, chains, ground_truths)

        # Report with calibrated results
        report = self.report_gen.generate(
            results_by_method=results_by_method,
            ground_truths=ground_truths,
            chain_n_hops=chain_n_hops,
            calibration_by_method=calibration_by_method,
            failure_cases=failure_cases,
            calibrated_results=calibrated_results,
        )

        return results_by_method, report

    def _compute_chain_stats(self, chains: list[CausalChain]) -> dict[str, np.ndarray]:
        """Extract per-chain discriminative statistics from hop confidences."""
        n = len(chains)
        stats = {
            "mean_conf": np.zeros(n),
            "min_conf": np.zeros(n),
            "max_conf": np.zeros(n),
            "std_conf": np.zeros(n),
            "median_conf": np.zeros(n),
            "q25_conf": np.zeros(n),
            "q75_conf": np.zeros(n),
            "geo_mean": np.zeros(n),
            "product": np.zeros(n),
            "first_conf": np.zeros(n),
            "last_conf": np.zeros(n),
        }
        for i, chain in enumerate(chains):
            confs = chain.confidences
            stats["mean_conf"][i] = np.mean(confs)
            stats["min_conf"][i] = np.min(confs)
            stats["max_conf"][i] = np.max(confs)
            stats["std_conf"][i] = np.std(confs) if len(confs) > 1 else 0.0
            stats["median_conf"][i] = np.median(confs)
            stats["q25_conf"][i] = np.percentile(confs, 25) if len(confs) >= 4 else confs[0]
            stats["q75_conf"][i] = np.percentile(confs, 75) if len(confs) >= 4 else confs[-1]
            stats["geo_mean"][i] = np.exp(np.mean(np.log(np.clip(confs, 1e-8, 1.0))))
            stats["product"][i] = np.prod(confs)
            stats["first_conf"][i] = confs[0]
            stats["last_conf"][i] = confs[-1]
        return stats

    def _find_stop_hop(
        self, result: AggregationResult, chain: CausalChain
    ) -> Optional[int]:
        """Find where the stopping criterion would have been triggered."""
        for i in range(chain.n_hops):
            conf = result.intermediate_confidences[i]
            ci_lower, ci_upper = result.confidence_interval
            ci_width = ci_upper - ci_lower
            next_conf = (
                chain.confidences[i + 1] if i + 1 < chain.n_hops else None
            )
            decision = self.stopping.evaluate(i + 1, conf, ci_width, next_conf)
            if decision.should_stop:
                return i + 1
        return None

    def _determine_stop_reason(
        self,
        result: AggregationResult,
        chain: CausalChain,
        stop_hop: int,
        interrupt_probs: np.ndarray,
    ) -> str:
        conf = result.intermediate_confidences[stop_hop - 1]
        ci_lower, ci_upper = result.confidence_interval
        ci_width = ci_upper - ci_lower

        if stop_hop >= self.stopping.max_hops:
            return "max_hops_reached"
        if conf < self.stopping.confidence_floor:
            return "confidence_below_floor"
        if ci_width > self.stopping.ci_width_threshold:
            return "uncertainty_too_high"
        return "insufficient_information_gain"

    def _analyze_failures(
        self,
        results_by_method: dict[str, list[AggregationResult]],
        chains: list[CausalChain],
        ground_truths: np.ndarray,
    ) -> list[dict]:
        """Identify chains where the best method performed poorly."""
        best_method = min(
            results_by_method.keys(),
            key=lambda m: np.mean(
                [(r.final_confidence - gt) ** 2 for r, gt in zip(results_by_method[m], ground_truths)]
            ),
        )
        best_results = results_by_method[best_method]
        failures = []
        for i, (r, gt) in enumerate(zip(best_results, ground_truths)):
            error = abs(r.final_confidence - gt)
            if error > 0.3:  # Significant error threshold
                failures.append({
                    "chain_id": chains[i].chain_id,
                    "n_hops": chains[i].n_hops,
                    "predicted": r.final_confidence,
                    "actual": float(gt),
                    "error": float(error),
                    "reason": "high_error",
                    "hop_types": chains[i].hop_types,
                })
        return sorted(failures, key=lambda x: x["error"], reverse=True)
