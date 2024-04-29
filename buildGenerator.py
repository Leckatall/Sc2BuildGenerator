import Zerg
import SC2Constants as SC

STANDARD_ZERG_BUILD = {
    13: "Overlord",
    16: "Hatchery",
    18: "Extractor",
    19: "SpawningPool",
}


class BuildGenerator:
    def __init__(self):
        pass

    def standard_zerg(self):
        ...

    def optimize_build(self, goal):
        ...

    # TODO: fix this terrible garbage
    def generate_build(self):
        BUILD_LENGTH = 10
        zerg_players: list[list[Zerg.ZergPlayer]] = [[Zerg.ZergPlayer()]] + [list() for _ in range(BUILD_LENGTH)]
        for time in range(BUILD_LENGTH):
            for player in zerg_players[time]:
                for action in player.get_possible_actions(0):
                    next_player = Zerg.ZergPlayer(tuple(player.events))
                    if action in SC.ZERG_STRUCTURES:
                        next_player.make_structure(time, action)
                    elif action in SC.ZERG_UNITS:
                        next_player.make_unit(time, action)
                    zerg_players[time + 1].append(next_player)
        for time, current_players in enumerate(zerg_players):
            print(f"@time: {time}")
            for player in current_players:
                print(f"{player.get_units(time) = }")
                print(f"{player.get_structures(time) = }")

build_generatoir = BuildGenerator()
build_generatoir.generate_build()






