from dataclasses import dataclass, replace


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


@dataclass
class Bank:
    minerals: float
    vespene: float

    def __add__(self, other):
        return Bank(self.minerals + other.minerals, self.vespene + other.vespene)


@dataclass
class IncomeArguments:
    time: int  # Time these arguments were put in place

    base_count: int  # For calculating mineral worker over-saturation
    mineral_workers: int

    vespene_geyser_count: int  # For calculating vespene worker over-saturation
    vespene_workers: int


def get_mineral_income(income_args: IncomeArguments) -> float:
    max_optimal_mineral_workers = income_args.base_count * 16
    max_total_mineral_workers = income_args.base_count * 24

    if income_args.mineral_workers <= max_optimal_mineral_workers:
        return income_args.mineral_workers * GATHER_RATES["mineralsOptimal"]
    max_optimal_income = max_optimal_mineral_workers * GATHER_RATES["mineralsOptimal"]
    suboptimal_workers = min(income_args.mineral_workers - max_optimal_mineral_workers,
                             max_total_mineral_workers - max_optimal_mineral_workers)
    return max_optimal_income + (suboptimal_workers * GATHER_RATES["mineralsSuboptimal"])


def get_vespene_income(income_args: IncomeArguments) -> float:
    max_optimal_vespene_workers = income_args.vespene_geyser_count * 2
    max_total_vespene_workers = income_args.vespene_geyser_count * 3

    if income_args.mineral_workers <= max_optimal_vespene_workers:
        return income_args.mineral_workers * GATHER_RATES["vespeneOptimal"]
    max_optimal_income = max_optimal_vespene_workers * GATHER_RATES["vespeneOptimal"]
    suboptimal_workers = min(income_args.mineral_workers - max_optimal_vespene_workers,
                             max_total_vespene_workers - max_optimal_vespene_workers)
    return max_optimal_income + (suboptimal_workers * GATHER_RATES["vespeneSuboptimal"])

def get_max_vespene_workers(income_args: IncomeArguments) -> int:
    return income_args.vespene_geyser_count * 3

class ResourceManager:
    def __init__(self):
        self.income_args_list: list[IncomeArguments] = [IncomeArguments(0, 1, 12, 0, 0)]

    def get_args_for_time(self, time) -> IncomeArguments:
        for current_income_args, next_income_args in zip(self.income_args_list, self.income_args_list[1:]):
            if current_income_args.time < time < next_income_args:
                return current_income_args
        return self.income_args_list[0]

    def set_args_at_time(self, args):
        self.income_args_list.append(args)
        self.income_args_list.sort(key=lambda x: x.time)

    def get_total_mined(self, time):
        if time == 0:
            return Bank(50, 0)
        income_args = self.get_args_for_time(time)
        duration = time - income_args.time
        return self.get_total_mined(income_args.time) + Bank(get_mineral_income(income_args) * duration,
                                                             get_vespene_income(income_args) * duration)

    def move_workers(self, time, count: int, to_vespene: bool = True) -> int:
        """
        :return: the amount of workers that were moved
        :rtype: int
        """
        current_args = self.get_args_for_time(time)
        if to_vespene:
            # M -> V
            if get_max_vespene_workers(current_args) > (current_args.vespene_workers + count):
                if current_args.mineral_workers > count:
                    # M(count) -> V
                    self.set_args_at_time(replace(current_args,
                                                  time=time,
                                                  mineral_workers=current_args.mineral_workers - count,
                                                  vespene_workers=current_args.vespene_workers + count))
                    return count

                # M -> V & M < count
                self.set_args_at_time(replace(current_args,
                                              time=time,
                                              mineral_workers=0,
                                              vespene_workers=current_args.vespene_workers + current_args.mineral_workers))
                return current_args.mineral_workers

            # M(count) > V(max):: M(V(max)) -> V
            movable_workers = get_max_vespene_workers(current_args) - current_args.vespene_workers
            self.set_args_at_time(replace(current_args,
                                          time=time,
                                          mineral_workers=current_args.mineral_workers - movable_workers,
                                          vespene_workers=current_args.vespene_workers + movable_workers))
            return movable_workers

        # V -> M
        if current_args.vespene_workers > count:
            # V(count) -> M
            self.set_args_at_time(replace(current_args,
                                          time=time,
                                          mineral_workers=current_args.mineral_workers + count,
                                          vespene_workers=current_args.vespene_workers - count))
            return count

        # V -> M & V < count
        self.set_args_at_time(replace(current_args,
                                      time=time,
                                      mineral_workers=current_args.mineral_workers + current_args.vespene_workers,
                                      vespene_workers=0))
        return current_args.vespene_workers

    def add_vespene_geyser(self, time) -> bool:
        current_args = self.get_args_for_time(time)
        if current_args.base_count * 2 > current_args.vespene_geyser_count:
            self.set_args_at_time(replace(current_args,
                                          time=time,
                                          vespene_geyser_count=current_args.vespene_geyser_count + 1))
            return True
        return False




















