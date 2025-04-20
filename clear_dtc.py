import obd

def connect_obd(port="/dev/rfcomm0"):
    connection = obd.OBD(port)
    if not connection.is_connected():
        print("❌ OBD-II adapter not connected. Check Bluetooth and try again.")
        exit()
    return connection

def read_dtc(connection):
    print("\n🔍 Reading Diagnostic Trouble Codes...\n")

    stored = connection.query(obd.commands.GET_DTC)
    print("Stored DTCs:" if stored and stored.value else "✅ No stored codes.")
    if stored and stored.value:
        for code in stored.value:
            print(code)

    pending = connection.query(obd.commands.GET_CURRENT_DTC)
    print("\nPending DTCs:" if pending and pending.value else "\n✅ No pending codes.")
    if pending and pending.value:
        for code in pending.value:
            print(code)

    if "0A" in connection.supported_commands:
        permanent_cmd = obd.OBDCommand("PERMANENT_DTC", "Get permanent DTCs", b"0A", 6, obd.decoders.dtc)
        permanent = connection.query(permanent_cmd)
        print("\nPermanent DTCs:" if permanent and permanent.value else "\n✅ No permanent codes.")
        if permanent and permanent.value:
            for code in permanent.value:
                print(code)
    else:
        print("\n⚠️ Mode 0A not supported.")

def clear_dtc(connection):
    confirm = input("⚠️ Are you sure you want to clear all DTCs? (y/N): ").lower()
    if confirm == "y":
        response = connection.query(obd.commands.CLEAR_DTC)
        print("✅ DTCs cleared." if response.is_successful() else "❌ Failed to clear DTCs.")
    else:
        print("❎ DTC clear aborted.")

def main():
    conn = connect_obd()

    while True:
        print("\n==== DTC Tool ====")
        print("1) View DTC Codes")
        print("2) Clear DTC Codes")
        print("3) Exit")
        choice = input("Enter your choice: ").strip()

        if choice == "1":
            read_dtc(conn)
        elif choice == "2":
            clear_dtc(conn)
        elif choice == "3":
            print("👋 Exiting...")
            break
        else:
            print("❌ Invalid selection. Please choose 1, 2, or 3.")

if __name__ == "__main__":
    main()