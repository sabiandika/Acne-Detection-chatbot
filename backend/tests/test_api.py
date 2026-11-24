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
    def test_chat_contract_is_compatible_and_stateless(self, process):
        response = self.client.post("/api/chat", json={"message": "kulit saya merah"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"ok": True, "reply": "Balasan chatbot"})
        self.assertEqual(process.call_args.args, ("kulit saya merah",))
        self.assertTrue(process.call_args.kwargs["request_id"])

    @unittest.skipUnless(FLASK_AVAILABLE, "Flask is not installed in this environment")
    def test_conversation_history_is_not_accepted_or_stored(self):
        response = self.client.post("/api/chat", json={
            "message": "apa penyebab jerawat?", "history": [{"role": "assistant", "content": "made up"}],
        })
        self.assertEqual(response.status_code, 400)

    @unittest.skipUnless(FLASK_AVAILABLE, "Flask is not installed in this environment")
    @patch("routes.chat_routes.process", return_value="Balasan")
    def test_separate_requests_receive_isolated_request_ids(self, process):
        for message in ("apa itu jerawat?", "bagaimana merawat kulit?"):
            response = self.client.post("/api/chat", json={"message": message})
            self.assertEqual(response.status_code, 200)
        ids = [call.kwargs["request_id"] for call in process.call_args_list]
        self.assertEqual(len(set(ids)), 2)
        self.assertEqual([call.args[0] for call in process.call_args_list], [
            "apa itu jerawat?", "bagaimana merawat kulit?",
        ])

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
