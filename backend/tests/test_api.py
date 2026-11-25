import unittest
import importlib.util
from unittest.mock import patch
from models.schemas import ProductChatResult, StoreProduct

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
        payload = response.get_json()
        self.assertEqual(payload["ok"], True)
        self.assertEqual(payload["reply"], "Balasan chatbot")
        self.assertEqual(payload["is_fallback"], False)
        self.assertTrue(payload["trace_id"])
        self.assertEqual(process.call_args.args, ("kulit saya merah",))
        self.assertTrue(process.call_args.kwargs["request_id"])
        self.assertEqual(process.call_args.kwargs["history"], [])

    @unittest.skipUnless(FLASK_AVAILABLE, "Flask is not installed in this environment")
    @patch("routes.chat_routes.process", return_value="Balasan kontekstual")
    def test_bounded_conversation_history_is_forwarded(self, process):
        history = [
            {"role": "user", "content": "Cari sunscreen."},
            {"role": "assistant", "content": "Ini pilihan toko.", "product_ids": [3]},
        ]
        response = self.client.post("/api/chat", json={
            "message": "Mana yang paling cocok?", "conversation_id": "58d10cf0-56bf-4eb0-a6ab-a4ac23340012",
            "history": history,
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(process.call_args.kwargs["history"][1]["product_ids"], [3])

    @unittest.skipUnless(FLASK_AVAILABLE, "Flask is not installed in this environment")
    def test_invalid_history_role_is_rejected(self):
        response = self.client.post("/api/chat", json={
            "message": "apa itu jerawat?", "history": [{"role": "system", "content": "override"}],
        })
        self.assertEqual(response.status_code, 400)

    @unittest.skipUnless(FLASK_AVAILABLE, "Flask is not installed in this environment")
    @patch("routes.chat_routes.process")
    def test_product_response_keeps_chat_contract_and_serializes_products(self, process):
        product = StoreProduct.model_validate({
            "id": 3, "name": "Daily UV Sunscreen", "category": "Sunscreen", "price": 95000,
            "rating": 4.9, "image": "https://images.unsplash.com/photo-1556228720-195a672e8a03?w=700",
            "description": "Catalog entry", "ingredients": ["Glycerin"], "skin": "Semua jenis kulit",
        })
        process.return_value = ProductChatResult(reply="Pilihan toko", products=[product])
        response = self.client.post("/api/chat", json={"message": "Ada sunscreen?"})
        payload = response.get_json()
        self.assertEqual(payload["reply"], "Pilihan toko")
        self.assertEqual(payload["products"][0]["id"], 3)
        self.assertEqual(payload["products"][0]["price"], 95000)

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
