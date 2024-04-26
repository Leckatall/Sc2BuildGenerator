import main
import SC2IncomeCalculator as sic
import SC2Constants as SC


class ZergPlayer(main.Player):
    def __init__(self):
        super().__init__()

    def larvae_count(self, time):
        if time == 0:
            return 3

    def max_supply(self, time) -> int:
        base_count = self.income_manager.get_args_for_time(time).base_count
        return (base_count * 6) + (self.supply_capacitor_count * 8)

    def current_supply(self, time) -> int:
        pass

    def make_base(self, time):
        pass

    def make_supply_capacitor(self, time):
        pass

    def make_worker(self, time):
        pass

    def make_structure(self, time, structure_name):
        expense_report = SC.ZERG_STRUCTURES[structure_name]
        if self.buy(time, expense_report):
            previous_args = self.income_manager.get_args_for_time(time)
            self.income_manager.set_args_at_time(time)

    def make_unit(self, time, unit_name):
        if self.larvae_count(time) < 1:
            return False
        expense_report = SC.ZERG_UNITS[unit_name]