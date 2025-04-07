import obd

# Connect to the OBD-II scanner
connection = obd.OBD("/dev/rfcomm0")

# Command to clear is CLEAR_DTC

if not connection.is_connected():
    print("❌ OBD-II adapter not connected. Check Bluetooth and try again.")
    exit()

# *DANGER* clear the code 
# *DANGER* obd.commands.CLEAR_DTC


# Read stored (active) DTCs (Mode 03)
stored_dtc_response = connection.query(obd.commands.GET_DTC)
if stored_dtc_response and stored_dtc_response.value:
    print("Stored Diagnostic Trouble Codes:")
    for code in stored_dtc_response.value:
        print(code)
else:
    print("No stored error codes found.")

# Read pending DTCs (Mode 07) - FIXED
pending_dtc_response = connection.query(obd.commands.GET_CURRENT_DTC)

if pending_dtc_response and pending_dtc_response.value:
    print("\nPending Diagnostic Trouble Codes:")
    for code in pending_dtc_response.value:
        print(code)
else:
    print("No pending error codes found.")

# Check if Mode 0A (Permanent DTCs) is supported - FIXED
if "0A" in connection.supported_commands:
    permanent_dtc_cmd = obd.OBDCommand(
        "PERMANENT_DTC", "Get permanent DTCs", b"0A", 6, obd.decoders.dtc
    )
    permanent_dtc_response = connection.query(permanent_dtc_cmd)

    if permanent_dtc_response and permanent_dtc_response.value:
        print("\nPermanent Diagnostic Trouble Codes:")
        for code in permanent_dtc_response.value:
            print(code)
    else:
        print("No permanent error codes found.")
else:
    print("⚠️ Permanent DTCs (Mode 0A) are not supported by this adapter or vehicle.")