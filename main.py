from functools import reduce

import SC2IncomeCalculator as sic
from abc import ABC, abstractmethod
import SC2Constants as SC
from SC2Constants import Expense
from dataclasses import dataclass


@dataclass(frozen=True)
class CurrentIncome:
    time: int
    minerals: float
    vespene: float


@dataclass
class PlayerBalance:
    minerals: int
    vespene: int
    supply: int


@dataclass(frozen=True)
class Event:
    time: int
    name: str
    expense: Expense

    def finished(self, time) -> bool:
        return time < self.time + self.expense.build_time


@dataclass(frozen=True)
class Unit(Event):
    @property
    def supply(self):
        return self.expense.supply


@dataclass(frozen=True)
class Ability(Event):
    def __init__(self, time: int, name: str, cooldown: int):
        super().__init__(time, name, Expense(*[0]*3, cooldown))


class Player(ABC):
    def __init__(self):
        self.income_manager: sic.IncomeManager = sic.IncomeManager()
        self.supply_capacitor_count = 0
        self.bank_statement = []
        self.units: dict
        self.structures: dict
        # self.events[time] ->
        self.events: list[Event] = []

    def get_balance(self, time) -> PlayerBalance:
        total_mined = self.income_manager.get_total_mined(time)
        total_expenses = self.get_total_expenses(time)
        return PlayerBalance(
            int(total_mined.minerals) - total_expenses.minerals,
            int(total_mined.vespene) - total_expenses.vespene,
            self.free_supply(time)
        )

    def get_total_expenses(self, time) -> Expense:
        return reduce((lambda x, y: x.expense + y.expense), self.get_events_before(time))

    def get_events_before(self, time) -> list[Event]:
        for index, event in enumerate(self.events):
            if event.time > time:
                return self.events[:index]
        return self.events

    def add_event(self, event):
        self.events.append(event)
        self.events.sort(key=lambda x: x.time)

    def can_afford(self, time: int, expense) -> bool:
        current_balance = self.get_balance(time)
        if current_balance.minerals < expense.minerals:
            return False
        if current_balance.vespene < expense.vespene:
            return False
        if current_balance.supply < expense.supply:
            return False
        return True

    def free_supply(self, time) -> int:
        return self.get_total_expenses(time).supply

    @abstractmethod
    def start_events(self): ...

    @abstractmethod
    def make_base(self, time): ...

    @abstractmethod
    def make_worker(self, time): ...

    @abstractmethod
    def make_structure(self, time, structure_name): ...

    @abstractmethod
    def make_unit(self, time, unit_name): ...








