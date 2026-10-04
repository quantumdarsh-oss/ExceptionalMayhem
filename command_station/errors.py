"""
The ship's anomaly registry.

TASK 7: Each exception currently stores its data but has no readable
message. Add __str__ and __repr__ to every class below.

  __str__  -> for Captain Roz: a clear, human-readable message.
  __repr__ -> for engineers debugging: shows the class and its data,
              looking like the code that would recreate it.

Tip: in __repr__, use type(self).__name__ instead of hard-coding the
class name, so subclasses get a correct repr for free.
"""


class StarshipError(Exception):
    """Base class for all ship anomalies."""


class SensorFaultError(StarshipError):
    def __init__(self, faulty_sensors):
        self.faulty_sensors = faulty_sensors
        super().__init__(faulty_sensors)

    # TODO __str__  -> "Too many faulty sensors: P03, P05"
    # TODO __repr__ -> "SensorFaultError(faulty_sensors=['P03', 'P05'])"


class PressureLossError(StarshipError):
    def __init__(self, pressure):
        self.pressure = pressure
        super().__init__(pressure)

    # TODO __str__  -> "Cabin pressure unsafe: 93.8 kPa"   (1 decimal place)
    # TODO __repr__ -> "PressureLossError(pressure=93.8)"   (use !r)


class AirlockSealError(StarshipError):
    def __init__(self, failed_clamps):
        self.failed_clamps = failed_clamps
        super().__init__(failed_clamps)

    # TODO __str__  -> "Clamps not sealed: L3, L4"
    # TODO __repr__ -> "AirlockSealError(failed_clamps=['L3', 'L4'])"().__init__(f"Clamps not sealed: {', '.join(failed_clamps)}")