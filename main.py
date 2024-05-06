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

    @property
    def finish_time(self) -> int:
        return self.time + self.expense.build_time

    def finished(self, time: int) -> bool:
        return time < self.finish_time

    def __repr__(self):
        return f"Event(name: {self.name}, time: {self.time}, expense: {self.expense})"


@dataclass(frozen=True)
class Unit(Event):
    @property
    def supply(self):
        return self.expense.supply


@dataclass(frozen=True)
class Structure(Event):
    # A very useful class not just made to fit in lmao
    ...


@dataclass(frozen=True)
class Ability(Event):
    def __init__(self, time: int, name: str, cooldown: int):
        super().__init__(time, name, Expense(*[0]*3, cooldown))


class Player(ABC):
    def __init__(self, events: tuple[Event] = ()):
        # self.events[time] ->
        self.events: list[Event] = list(events)

        self.income_manager: sic.IncomeManager = sic.IncomeManager()

    def __eq__(self, other):
        return self.events == other.events

    def __repr__(self):
        last_event_time = self.events[-1].time
        return f"""
        Player_type: {type(self)},
        Player_last_event_time: {last_event_time},
        Player_bank: {self.get_balance(last_event_time)},
        Player_total_mined: {self.income_manager.get_total_mined(last_event_time)},
        Player_units: {self.get_units(last_event_time)},
        Player_structures: {self.get_structures(last_event_time)},
        Player_event_count: {len(self.events)},
        Player_last_event: {self.events[-1]}
        """

    def get_balance(self, time) -> PlayerBalance:
        total_mined = self.income_manager.get_total_mined(time)
        total_expenses = self.get_total_expenses(time)
        return PlayerBalance(
            int(total_mined.minerals) - total_expenses.minerals,
            int(total_mined.vespene) - total_expenses.vespene,
            self.free_supply(time)
        )

    def get_total_expenses(self, time) -> Expense:
        previous_events = self.get_events_before(time)
        total_expenses = Expense(0, 0, 0, -1)
        for event in previous_events:
            total_expenses += event.expense
        return total_expenses

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

    def get_supply(self, time: int) -> int:
        previous_events = self.get_events_before(time)
        supply = 0
        for event in previous_events:
            if isinstance(event, Unit):
                supply += event.expense.supply
        return supply

    def free_supply(self, time: int) -> int:
        return -self.get_total_expenses(time).supply

    def current_build(self) -> str:
        return "\n".join([f"@{event.time}: {event.name}" for event in self.events])

    def get_units(self, time: int) -> dict:
        units = dict()
        for event in self.events:
            if event.time > time:
                return units
            if isinstance(event, Unit):
                units.setdefault(event.name, 0)
                units[event.name] += 1
        return units

    def get_structures(self, time):
        # structures is indexed by structure name and returns structure count
        structures: dict[str: int] = dict()
        for event in self.events:
            if event.time > time:
                return structures
            if isinstance(event, Structure):
                structures.setdefault(event.name, 0)
                structures[event.name] += 1
        return structures

    @abstractmethod
    def start_events(self): ...

    @abstractmethod
    def make_base(self, time): ...

    @abstractmethod
    def make_worker(self, time): ...

    @abstractmethod
    def make_structure(self, time, structure_name) -> bool: ...

    @abstractmethod
    def make_unit(self, time, unit_name) -> bool: ...

    @abstractmethod
    def get_tech(self, time: int) -> set: ...

    @abstractmethod
    def get_possible_actions(self, time: int):
        ...


if __name__ == "__main__":
    while True:
        eval(input("command: "))

