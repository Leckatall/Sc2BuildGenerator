from dataclasses import dataclass


@dataclass(frozen=True)
class Expense:
    minerals: int
    vespene: int
    supply: int
    build_time: int

    def __add__(self, other):
        return Expense(self.minerals + other.minerals,
                       self.vespene + other.vespene,
                       self.supply + other.supply,
                       -1)

    def __radd__(self, other):
        return Expense(self.minerals + other.minerals,
                       self.vespene + other.vespene,
                       self.supply + other.supply,
                       -1)


# Sanitized the data with data lore
ZERG_STRUCTURES = {
    "BanelingNest": Expense(100, 50, 0, 43),
    "CreepTumor": Expense(0, 0, 0, 11),
    "EvolutionChamber": Expense(75, 0, 0, 25),
    "Extractor": Expense(25, 0, 0, 21),
    "GreaterSpire": Expense(100, 150, 0, 71),
    "Hatchery": Expense(300, 0, -6, 71),
    "Hive": Expense(200, 150, 0, 71),
    "HydraliskDen": Expense(100, 100, 0, 29),
    "InfestationPit": Expense(100, 100, 0, 36),
    "Lair": Expense(150, 100, 0, 57),
    "LurkerDen": Expense(100, 150, 0, 57),
    "NydusNetwork": Expense(150, 150, 0, 36),
    "RoachWarren": Expense(150, 0, 0, 39),
    "SpawningPool": Expense(200, 0, 0, 46),
    "SpineCrawler": Expense(100, 0, 0, 36),
    "Spire": Expense(200, 200, 0, 71),
    "SporeCrawler": Expense(75, 0, 0, 21),
    "UltraliskCavern": Expense(150, 200, 0, 46)
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

ZERG_TECH = {
    'Hatchery',

    'SpawningPool',
    'Queen',  # For CreepTumor
    'RoachWarren',
    'BanelingNest'

    'Lair',
    'Overseer',  # For Changeling
    'HydraliskDen',
    'Spire',
    'InfestationPit',
    'LurkerDen',

    'Hive',
    'UltraliskCavern',
    'GreaterSpire',
}

# Assumes we will never lose a piece of tech lol
ZERG_TECH_REQUIREMENTS = {
    "BanelingNest": "SpawningPool",
    "RoachWarren": "SpawningPool",
    "SpineCrawler": "SpawningPool",
    "SporeCrawler": "SpawningPool",
    "Queen": "SpawningPool",
    "ZerglingPair": "SpawningPool",
    "Lair": "SpawningPool",

    "Baneling": "BanelingNest",
    "Roach": "RoachWarren",
    "Ravager": "RoachWarren",
    "CreepTumor": "Queen",

    "Overseer": "Lair",
    "HydraliskDen": "Lair",
    "InfestationPit": "Lair",
    "NydusNetwork": "Lair",
    "Spire": "Lair",
    "Hive": "InfestationPit",

    "LurkerDen": "HydraliskDen",
    "Mutalisk": "Spire",
    "Corruptor": "Spire",

    "SwarmHost": "InfestationPit",
    "Infestor": "InfestationPit",

    "UltraliskCavern": "Hive",

    "Changeling": "Overseer",
    "Hydralisk": "HydraliskDen",
    "Lurker": "LurkerDen",

    "GreaterSpire": "Hive",
    "Viper": "Hive",

    "Ultralisk": "UltraliskCavern",
    "BroodLord": "GreaterSpire"
}

ZERG_MORPHS_FROM = {
    "Baneling": "ZerglingPair",
    "Overseer": "Overlord",
    "Lair": "Hatchery",
    "Hive": "Lair",
    "Lurker": "Hydralisk",
    "GreaterSpire": "Spire",
    "BroodLord": "Corruptor",
}

# print(set(ZERG_TECH_REQUIREMENTS.values()))
