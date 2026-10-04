"""
Deck 01: The Airlock — Captain Roz's control module.

The station is in EMERGENCY STATE. Fix each function so the airlock
survives bad sensor data, restores pressure, and docks the Kestrel
safely, or fails with a clear, specific error.
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
    """
    Convert one raw pressure reading into a float.

    Return the float if it is a number between 0 and 200 (inclusive).
    Return None for anything else: text, None, or out-of-range values.

    Requirements:
      - Handle ValueError and TypeError in SEPARATE except blocks.
      - Do the range check in an `else` block, not inside `try`.
    """
    return float(raw)


def cabin_pressure(readings):
    """
    Return the average of all valid readings from the 15 sensors.

    Raises:
      SensorFaultError: if fewer than MIN_VALID_SENSORS readings are valid.
        Its faulty_sensors must list the IDs of every faulty sensor, sorted.
    """
    ...


def verify_pressure(pressure):
    """
    Raise PressureLossError if pressure is outside SAFE_MIN..SAFE_MAX.
    Return None if it is safe.
    """
    ...




def check_clamps(lock_sensors):
    """
    Confirm all five clamps (CLAMP_IDS) are engaged.

    Use EAFP style: read lock_sensors[clamp]["engaged"] directly and
    handle the KeyError, instead of checking keys first.

    A clamp fails if it is disengaged, has no data, or is missing entirely.

    Raises:
      AirlockSealError: listing every failed clamp, in L1..L5 order.
    Returns:
      True if all clamps are engaged.
    """
    ...


def emergency_dock(pressure_readings, lock_sensors, cabin, incident_log):
    """
    Run the full docking sequence. Return "DOCKED" on success.

    1. Calculate cabin pressure and store it in cabin["pressure"].
    2. If it is unsafe, repressurize and verify again.
    3. Check the clamps.

    Requirements:
      - If anything goes wrong with the clamps, append
        "SEAL FAILURE: <error message>" to incident_log, then re-raise the
        SAME exception with a bare `raise`.
      - Return "DOCKED" from an `else` block.
      - In `finally`, always append "Captain Roz: docking attempt logged".
    """
    ...

# --- TASK 8: Define two custom exceptions -----------------------------------

class ReserveDepletedError:   # TODO: choose the right parent class
    """
    Raised when the reserve tank can't supply enough air.

    It must still be caught by `except PressureLossError`, so any code
    written for Tasks 1-6 keeps working.

    __init__(self, pressure, needed, available)
      - store all three as attributes
    __str__  -> "Reserve depleted: need 41.3 kPa, only 5.0 kPa available"
    __repr__ -> "ReserveDepletedError(pressure=60.0, needed=41.3, available=5.0)"
    """


class BreachDetectedError:    # TODO: choose the right parent class
    """
    Raised when one ring of sensors shows the hull breach.

    It is a kind of pressure loss, so it should also be a PressureLossError.

    __init__(self, ring, pressure)
      - store ring and pressure as attributes
    __str__  -> "Breach detected in Ring C: 86.2 kPa"
    __repr__ -> "BreachDetectedError(ring='C', pressure=86.2)"
    """


# --- Updated Task 4 ---------------------------------------------------------

def repressurize(cabin):
    """
    (Same as before, with one change.)

    If the reserve doesn't hold enough air, raise ReserveDepletedError
    instead of a plain PressureLossError, including how much air was
    needed and how much was available.
    """
    ...


# --- TASK 9 ------------------------------------------------------------------

def locate_breach(readings):
    """
    Find the ring with the lowest average valid pressure.

    - Use parse_reading() and ignore faulty sensors.
    - Skip any ring with no valid readings at all.
    - If the lowest ring average is below SAFE_MIN, raise
      BreachDetectedError(ring, average).
    - Otherwise return None (no breach found).
    """
    ...