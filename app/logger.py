import csv
import sys
import os
import datetime
from threading import Thread
import time
from app.obd_interface import get_obd_connection, get_latest_data, get_vehicle_vin, filtered_pids

cached_vin = None

# # Add root directory to path {Development}
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# import config

from config import LOG_INTERVAL, PIDS_TO_WATCH, SHUDDER_RPM_THRESHOLD, SHUDDER_DEBOUNCE_SECONDS

last_shudder_time = 0

def log_loop():
    global cached_vin

    # Checks for data directory, creates if it doesn't exist
    os.makedirs("data",exist_ok=True)

    while True:
        if get_obd_connection():
            data = get_latest_data()
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

            cached_vin = get_vehicle_vin()
            safe_vin = cached_vin.replace(":", "_").replace(" ", "_").replace("/", "_")
            today = datetime.date.today().isoformat()  # e.g. '2025-04-04'
            
            file_path = f"data/obd_log_{today}_{safe_vin}.csv"

            file_exists = os.path.isfile(file_path)

            with open(file_path, 'a', newline='') as file:
                writer = csv.writer(file)

                # Write header row one time
                if not file_exists:
                    
                    writer.writerow(["# VIN: {cached_vin}"])
                    header = ['timestamp'] + [cmd.name for cmd in filtered_pids]
                    writer.writerow(header)

                # Build row
                timestamp = datetime.datetime.now().isoformat()
                row = [timestamp] + [data.get(cmd.name) for cmd in filtered_pids]
                writer.writerow(row)
                file.flush()
                   
        time.sleep(LOG_INTERVAL)

# dedicated thread for the logging loop. This lets us automatically shutdown this loop if the main app quits.
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

    with open(file_path, 'a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["timestamp", "rpm", "message"])
        writer.writerow([timestamp, rpm, message])
        file.flush()