# main script for development purposes without flask to test the backend frame work
from app.obd_interface import start_connection_thread
from app.logger import start_logging_thread
import time

def main():
    print("Starting OBD connection thread...")
    start_connection_thread()

    print("Starting data logger...")
    start_logging_thread()

    print("Systems is running. Press Ctrl+C to exit.")

    try:
        while True:
            time.sleep(1) # keeps main thread alive without hogging CPU??

    except KeyboardInterrupt:
        print("\nShutting down.")

if __name__ == "__main__":
    main()