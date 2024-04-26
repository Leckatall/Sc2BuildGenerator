from dataclasses import dataclass


@dataclass(frozen=True)
class Expense:
    minerals: int
    vespene: int
    supply: int
    build_time: int


# Sanitized the data with data lore
ZERG_STRUCTURES = {
    'Baneling Nest': Expense(100, 50, 0, 43),
    'CreepTumor': Expense(0, 0, 0, 11),
    'Evolution Chamber': Expense(75, 0, 0, 25),
    'Extractor': Expense(25, 0, 0, 21),
    'GreaterSpire': Expense(100, 150, 0, 71),
    'Hatchery': Expense(300, 0, 0, 71),
    'Hive': Expense(200, 150, 0, 71),
    'HydraliskDen': Expense(100, 100, 0, 29),
    'InfestationPit': Expense(100, 100, 0, 36),
    'Lair': Expense(150, 100, 0, 57),
    'LurkerDen': Expense(100, 150, 0, 57),
    'NydusNetwork': Expense(150, 150, 0, 36),
    'RoachWarren': Expense(150, 0, 0, 39),
    'SpawningPool': Expense(200, 0, 0, 46),
    'SpineCrawler': Expense(100, 0, 0, 36),
    'Spire': Expense(200, 200, 0, 71),
    'SporeCrawler': Expense(75, 0, 0, 21),
    'UltraliskCavern': Expense(150, 200, 0, 46)
}

ZERG_UNITS = {
    "Drone": Expense(50, 0, 1, 12),
    "Overlord": Expense(100, 0, -8, 18),
    "Queen": Expense(150, 0, 2, 26),
    "ZerglingPair": Expense(50, 0, 1, 17),
    "Baneling": Expense(25, 25, 0, 14),
    "Roach": Expense(75, 25, 2, 19),
    "Ravager": Expense(25, 75, 1, 12),
    "Overseer": Expense(50, 50, 0, 12),
    "Changeling": Expense(0, 0, 0, 0),
    "Hydralisk": Expense(100, 50, 2, 24),
    "Lurker": Expense(50, 100, 1, 18),
    "Mutalisk": Expense(100, 100, 2, 24),
    "Corruptor": Expense(150, 100, 2, 29),
    "SwarmHost": Expense(100, 75, 3, 29),
    "Infestor": Expense(100, 150, 2, 36),
    "Viper": Expense(100, 200, 3, 29),
    "Ultralisk": Expense(275, 200, 6, 39),
    "BroodLord": Expense(150, 150, 2, 24),
}
