from enum import auto, StrEnum


class CarStatuse(StrEnum):
    ORDERED = auto()
    REPAIRED = auto()
    FREE = auto()


class Brand(StrEnum):
    TOYOTA = auto()
    HONDA = auto()
    FORD = auto()
    BMW = auto()
    MERCEDES_BENZ = auto()
    VOLKSWAGEN = auto()
    NISSAN = auto()
    HYUNDAI = auto()
    AUDI = auto()
    SUBARU = auto()
    KIA = auto()
    TESLA = auto()
    MAZDA = auto()


class Transmission(StrEnum):
    MANUAL = auto()
    AUTOMATIC = auto()
    AUTOMATED_MANUAL = auto()
    HYDROSTATIC = auto()


class FuelType(StrEnum):
    GASOLINE = auto()
    DIESEL = auto()
    ELECTRIC = auto()
    HYBRID = auto()
    NATURAL_GAS = auto()
    ETHANOL = auto()


class Color(StrEnum):
    WHITE = auto()
    BLACK = auto()
    SILVER = auto()
    GRAY = auto()
    BLUE = auto()
    BROWN = auto()
    GOLD = auto()
    BRONZE = auto()


class Category(StrEnum):
    ECONOMY = auto()
    COMPACT = auto()
    SUV = auto()
    CROSSOVER = auto()
    LUXURY = auto()
    SPORTS = auto()
    CONVERTIBLE = auto()
    MINIVAN = auto()
    PICKUP_TRUCK = auto()
