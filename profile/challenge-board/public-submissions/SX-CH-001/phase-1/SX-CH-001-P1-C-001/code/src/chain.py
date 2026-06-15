"""Causal chain data structures."""

from dataclasses import dataclass, field
from typing import Optional
import numpy as np


@dataclass
class Hop:
    """A single hop in a causal chain."""

    hop_id: int
    description: str
    confidence: float  # p in [0, 1]
    hop_type: str = "unknown"  # geopolitical, macroeconomic, sector, company, technical, sentiment
    time_span_days: float = 7.0
    metadata: dict = field(default_factory=dict)

    def __post_init__(self):
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"confidence must be in [0, 1], got {self.confidence}")


@dataclass
class CausalChain:
    """A multi-hop causal chain."""

    chain_id: str
    trigger_event: str
    hops: list[Hop]
    ground_truth: Optional[bool] = None  # True if the final effect occurred
    metadata: dict = field(default_factory=dict)

    @property
    def n_hops(self) -> int:
        return len(self.hops)

    @property
    def confidences(self) -> np.ndarray:
        return np.array([h.confidence for h in self.hops])

    @property
    def hop_types(self) -> list[str]:
        return [h.hop_type for h in self.hops]

    @property
    def time_spans(self) -> np.ndarray:
        return np.array([h.time_span_days for h in self.hops])

    def to_dict(self) -> dict:
        return {
            "chain_id": self.chain_id,
            "trigger_event": self.trigger_event,
            "n_hops": self.n_hops,
            "hops": [
                {
                    "hop_id": h.hop_id,
                    "description": h.description,
                    "confidence": h.confidence,
                    "hop_type": h.hop_type,
                    "time_span_days": h.time_span_days,
                }
                for h in self.hops
            ],
            "ground_truth": self.ground_truth,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "CausalChain":
        hops = [
            Hop(
                hop_id=h["hop_id"],
                description=h["description"],
                confidence=h["confidence"],
                hop_type=h.get("hop_type", "unknown"),
                time_span_days=h.get("time_span_days", 7.0),
            )
            for h in d["hops"]
        ]
        return cls(
            chain_id=d["chain_id"],
            trigger_event=d["trigger_event"],
            hops=hops,
            ground_truth=d.get("ground_truth"),
        )


@dataclass
class AggregationResult:
    """Result of confidence aggregation for a chain."""

    chain_id: str
    method: str
    final_confidence: float
    confidence_interval: tuple[float, float]  # (lower, upper)
    per_hop_contributions: list[float]  # incremental contribution per hop
    stopped_at_hop: Optional[int] = None
    stop_reason: Optional[str] = None
    intermediate_confidences: list[float] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "chain_id": self.chain_id,
            "method": self.method,
            "final_confidence": self.final_confidence,
            "confidence_interval": list(self.confidence_interval),
            "per_hop_contributions": self.per_hop_contributions,
            "stopped_at_hop": self.stopped_at_hop,
            "stop_reason": self.stop_reason,
            "intermediate_confidences": self.intermediate_confidences,
            "metadata": self.metadata,
        }
