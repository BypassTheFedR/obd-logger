import csv
import logging
import os
import datetime
from threading import Thread
import time
from app.obd_interface import get_obd_connection, get_latest_data, get_vehicle_vin, get_filtered_pids
from config import LOG_INTERVAL, SHUDDER_RPM_THRESHOLD, SHUDDER_DEBOUNCE_SECONDS
import obd

cached_vin = None
last_shudder_time = 0
vehicle_active = True

def log_loop():
    global cached_vin, vehicle_active

    time.sleep(2)
    os.makedirs("data", exist_ok=True)

    while not get_filtered_pids():
        logging.debug("[LOG] Waiting for filtered PIDS...")
        time.sleep(0.5)

    while True:
        if get_obd_connection():
            data = get_latest_data()
            if not data:
                if vehicle_active:
                    logging.info("[OBD] Vehicle appears to be off or ECU asleep. Skipping data log.")
                    vehicle_active = False
                time.sleep(LOG_INTERVAL)
                continue
            else:
                if not vehicle_active:
                    logging.info("[OBD] Vehicle appears to be active again.")
                    vehicle_active = True
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

                row = [timestamp] + [format_val(data.get(cmd.name, "N/A")) for cmd in current_pids if "MISFIRE_CYLINDER" not in cmd.name]

                writer.writerow(row)
                file.flush()

                misfire_data = []

                # Check for misfires
                for cmd in get_filtered_pids():
                    if "MISFIRE_CYLINDER" in cmd.name:
                        value = data.get(cmd.name)
                        if hasattr(value, "misfire_count") and value.misfire_count > 0:
                            logging.warning(f"[MISFIRE] {cmd.name}: {value.misfire_count}")
                            misfire_data.append([timestamp, cmd.name, value.misfire_count])
                
                if misfire_data:
                    # os.makedirs("data", exist_ok=True)
                    misfire_path = "data/misfire_log.csv"
                    misfire_file_exists = os.path.isfile(misfire_path)
                    with open(misfire_path, 'a', newline='') as f:
                        writer = csv.writer(f)
                        if not misfire_file_exists:
                            writer.writerow(["timestamp", "cylinder", "misfire_info"])
                        writer.writerows(misfire_data)
                        f.flush()
                        logging.warning(f"[MISFIRE] Logged misfire(s): {misfire_data}")

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
    conn = get_obd_connection()
    freeze_frame = "N/A"

    if conn:
        try:
            freeze = conn.query(obd.commands.FREEZE_DTC)
            if freeze and freeze.value:
                freeze_frame = ", ".join(freeze.value) if isinstance(freeze.value, list) else str(freeze.value)
        except Exception as e:
            logging.warning(f"[OBD] Error retrieving freeze frame DTC: {e}")

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
        f"STFT1: {stft1}, LTFT1: {ltft1}, STFT2: {stft2}, LTFT2: {ltft2}, FreezeFrame: {freeze_frame}"
    )

    with open(file_path, 'a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow([
                "timestamp", "rpm", "speed", "maf",
                "stft1", "ltft1", "stft2", "ltft2", "freeze_frame", "message"
            ])
        writer.writerow([
            timestamp,
            format_val(rpm),
            format_val(speed),
            format_val(maf),
            format_val(stft1),
            format_val(ltft1),
            format_val(stft2),
            format_val(ltft2),
            freeze_frame,
            message
        ])
        file.flush()

def format_val(val):
    if isinstance(val, (int,float)):
        return round(val,2)
    return str(val)
