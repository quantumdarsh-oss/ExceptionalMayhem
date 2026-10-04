"""
Deck 01: The Airlock — Captain Roz's control module.
SOLUTION
"""
from command_station.errors import SensorFaultError, PressureLossError, AirlockSealError

SAFE_MIN, SAFE_MAX = 95.0, 105.0
TARGET_PRESSURE = 101.3
MIN_VALID_SENSORS = 10
CLAMP_IDS = ["L1", "L2", "L3", "L4", "L5"]


RINGS = {
    "A": ["P01", "P02", "P03", "P04", "P05"],
    "B": ["P06", "P07", "P08", "P09", "P10"],
    "C": ["P11", "P12", "P13", "P14", "P15"],
}

def parse_reading(raw):
    """Convert one raw pressure reading into a float, or None if faulty."""
    try:
        value = float(raw)
    except ValueError:
        # Text like "ERR" or "static"
        return None
    except TypeError:
        # A silent sensor sending None
        return None
    else:
        # Only runs if the conversion worked
        if 0 <= value <= 200:
            return value
        return None


def cabin_pressure(readings):
    """Return the average of all valid readings from the 15 sensors."""
    valid = []
    faulty = []

    for sensor_id, raw in readings.items():
        value = parse_reading(raw)
        if value is None:
            faulty.append(sensor_id)
        else:
            valid.append(value)

    if len(valid) < MIN_VALID_SENSORS:
        raise SensorFaultError(sorted(faulty))

    return sum(valid) / len(valid)


def verify_pressure(pressure):
    """Raise PressureLossError if pressure is outside the safe range."""
    if not SAFE_MIN <= pressure <= SAFE_MAX:
        raise PressureLossError(pressure)


def repressurize(cabin):
    """Open the reserve valve and raise cabin pressure to TARGET_PRESSURE."""
    needed = TARGET_PRESSURE - cabin["pressure"]
    if needed <= 0:
        return  # nothing to add

    cabin["valve_open"] = True
    try:
        if cabin["reserve"] < needed:
            # Fail BEFORE changing anything, so the ship isn't half-updated
            raise PressureLossError(cabin["pressure"])
        cabin["reserve"] -= needed
        cabin["pressure"] = TARGET_PRESSURE
    finally:
        # Safety first: the valve always closes, success or failure
        cabin["valve_open"] = False


def check_clamps(lock_sensors):
    """Confirm all five clamps are engaged (EAFP style)."""
    failed = []

    for clamp in CLAMP_IDS:
        try:
            engaged = lock_sensors[clamp]["engaged"]
        except KeyError:
            # Clamp missing entirely, or silent with no "engaged" data
            failed.append(clamp)
        else:
            if engaged is not True:
                failed.append(clamp)

    if failed:
        raise AirlockSealError(failed)
    return True


def emergency_dock(pressure_readings, lock_sensors, cabin, incident_log):
    """Run the full docking sequence. Return "DOCKED" on success."""
    try:
        cabin["pressure"] = cabin_pressure(pressure_readings)

        try:
            verify_pressure(cabin["pressure"])
        except PressureLossError:
            repressurize(cabin)
            verify_pressure(cabin["pressure"])   # confirm the fix worked

        check_clamps(lock_sensors)

    except AirlockSealError as e:
        incident_log.append(f"SEAL FAILURE: {e}")
        raise   # same exception, original traceback preserved

    else:
        return "DOCKED"

    finally:
        incident_log.append("Captain Roz: docking attempt logged")

# --- TASK 8 ------------------------------------------------------------------

class ReserveDepletedError(PressureLossError):
    """Raised when the reserve tank can't supply enough air."""

    def __init__(self, pressure, needed, available):
        super().__init__(pressure)
        self.needed = needed
        self.available = available

    def __str__(self):
        return (f"Reserve depleted: need {self.needed:.1f} kPa, "
                f"only {self.available:.1f} kPa available")

    def __repr__(self):
        return (f"{type(self).__name__}(pressure={self.pressure!r}, "
                f"needed={self.needed!r}, available={self.available!r})")


class BreachDetectedError(PressureLossError):
    """Raised when one ring of sensors shows the hull breach."""

    def __init__(self, ring, pressure):
        super().__init__(pressure)
        self.ring = ring

    def __str__(self):
        return f"Breach detected in Ring {self.ring}: {self.pressure:.1f} kPa"

    def __repr__(self):
        return f"{type(self).__name__}(ring={self.ring!r}, pressure={self.pressure!r})"


# --- Updated Task 4 ----------------------------------------------------------

def repressurize(cabin):
    needed = TARGET_PRESSURE - cabin["pressure"]
    if needed <= 0:
        return

    cabin["valve_open"] = True
    try:
        if cabin["reserve"] < needed:
            raise ReserveDepletedError(cabin["pressure"], needed, cabin["reserve"])
        cabin["reserve"] -= needed
        cabin["pressure"] = TARGET_PRESSURE
    finally:
        cabin["valve_open"] = False


# --- TASK 9 ------------------------------------------------------------------

def locate_breach(readings):
    ring_averages = {}

    for ring, sensor_ids in RINGS.items():
        values = [parse_reading(readings.get(sid)) for sid in sensor_ids]
        valid = [v for v in values if v is not None]
        if valid:
            ring_averages[ring] = sum(valid) / len(valid)

    if not ring_averages:
        return None

    worst_ring = min(ring_averages, key=ring_averages.get)
    if ring_averages[worst_ring] < SAFE_MIN:
        raise BreachDetectedError(worst_ring, ring_averages[worst_ring])
    return None