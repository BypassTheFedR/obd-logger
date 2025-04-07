from app import create_app
from config import WEB_PORT

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=WEB_PORT, debug=True)
