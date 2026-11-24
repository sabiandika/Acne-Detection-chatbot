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
        self.assertEqual(chatbot_service.scope_filter.classify_intent("muka saya jerawatan"), "symptom_analysis")
        self.assertEqual(chatbot_service.scope_filter.classify_intent("Siapa presiden Indonesia?"), "out_of_scope")
        self.assertEqual(chatbot_service.scope_filter.classify_intent("berapa dosis obat jerawat"), "unsafe_medical_request")

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
        self.assertEqual(len(messages), 3)
        self.assertEqual(messages[0]["role"], "system")
        self.assertIn("Jangan mengarang", messages[0]["content"])
        self.assertEqual(messages[1]["role"], "user")
        self.assertEqual(messages[2]["role"], "system")

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
