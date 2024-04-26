import SC2IncomeCalculator as sic
from abc import ABC, abstractmethod
import SC2Constants as sc
from dataclasses import dataclass


@dataclass(frozen=True)
class CurrentIncome:
    time: int
    minerals: float
    vespene: float


@dataclass(frozen=True)
class Expense:
    time: int
    minerals: int
    vespene: int
    supply: int




@dataclass
class GameState:
    minerals: float
    vespene: float
    free_supply: int


class Player(ABC):
    def __init__(self):
        self.time = 0
        self.income_generator = sic.IncomeCalculator()
        self.supply_capacitor_count = 0
        # list of CurrentIncome. resources becomes (time - self.income[-1]["time"]) * self.income[-1]["resource"]
        self.incomes = [CurrentIncome(0,
                                      self.income_generator.get_mineral_income(),
                                      self.income_generator.get_vespene_income())]
        self.bank_statement = [Bank(50, 0, self.free_supply(0))]
        self._expenses: list[Expense] = []
        self.units = dict()
        self.structures = dict()
        # self.events[time] ->
        self.events = dict()

    def update_bank(self, time):
        # Calculate total money generated
        current_time = 1
        for current_income, future_income in zip(self.incomes, self.incomes[1:]):
            while current_time < min(time, future_income.time):
                previous_balance = self.bank_statement[current_time - 1]
                self.bank_statement[current_time] = Bank(previous_balance.minerals + current_income.minerals,
                                                         previous_balance.vespene + current_income.vespene,
                                                         previous_balance.free_supply)
                # Alternative
                # current_balance = previous_balance
                # current_balance.minerals += current_income.minerals
                # current_balance.vespene += current_income.vespene
                # self.bank_statement[current_time] = current_balance

                current_time += 1

        # Account for _expenses
        for expense in self._expenses:
            for statement in self.bank_statement[expense.time:time + 1]:
                statement.minerals -= expense.minerals
                statement.vespene -= expense.vespene
                statement.free_supply -= expense.supply

    def add_expense(self, expense):
        self._expenses.append(expense)
        for statement in self.bank_statement[expense.time:]:
            statement.minerals -= expense.minerals
            statement.vespene -= expense.vespene
            statement.free_supply -= expense.supply

    def add_free_supply(self, time, supply_qty):
        for statement in self.bank_statement[time:]:
            statement.free_supply += supply_qty

    def use_supply(self, time, supply_qty):
        for statement in self.bank_statement[time:]:
            statement.free_supply -= supply_qty

    def buy(self, time, mineral_cost, vespene_cost, supply_cost) -> bool:
        if not self.bank_statement[time]:
            self.update_bank(time)
        if self.bank_statement[time].minerals < mineral_cost:
            return False
        if self.bank_statement[time].vespene < vespene_cost:
            return False
        if self.bank_statement[time].free_supply < supply_cost:
            return False
        # self.bank_statement[time].minerals -= mineral_cost
        # self.bank_statement[time].vespene -= vespene_cost
        # self.bank_statement[time].supply -= supply_cost
        self.add_expense(Expense(time, mineral_cost, vespene_cost, supply_cost))
        return True

    # DP opportunity
    def total_minerals(self, time):
        minerals = 50
        income_iterator = iter(self.incomes)
        current_income = income_iterator.__next__()
        while (future_income := income_iterator.__next__()).time < time:
            minerals += current_income.minerals * (future_income.time - current_income.time)
            current_income = future_income
        return minerals + (current_income.minerals * (time - current_income.time))

    def total_vespene(self, time, incomes_processed=1):
        if time == 0:
            return 0
        income = self.income[-incomes_processed]
        if income.time > time:
            return self.total_vespene(time, incomes_processed + 1)
        return (income.vespene * (time - income.time)) + self.total_vespene(income.time, incomes_processed + 1)

    def move_worker(self, time, to_vespene: bool = True):
        self.income_generator.move_workers(1, to_vespene)



    def free_supply(self, time) -> int: return self.max_supply(time) - self.used_supply(time)
    @abstractmethod
    def max_supply(self, time) -> int: ...

    @abstractmethod
    def used_supply(self, time) -> int: ...

    @abstractmethod
    def make_base(self): ...

    @abstractmethod
    def make_supply_capacitor(self): ...

    @abstractmethod
    def make_worker(self): ...

    @abstractmethod
    def make_structure(self, structure_name): ...

    @abstractmethod
    def make_unit(self): ...


HATCH_SUPPLY = 6
OVERLORD_SUPPLY = 8


class ZergPlayer(Player):
    def __init__(self):
        super().__init__()
        self.spent_larvae = 0

    def larvae_count(self, time):
        if time == 0:
            return 3

    @property
    def max_supply(self) -> int:
        return (self.base_count * 6) + (self.supply_capacitor_count * 8)

    @property
    def current_supply(self) -> int:
        pass

    def make_base(self):
        pass

    def make_supply_capacitor(self):
        pass

    def make_worker(self):
        pass

    def make_structure(self, time, structure_name):
        structure_info = sc.ZERG_STRUCTURES[structure_name]
        if self.buy(structure_info["Minerals"], structure_info["Vespene"], 0):
            self.incomes.append(CurrentIncome(time, ))

    def make_unit(self, time, unit_id):
        if self.larvae_count(time) < 1:
            return False
        if





















