import unittest
from unittest.mock import patch

from services import chatbot_service
from services.ollama_service import OllamaError, chat
from utils import text_normalizer


class ChatbotTests(unittest.TestCase):
    def test_normalizes_existing_slang(self):
        self.assertEqual(text_normalizer.normalisasi("muka gw gatel bgt"), "wajah saya gatal banget")

    def test_scope_filter_uses_keyword_path(self):
        with patch("services.scope_filter.llm_score", return_value=8):
            _, label = chatbot_service.scope_filter.classify("muka saya jerawatan")
        self.assertEqual(label, "dalam")

    def test_out_of_scope_message_is_rejected(self):
        with patch.object(chatbot_service.scope_filter, "classify", return_value=(10, "luar")):
            reply = chatbot_service.process("resep nasi goreng")
        self.assertIn("skincare", reply)

    @patch("services.ollama_service.requests.post")
    def test_ollama_connection_error_is_wrapped(self, post):
        import requests

        post.side_effect = requests.ConnectionError("private host detail")
        with self.assertRaises(OllamaError):
            chat([{"role": "user", "content": "hello"}])


if __name__ == "__main__":
    unittest.main()
