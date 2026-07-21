import unittest

from chronorag_public.schemas import EvidenceObligation, TemporalRecord
from chronorag_public.validators import TRACE_STEPS, validate_obligations, validate_record, validate_trace_steps


class ValidatorTests(unittest.TestCase):
    def test_validate_obligations_accepts_complete(self):
        validate_obligations([EvidenceObligation("E1", "Acme Holdings", "Revenue", "FY2025 Q1")])

    def test_validate_obligations_rejects_duplicates(self):
        with self.assertRaises(ValueError):
            validate_obligations([
                EvidenceObligation("E1", "Acme Holdings", "Revenue", "FY2025 Q1"),
                EvidenceObligation("E1", "Beta Systems", "Revenue", "FY2025 Q1"),
            ])

    def test_validate_record_accepts_source_target_split(self):
        validate_record(TemporalRecord("r1", "Acme Holdings", "Revenue", "FY2025 Q1", "$125.0 million", "FY2025 Q1 call"))

    def test_trace_order_is_locked(self):
        validate_trace_steps(list(TRACE_STEPS))


if __name__ == "__main__":
    unittest.main()
