from flask import Blueprint, render_template, jsonify
from app.obd_interface import get_latest_data, get_obd_connection, get_vehicle_vin
from config import AUTO_REFRESH_SECONDS

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template(
        "dashboard.html",
        connected=bool(get_obd_connection()),
        vin=get_vehicle_vin(),
        data=get_latest_data(),
        refresh=AUTO_REFRESH_SECONDS
    )

@main.route('/data')
def data():
    return jsonify(get_latest_data())