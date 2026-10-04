"""
Deck 01: The Airlock — "Pressure Drop"
Diagnostics for Captain Roz's control module.

Run with:  python launch.py 01
"""
import copy

import pytest

from command_station.errors import (
    StarshipError,
    SensorFaultError,
    PressureLossError,
    AirlockSealError,
)
from deck_01_airlock.airlock import (
    parse_reading,
    cabin_pressure,
    verify_pressure,
    repressurize,
    check_clamps,
    emergency_dock,
    locate_breach,
    ReserveDepletedError,
    BreachDetectedError,
)
from deck_01_airlock.station_data import PRESSURE_SENSORS, LOCK_SENSORS

DOCK_LOG = "Captain Roz: docking attempt logged"


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def cabin():
    """A fresh cabin for every test, so one test can't affect another."""
    return {"pressure": 0.0, "reserve": 20.0, "valve_open": False}


@pytest.fixture
def sealed_clamps():
    """All five clamps engaged, as after Roz's manual repair."""
    return {f"L{i}": {"engaged": True} for i in range(1, 6)}


@pytest.fixture
def live_clamps():
    """A copy of the live lock data, safe to modify inside a test."""
    return copy.deepcopy(LOCK_SENSORS)


@pytest.fixture
def healthy_readings():
    """All 15 pressure sensors reading a safe value."""
    return {f"P{i:02}": "101.0" for i in range(1, 16)}


# =============================================================================
# Task 1: parse_reading
# =============================================================================

@pytest.mark.parametrize("raw, expected", [
    ("101.2", 101.2),
    ("0", 0.0),        # lower boundary is valid
    ("200", 200.0),    # upper boundary is valid
    (99.5, 99.5),      # already a number
])
def test_parse_valid_readings(raw, expected):
    assert parse_reading(raw) == expected


@pytest.mark.parametrize("raw", [
    "ERR",       # text        -> ValueError
    "static",    # text        -> ValueError
    None,        # silent      -> TypeError
    "-4.0",      # below range
    "200.1",     # above range
    "1e9",       # converts fine, but impossible
])
def test_parse_faulty_readings_return_none(raw):
    assert parse_reading(raw) is None


# =============================================================================
# Task 2: cabin_pressure
# =============================================================================

def test_live_cabin_pressure():
    # 5 faulty sensors ignored, exactly 10 valid remain
    assert cabin_pressure(PRESSURE_SENSORS) == pytest.approx(93.83, abs=0.01)


def test_cabin_pressure_all_healthy(healthy_readings):
    assert cabin_pressure(healthy_readings) == pytest.approx(101.0)


def test_too_many_faults_raises_sensor_fault():
    readings = {f"P{i:02}": "ERR" for i in range(1, 16)}
    with pytest.raises(SensorFaultError) as exc:
        cabin_pressure(readings)
    assert len(exc.value.faulty_sensors) == 15


def test_faulty_sensors_are_listed_sorted():
    # Built in reverse order: 9 valid (P01-P09), 6 faulty (P10-P15)
    readings = {}
    for i in range(15, 0, -1):
        readings[f"P{i:02}"] = "ERR" if i >= 10 else "100"
    with pytest.raises(SensorFaultError) as exc:
        cabin_pressure(readings)
    assert exc.value.faulty_sensors == ["P10", "P11", "P12", "P13", "P14", "P15"]


# =============================================================================
# Task 3: verify_pressure
# =============================================================================

@pytest.mark.parametrize("pressure", [95.0, 101.3, 105.0])
def test_safe_pressure_passes(pressure):
    assert verify_pressure(pressure) is None


@pytest.mark.parametrize("pressure", [94.9, 105.1, 0.0])
def test_unsafe_pressure_raises(pressure):
    with pytest.raises(PressureLossError) as exc:
        verify_pressure(pressure)
    assert exc.value.pressure == pressure


# =============================================================================
# Task 4 (updated in Task 9): repressurize
# =============================================================================

def test_repressurize_success(cabin):
    cabin["pressure"] = 93.0
    repressurize(cabin)
    assert cabin["pressure"] == pytest.approx(101.3)
    assert cabin["reserve"] == pytest.approx(11.7)
    assert cabin["valve_open"] is False


def test_repressurize_not_needed(cabin):
    cabin["pressure"] = 102.0
    repressurize(cabin)
    assert cabin["pressure"] == 102.0
    assert cabin["reserve"] == 20.0
    assert cabin["valve_open"] is False


def test_valve_closes_even_when_reserve_is_empty():
    cabin = {"pressure": 60.0, "reserve": 5.0, "valve_open": False}
    with pytest.raises(PressureLossError):
        repressurize(cabin)
    assert cabin["valve_open"] is False


def test_failed_repressurize_changes_nothing():
    cabin = {"pressure": 60.0, "reserve": 5.0, "valve_open": False}
    with pytest.raises(PressureLossError):
        repressurize(cabin)
    assert cabin["pressure"] == 60.0
    assert cabin["reserve"] == 5.0


def test_repressurize_raises_reserve_depleted():
    cabin = {"pressure": 60.0, "reserve": 5.0, "valve_open": False}
    with pytest.raises(ReserveDepletedError) as exc:
        repressurize(cabin)
    assert exc.value.pressure == 60.0
    assert exc.value.needed == pytest.approx(41.3)
    assert exc.value.available == 5.0


# =============================================================================
# Task 5: check_clamps
# =============================================================================

def test_all_clamps_sealed(sealed_clamps):
    assert check_clamps(sealed_clamps) is True


def test_live_clamps_report_l3_and_l4():
    with pytest.raises(AirlockSealError) as exc:
        check_clamps(LOCK_SENSORS)
    assert exc.value.failed_clamps == ["L3", "L4"]


