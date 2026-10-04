"""Live readings from Airlock Cabin A at the moment of the emergency."""

PRESSURE_SENSORS = {
    # Ring A: inner cabin
    "P01": "101.2", "P02": "100.9", "P03": "ERR",   "P04": "101.4", "P05": None,
    # Ring B: mid-cabin
    "P06": "99.8",  "P07": "-4.0",  "P08": "100.1", "P09": "88.4",  "P10": "87.9",
    # Ring C: docking collar (near the breach)
    "P11": "86.5",  "P12": "static", "P13": "85.9", "P14": "86.2",  "P15": "1e9",
}

LOCK_SENSORS = {
    "L1": {"engaged": True},
    "L2": {"engaged": True},
    "L3": {"engaged": False},   # clamp jammed by debris
    "L4": {},                   # sensor silent, no data
    "L5": {"engaged": True},
}

CABIN = {
    "pressure": 0.0,     # filled in once calculated
    "reserve": 20.0,     # kPa of emergency air available in the reserve tank
    "valve_open": False,
}
if __name__ == "__main__":
    pass