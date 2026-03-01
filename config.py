"""
config.py — Load inverter and exporter settings from the .env file.
"""
import os
from dotenv import load_dotenv

load_dotenv()

INVERTER_IP          = os.getenv("INVERTER_IP", "192.168.0.6")
INVERTER_SERIAL      = int(os.getenv("INVERTER_SERIAL", "0"))
INVERTER_PORT        = int(os.getenv("INVERTER_PORT", "8899"))
INVERTER_MB_SLAVE_ID = int(os.getenv("INVERTER_MB_SLAVE_ID", "1"))
EXPORTER_PORT        = int(os.getenv("EXPORTER_PORT", "9105"))
POLL_INTERVAL        = int(os.getenv("POLL_INTERVAL", "5"))
