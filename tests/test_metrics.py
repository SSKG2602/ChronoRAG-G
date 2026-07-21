from decimal import Decimal, ROUND_HALF_UP
from fractions import Fraction
from pathlib import Path

import pytest

from chronorag_public import (
    answer_accuracy,
    format_percentage,
    hybrid_evidence_resolution,
    hybrid_success,
    micro_slot_resolution,
    strict_slot_resolution,
)
from chronorag_public.results import PUBLIC_METRICS

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize(
    ("function", "numerator", "denominator", "display"),
    [
        (answer_accuracy, 811, 1005, "80.6965"),
        (answer_accuracy, 692, 850, "81.4118"),
        (answer_accuracy, 119, 155, "76.7742"),
        (strict_slot_resolution, 846, 882, "95.9184"),
        (micro_slot_resolution, 3837, 3889, "98.6629"),
        (hybrid_evidence_resolution, 978, 1005, "97.3134"),
    ],
)
def test_frozen_metric_arithmetic(function, numerator, denominator, display):
    result = function(numerator, denominator)
    assert result.numerator == numerator
    assert result.denominator == denominator
    assert result.fraction == Fraction(numerator, denominator)
    assert format_percentage(result) == display


def test_zero_denominator_is_explicit():
    result = answer_accuracy(0, 0)
    assert result.numerator == 0 and result.denominator == 0
    assert result.fraction is None
    assert result.decimal is None and result.percentage is None
    assert result.reason_code == "ZERO_DENOMINATOR"


@pytest.mark.parametrize(
    ("answer_proven", "trace_complete", "expected"),
    [(False, False, False), (False, True, True), (True, False, True), (True, True, True)],
)
def test_hybrid_truth_table(answer_proven, trace_complete, expected):
    assert hybrid_success(answer_proven, trace_complete) is expected


def _assert_stored_ratio(numerator, denominator, decimal_value, percentage_value):
    exact_decimal = Decimal(numerator) / Decimal(denominator)
    decimal_places = len(str(decimal_value).split(".")[1])
    percent_places = len(str(percentage_value).split(".")[1])
    assert Decimal(str(decimal_value)) == exact_decimal.quantize(
        Decimal(1).scaleb(-decimal_places), rounding=ROUND_HALF_UP
    )
    assert Decimal(str(percentage_value)) == (exact_decimal * 100).quantize(
        Decimal(1).scaleb(-percent_places), rounding=ROUND_HALF_UP
    )


def test_public_metric_constants_recompute_key_ratios():
    _assert_stored_ratio(PUBLIC_METRICS["accepted"], PUBLIC_METRICS["total"], "0.8070", "80.70")
    strict_num, strict_den = PUBLIC_METRICS["strict_trace_slot_coverage"]
    _assert_stored_ratio(strict_num, strict_den, "0.9592", "95.92")
    micro_num, micro_den = PUBLIC_METRICS["micro_required_slot_coverage"]
    _assert_stored_ratio(micro_num, micro_den, "0.9866", "98.66")
    hybrid_num, hybrid_den = PUBLIC_METRICS["hybrid_evidence_resolution"]
    _assert_stored_ratio(hybrid_num, hybrid_den, "0.9731", "97.31")
    trace_complete_rejected, _ = PUBLIC_METRICS["trace_complete_rejected"]
    assert PUBLIC_METRICS["accepted"] + trace_complete_rejected == hybrid_num
