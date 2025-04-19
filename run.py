import logging
import os
from app.obd_interface import start_connection_thread
from app.logger import start_logging_thread
import time

# Setup logging
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.DEBUG,
    filename="logs/runtime.log",
    filemode="a",
    format="%(asctime)s [%(levelname)s] %(message)s"
    # level=logging.INFO
)

def main():
    logging.info("Starting OBD connection thread.")
    start_connection_thread()

    logging.info("Starting data logger thread...")
    start_logging_thread()

    logging.info("System running.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("Shutting down due to keyboard interrupt.")

if __name__ == "__main__":
    main()
