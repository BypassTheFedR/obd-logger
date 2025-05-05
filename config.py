import obd

LOG_INTERVAL = 2 # seconds between logging events

# Adding mis fire pids and then adding them to the filtered PIDS
MISFIRE_PIDS = [
    obd.commands.MONITOR_MISFIRE_CYLINDER_1,
    obd.commands.MONITOR_MISFIRE_CYLINDER_2,
    obd.commands.MONITOR_MISFIRE_CYLINDER_3,
    obd.commands.MONITOR_MISFIRE_CYLINDER_4,
    obd.commands.MONITOR_MISFIRE_CYLINDER_5,
    obd.commands.MONITOR_MISFIRE_CYLINDER_6,
    obd.commands.MONITOR_MISFIRE_CYLINDER_7,
    obd.commands.MONITOR_MISFIRE_CYLINDER_8,  # If supported
]

# list of parameters to monitor/ log
PIDS_TO_WATCH = [
    obd.commands.ENGINE_LOAD,
    obd.commands.RPM,
    obd.commands.COOLANT_TEMP,
    obd.commands.FUEL_TEMP,
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
    obd.commands.SPEED,
    obd.commands.BAROMETRIC_PRESSURE
] + MISFIRE_PIDS

SHUDDER_RPM_THRESHOLD = 550
SHUDDER_DEBOUNCE_SECONDS = 15
WEB_PORT = 5000
AUTO_REFRESH_SECONDS = 5
OBD_RETRY_FAST_INTERVAL = 5
OBD_RETRY_FAST_DURATION = 60
OBD_RETRY_SLOW_INTERVAL = 60
OBD_PORT = "/dev/rfcomm0"