from flask import Flask
from app.obd_interface import start_connection_thread

def create_app():

    app = Flask(__name__)

    # start the connection to obd
    start_connection_thread()

    # import and register routes, blueprints, etc.

    from app.routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app