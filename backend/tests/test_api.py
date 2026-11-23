import unittest
import importlib.util
from unittest.mock import patch

FLASK_AVAILABLE = importlib.util.find_spec("flask") is not None
if FLASK_AVAILABLE:
    from app import create_app
else:
    create_app = None


class ApiTests(unittest.TestCase):
    @unittest.skipUnless(FLASK_AVAILABLE, "Flask is not installed in this environment")
    def setUp(self):
        self.client = create_app().test_client()

    @unittest.skipUnless(FLASK_AVAILABLE, "Flask is not installed in this environment")
    @patch("routes.chat_routes.process", return_value="Balasan chatbot")
    def test_chat_contract_is_compatible(self, process):
        response = self.client.post("/api/chat", json={"message": "kulit saya merah"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"ok": True, "reply": "Balasan chatbot"})
        process.assert_called_once_with("kulit saya merah")

    @unittest.skipUnless(FLASK_AVAILABLE, "Flask is not installed in this environment")
    def test_chat_rejects_empty_message(self):
        response = self.client.post("/api/chat", json={"message": "  "})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()["ok"], False)

    @unittest.skipUnless(FLASK_AVAILABLE, "Flask is not installed in this environment")
    @patch("routes.health_routes.is_available", return_value=False)
    def test_health_contract_is_compatible(self, _availability):
        response = self.client.get("/api/health")
        self.assertEqual(response.get_json(), {"backend": True, "ollama": False})


if __name__ == "__main__":
    unittest.main()
