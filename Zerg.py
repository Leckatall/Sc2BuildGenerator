import main
import SC2IncomeCalculator as sic
import SC2Constants as SC
from dataclasses import dataclass

class ZergStructure(main.Event):
    def __init__(self, time, name):
        super().__init__(time, name, SC.ZERG_STRUCTURES[name])


@dataclass
class Hatch:
    larvae: int
    next_larvae_time: int

    def use_larvae(self, time):
        self.larvae -= 1
        if self.larvae < 3:
            self.next_larvae_time = time + 11

    def update(self, time):
        if self.larvae >= 3:
            self.next_larvae_time = -1
            return
        if self.next_larvae_time == -1:
            self.next_larvae_time = time + 11
            return

        if self.next_larvae_time == time:
            self.larvae += 1
            self.next_larvae_time = time + 11
            return

class ZergUnit(main.Unit):
    def __init__(self, time, name):
        super().__init__(time, name, SC.ZERG_UNITS[name])


class ZergPlayer(main.Player):
    def __init__(self):
        super().__init__()

        self.structures = {structure: 0 for structure in SC.ZERG_STRUCTURES.keys()}
        self.injectable_hatches = 1
        self.start_events()

    def start_events(self):
        self.add_event(ZergStructure(-71, "Hatchery"))
        self.add_event(ZergUnit(-18, "Overlord"))
        [self.add_event(ZergUnit(-12, "Drone")) for _ in range(12)]

    def available_energy(self, time) -> int:
        previous_events = self.get_events_before(time)
        finished_queens = sum([event.name == "Queen" and event.finished(time) for event in previous_events])
        used_queen_abilities = sum([(event.name == "Inject" or event.name == "SpreadCreep") and not event.finished(time)
                                    for event in previous_events])
        return finished_queens - used_queen_abilities

    def available_injects(self, time) -> int:
        previous_events = self.get_events_before(time)
        finished_hatcheries = sum([event.name == "Hatchery" and event.finished(time) for event in previous_events])
        finished_queens = sum([event.name == "Queen" and event.finished(time) for event in previous_events])

        injected_hatcheries = sum([event.name == "Inject" and not event.finished(time) for event in previous_events])
        creep_spread = sum([event.name == "SpreadCreep" and not event.finished(time) for event in previous_events])

        if injected_hatcheries >= min(finished_hatcheries, finished_queens):
            return 0
        return min(finished_hatcheries - injected_hatcheries, finished_queens - (injected_hatcheries + creep_spread))

    def inject(self, time):
        if self.available_injects(time) > 0:
            self.add_event(main.Ability(time, "Inject", 29))

    def max_inject(self, time):
        [self.add_event(main.Ability(time, "Inject", 29)) for _ in range(self.available_injects(time))]

    def spread_creep(self, time) -> bool:
        if self.available_energy(time) > 0:
            self.add_event(main.Ability(time, "SpreadCreep", 29))
            return True
        return False

    def _get_larvae_events(self, time):
        previous_events = self.get_events_before(time)
        larvae_events = ["Hatchery", "Inject"]

        relevant_events = sorted(list(
            filter(lambda x: x.name in larvae_events or type(x) is ZergUnit, previous_events)),
            key=lambda a: a.time)
        events_at_time: dict[int: list[main.Event]] = dict()
        for event in relevant_events:
            if type(event) is ZergUnit:
                events_at_time.setdefault(event.time, []).append(event)
            else:
                events_at_time.setdefault(event.finish_time, []).append(event)
        return events_at_time



    def larvae_count(self, time):
        events_at_time = self._get_larvae_events(time)
        hatcheries = [Hatch(3, -1)]
        for current_time in range(time + 1):
            for events in events_at_time.get(current_time, []):
                if type(events) is ZergUnit:
                    hatcheries[0]["larvae"] -= 1
                elif events.name == "Hatchery":
                    hatcheries.append({"larvae": 0, "next_larvae_time": current_time + 11})
                elif events.name == "Inject":
                    hatcheries[-1]["larvae"] += 3
            for hatch in hatcheries:

            hatcheries.sort(key=lambda x: x.larvae, reverse=True)

        return sum([hatch["larvae"] for hatch in hatcheries])









    def make_base(self, time):
        self.income_manager.change_args_at_time(time, base_count=1)

    def make_worker(self, time):
        self.income_manager.change_args_at_time(time, mineral_workers=1)

    def make_structure(self, time, structure_name):
        expense_report = SC.ZERG_STRUCTURES[structure_name]
        if self.can_afford(time, expense_report) and self.income_manager.kill_worker(time):
            structure_event = main.Event(time, structure_name, expense_report)
            self.add_event(structure_event)

    def make_unit(self, time, unit_name):
        if self.larvae_count(time) < 1:
            return False
        expense_report = SC.ZERG_UNITS[unit_name]
        if self.can_afford(time, expense_report):
            unit_event = main.Unit(time, unit_name, expense_report)
            self.add_event(unit_event)
            if unit_name == "Drone":
                self.make_worker(time)




