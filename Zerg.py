import main
import SC2IncomeCalculator as sic
import SC2Constants as SC
from dataclasses import dataclass


class ZergStructure(main.Structure):
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

    def inject(self):
        self.larvae += 3
        self.next_larvae_time = -1

    def update(self, time):
        # Manages passive larvae production
        if self.next_larvae_time == time:
            self.larvae += 1
            self.next_larvae_time = time + 11 if self.larvae < 3 else -1


class ZergUnit(main.Unit):
    def __init__(self, time, name):
        super().__init__(time, name, SC.ZERG_UNITS[name])


@dataclass(frozen=True)
class ZergUnitMorphed(ZergUnit):
    morphed_from: str


class ZergPlayer(main.Player):
    def __init__(self, events: tuple[main.Event] = ()):
        super().__init__(events)

        # self.structures = {structure: 0 for structure in SC.ZERG_STRUCTURES.keys()}
        self.injectable_hatches = 1
        self.start_events()

    def start_events(self):
        self.add_event(ZergStructure(-71, "Hatchery"))
        self.add_event(ZergUnit(-18, "Overlord"))
        [self.add_event(ZergUnit(-12, "Drone")) for _ in range(12)]
        self.add_event(main.Event(0, "ZergStart", SC.Expense(-1000, 0, 0, 0)))

    def available_energy(self, time) -> int:
        previous_events = self.get_events_before(time)
        finished_queens = sum([event.name == "Queen" and event.finished(time) for event in previous_events])
        used_queen_abilities = sum([(event.name == "Inject" or event.name == "SpreadCreep") and not event.finished(time)
                                    for event in previous_events])
        return finished_queens - used_queen_abilities

    def available_injects(self, time) -> int:
        # It works but I thinnk it could look nicer
        previous_events = self.get_events_before(time)
        finished_hatcheries = sum([event.name == "Hatchery" and event.finished(time) for event in previous_events])
        finished_queens = sum([event.name == "Queen" and event.finished(time) for event in previous_events])

        injected_hatcheries = sum([event.name == "Inject" and not event.finished(time) for event in previous_events])
        creep_spread = sum([event.name == "SpreadCreep" and not event.finished(time) for event in previous_events])

        if injected_hatcheries >= min(finished_hatcheries, finished_queens):
            return 0
        return min(finished_hatcheries - injected_hatcheries, finished_queens - (injected_hatcheries + creep_spread))

    def inject(self, time) -> bool:
        if self.available_injects(time) > 0:
            self.add_event(main.Ability(time, "Inject", 29))
            return True
        return False

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

    def larvae_count(self, time: int) -> int:
        events_at_time = self._get_larvae_events(time)
        hatcheries: list[Hatch] = [Hatch(3, -1)]
        for current_time in range(time + 1):
            for events in events_at_time.get(current_time, []):
                if type(events) is ZergUnit:
                    hatcheries[0].use_larvae(time)
                elif events.name == "Hatchery":
                    hatcheries.append(Hatch(0, current_time + 11))
                elif events.name == "Inject":
                    hatcheries[-1].inject()
            map(lambda hatch: hatch.update(current_time), hatcheries)
            hatcheries.sort(key=lambda x: x.larvae, reverse=True)
        return sum([hatch.larvae for hatch in hatcheries])

    def get_units(self, time: int) -> dict:
        units = super().get_units(time)  # total units made
        for morphed_unit in units.keys() & SC.ZERG_MORPHS_FROM.keys():
            units[SC.ZERG_MORPHS_FROM[morphed_unit]] -= 1
        structure_count = sum(super().get_structures(time).values())
        units["Drone"] -= structure_count - 1  # "-1" to account for the starting hatch
        return units

    def get_structures(self, time):
        structures = super().get_structures(time)  # total structures made
        for morphed_structure in structures.keys() & SC.ZERG_MORPHS_FROM.keys():
            structures[SC.ZERG_MORPHS_FROM[morphed_structure]] -= 1
        return structures

    def get_tech(self, time: int) -> set:
        structures = super().get_structures(time)
        return {structure for structure in structures.keys() if structure in SC.ZERG_TECH}

    def make_base(self, time):
        self.income_manager.change_args_at_time(time + SC.ZERG_STRUCTURES["Hatchery"].build_time, base_count=1)

    def make_worker(self, time):
        self.income_manager.change_args_at_time(time + SC.ZERG_UNITS["Drone"].build_time, mineral_workers=1)

    def can_make_structure(self, time, structure_name) -> bool:
        current_structures = super().get_structures(time)
        # Do we have the tech to make this structure?
        if SC.ZERG_TECH_REQUIREMENTS.get(structure_name, "Hatchery") not in self.get_tech(time):
            return False

        # Checks if it's a morphing structure (which requires a structure to morph from)
        if structure_name in SC.ZERG_MORPHS_FROM.keys():
            if current_structures[SC.ZERG_MORPHS_FROM[structure_name]] < 1:
                return False

        # You can only make 2 extractors per base
        if structure_name == "Extractor":
            if current_structures.get("Extractor", 0) >= 2 * current_structures["Hatchery"]:
                return False

        # Can we afford the unit (minerals, vespene, supply)
        expense_report = SC.ZERG_STRUCTURES[structure_name]
        if self.can_afford(time, expense_report) and self.income_manager.get_total_workers(time) > 0:
            return True

    # NGL make_structure and make_unit could just be one thing I think. Ig for zerg it's a lil necessary?
    # Should we be checking if we can perform the action in the same method we do it? Apparently not lol. I changed it.
    def make_structure(self, time, structure_name) -> bool:
        if self.can_make_structure(time, structure_name):
            # Add the structure
            expense_report = SC.ZERG_STRUCTURES[structure_name]
            structure_event = main.Structure(time, structure_name, expense_report)
            self.add_event(structure_event)
            # Kill the worker required to make the structure in the income manager
            self.income_manager.kill_worker(time)

            if structure_name == "Hatchery":
                # If the structure is a hatchery, add it to the income manager
                self.make_base(time)
            # The structure was made -> True
            return True
        # The structure wasn't made -> False
        return False

    def can_make_unit(self, time, unit_name) -> bool:
        # Do we have the tech to make this unit?
        if SC.ZERG_TECH_REQUIREMENTS.get(unit_name, "Hatchery") not in self.get_tech(time):
            return False

        # Checks if it's a morphing unit (which requires a unit to morph from)
        if unit_name in SC.ZERG_MORPHS_FROM.keys():
            if super().get_units(time)[SC.ZERG_MORPHS_FROM[unit_name]] < 1:
                return False

        # Not a morphing unit so requires a larvae
        elif self.larvae_count(time) < 1:
            return False

        # Can we afford the unit (minerals, vespene, supply)
        expense_report = SC.ZERG_UNITS[unit_name]
        if self.can_afford(time, expense_report):
            return True
        return False

    def make_unit(self, time, unit_name) -> bool:
        if self.can_make_unit(time, unit_name):
            # Add the unit
            expense_report = SC.ZERG_UNITS[unit_name]
            unit_event = main.Unit(time, unit_name, expense_report)
            self.add_event(unit_event)

            if unit_name == "Drone":
                # If the unit is a drone, add it to the income manager
                self.make_worker(time)
            # The unit was made -> True
            return True
        # No unit was made -> False
        return False

    def perform_action(self, time, action) -> bool:
        if action in SC.ZERG_UNITS:
            return self.make_unit(time, action)
        elif action in SC.ZERG_STRUCTURES:
            return self.make_structure(time, action)
        elif action == "Inject":
            return self.inject(time)
        elif action == "MoveToVespene":
            return bool(self.income_manager.move_workers(time, 1))
        elif action == "MoveToMinerals":
            return bool(self.income_manager.move_workers(time, 1, False))
        else:
            print(f"action: {action} not recognised")

    def get_possible_actions(self, time: int):
        possible_actions = []
        # for action in SC.ZERG_UNITS.keys():
        #     if self.can_make_unit(time, action):
        #         # possible_actions.append(lambda x: x.make_unit(time, action))
        #         possible_actions.append(action)
        # for action in SC.ZERG_STRUCTURES.keys():
        #     if self.can_make_structure(time, action):
        #         # possible_actions.append(lambda x: x.make_structure(time, action))
        #         possible_actions.append(action)
        for action in [*SC.ZERG_UNITS, *SC.ZERG_STRUCTURES]:
            if SC.ZERG_TECH_REQUIREMENTS.get(action, "Hatchery") in self.get_tech(time):
                possible_actions.append(action)
        return possible_actions

    def get_potential_actions(self, time: int) -> list[str]:
        potential_actions = []
        for action in [*SC.ZERG_UNITS, *SC.ZERG_STRUCTURES]:
            if SC.ZERG_TECH_REQUIREMENTS.get(action, "Hatchery") in self.get_tech(time):
                potential_actions.append(action)
        current_income_args = self.income_manager.get_args_for_time(time)
        if sic.get_max_vespene_workers(current_income_args) > current_income_args.vespene_workers:
            potential_actions.append("MoveToVespene")
        if current_income_args.vespene_workers > 0:
            potential_actions.append("MoveToMinerals")
        return potential_actions


if __name__ == "__main__":
    while True:
        me = ZergPlayer()
        print("worked")
        eval("ZergPlayer()")
        eval(input("command: "))
