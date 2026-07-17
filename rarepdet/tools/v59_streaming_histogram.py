"""Bounded deterministic streaming histograms for the V59 diagnostic."""

from __future__ import annotations

import math
from dataclasses import dataclass

import torch


BIN_COUNT = 16_384
LOGIT_LOW = -64.0
LOGIT_HIGH = 64.0
LOGIT_WIDTH = (LOGIT_HIGH - LOGIT_LOW) / BIN_COUNT
PROBABILITY_FLOOR = 1e-12
DEFAULT_QUANTILES = (0.0, 0.001, 0.01, 0.05, 0.25, 0.5, 0.75, 0.95, 0.99, 0.999, 1.0)


@dataclass(frozen=True)
class HistogramSpec:
    kind: str
    bins: int = BIN_COUNT

    def as_dict(self) -> dict[str, object]:
        if self.kind == "logit":
            return {
                "kind": self.kind,
                "bins": self.bins,
                "range": [LOGIT_LOW, LOGIT_HIGH],
                "bin_width": LOGIT_WIDTH,
                "underflow": f"value < {LOGIT_LOW}",
                "overflow": f"value > {LOGIT_HIGH}",
            }
        if self.kind == "probability":
            return {
                "kind": self.kind,
                "bins": self.bins,
                "range": [PROBABILITY_FLOOR, 1.0],
                "spacing": "logarithmic",
                "exact_zero_bucket": True,
                "positive_underflow": f"0 < value < {PROBABILITY_FLOOR}",
            }
        raise ValueError(f"Unknown histogram kind: {self.kind}")


