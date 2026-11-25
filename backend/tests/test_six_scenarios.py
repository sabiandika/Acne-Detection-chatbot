"""Automated end-to-end scenario tests for Rijema Dira AI Skincare Chatbot."""

import unittest
from unittest.mock import patch

from services import chatbot_service
from utils.logger import PipelineTrace


def _stub_grounded_llm(messages, json_mode=False):
    """Simulate grounded Gemma 3 4B JSON output strictly using retrieved evidence IDs."""
    evidence_block = messages[-1]["content"]
    user_query = messages[-2]["content"].lower()
    topic_block = messages[1]["content"].lower()

    if "kusam" in user_query or "kusam" in topic_block:
        if "[aad-dull-dry-skin-care]" in evidence_block:
            return (
                '{"answer":"Wajah kusam berkaitan dengan penumpukan sel kulit mati, kulit kering atau kurang terhidrasi, '
                'serta paparan sinar matahari tanpa tabir surya. Perawatan dasar meliputi pembersih lembut, pelembap, dan tabir surya.",'
                '"source_ids":["aad-dull-dry-skin-care"]}'
            )
    if "kemerahan" in user_query or "peradangan" in user_query:
        if "[nhs-acne-inflammation-redness]" in evidence_block:
            return (
                '{"answer":"Wajah dapat mengalami kemerahan ketika sebum berlebih dan sel kulit mati menyumbat folikel rambut '
                'sehingga memicu respons peradangan kulit.",'
                '"source_ids":["nhs-acne-inflammation-redness"]}'
            )
    if "komedo" in user_query and "papula" in user_query:
        if "[aad-acne-lesions-comparison]" in evidence_block:
            return (
                '{"answer":"Komedo terbentuk akibat pori-pori tersumbat tanpa peradangan berat, sedangkan papula adalah benjolan kecil '
                'berwarna merah dan lunak akibat dinding pori mengalami peradangan.",'
                '"source_ids":["aad-acne-lesions-comparison"]}'
            )
    if "penyebab" in user_query:
        return (
            '{"answer":"Penyebab jerawat berkaitan dengan pori-pori yang tersumbat dan minyak dapat menyumbat pori.",'
            '"source_ids":["aad-acne-causes"]}'
        )
    if "mengatasi" in user_query or "saran" in user_query:
        return (
            '{"answer":"Cuci wajah dengan lembut hingga dua kali sehari dan setelah berkeringat, gunakan pembersih lembut, jangan memencet jerawat, dan pilih produk non-comedogenic.",'
            '"source_ids":["aad-acne-care"]}'
        )
    return (
        '{"answer":"Jerawat adalah kondisi kulit yang menimbulkan komedo, jerawat, atau nodul akibat pori-pori tersumbat.",'
        '"source_ids":["aad-acne-overview"]}'
    )


