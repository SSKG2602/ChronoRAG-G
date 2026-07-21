import unittest

from chronorag_public.assembler import assemble_slot_preserving_answer, render_enumeration
from chronorag_public.registry import EvidenceRegistry
from chronorag_public.schemas import EvidenceObligation, TemporalRecord


class RegistryAssemblerTests(unittest.TestCase):
    def make_registry(self):
        registry = EvidenceRegistry()
        registry.add_record(TemporalRecord("r1", "Acme Holdings", "Revenue", "FY2025 Q1", "$125.0 million", "FY2025 Q1 call"))
        registry.add_record(TemporalRecord("r2", "Acme Holdings", "Operating Margin", "FY2025 Q1", "18.4%", "FY2025 Q1 call"))
        return registry

    def test_registry_returns_candidate(self):
        candidates = self.make_registry().candidates_for(EvidenceObligation("E1", "Acme Holdings", "Revenue", "FY2025 Q1"))
        self.assertEqual(len(candidates), 1)

    def test_registry_is_case_insensitive(self):
        candidates = self.make_registry().candidates_for(EvidenceObligation("E1", "acme holdings", "revenue", "fy2025 q1"))
        self.assertEqual(candidates[0].record.value, "$125.0 million")

    def test_slot_assembly_complete(self):
        obligations = [
            EvidenceObligation("E1", "Acme Holdings", "Revenue", "FY2025 Q1"),
            EvidenceObligation("E2", "Acme Holdings", "Operating Margin", "FY2025 Q1"),
        ]
        answer = assemble_slot_preserving_answer(obligations, self.make_registry())
        self.assertTrue(answer.complete)
        self.assertEqual(answer.values_by_obligation["E2"], "18.4%")

    def test_render_preserves_all_obligations(self):
        obligations = [
            EvidenceObligation("E1", "Acme Holdings", "Revenue", "FY2025 Q1", label="Revenue"),
            EvidenceObligation("E2", "Acme Holdings", "Operating Margin", "FY2025 Q1", label="Margin"),
        ]
        text = render_enumeration(obligations, assemble_slot_preserving_answer(obligations, self.make_registry()))
        self.assertIn("Revenue: $125.0 million", text)
        self.assertIn("Margin: 18.4%", text)


if __name__ == "__main__":
    unittest.main()