class StreamingHistogram:
    """CPU int64 counts with bounded storage and streamed float64 moments."""

    def __init__(self, kind: str) -> None:
        if kind not in {"logit", "probability"}:
            raise ValueError(f"Unknown histogram kind: {kind}")
        self.kind = kind
        self.counts = torch.zeros(BIN_COUNT, dtype=torch.int64, device="cpu")
        self.count = 0
        self.nonfinite_count = 0
        self.invalid_range_count = 0
        self.underflow_count = 0
        self.overflow_count = 0
        self.zero_count = 0
        self.sum = 0.0
        self.sum_squares = 0.0
        self.minimum = math.inf
        self.maximum = -math.inf
        self.minimum_positive = math.inf

    @property
    def retained_bytes(self) -> int:
        return self.counts.numel() * self.counts.element_size() + 128

    def update(self, values: torch.Tensor) -> None:
        flat = values.detach().flatten()
        if flat.numel() == 0:
            return
        finite = torch.isfinite(flat)
        self.nonfinite_count += int((~finite).sum().cpu())
        valid = flat[finite]
        if valid.numel() == 0:
            return
        moments = valid.to(dtype=torch.float64)
        self.count += int(valid.numel())
        self.sum += float(moments.sum().cpu())
        self.sum_squares += float((moments * moments).sum().cpu())
        self.minimum = min(self.minimum, float(valid.min().cpu()))
        self.maximum = max(self.maximum, float(valid.max().cpu()))
        if self.kind == "logit":
            self._update_logits(valid)
        else:
            self._update_probabilities(valid)

    def _update_logits(self, values: torch.Tensor) -> None:
        under = values < LOGIT_LOW
        over = values > LOGIT_HIGH
        self.underflow_count += int(under.sum().cpu())
        self.overflow_count += int(over.sum().cpu())
        inside = values[~under & ~over]
        if inside.numel() == 0:
            return
        indices = torch.floor((inside.to(torch.float64) - LOGIT_LOW) / LOGIT_WIDTH).to(torch.int64)
        indices.clamp_(0, BIN_COUNT - 1)
        self.counts += torch.bincount(indices, minlength=BIN_COUNT).cpu()

    def _update_probabilities(self, values: torch.Tensor) -> None:
        invalid = (values < 0) | (values > 1)
        self.invalid_range_count += int(invalid.sum().cpu())
        values = values[~invalid]
        if values.numel() == 0:
            return
        zero = values == 0
        under = (values > 0) & (values < PROBABILITY_FLOOR)
        self.zero_count += int(zero.sum().cpu())
        self.underflow_count += int(under.sum().cpu())
        positive = values[values > 0]
        if positive.numel():
            self.minimum_positive = min(self.minimum_positive, float(positive.min().cpu()))
        inside = values[(values >= PROBABILITY_FLOOR) & (values <= 1)]
        if inside.numel() == 0:
            return
        denominator = -math.log(PROBABILITY_FLOOR)
        indices = torch.floor(
            (torch.log(inside.to(torch.float64)) - math.log(PROBABILITY_FLOOR)) / denominator * BIN_COUNT
        ).to(torch.int64)
        indices.clamp_(0, BIN_COUNT - 1)
        self.counts += torch.bincount(indices, minlength=BIN_COUNT).cpu()

    def _logit_rank_interval(self, rank: int) -> tuple[float, float, str]:
        if rank < self.underflow_count:
            return self.minimum, LOGIT_LOW, "underflow"
        rank -= self.underflow_count
        cumulative = torch.cumsum(self.counts, dim=0)
        index = int(torch.searchsorted(cumulative, torch.tensor(rank + 1, dtype=torch.int64)).item())
        if index < BIN_COUNT:
            lower = LOGIT_LOW + index * LOGIT_WIDTH
            upper = lower + LOGIT_WIDTH
            return lower, upper, f"bin:{index}"
        return LOGIT_HIGH, self.maximum, "overflow"

    def _probability_rank_interval(self, rank: int) -> tuple[float, float, str]:
        if rank < self.zero_count:
            return 0.0, 0.0, "zero"
        rank -= self.zero_count
        if rank < self.underflow_count:
            return self.minimum_positive, PROBABILITY_FLOOR, "positive_underflow"
        rank -= self.underflow_count
        cumulative = torch.cumsum(self.counts, dim=0)
        index = int(torch.searchsorted(cumulative, torch.tensor(rank + 1, dtype=torch.int64)).item())
        if index >= BIN_COUNT:
            raise RuntimeError("Probability histogram rank exceeds represented counts")
        log_low = math.log(PROBABILITY_FLOOR)
        step = -log_low / BIN_COUNT
        lower = math.exp(log_low + index * step)
        upper = 1.0 if index == BIN_COUNT - 1 else math.exp(log_low + (index + 1) * step)
        return lower, upper, f"bin:{index}"

    def quantile_interval(self, q: float) -> dict[str, object]:
        if not 0 <= q <= 1:
            raise ValueError(f"Invalid quantile: {q}")
        if self.count == 0:
            return {"q": q, "available": False, "reason": "empty"}
        if self.nonfinite_count or self.invalid_range_count:
            raise RuntimeError("Quantile requested from histogram with invalid values")
        if q == 0:
            return {"q": q, "available": True, "lower": self.minimum, "upper": self.minimum,
                    "rank_floor": 0, "rank_ceil": 0, "locations": ["exact_minimum"]}
        if q == 1:
            rank = self.count - 1
            return {"q": q, "available": True, "lower": self.maximum, "upper": self.maximum,
                    "rank_floor": rank, "rank_ceil": rank, "locations": ["exact_maximum"]}
        position = (self.count - 1) * q
        lower_rank = math.floor(position)
        upper_rank = math.ceil(position)
        locator = self._logit_rank_interval if self.kind == "logit" else self._probability_rank_interval
        lower_interval = locator(lower_rank)
        upper_interval = locator(upper_rank)
        return {
            "q": q,
            "available": True,
            "lower": min(lower_interval[0], upper_interval[0]),
            "upper": max(lower_interval[1], upper_interval[1]),
            "rank_floor": lower_rank,
            "rank_ceil": upper_rank,
            "locations": [lower_interval[2], upper_interval[2]],
        }

    def summary(self, quantiles: tuple[float, ...] = DEFAULT_QUANTILES) -> dict[str, object]:
        represented = int(self.counts.sum()) + self.underflow_count + self.overflow_count
        if self.kind == "probability":
            represented += self.zero_count
        if represented + self.invalid_range_count != self.count:
            raise RuntimeError(
                f"Histogram accounting mismatch: represented={represented}, invalid={self.invalid_range_count}, "
                f"count={self.count}"
            )
        nonzero = torch.where(self.counts != 0)[0]
        result = {
            "spec": HistogramSpec(self.kind).as_dict(),
            "count": self.count,
            "nonfinite_count": self.nonfinite_count,
            "invalid_range_count": self.invalid_range_count,
            "minimum": None if self.count == 0 else self.minimum,
            "maximum": None if self.count == 0 else self.maximum,
            "mean": None if self.count == 0 else self.sum / self.count,
            "second_moment": None if self.count == 0 else self.sum_squares / self.count,
            "underflow_count": self.underflow_count,
            "overflow_count": self.overflow_count,
            "zero_count": self.zero_count,
            "nonzero_bins": [[int(index), int(self.counts[index])] for index in nonzero],
            "quantile_intervals": {format(q, ".3g"): self.quantile_interval(q) for q in quantiles},
            "retained_bytes": self.retained_bytes,
        }
        return result


