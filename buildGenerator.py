import Zerg
import SC2Constants as SC
import SC2IncomeCalculator as sic
import random
import time

STANDARD_ZERG_BUILD = {
    13: "Overlord",
    16: "Hatchery",
    18: "Extractor",
    19: "SpawningPool",
}

BUILD_LENGTH = 4


def undo_last_action(player):
    last_action = player.events.pop()
    if last_action.name == "Drone" or last_action is Zerg.ZergStructure:
        player.income_manager.self.income_args_list.pop()


class BuildGenerator:
    def __init__(self):
        self.total_players_simulated = 0
        self.actions_explored = 0
        self.builds = set()
        self.all_builds = set()

    def standard_zerg(self):
        ...

    def score_player(self, player, metric=None):
        return player.income_manager.get_total_mined(1000).minerals

    def get_best_player(self, players, metric=None):
        best_player = {"Player": players[0], "Score": self.score_player(players[0])}
        for player in players[1:]:
            current_player_score = self.score_player(player)
            if current_player_score > best_player["Score"]:
                best_player["Player"] = player
                best_player["Score"] = current_player_score
        return best_player["Player"]

    DEFAULT_ACTIONS = {"Drone", "Overlord", "EvolutionChamber", "Extractor", "Hatchery", "SpawningPool"}

    def all_build_orders(self, build_order=None):
        if not build_order:
            return [self.all_build_orders((action,)) for action in self.DEFAULT_ACTIONS]
        if len(build_order) > BUILD_LENGTH:
            self.all_builds.add(build_order)
            return build_order
        possible_actions = {unlocked_action for completed_action in set(build_order)
                            for unlocked_action in SC.ZERG_TECH_UNLOCKS.get(completed_action, [])}
        possible_actions.update(self.DEFAULT_ACTIONS)
        if "SpawningPool" in build_order:
            possible_actions.remove("SpawningPool")
        [self.all_build_orders(build_order + (action,)) for action in possible_actions]

    def execute_action(self, player, action):
        # currently only gonna work for Zerg. Kinda like everything else loll. Ig it's kinda obv which race I play
        last_player_event_time = player.events[-1].time + 1
        current_player_balance = player.get_balance(last_player_event_time + 1)
        current_player_income_args = player.income_manager.get_args_for_time(last_player_event_time)
        if action_expense := (SC.ZERG_STRUCTURES | SC.ZERG_UNITS).get(action, False):
            expense_to_player = SC.Expense(max(action_expense.minerals - current_player_balance.minerals, 0),
                                           max(action_expense.vespene - current_player_balance.vespene, 0),
                                           max(action_expense.supply - current_player_balance.supply, 0),
                                           action_expense.build_time)

            delay_to_afford_action = sic.time_to_gather(expense_to_player, current_player_income_args)
            if not player.perform_action(last_player_event_time + delay_to_afford_action, action):
                # print(f"unable to perform action: {action}")
                return False
        return True

    def dfs_build_gen(self, actions=None):
        zerg_player: Zerg.ZergPlayer = Zerg.ZergPlayer()
        self.total_players_simulated += 1
        self.builds.add(actions)
        if not actions:
            actions: tuple[str] = tuple()
        else:
            for action in actions:
                # do the action
                if not self.execute_action(zerg_player, action):
                    return zerg_player

        if len(actions) > BUILD_LENGTH:
            return zerg_player

        potential_actions = {action: None for action in zerg_player.get_potential_actions(zerg_player.events[-1].time)}
        for action in potential_actions:
            potential_actions[action] = self.dfs_build_gen(actions + (action,))
            # print(f"Action({action}) led to Player: {potential_actions[action]}\n")
        return self.get_best_player(list(potential_actions.values()))

    def speed_build_gen(self, zerg_player: Zerg.ZergPlayer):
        self.actions_explored += 1
        best_score = (list[str], 0)
        potential_actions = zerg_player.get_potential_actions(zerg_player.events[-1].time)
        for action in potential_actions:
            self.execute_action(zerg_player, action)
            self.speed_build_gen(zerg_player)
            score = self.score_player(zerg_player)
            if score > best_score[1]:
                best_score = ([action] + score[0], score[1])
            undo_last_action(zerg_player)
            # print(f"Action({action}) led to Player: {potential_actions[action]}\n")
        return best_score

    # TODO: fix this terrible garbage
    def generate_build(self):
        zerg_player: Zerg.ZergPlayer = Zerg.ZergPlayer()
        potential_actions = zerg_player.get_potential_actions(zerg_player.events[-1].time)


if __name__ == "__main__":
    build_generatoir = BuildGenerator()
    start_recursive = time.perf_counter()
    best_player = build_generatoir.dfs_build_gen()
    recursive_time_taken = time.perf_counter() - start_recursive
    print("-----finished generating------")
    print(f"generated: {build_generatoir.total_players_simulated} players in {recursive_time_taken}")
    print(f"with {len(build_generatoir.builds)} unique builds")
    print(f"with a score of {build_generatoir.score_player(best_player)} the best player was:{best_player}")

    start_v2 = time.perf_counter()
    best_build, best_score = build_generatoir.speed_build_gen(Zerg.ZergPlayer())
    recursive_time_taken = time.perf_counter() - start_v2
    print("-----finished generating------")
    print(f"explored {build_generatoir.actions_explored} actions in {recursive_time_taken}")
    # print(f"with {len(build_generatoir.builds)} unique builds")
    print(f"with a score of {best_score} the best build was {best_build}")

    # start_all_builds = time.perf_counter()
    # all_builds = build_generatoir.all_build_orders()
    # allbuilds_time_taken = time.perf_counter() - start_all_builds
    # print("-------------")
    # print(f"generated: {len(build_generatoir.all_builds)} builds in {allbuilds_time_taken}")
    # print(f"{[','.join([''.join([letter for letter in action if letter.isupper()]).capitalize() for action in build]) for build in build_generatoir.all_builds]}")






