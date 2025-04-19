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
_filtered_pids = []

def try_connect():
    global connection, connected, filtered_pids

    start_time = time.time()

    while True:
        if not connected:
            try:
                logging.info("[OBD] Attempting to connect...")
                connection = obd.OBD(portstr=OBD_PORT, fast=False)
                connected = connection.is_connected()

                if connected:
                    logging.info("[OBD] Connected to OBD-II adapter.")
                    set_filtered_pids([pid for pid in PIDS_TO_WATCH if pid in connection.supported_commands])
                    logging.info(f"[OBD] Watching {len(get_filtered_pids())} supported PIDs: {[pid.name for pid in get_filtered_pids()]}")
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
    conn = get_obd_connection()
    if not conn:
        return {}

    data = {}
    for cmd in get_filtered_pids():
        try:
            response = conn.query(cmd)
            if response and response.value is not None:
                val = response.value.magnitude
                data[cmd.name] = val
                logging.debug(f"[DATA] {cmd.name} = {val}")
            else:
                data[cmd.name] = None
                logging.debug(f"[DATA] {cmd.name} = None")
        except Exception as e:
            data[cmd.name] = None
            logging.warning(f"[OBD] Failed to query {cmd.name}: {e}")
    return data

def get_vehicle_vin():
    conn = get_obd_connection()
    if conn:
        try:
            response = conn.query(obd.commands.VIN)
            if response and response.value:
                return str(response.value)
        except Exception as e:
            logging.warning(f"[OBD] VIN query failed: {e}")
    return "Unknown VIN"

def set_filtered_pids(pids):
    global _filtered_pids
    _filtered_pids = pids

def get_filtered_pids():
    return _filtered_pids