import obd
import time
from threading import Thread
from config import PIDS_TO_WATCH

connection = None
connected =False
data_buffer = {}
filtered_pids = []

def try_connect():
    global connection, connected, filtered_pids
    while not connected:
        try:
            connection = obd.Async()
            connected = connection.is_connected()
            if connected:
                print("OBD-II connected!")

                filtered_pids = [pid for pid in PIDS_TO_WATCH if pid in connection.supported_commands]
                print(f"Filtered PIDs ({len(filtered_pids)}):", [pid.name for pid in filtered_pids])

                setup_async_watchers()
            else:
                print("OBD-II not connected, retrying.")
        except Exception as e:
            print(f"Connection error: {e}")
        time.sleep(3) # wait before retrying

def start_connection_thread():
    t = Thread(target=try_connect, daemon=True)
    t.start()

def get_obd_connection():
    return connection if connected else None

def get_latest_data():
    return data_buffer.copy()

def handle_response(cmd):
    def callback(response):
        if response and response.value is not None:
            data_buffer[cmd.name] = response.value.magnitude
        else:
            data_buffer[cmd.name] = None
    return callback

def setup_async_watchers():
    for cmd in filtered_pids:
        connection.watch(cmd, callback=handle_response(cmd))
    connection.start()

def get_vehicle_vin():
    conn = get_obd_connection()
    if conn:
        response = conn.query(obd.commands.VIN)
        if response and response.value:
            return str(response.value)
    return "Unknown VIN"