def test_missing_clamp_counts_as_failed(sealed_clamps):
    del sealed_clamps["L5"]
    with pytest.raises(AirlockSealError) as exc:
        check_clamps(sealed_clamps)
    assert exc.value.failed_clamps == ["L5"]


def test_every_failure_is_reported_in_order(live_clamps):
    del live_clamps["L1"]              # missing
    live_clamps["L5"] = {}             # silent
    with pytest.raises(AirlockSealError) as exc:
        check_clamps(live_clamps)
    assert exc.value.failed_clamps == ["L1", "L3", "L4", "L5"]


# =============================================================================
# Task 6: emergency_dock
# =============================================================================

def test_dock_failure_is_logged_and_reraised(cabin):
    log = []
    with pytest.raises(AirlockSealError):
        emergency_dock(PRESSURE_SENSORS, LOCK_SENSORS, cabin, log)
    assert log == [
        "SEAL FAILURE: Clamps not sealed: L3, L4",
        DOCK_LOG,
    ]


def test_dock_succeeds_after_repair(cabin, sealed_clamps):
    log = []
    result = emergency_dock(PRESSURE_SENSORS, sealed_clamps, cabin, log)
    assert result == "DOCKED"
    assert log == [DOCK_LOG]


def test_dock_restores_cabin_pressure(cabin, sealed_clamps):
    emergency_dock(PRESSURE_SENSORS, sealed_clamps, cabin, [])
    assert cabin["pressure"] == pytest.approx(101.3)
    assert cabin["reserve"] == pytest.approx(12.53, abs=0.01)
    assert cabin["valve_open"] is False


def test_sensor_fault_passes_through_dock(cabin, sealed_clamps):
    readings = {f"P{i:02}": "ERR" for i in range(1, 16)}
    log = []
    with pytest.raises(SensorFaultError):
        emergency_dock(readings, sealed_clamps, cabin, log)
    assert log == [DOCK_LOG]   # finally ran, but no SEAL FAILURE entry


def test_reserve_depleted_passes_through_dock(sealed_clamps):
    cabin = {"pressure": 0.0, "reserve": 1.0, "valve_open": False}
    log = []
    with pytest.raises(ReserveDepletedError):
        emergency_dock(PRESSURE_SENSORS, sealed_clamps, cabin, log)
    assert log == [DOCK_LOG]
    assert cabin["valve_open"] is False


# =============================================================================
# Task 7: __str__ and __repr__ in starship/errors.py
# =============================================================================

def test_sensor_fault_str_and_repr():
    e = SensorFaultError(["P03", "P05"])
    assert str(e) == "Too many faulty sensors: P03, P05"
    assert repr(e) == "SensorFaultError(faulty_sensors=['P03', 'P05'])"


def test_pressure_loss_str_and_repr():
    e = PressureLossError(93.8)
    assert str(e) == "Cabin pressure unsafe: 93.8 kPa"
    assert repr(e) == "PressureLossError(pressure=93.8)"


def test_pressure_loss_str_rounds_to_one_decimal():
    assert str(PressureLossError(93.8333)) == "Cabin pressure unsafe: 93.8 kPa"


def test_airlock_seal_str_and_repr():
    e = AirlockSealError(["L3", "L4"])
    assert str(e) == "Clamps not sealed: L3, L4"
    assert repr(e) == "AirlockSealError(failed_clamps=['L3', 'L4'])"


def test_all_errors_are_starship_errors():
    for error in (SensorFaultError, PressureLossError, AirlockSealError):
        assert issubclass(error, StarshipError)


# =============================================================================
# Task 8: custom errors in airlock.py
# =============================================================================

def test_new_errors_are_pressure_losses():
    assert issubclass(ReserveDepletedError, PressureLossError)
    assert issubclass(BreachDetectedError, PressureLossError)


def test_reserve_depleted_caught_as_pressure_loss():
    try:
        raise ReserveDepletedError(60.0, 41.3, 5.0)
    except PressureLossError as e:
        assert isinstance(e, ReserveDepletedError)


def test_reserve_depleted_str_and_repr():
    e = ReserveDepletedError(60.0, 41.3, 5.0)
    assert e.pressure == 60.0
    assert str(e) == "Reserve depleted: need 41.3 kPa, only 5.0 kPa available"
    assert repr(e) == "ReserveDepletedError(pressure=60.0, needed=41.3, available=5.0)"


def test_breach_detected_str_and_repr():
    e = BreachDetectedError("C", 86.2)
    assert e.ring == "C"
    assert e.pressure == 86.2
    assert str(e) == "Breach detected in Ring C: 86.2 kPa"
    assert repr(e) == "BreachDetectedError(ring='C', pressure=86.2)"


# =============================================================================
# Task 9: locate_breach
# =============================================================================

def test_locate_breach_finds_ring_c():
    with pytest.raises(BreachDetectedError) as exc:
        locate_breach(PRESSURE_SENSORS)
    assert exc.value.ring == "C"
    assert exc.value.pressure == pytest.approx(86.2, abs=0.01)


def test_no_breach_when_all_rings_safe(healthy_readings):
    assert locate_breach(healthy_readings) is None


def test_ring_with_no_valid_readings_is_skipped(healthy_readings):
    for sid in ["P11", "P12", "P13", "P14", "P15"]:
        healthy_readings[sid] = "ERR"
    assert locate_breach(healthy_readings) is None


def test_no_valid_readings_anywhere_returns_none():
    readings = {f"P{i:02}": "ERR" for i in range(1, 16)}
    assert locate_breach(readings) is None