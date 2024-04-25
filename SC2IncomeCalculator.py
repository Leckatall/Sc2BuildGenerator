
GATHER_RATES = {
    "mineralsOptimal": 58,
    "mineralsSuboptimal": 27,
    "goldMineralsOptimal": 83,
    "goldMineralsSuboptimal": 34,
    "vespeneOptimal": 61,
    "vespeneSuboptimal": 40,
    "richVespeneOptimal": 122,
    "richVespeneSuboptimal": 80
}

STARTING_VALUES = {
    "base_count": 1,
    "vespene_geyser_count": 0,
    "mineral_workers": 12,
    "vespene_workers": 0
}


class IncomeCalculator:
    def __init__(self):
        self.base_count = STARTING_VALUES["base_count"]
        self.vespene_geyser_count = STARTING_VALUES["vespene_geyser_count"]
        self.mineral_workers = STARTING_VALUES["mineral_workers"]
        self.vespene_workers = STARTING_VALUES["vespene_workers"]

    def add_vespene_geyser(self) -> bool:
        if self.base_count * 2 > self.vespene_geyser_count:
            self.vespene_geyser_count += 1
            return True
        return False

    def get_mineral_income(self) -> int:
        max_optimal_mineral_workers = self.base_count * 16
        max_total_mineral_workers = self.base_count * 24

        if self.mineral_workers <= max_optimal_mineral_workers:
            return self.mineral_workers * GATHER_RATES["mineralsOptimal"]
        max_optimal_income = max_optimal_mineral_workers * GATHER_RATES["mineralsOptimal"]
        suboptimal_workers = min(self.mineral_workers - max_optimal_mineral_workers,
                                 max_total_mineral_workers - max_optimal_mineral_workers)
        return max_optimal_income + (suboptimal_workers * GATHER_RATES["mineralsSuboptimal"])

    def get_vespene_income(self) -> int:
        max_optimal_vespene_workers = self.vespene_geyser_count * 2
        max_total_vespene_workers = self.vespene_geyser_count * 3

        if self.mineral_workers <= max_optimal_vespene_workers:
            return self.mineral_workers * GATHER_RATES["vespeneOptimal"]
        max_optimal_income = max_optimal_vespene_workers * GATHER_RATES["vespeneOptimal"]
        suboptimal_workers = min(self.mineral_workers - max_optimal_vespene_workers,
                                 max_total_vespene_workers - max_optimal_vespene_workers)
        return max_optimal_income + (suboptimal_workers * GATHER_RATES["vespeneSuboptimal"])

















