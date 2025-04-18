import obd
import time
import logging
from threading import Thread
from config import (
    PIDS_TO_WATCH,
    OBD_RETRY_FAST_INTERVAL,
    OBD_RETRY_SLOW_INTERVAL,
    OBD_RETRY_FAST_DURATION,
    OBD_PORT
)

connection = None
connected = False
data_buffer = {}
filtered_pids = []

def try_connect():
    global connection, connected, filtered_pids

    start_time = time.time()
    
    while True:
        if not connected:
            try:
                logging.info("[OBD] Attempting to connect...")
                connection = obd.Async(portstr=OBD_PORT, fast=False)
                connected = connection.is_connected()

                if connected:
                    logging.info("[OBD] Connected to OBD-II adapter.")
                    filtered_pids = [pid for pid in PIDS_TO_WATCH if pid in connection.supported_commands]
                    logging.info(f"[OBD] Watching {len(filtered_pids)} supported PIDs: {[pid.name for pid in filtered_pids]}")
                    setup_async_watchers()
                    start_time = time.time()
                else:
                    logging.warning("[OBD] Connection failed.")
            except Exception as e:
                logging.error(f"[OBD] Exception during connection: {e}")
            
            elapsed = time.time() - start_time
            if elapsed < OBD_RETRY_FAST_DURATION:
                time.sleep(OBD_RETRY_FAST_INTERVAL)
            else:
                time.sleep(OBD_RETRY_SLOW_INTERVAL)
        else:
            if not connection.is_connected():
                logging.warning("[OBD] Lost connection. Will attempt to reconnect...")
                connected = False
                connection.close()

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