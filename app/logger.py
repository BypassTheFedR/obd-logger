import csv
import logging
import os
import datetime
from threading import Thread
import time
from app.obd_interface import get_obd_connection, get_latest_data, get_vehicle_vin, get_filtered_pids
from config import LOG_INTERVAL, SHUDDER_RPM_THRESHOLD, SHUDDER_DEBOUNCE_SECONDS

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

                row = [timestamp] + [format_val(data.get(cmd.name, "N/A")) for cmd in current_pids]

                writer.writerow(row)
                file.flush()

                # Check for misfires
                for cmd in get_filtered_pids():
                    if "MISFIRE_CYLINDER" in cmd.name:
                        value = data.get(cmd.name)
                        if hasattr(value, "misfire_count") and value.misfire_count > 0:
                            logging.warning(f"[MISFIRE] {cmd.name}: {value.misfire_count}")

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
    maf = data.get("MAF", "N/A")
    speed = data.get("SPEED", "N/A")
    stft1 = data.get("SHORT_FUEL_TRIM_1", "N/A")
    ltft1 = data.get("LONG_FUEL_TRIM_1", "N/A")
    stft2 = data.get("SHORT_FUEL_TRIM_2", "N/A")
    ltft2 = data.get("LONG_FUEL_TRIM_2", "N/A")
    timestamp = datetime.datetime.now().isoformat()

    logging.warning(
        f"[SHUDDER] {message} - RPM: {rpm}, SPEED: {speed}, MAF: {maf} g/s, "
        f"STFT1: {stft1}, LTFT1: {ltft1}, STFT2: {stft2}, LTFT2: {ltft2}"
    )

    with open(file_path, 'a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow([
                "timestamp", "rpm", "speed", "maf",
                "stft1", "ltft1", "stft2", "ltft2", "message"
            ])
        writer.writerow([
            timestamp, rpm, speed, maf,
            stft1, ltft1, stft2, ltft2, message
        ])
        file.flush()

def format_val(val):
    if isinstance(val, (int,float)):
        return round(val,2)
    return val
