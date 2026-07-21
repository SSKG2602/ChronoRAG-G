import unittest
from decimal import Decimal

from chronorag_public.normalization import normalize_entity, normalize_key, normalize_metric, normalize_period, parse_percent


class NormalizationTests(unittest.TestCase):
    def test_entity_normalization(self):
        self.assertEqual(normalize_entity("  Acme   Holdings "), "acme holdings")

    def test_metric_normalization(self):
        self.assertEqual(normalize_metric("Operating_Margin"), "operating margin")

    def test_period_normalization(self):
        self.assertEqual(normalize_period("fy2025 q1"), "FY2025 Q1")

    def test_percent_parse(self):
        self.assertEqual(parse_percent("18.4%"), Decimal("18.4"))

    def test_normalized_key(self):
        self.assertEqual(normalize_key("Acme Holdings", "Revenue", "fy2025 q1"), ("acme holdings", "revenue", "FY2025 Q1"))


if __name__ == "__main__":
    unittest.main()
