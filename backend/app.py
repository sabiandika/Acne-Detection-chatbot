"""Flask application entry point."""

from flask import Flask
from flask_cors import CORS

try:
    from dotenv import load_dotenv
except ImportError:  # Keep app importable before optional local environment setup.
    load_dotenv = lambda: None

load_dotenv()

from config import FLASK_DEBUG, FLASK_HOST, FLASK_PORT  # noqa: E402
from routes.chat_routes import chat_blueprint  # noqa: E402
from routes.health_routes import health_blueprint  # noqa: E402
from utils.logger import configure_logging  # noqa: E402


def create_app():
    app = Flask(__name__)
    app.config["MAX_CONTENT_LENGTH"] = 32 * 1024
    CORS(app)
    app.register_blueprint(chat_blueprint)
    app.register_blueprint(health_blueprint)
    configure_logging()
    return app


app = create_app()


if __name__ == "__main__":
    print(f"Backend API running at http://{FLASK_HOST}:{FLASK_PORT}")
    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=FLASK_DEBUG)
