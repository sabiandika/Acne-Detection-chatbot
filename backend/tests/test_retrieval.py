import unittest
from unittest.mock import patch
import requests
from types import SimpleNamespace

from services.evidence_validation import validate_answer
from services.retrieval_service import retrieve


class RetrievalTests(unittest.TestCase):
    def test_retrieval_returns_validated_source_metadata(self):
        with patch("services.retrieval_service.requests.post", side_effect=requests.ConnectionError("offline")):
            documents = retrieve("jerawat perawatan kulit")
        self.assertTrue(documents)
        self.assertTrue(all(str(document.source_url).startswith("https://") for document in documents))
        self.assertTrue(all(document.verification_status == "verified" for document in documents))

    def test_evidence_validator_rejects_unknown_ids_and_dosage(self):
        with patch("services.retrieval_service.requests.post", side_effect=requests.ConnectionError("offline")):
            documents = retrieve("jerawat perawatan")
        self.assertFalse(validate_answer("jerawat", "[fake-source] pakai ini", documents))
        self.assertFalse(validate_answer("jerawat", "Minum dosis 20 mg.", documents))
        self.assertFalse(validate_answer("jerawat", "Antibiotik menyembuhkan jerawat.", documents))

    def test_evidence_validator_accepts_relevant_supported_words(self):
        document = SimpleNamespace(
            document_id="aad-overview", title="Pengertian jerawat",
            content="Jerawat adalah kondisi kulit.", source="AAD", source_url="https://www.aad.org/",
        )
        self.assertTrue(validate_answer("apa itu jerawat", "Jerawat adalah kondisi kulit.", [document]))


if __name__ == "__main__":
    unittest.main()
