
GATHER_RATES_PER_MIN = {
    "mineralsOptimal": 58,
    "mineralsSuboptimal": 27,
    "goldMineralsOptimal": 83,
    "goldMineralsSuboptimal": 34,
    "vespeneOptimal": 61,
    "vespeneSuboptimal": 40,
    "richVespeneOptimal": 122,
    "richVespeneSuboptimal": 80
}

GATHER_RATES = {key: GATHER_RATES_PER_MIN[key]/60 for key in GATHER_RATES_PER_MIN.keys()}

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

    @property
    def max_vespene_workers(self) -> int: return self.vespene_geyser_count * 3

    # Could enable multiple workers to be moved at once?
    def move_workers(self, count: int, to_vespene: bool = True) -> int:
        """
        :return: the amount of workers that were moved
        :rtype: int
        """
        if to_vespene:
            # M -> V
            if self.max_vespene_workers > (self.vespene_workers + count):
                if self.mineral_workers > count:
                    # M(count) -> V
                    self.mineral_workers -= count
                    self.vespene_workers += count
                    return count

                # M -> V & M < count
                self.mineral_workers = 0
                self.vespene_workers += self.mineral_workers
                return self.mineral_workers

            # M(count) > V(max):: M(V(max)) -> V
            movable_workers = self.max_vespene_workers - self.vespene_workers
            self.mineral_workers -= movable_workers
            self.vespene_workers += movable_workers
            return movable_workers

        # V -> M
        if self.vespene_workers > count:
            # V(count) -> M
            self.mineral_workers -= count
            self.vespene_workers += count
            return count

        # V -> M & V < count
        self.vespene_workers = 0
        self.mineral_workers += self.vespene_workers
        return self.vespene_workers

    def add_vespene_geyser(self) -> bool:
        if self.base_count * 2 > self.vespene_geyser_count:
            self.vespene_geyser_count += 1
            return True
        return False

    def get_mineral_income(self) -> float:
        max_optimal_mineral_workers = self.base_count * 16
        max_total_mineral_workers = self.base_count * 24

        if self.mineral_workers <= max_optimal_mineral_workers:
            return self.mineral_workers * GATHER_RATES["mineralsOptimal"]
        max_optimal_income = max_optimal_mineral_workers * GATHER_RATES["mineralsOptimal"]
        suboptimal_workers = min(self.mineral_workers - max_optimal_mineral_workers,
                                 max_total_mineral_workers - max_optimal_mineral_workers)
        return max_optimal_income + (suboptimal_workers * GATHER_RATES["mineralsSuboptimal"])

    def get_vespene_income(self) -> float:
        max_optimal_vespene_workers = self.vespene_geyser_count * 2
        max_total_vespene_workers = self.vespene_geyser_count * 3

        if self.mineral_workers <= max_optimal_vespene_workers:
            return self.mineral_workers * GATHER_RATES["vespeneOptimal"]
        max_optimal_income = max_optimal_vespene_workers * GATHER_RATES["vespeneOptimal"]
        suboptimal_workers = min(self.mineral_workers - max_optimal_vespene_workers,
                                 max_total_vespene_workers - max_optimal_vespene_workers)
        return max_optimal_income + (suboptimal_workers * GATHER_RATES["vespeneSuboptimal"])

















