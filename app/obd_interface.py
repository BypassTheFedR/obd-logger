import obd
import time
from threading import Thread
from config import PIDS_TO_WATCH

connection = None
connected =False
data_buffer = {}

def try_connect():
    global connection, connected
    while not connected:
        try:
            connection = obd.Async()
            connected = connection.is_connected()
            if connected:
                print("OBD-II connected!")
                setup_async_watchers()
            else:
                print("OBD-II not connected retrying.")
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
    for cmd in PIDS_TO_WATCH:
        connection.watch(cmd, callback=handle_response(cmd))
    connection.start()


