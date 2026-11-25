import unittest
from unittest.mock import patch
from types import SimpleNamespace

from services import chatbot_service
from services.ollama_service import OllamaError, chat
from utils import text_normalizer


class ChatbotTests(unittest.TestCase):
    def test_normalizes_existing_slang(self):
        self.assertEqual(text_normalizer.normalisasi("muka gw gatel bgt"), "wajah saya gatal banget")

    def test_negated_symptoms_do_not_become_positive_scores(self):
        result = text_normalizer.skor_leksikon("kulit saya tidak merah dan tidak ada jerawat")
        self.assertEqual(result["iritasi"], 0.0)
        self.assertEqual(result["jerawat"], 0.0)

    def test_scope_filter_is_deterministic_and_classifies_domain(self):
        self.assertEqual(chatbot_service.scope_filter.classify_intent("muka saya jerawatan"), "skin_analysis")
        self.assertEqual(chatbot_service.scope_filter.classify_intent("berikan sumber terkait jerawat kemerahan"), "source_request")
        self.assertEqual(chatbot_service.scope_filter.classify_intent("rekomendasi produk yang ada di toko"), "product_recommendation")
        self.assertEqual(chatbot_service.scope_filter.classify_intent("ada sunscreen"), "product_search")
        self.assertEqual(chatbot_service.scope_filter.classify_intent("Apa penyebab jerawat?"), "skin_information")
        self.assertEqual(chatbot_service.scope_filter.classify_intent("Siapa presiden Indonesia?"), "out_of_scope")
        self.assertEqual(chatbot_service.scope_filter.classify_intent("berapa dosis obat jerawat"), "unsafe_medical_request")

    def test_contextual_intent_resolution(self):
        acne_history = [{"role": "user", "content": "Apa itu jerawat?"}]
        cases = (
            ("Apa itu jerawat?", [], "skin_information"),
            ("Ada saran untuk masalah itu?", acne_history, "skincare_advice"),
            ("Berikan sumbernya.", acne_history, "source_request"),
            ("Produk apa yang cocok?", acne_history, "product_recommendation"),
            ("Bagaimana cara mengatasinya?", acne_history, "skincare_advice"),
            ("Buatkan program Python.", acne_history, "out_of_scope"),
            ("Bagaimana dengan yang tadi?", acne_history, "general_skincare"),
            ("Bagaimana cara mengatasinya?", [], "clarification_needed"),
        )
        for message, history, expected in cases:
            with self.subTest(message=message):
                context = chatbot_service.scope_filter.resolve_context(message, history)
                self.assertEqual(chatbot_service.scope_filter.classify_contextual_intent(message, context), expected)
        product_history = acne_history + [
            {"role": "assistant", "content": "Produk toko tersedia.", "product_ids": [3]},
        ]
        context = chatbot_service.scope_filter.resolve_context("Mana yang lebih bagus?", product_history)
        self.assertEqual(
            chatbot_service.scope_filter.classify_contextual_intent(
                "Mana yang lebih bagus?", context, has_product_context=True,
            ),
            "product_comparison",
        )

    def test_contextless_followup_asks_for_clarification(self):
        answer = chatbot_service.process("Bagaimana cara mengatasinya?")
        self.assertIn("jelaskan masalah atau topik", answer)

    @patch("services.chatbot_service.inference.analyze", side_effect=AssertionError("fuzzy must not run"))
    @patch("services.chatbot_service.retrieval_service.retrieve")
    def test_source_request_cites_retrieved_sources_without_fuzzy(self, retrieve, _fuzzy):
        retrieve.return_value = [SimpleNamespace(
            document_id="aad-acne-causes", title="Penyebab jerawat", source="AAD",
            source_url="https://www.aad.org/public/diseases/acne/causes/acne-causes",
        )]
        answer = chatbot_service.process("Berikan sumber terkait wajah jerawat kemerahan.")
        self.assertIn("Penyebab jerawat", answer)
        self.assertIn("https://www.aad.org/public/diseases/acne/causes/acne-causes", answer)

    @patch("services.chatbot_service.chat")
    def test_product_search_returns_actual_catalog_products_without_llm(self, chat):
        result = chatbot_service.process("Ada sunscreen?")
        self.assertEqual(result.products[0].id, 3)
        self.assertEqual(result.products[0].name, "Daily UV Sunscreen")
        self.assertEqual(result.products[0].price, 95000)
        chat.assert_not_called()

    @patch("services.chatbot_service.chat")
    def test_oily_skin_recommendations_only_use_store_skin_metadata(self, chat):
        result = chatbot_service.process("Produk untuk kulit berminyak apa?")
        self.assertTrue(result.products)
        self.assertTrue(all(
            "semua jenis kulit" in product.skin.lower() or "berminyak" in product.skin.lower()
            for product in result.products
        ))
        self.assertFalse(any(hasattr(product, "stock") for product in result.products))
        chat.assert_not_called()

    def test_missing_product_ingredient_data_is_not_invented(self):
        result = chatbot_service.process("Rekomendasikan produk dengan kandungan X.")
        self.assertEqual(result.products, [])
        self.assertIn("data kandungan", result.reply)

    @patch("services.chatbot_service.chat")
    def test_vague_product_followup_uses_only_previous_catalog_ids(self, chat):
        result = chatbot_service.process("Mana yang paling cocok?", history=[
            {"role": "user", "content": "Cari sunscreen."},
            {"role": "assistant", "content": "Berikut produk toko.", "product_ids": [3]},
        ])
        self.assertEqual([product.id for product in result.products], [3])
        self.assertIn("Perbandingan berdasarkan data katalog", result.reply)
        chat.assert_not_called()

    def test_vague_product_followup_without_context_does_not_invent(self):
        result = chatbot_service.process("Mana yang paling cocok?")
        self.assertIn("jelaskan masalah atau topik", result)

    def test_out_of_scope_message_is_rejected(self):
        with patch("services.chatbot_service.chat") as generate:
            reply = chatbot_service.process("resep nasi goreng")
        self.assertIn("skincare", reply)
        generate.assert_not_called()

    @patch("services.chatbot_service.chat")
    @patch("services.chatbot_service.retrieval_service.retrieve")
    def test_unverified_answer_abstains_after_one_retry(self, retrieve, chat):
        retrieve.return_value = [SimpleNamespace(
            document_id="nhs-acne-self-care", title="Perawatan jerawat",
            content="Gunakan pembersih lembut untuk jerawat.", source="NHS",
            source_url="https://www.nhs.uk/conditions/acne/",
        )]
        call_messages = []
        def invalid_response(messages, json_mode=False):
            call_messages.append(list(messages))
            return '{"answer":"Antibiotik menghilangkan jerawat","source_ids":["nhs-acne-self-care"]}'
        chat.side_effect = invalid_response
        result = chatbot_service._answer_educational_question("cara jerawat")
        self.assertIn("belum dapat menyusun jawaban", result)
        self.assertEqual(chat.call_count, 2)
        messages = call_messages[0]
        self.assertEqual(len(messages), 4)
        self.assertEqual(messages[0]["role"], "system")
        self.assertIn("Jangan mengarang", messages[0]["content"])
        self.assertIn("RESOLVED INTENT", messages[1]["content"])
        self.assertEqual(messages[2]["role"], "user")
        self.assertEqual(messages[3]["role"], "system")

    @patch("services.chatbot_service.chat", return_value=(
        '{"answer":"Jerawat adalah kondisi kulit.","source_ids":["aad-overview"]}'
    ))
    @patch("services.chatbot_service.retrieval_service.retrieve")
    def test_general_acne_question_uses_evidence_generation(self, retrieve, chat):
        retrieve.return_value = [SimpleNamespace(
            document_id="aad-overview", title="Pengertian jerawat",
            content="Jerawat adalah kondisi kulit.", source="AAD",
            source_url="https://www.aad.org/",
        )]
        answer = chatbot_service.process("Apa itu jerawat?")
        self.assertIn("Jerawat adalah kondisi kulit.", answer)
        self.assertIn("https://www.aad.org/", answer)
        chat.assert_called_once()

    @patch("services.chatbot_service.chat", side_effect=[
        "not-json",
        '{"answer":"Jerawat adalah kondisi kulit.","source_ids":["aad-overview"]}',
    ])
    @patch("services.chatbot_service.retrieval_service.retrieve")
    def test_invalid_json_gets_one_retry_then_validates(self, retrieve, chat):
        retrieve.return_value = [SimpleNamespace(
            document_id="aad-overview", title="Pengertian jerawat",
            content="Jerawat adalah kondisi kulit.", source="AAD",
            source_url="https://www.aad.org/",
        )]
        answer = chatbot_service._answer_educational_question("Apa itu jerawat?")
        self.assertIn("Jerawat adalah kondisi kulit.", answer)
        self.assertEqual(chat.call_count, 2)

    @patch("services.chatbot_service.chat")
    def test_complete_symptoms_keep_fuzzy_response_deterministic(self, chat):
        answer = chatbot_service.process("Kulit saya berminyak, jerawat, merah, dan kering.")
        self.assertIn("Perkiraan komputasi", answer)
        self.assertIn("skor", answer)
        chat.assert_not_called()

    def test_partial_symptoms_run_fuzzy_without_filling_missing_values(self):
        answer = chatbot_service.process("Kulit saya berminyak.")
        self.assertIn("Perkiraan komputasi", answer)
        self.assertIn("Analisis ini hanya dihitung", answer)
        self.assertIn("jerawat/bruntusan/komedo", answer)

    def test_partial_symptom_trace_lists_explicit_and_missing_inputs(self):
        from utils.logger import PipelineTrace

        trace = PipelineTrace(request_id="test-partial")
        chatbot_service.process("Kulit saya berminyak.", trace=trace)
        self.assertEqual(trace.fuzzy_result["explicit_inputs"], {"keminyakan": 5.0})
        self.assertEqual(
            set(trace.fuzzy_result["missing_inputs"]),
            {"jerawat", "iritasi", "kekeringan"},
        )

    @patch("services.chatbot_service.chat")
    def test_comparison_cues_do_not_filter_catalog_product_names(self, chat):
        result = chatbot_service.process("Bandingkan dua produk moisturizer")
        self.assertGreaterEqual(len(result.products), 2)
        self.assertTrue(all(product.category == "Moisturizer" for product in result.products))
        chat.assert_not_called()

    @patch("services.ollama_service.requests.post")
    def test_ollama_connection_error_is_wrapped(self, post):
        import requests

        post.side_effect = requests.ConnectionError("private host detail")
        with self.assertRaises(OllamaError):
            chat([{"role": "user", "content": "hello"}])

    @patch("services.ollama_service.requests.post")
    def test_ollama_uses_conservative_non_streaming_options(self, post):
        response = post.return_value
        response.json.return_value = {"message": {"content": "{}"}}
        chat([{"role": "user", "content": "apa itu jerawat"}], json_mode=True)
        payload = post.call_args.kwargs["json"]
        self.assertFalse(payload["stream"])
        self.assertEqual(payload["format"], "json")
        self.assertEqual(payload["options"]["temperature"], 0.1)
        self.assertEqual(payload["options"]["num_predict"], 300)
        self.assertIn("top_p", payload["options"])


if __name__ == "__main__":
    unittest.main()