def validate_histogram_implementation() -> dict[str, object]:
    cases = {
        "logit_edges": ("logit", torch.tensor([-80.0, -64.0, -1.0, -1.0, 0.0, 0.25, 64.0, 90.0])),
        "probability_edges": (
            "probability",
            torch.tensor([0.0, 0.0, 1e-15, 1e-12, 1e-9, 0.01, 0.5, 1.0], dtype=torch.float64),
        ),
        "repeated_logits": ("logit", torch.tensor([3.25] * 101)),
        "empty_probability": ("probability", torch.tensor([], dtype=torch.float32)),
    }
    results: dict[str, object] = {}
    for name, (kind, values) in cases.items():
        direct = values[torch.isfinite(values)]
        histogram = StreamingHistogram(kind)
        histogram.update(values)
        summary = histogram.summary()
        checks = {
            "count": histogram.count == direct.numel(),
            "minimum": direct.numel() == 0 or histogram.minimum == float(direct.min()),
            "maximum": direct.numel() == 0 or histogram.maximum == float(direct.max()),
            "mean": direct.numel() == 0 or math.isclose(summary["mean"], float(direct.double().mean()), abs_tol=1e-15),
            "second_moment": direct.numel() == 0 or math.isclose(
                summary["second_moment"], float((direct.double() ** 2).mean()), rel_tol=1e-15, abs_tol=1e-15
            ),
        }
        quantile_checks = {}
        if direct.numel():
            for q in DEFAULT_QUANTILES:
                exact = float(torch.quantile(direct.double(), q))
                interval = histogram.quantile_interval(q)
                quantile_checks[format(q, ".3g")] = interval["lower"] <= exact <= interval["upper"]
        results[name] = {"checks": checks, "quantile_containment": quantile_checks}

    order_values = torch.linspace(-70, 70, 10_003, dtype=torch.float64)
    one = StreamingHistogram("logit")
    one.update(order_values)
    chunks = StreamingHistogram("logit")
    for chunk in reversed(list(order_values.split(137))):
        chunks.update(chunk)
    order_equal = torch.equal(one.counts, chunks.counts) and one.underflow_count == chunks.underflow_count and (
        one.overflow_count == chunks.overflow_count
    )
    storage = {
        "histogram_bytes": one.retained_bytes,
        "histograms_per_model": 4 * 7,
        "compact_float_values_per_model_upper_bound": 1845 * 20 + 32 * 512,
    }
    all_pass = all(
        all(record["checks"].values()) and all(record["quantile_containment"].values())
        for record in results.values()
    ) and order_equal
    return {
        "passed": all_pass,
        "cases": results,
        "chunk_and_update_order_histogram_counts_identical": order_equal,
        "storage_bound": storage,
        "all_value_quantiles_used_for_validation_only": True,
    }
