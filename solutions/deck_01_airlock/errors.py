"""The ship's anomaly registry. SOLUTION"""


class StarshipError(Exception):
    """Base class for all ship anomalies."""


class SensorFaultError(StarshipError):
    def __init__(self, faulty_sensors):
        self.faulty_sensors = faulty_sensors
        super().__init__(faulty_sensors)

    def __str__(self):
        return f"Too many faulty sensors: {', '.join(self.faulty_sensors)}"

    def __repr__(self):
        return f"{type(self).__name__}(faulty_sensors={self.faulty_sensors!r})"


class PressureLossError(StarshipError):
    def __init__(self, pressure):
        self.pressure = pressure
        super().__init__(pressure)

    def __str__(self):
        return f"Cabin pressure unsafe: {self.pressure:.1f} kPa"

    def __repr__(self):
        return f"{type(self).__name__}(pressure={self.pressure!r})"


class AirlockSealError(StarshipError):
    def __init__(self, failed_clamps):
        self.failed_clamps = failed_clamps
        super().__init__(failed_clamps)

    def __str__(self):
        return f"Clamps not sealed: {', '.join(self.failed_clamps)}"

    def __repr__(self):
        return f"{type(self).__name__}(failed_clamps={self.failed_clamps!r})"