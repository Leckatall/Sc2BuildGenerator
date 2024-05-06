import math
from dataclasses import dataclass, replace

from SC2Constants import Expense

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

GATHER_RATES = {key: GATHER_RATES_PER_MIN[key] / 60 for key in GATHER_RATES_PER_MIN.keys()}

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


@dataclass(frozen=True)
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


def time_to_gather(expense: Expense, income_args: IncomeArguments) -> int:
    """
    :param expense: should be the expense representing the
    difference between current player balance and what they want to buy
    no value in expense should be less than 0 other than build_time bc it isn't relevant here and thus is -1
    :param income_args:
    :return: time it will take with current income args to afford expense.
    return_key: {-1: "no vespene income but vespene is needed in the expense"
                 >tbd: "after tbd amount of time the time would be reduced by adding a worker"
                 }
    TO-DO?: could implement recursion where time_to_gather(expense.minerals + 50, income_args.workers + 1)?
    """
    if expense.minerals + expense.vespene == 0:
        return 0
    time_to_gather_vespene = 0
    if expense.vespene > 0:
        if income_args.vespene_workers == 0:
            return -1
        time_to_gather_vespene = expense.vespene // get_vespene_income(income_args)

    # No fucking clue why it needs to be type-casted // -> int?!?!
    time_to_gather_minerals: int = math.ceil(expense.minerals / get_mineral_income(income_args)) + 1
    # "Expected type in but got float instead" // -> int?! idk what they on ngl
    return max(time_to_gather_minerals,
               time_to_gather_vespene)


class IncomeManager:
    def __init__(self):
        self.income_args_list: list[IncomeArguments] = [IncomeArguments(0, 1, 12, 0, 0)]

    def get_args_for_time(self, time: int) -> IncomeArguments:
        for current_income_args, next_income_args in zip(self.income_args_list, self.income_args_list[1:]):
            if current_income_args.time < time < next_income_args.time:
                return current_income_args
        return self.income_args_list[0]

    def set_args_at_time(self, time, **kwargs):
        previous_args = self.get_args_for_time(time)

        self.income_args_list.append(replace(previous_args, time=time, **kwargs))
        self.income_args_list.sort(key=lambda x: x.time)

    def change_args_at_time(self, time, **kwargs) -> bool:
        """
        :param time:
        :type time: int
        :param kwargs: IncomeArgs(time) = previous_args + kwargs
        :type kwargs: int
        return important for self.kill_worker()
        :return: if args were changed
        :rtype: bool
        """
        previous_args = self.get_args_for_time(time)

        for key in kwargs.keys():
            kwargs[key] += previous_args.__dict__[key]
            if kwargs[key] < 0:
                return False
        self.income_args_list.append(replace(previous_args, time=time, **kwargs))
        self.income_args_list.sort(key=lambda x: x.time)
        return True

    def get_total_mined(self, time: int) -> Bank:
        if time == 0:
            return Bank(50, 0)
        income_args = self.get_args_for_time(time)
        duration = time - income_args.time
        return self.get_total_mined(income_args.time) + Bank(get_mineral_income(income_args) * duration,
                                                             get_vespene_income(income_args) * duration)

    def move_workers(self, time: int, count: int, to_vespene: bool = True) -> int:
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
                    self.change_args_at_time(time, mineral_workers=-count, vespene_workers=count)
                    return count

                # M -> V & M < count
                self.set_args_at_time(time, mineral_workers=0,
                                      vespene_workers=current_args.vespene_workers + current_args.mineral_workers)
                return current_args.mineral_workers

            # M(count) > V(max):: M(V(max)) -> V
            movable_workers = get_max_vespene_workers(current_args) - current_args.vespene_workers
            self.change_args_at_time(time, mineral_workers=-movable_workers, vespene_workers=movable_workers)
            return movable_workers

        # V -> M
        if current_args.vespene_workers > count:
            # V(count) -> M
            self.change_args_at_time(time, mineral_workers=count, vespene_workers=-count)
            return count

        # V -> M & V < count
        self.set_args_at_time(time, mineral_workers=current_args.mineral_workers + current_args.vespene_workers,
                              vespene_workers=0)
        return current_args.vespene_workers

    def workers_to_vespene(self, time: int, count: int) -> int:
        """
        :return: the amount of workers that were moved
        :rtype: int
        """
        for i in range(count, 0, -count//abs(count)):
            if self.change_args_at_time(time,
                                        mineral_workers=-i,
                                        vespene_workers=i):
                return i
        return 0

    def add_vespene_geyser(self, time: int) -> bool:
        current_args = self.get_args_for_time(time)
        if current_args.base_count * 2 > current_args.vespene_geyser_count:
            self.change_args_at_time(time, vespene_geyser_count=1)
            return True
        return False

    # More Niche Methods
    def get_total_workers(self, time: int) -> int:
        return self.get_args_for_time(time).mineral_workers + self.get_args_for_time(time).vespene_workers

    def kill_worker(self, time) -> bool:
        # Mainly for Zerg structures
        # return: A worker has been killed
        # prioritises killing mineral workers first
        return self.change_args_at_time(time, mineral_workers=-1) or self.change_args_at_time(time, vespene_workers=-1)





