# app/web_interface.py
from flask import Flask
from app.routes import routes
from config import WEB_PORT

app = Flask(__name__)
app.register_blueprint(routes)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=WEB_PORT, debug=True)