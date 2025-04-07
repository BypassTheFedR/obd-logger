import obd

LOG_INTERVAL = 2 # seconds between logging events

# list of parameters to monitor/ log
PIDS_TO_WATCH = [
    obd.commands.ENGINE_LOAD,
    obd.commands.RPM,
    obd.commands.SHORT_FUEL_TRIM_1,
    obd.commands.LONG_FUEL_TRIM_1,
    obd.commands.SHORT_FUEL_TRIM_2,
    obd.commands.LONG_FUEL_TRIM_2,
    obd.commands.TIMING_ADVANCE,
    obd.commands.O2_B1S1,
    obd.commands.O2_B1S2,
    obd.commands.MAF,
    obd.commands.INTAKE_PRESSURE,
    obd.commands.INTAKE_TEMP,
    obd.commands.THROTTLE_POS,
    obd.commands.SPEED
]

SHUDDER_RPM_THRESHOLD = 550
SHUDDER_DEBOUNCE_SECONDS = 15
WEB_PORT = 5000
AUTO_REFRESH_SECONDS = 5