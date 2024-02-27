from enum import auto, StrEnum


class OrderStatuses(StrEnum):
    ORDERED = auto()
    IN_PROGRES = auto()
    FINISHED = auto()
    CANCELED = auto()


class CarStatuses(StrEnum):
    ORDERED = auto()
    REPAIRED = auto()
    FREE = auto()
