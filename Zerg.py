from dataclasses import replace

import main
import SC2IncomeCalculator as sic
import SC2Constants as SC


class Queen(main.Unit):
    cooldown: int

    def inject(self):
        ...

    def spread_creep(self):
        ...


class ZergPlayer(main.Player):
    def __init__(self):
        super().__init__()

        self.structures = {structure: 0 for structure in SC.ZERG_STRUCTURES.keys()}

    def larvae_count(self, time):
        if time == 0:
            return 3

    def max_supply(self, time) -> int:
        base_count = self.income_manager.get_args_for_time(time).base_count
        return (base_count * 6) + (self.supply_capacitor_count * 8)

    def make_base(self, time):
        self.income_manager.change_args_at_time(time, base_count=1)

    def make_worker(self, time):
        pass

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






