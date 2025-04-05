import sys
import os

venv_path = "/home/pi/obd-venv"
site_packages = os.path.join(venv_path, "lib", "python3.11", "site-packages")  # Adjust Python version if needed

if os.path.exists(site_packages):
    sys.path.insert(0, site_packages)

import obd
import time
import csv

# Connect to OBD-II scanner
connection = obd.OBD("/dev/rfcomm0", fast=False)

# Log file location
log_file = "/home/pi/obd_dtc_log.csv"

# Ensure the log file exists and has a header
if not os.path.exists(log_file) or os.stat(log_file).st_size == 0:
    with open(log_file, "w", newline="") as file:  # Change "a" → "w" to prevent duplicate headers
        writer = csv.writer(file)
        writer.writerow(["Timestamp", "Stored DTCs", "Current DTCs"])

def check_dtc():
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

    if not connection.is_connected():
        print(f"[{timestamp}] OBD-II adapter disconnected. Retrying...")
        connection.reconnect()

        if not connection.is_connected():
            print(f"[{timestamp}] Failed to reconnect. Skipping this cycle.")
            return  # Skip logging if still disconnected
        
    try:
        # Get stored (active) error codes (Mode 03)
        stored_dtc_response = connection.query(obd.commands.GET_DTC)
        stored_dtcs = ", ".join(stored_dtc_response.value) if stored_dtc_response and stored_dtc_response.value else "None"

        # Get current DTCs (Mode 07)
        current_dtc_response = connection.query(obd.commands.GET_CURRENT_DTC)
        current_dtcs = ", ".join(current_dtc_response.value) if current_dtc_response and current_dtc_response.value else "None"

        # Print results
        print(f"[{timestamp}] Stored DTCs: {stored_dtcs} | Current DTCs: {current_dtcs}")

        # Save to log file
        with open(log_file, "a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([timestamp, stored_dtcs, current_dtcs])
    
    except Exception as e:
        print(f"[{timestamp}] Error checking DTCs: {e}")

# Run the check every minute
while True:
    check_dtc()
    time.sleep(60)
