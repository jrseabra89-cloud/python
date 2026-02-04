import types
import h_actors
import h_encounter
import h_actions

class Scene:
    def __init__(self, name):
        self.name = name
        self.description = ""
        self.roster = []

# ---------------------------------------------------------------------------
# Scenes
# ---------------------------------------------------------------------------

def start_call (game_state, party):
    scene = start
    h_encounter.report (f"{scene.name} - {scene.description}")

    h_encounter.report (f"Two minions bump into the party. Their eyes reveal their wicked intent.")
    
    party = h_encounter.run_encounter (scene, party)
    
    game_state = "last"
    return game_state, party

def last_call (game_state, party):
    scene = last
    h_encounter.report (f"{scene.name} - {scene.description}")
    
    party = h_encounter.run_encounter (scene, party)
    
    game_state = "END"
    return game_state, party


def choose_next(options):
    choice = h_actions.choose_options(options)
    return choice if choice else "last"


def scene_100_call(game_state, party):
    scene = scene_100
    h_encounter.report(f"{scene.name} - {scene.description}")

    options = {"200": "200", "300": "300"}
    game_state = choose_next(options)
    return game_state, party


def scene_200_call(game_state, party):
    scene = scene_200
    h_encounter.report(f"{scene.name} - {scene.description}")

    options = {"300": "300", "400": "400"}
    game_state = choose_next(options)
    return game_state, party


def scene_300_call(game_state, party):
    scene = scene_300
    h_encounter.report(f"{scene.name} - {scene.description}")

    options = {"400": "400", "500": "500"}
    game_state = choose_next(options)
    return game_state, party


def scene_400_call(game_state, party):
    scene = scene_400
    h_encounter.report(f"{scene.name} - {scene.description}")

    options = {"500": "500", "600": "600"}
    game_state = choose_next(options)
    return game_state, party


def scene_500_call(game_state, party):
    scene = scene_500
    h_encounter.report(f"{scene.name} - {scene.description}")

    options = {"600": "600"}
    game_state = choose_next(options)
    return game_state, party


def scene_600_call(game_state, party):
    scene = scene_600
    h_encounter.report(f"{scene.name} - {scene.description}")

    game_state = "END"
    return game_state, party

start = Scene ("start")
start.description = "introduction scene"
start.roster = [h_actors.minion, h_actors.grunt]

last = Scene ("last")
last.description = "last scene"
last.roster = [h_actors.nemesis]

scene_100 = Scene("100")
scene_100.description = "empty scene 100"
scene_100.roster = []

scene_200 = Scene("200")
scene_200.description = "empty scene 200"
scene_200.roster = []

scene_300 = Scene("300")
scene_300.description = "empty scene 300"
scene_300.roster = []

scene_400 = Scene("400")
scene_400.description = "empty scene 400"
scene_400.roster = []

scene_500 = Scene("500")
scene_500.description = "empty scene 500"
scene_500.roster = []

scene_600 = Scene("600")
scene_600.description = "empty scene 600"
scene_600.roster = []

scenario_list ={
    "start" : start_call,
    "100" : scene_100_call,
    "200" : scene_200_call,
    "300" : scene_300_call,
    "400" : scene_400_call,
    "500" : scene_500_call,
    "600" : scene_600_call,
    "last" : last_call
}
