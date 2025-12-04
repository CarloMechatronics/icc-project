import enum


class StrEnum(str, enum.Enum):
    """String-based Enum for predictable DB persistence."""

    def __str__(self) -> str:  # pragma: no cover - trivial
        return self.value


class GlobalRole(StrEnum):
    USER = "USER"
    SYSTEM_ADMIN = "SYSTEM_ADMIN"


class HomeRole(StrEnum):
    OWNER = "OWNER"
    MEMBER = "MEMBER"
    GUEST = "GUEST"


class DeviceType(StrEnum):
    SENSOR = "SENSOR"
    ACTUATOR = "ACTUATOR"
    HYBRID = "HYBRID"


class DeviceState(StrEnum):
    ON = "ON"
    OFF = "OFF"
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    ACTING = "ACTING"
    READING = "READING"
    ERROR = "ERROR"


class MeasureType(StrEnum):
    TEMPERATURE = "TEMPERATURE"
    HUMIDITY = "HUMIDITY"
    MOTION = "MOTION"


class EventType(StrEnum):
    TRIGGER = "TRIGGER"
    MANUAL = "MANUAL"
    ERROR = "ERROR"


class EventOrigin(StrEnum):
    USER = "USER"
    SYSTEM = "SYSTEM"
    RULE = "RULE"
