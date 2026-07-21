"""Exact deterministic aggregate metric arithmetic."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP, localcontext
from fractions import Fraction


@dataclass(frozen=True, slots=True)
class MetricResult:
    numerator: int
    denominator: int
    fraction: Fraction | None
    decimal: Decimal | None
    percentage: Decimal | None
    reason_code: str | None = None

    def as_dict(self) -> dict[str, int | str | None]:
        return {
            "numerator": self.numerator,
            "denominator": self.denominator,
            "fraction": str(self.fraction) if self.fraction is not None else None,
            "decimal": str(self.decimal) if self.decimal is not None else None,
            "percentage": str(self.percentage) if self.percentage is not None else None,
            "reason_code": self.reason_code,
        }


def _ratio(numerator: int, denominator: int) -> MetricResult:
    if isinstance(numerator, bool) or not isinstance(numerator, int) or numerator < 0:
        raise ValueError("numerator must be a non-negative integer")
    if isinstance(denominator, bool) or not isinstance(denominator, int) or denominator < 0:
        raise ValueError("denominator must be a non-negative integer")
    if denominator == 0:
        return MetricResult(numerator, denominator, None, None, None, "ZERO_DENOMINATOR")
    if numerator > denominator:
        raise ValueError("numerator cannot exceed denominator")
    exact = Fraction(numerator, denominator)
    with localcontext() as context:
        context.prec = 50
        decimal = Decimal(numerator) / Decimal(denominator)
        percentage = decimal * Decimal(100)
    return MetricResult(numerator, denominator, exact, decimal, percentage)


def format_percentage(result: MetricResult, places: int = 4) -> str | None:
    if result.percentage is None:
        return None
    if not 0 <= places <= 12:
        raise ValueError("places must be between zero and twelve")
    quantum = Decimal(1).scaleb(-places)
    return format(result.percentage.quantize(quantum, rounding=ROUND_HALF_UP), f".{places}f")


def answer_accuracy(accepted_answers: int, total_questions: int) -> MetricResult:
    return _ratio(accepted_answers, total_questions)


def strict_slot_resolution(
    strict_complete_questions: int, slot_bearing_questions: int
) -> MetricResult:
    return _ratio(strict_complete_questions, slot_bearing_questions)


def micro_slot_resolution(resolved_slots: int, required_slots: int) -> MetricResult:
    return _ratio(resolved_slots, required_slots)


def hybrid_success(answer_proven: bool, strict_trace_complete: bool) -> bool:
    if not isinstance(answer_proven, bool) or not isinstance(strict_trace_complete, bool):
        raise TypeError("hybrid inputs must be booleans")
    return answer_proven or strict_trace_complete


def hybrid_evidence_resolution(
    successful_questions: int, total_questions: int
) -> MetricResult:
    return _ratio(successful_questions, total_questions)
