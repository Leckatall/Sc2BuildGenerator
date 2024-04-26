from functools import reduce

import SC2IncomeCalculator as sic
from abc import ABC, abstractmethod
import SC2Constants as SC
from dataclasses import dataclass


@dataclass(frozen=True)
class CurrentIncome:
    time: int
    minerals: float
    vespene: float


@dataclass(frozen=True)
class Expense:
    minerals: int
    vespene: int
    supply: int

    def __add__(self, other):
        return Expense(self.minerals + other.minerals,
                       self.vespene + other.vespene,
                       self.supply + other.supply)

@dataclass
class Unit:
    id: int
    name: str
    expense: Expense

    @property
    def supply(self):
        return self.expense.supply

@dataclass
class PlayerBalance:
    minerals: int
    vespene: int
    supply: int


class Player(ABC):
    def __init__(self):
        self.income_manager = sic.IncomeManager()
        self.supply_capacitor_count = 0
        self.bank_statement = []
        self._expenses: list[Expense] = []
        self.units = dict()
        self.structures = dict()
        # self.events[time] ->
        self.events = dict()

    def get_balance(self, time) -> PlayerBalance:
        total_mined = self.income_manager.get_total_mined(time)
        total_expenses = reduce((lambda x,y:x+y), self.get_expenses_before(time))
        return PlayerBalance(
            int(total_mined.minerals) - total_expenses.minerals,
            int(total_mined.vespene) - total_expenses.vespene,
            self.free_supply(time)
        )
        # Expense is jank rn bc it contains time

    def get_expenses_before(self, time):
        for index, expense in enumerate(self._expenses):
            if expense.time > time:
                return self._expenses[:index]
        return self._expenses

    def add_expense(self, expense):
        self._expenses.append(expense)
        for statement in self.bank_statement[expense.time:]:
            statement.minerals -= expense.minerals
            statement.vespene -= expense.vespene
            statement.supply -= expense.supply

    def add_free_supply(self, time, supply_qty):
        for statement in self.bank_statement[time:]:
            statement.supply += supply_qty

    def use_supply(self, time, supply_qty):
        for statement in self.bank_statement[time:]:
            statement.supply -= supply_qty

    def buy(self, time: int, expense) -> bool:
        current_balance = self.get_balance(time)
        if current_balance.minerals < expense.minerals:
            return False
        if current_balance.vespene < expense.vespene:
            return False
        if current_balance.supply < expense.supply:
            return False
        # self.bank_statement[time].minerals -= mineral_cost
        # self.bank_statement[time].vespene -= vespene_cost
        # self.bank_statement[time].supply -= supply_cost
        self.add_expense(expense)
        return True

    def free_supply(self, time) -> int: return self.max_supply(time) - self.used_supply(time)

    @abstractmethod
    def max_supply(self, time) -> int: ...

    @abstractmethod
    def used_supply(self, time) -> int: ...

    @abstractmethod
    def make_base(self, time): ...

    @abstractmethod
    def make_supply_capacitor(self, time): ...

    @abstractmethod
    def make_worker(self, time): ...

    @abstractmethod
    def make_structure(self, time, structure_name): ...

    @abstractmethod
    def make_unit(self, time, unit_name): ...