class SixScenariosTests(unittest.TestCase):
    @patch("services.retrieval_service._semantic_rank", return_value=[])
    @patch("services.chatbot_service.chat", side_effect=_stub_grounded_llm)
    def test_1_multi_turn_context_conversation(self, _mock_chat, _mock_embed):
        history = []

        r1 = chatbot_service.process("Apa itu jerawat?", history=history)
        self.assertIn("Jerawat adalah kondisi kulit", r1)
        history.extend([
            {"role": "user", "content": "Apa itu jerawat?"},
            {"role": "assistant", "content": r1[:900]},
        ])

        t2 = PipelineTrace(request_id="ctx-2")
        r2 = chatbot_service.process("Apa penyebabnya?", history=history, trace=t2)
        self.assertEqual(t2.detected_intent, "skin_information")
        self.assertIn("Apa itu jerawat?", t2.resolved_context)
        self.assertIn("pori-pori yang tersumbat", r2)
        history.extend([
            {"role": "user", "content": "Apa penyebabnya?"},
            {"role": "assistant", "content": r2[:900]},
        ])

        t3 = PipelineTrace(request_id="ctx-3")
        r3 = chatbot_service.process("Bagaimana cara mengatasinya?", history=history, trace=t3)
        self.assertEqual(t3.detected_intent, "skincare_advice")
        self.assertIn("pembersih lembut", r3)
        history.extend([
            {"role": "user", "content": "Bagaimana cara mengatasinya?"},
            {"role": "assistant", "content": r3[:900]},
        ])

        t4 = PipelineTrace(request_id="ctx-4")
        r4 = chatbot_service.process("Ada saran produk?", history=history, trace=t4)
        self.assertEqual(t4.detected_intent, "product_recommendation")
        self.assertTrue(len(r4.products) >= 1)
        history.extend([
            {"role": "user", "content": "Ada saran produk?"},
            {
                "role": "assistant",
                "content": r4.reply,
                "product_ids": [p.id for p in r4.products],
            },
        ])

        t5 = PipelineTrace(request_id="ctx-5")
        r5 = chatbot_service.process("Mana yang lebih cocok?", history=history, trace=t5)
        self.assertEqual(t5.detected_intent, "product_comparison")
        self.assertEqual([p.id for p in r5.products], [p.id for p in r4.products])

    @patch("services.retrieval_service._semantic_rank", return_value=[])
    @patch("services.chatbot_service.chat", side_effect=_stub_grounded_llm)
    def test_2_skincare_information_queries(self, _mock_chat, _mock_embed):
        queries = (
            ("Apa itu jerawat?", "Jerawat adalah kondisi kulit"),
            ("Apa penyebab wajah kusam?", "penumpukan sel kulit mati"),
            ("Kenapa wajah mengalami kemerahan?", "peradangan kulit"),
            ("Apa perbedaan komedo dan papula?", "peradangan berat"),
        )
        for query, expected_snippet in queries:
            with self.subTest(query=query):
                trace = PipelineTrace(request_id="info-test")
                reply = chatbot_service.process(query, trace=trace)
                self.assertEqual(trace.detected_intent, "skin_information")
                self.assertIn(expected_snippet, reply)
                self.assertIn("https://", reply)

    @patch("services.retrieval_service._semantic_rank", return_value=[])
    @patch("services.chatbot_service.inference.analyze", side_effect=AssertionError("Fuzzy must not run"))
    def test_3_source_requests(self, _mock_fuzzy, _mock_embed):
        for query in (
            "Berikan sumber tentang jerawat.",
            "Berikan referensi ilmiah mengenai acne inflammation.",
            "Berikan sumber terkait wajah jerawat kemerahan.",
        ):
            with self.subTest(query=query):
                trace = PipelineTrace(request_id="src-test")
                reply = chatbot_service.process(query, trace=trace)
                self.assertEqual(trace.detected_intent, "source_request")
                self.assertIn("https://", reply)
                self.assertIsNone(trace.fallback_reason)

    @patch("services.chatbot_service.chat", side_effect=AssertionError("LLM must not run for deterministic fuzzy"))
    def test_4_skin_analysis_explicit_symptoms_only(self, _mock_chat):
        cases = (
            ("Wajah saya berminyak dan berjerawat.", {"keminyakan", "jerawat"}, {"iritasi", "kekeringan"}),
            ("Kulit saya kering dan mengelupas.", {"kekeringan"}, {"keminyakan", "jerawat", "iritasi"}),
            ("Saya mengalami jerawat kemerahan.", {"jerawat", "iritasi"}, {"keminyakan", "kekeringan"}),
        )
        for query, expected_explicit, expected_missing in cases:
            with self.subTest(query=query):
                trace = PipelineTrace(request_id="fuzzy-test")
                reply = chatbot_service.process(query, trace=trace)
                self.assertEqual(trace.detected_intent, "skin_analysis")
                self.assertEqual(set(trace.fuzzy_result["explicit_inputs"].keys()), expected_explicit)
                self.assertEqual(set(trace.fuzzy_result["missing_inputs"]), expected_missing)
                self.assertIn("Perkiraan komputasi", reply)
                self.assertIn("tidak ditambahkan secara otomatis", reply)

    @patch("services.chatbot_service.chat", side_effect=AssertionError("LLM must not invent products"))
    def test_5_product_catalog_queries(self, _mock_chat):
        rec = chatbot_service.process("Rekomendasi produk di toko.")
        self.assertTrue(len(rec.products) >= 1)

        sunscreen = chatbot_service.process("Cari sunscreen.")
        self.assertEqual([p.name for p in sunscreen.products], ["Daily UV Sunscreen"])

        oily_moist = chatbot_service.process("Ada moisturizer untuk kulit berminyak?")
        self.assertEqual([p.name for p in oily_moist.products], ["Soothing Gel Moisturizer"])

        compare = chatbot_service.process("Bandingkan dua produk moisturizer.")
        self.assertEqual(
            {p.name for p in compare.products},
            {"Hydrating Moisturizer", "Soothing Gel Moisturizer"},
        )
        self.assertIn("Perbandingan berdasarkan data katalog", compare.reply)

    @patch("services.chatbot_service.chat", side_effect=AssertionError("LLM must not run for out-of-scope"))
    def test_6_out_of_scope_queries(self, _mock_chat):
        for query in ("Buatkan program Python.", "Jelaskan sejarah Perang Dunia II."):
            with self.subTest(query=query):
                trace = PipelineTrace(request_id="oos-test")
                reply = chatbot_service.process(query, trace=trace)
                self.assertEqual(trace.detected_intent, "out_of_scope")
                self.assertIn("skincare", reply.lower())


if __name__ == "__main__":
    unittest.main()
