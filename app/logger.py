import csv
import logging
import os
import datetime
from threading import Thread
import time
from app.obd_interface import get_obd_connection, get_latest_data, get_vehicle_vin, get_filtered_pids
from config import LOG_INTERVAL, PIDS_TO_WATCH, SHUDDER_RPM_THRESHOLD, SHUDDER_DEBOUNCE_SECONDS

cached_vin = None
last_shudder_time = 0

def log_loop():
    global cached_vin

    time.sleep(2)
    os.makedirs("data", exist_ok=True)

    while not get_filtered_pids():
        logging.debug("[LOG] Waiting for filtered PIDS...")
        time.sleep(0.5)

    while True:
        if get_obd_connection():
            data = get_latest_data()
            today = datetime.date.today().isoformat()
            file_path = f"data/obd_log_{today}.csv"
            file_exists = os.path.isfile(file_path)

            with open(file_path, 'a', newline='') as file:
                writer = csv.writer(file)
                current_pids = get_filtered_pids()

                # Write the header row if necessary
                if not file_exists:
                    writer.writerow(['timestamp'] + [cmd.name for cmd in current_pids])

                # Write data at intervals
                timestamp = datetime.datetime.now().isoformat()

                row = [timestamp] + [data.get(cmd.name, "N/A") for cmd in current_pids]
                # logging.debug(f"[LOG] Writing row: {row}")
                # logging.debug(f"[LOG] Current data: {data}")
                # logging.debug(f"[LOG] Filtered PIDs: {[cmd.name for cmd in filtered_pids]}")        

                writer.writerow(row)
                file.flush()

            rpm = data.get("RPM")
            speed = data.get("SPEED")

            if (
                rpm is not None and
                speed is not None and
                speed <= 1 and
                rpm < SHUDDER_RPM_THRESHOLD and
                time.time() - last_shudder_time > SHUDDER_DEBOUNCE_SECONDS
            ):
                log_shudder_event("auto: rpm dip at idle")
                last_shudder_time = time.time()

            if not cached_vin:
                cached_vin = get_vehicle_vin()
                logging.info(f"[LOG] Detected VIN: {cached_vin}")

        time.sleep(LOG_INTERVAL)

def start_logging_thread():
    t = Thread(target=log_loop, daemon=True)
    t.start()

def log_shudder_event(message="shudder observed"):
    os.makedirs("data", exist_ok=True)
    file_path = "data/event_log.csv"
    file_exists = os.path.isfile(file_path)

    data = get_latest_data()
    rpm = data.get("RPM", "N/A")
    timestamp = datetime.datetime.now().isoformat()

    logging.info(f"[SHUDDER] {message} - RPM: {rpm}")

    with open(file_path, 'a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["timestamp", "rpm", "message"])
        writer.writerow([timestamp, rpm, message])
        file.flush()
