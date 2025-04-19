import obd

def print_codes(title, response):
    if response and response.value:
        print(f"\n{title}:")
        for code in response.value:
            print(f" - {code}")
    else:
        print(f"No {title.lower()} found.")

def clear_dtc(connection):
    confirm = input("⚠️  This will clear all stored and pending DTCs. Type 'YES' to proceed: ")
    if confirm.strip().upper() == 'YES':
        result = connection.query(obd.commands.CLEAR_DTC)
        if result.is_null():
            print("✅ DTCs cleared (response was empty).")
        else:
            print(f"✅ Response: {result.value}")
    else:
        print("❌ Clear DTC operation cancelled.")

def main():
    print("🔌 Connecting to OBD-II adapter...")
    connection = obd.OBD("/dev/rfcomm0")  # Adjust port as needed

    if not connection.is_connected():
        print("❌ OBD-II adapter not connected. Check Bluetooth and try again.")
        return

    # --- Read Stored DTCs (Mode 03)
    stored_dtc_response = connection.query(obd.commands.GET_DTC)
    print_codes("Stored Diagnostic Trouble Codes", stored_dtc_response)

    # --- Read Pending DTCs (Mode 07)
    pending_dtc_response = connection.query(obd.commands.GET_CURRENT_DTC)
    print_codes("Pending Diagnostic Trouble Codes", pending_dtc_response)

    # --- Read Permanent DTCs (Mode 0A)
    if obd.commands.PERMANENT_DTC in connection.supported_commands:
        permanent_dtc_response = connection.query(obd.commands.PERMANENT_DTC)
        print_codes("Permanent Diagnostic Trouble Codes", permanent_dtc_response)
    else:
        print("⚠️ Permanent DTCs (Mode 0A) are not supported by this adapter or vehicle.")

    # --- Read Freeze Frame Data (Mode 02)
    freeze_frame = connection.query(obd.commands.FREEZE_DTC)
    if freeze_frame and freeze_frame.value:
        print("\n📸 Freeze Frame Data:")
        print(freeze_frame.value)
    else:
        print("No freeze frame data available.")

    # --- Optional DTC Clearing
    if input("\nDo you want to clear all DTCs? (y/N): ").strip().lower() == "y":
        clear_dtc(connection)

if __name__ == "__main__":
    main()
