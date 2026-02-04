import types
import h_actors
import h_encounter
import h_actions

class Scene:
    def __init__(self, name):
        self.name = name
        self.description = ""
        self.roster = []
        self.event = None
        self.aftermath = ""

# ---------------------------------------------------------------------------
# Scenes
# ---------------------------------------------------------------------------

def start_call (game_state, party):
    scene = start
    h_encounter.report (f"{scene.name} - {scene.description}")

    h_encounter.report (f"Two minions bump into the party. Their eyes reveal their wicked intent.")
    
    party = h_encounter.run_encounter (scene, party)

    if scene.aftermath:
        h_encounter.report(scene.aftermath)

    h_actors.apply_boon(party)
    
    game_state = "last"
    return game_state, party

def last_call (game_state, party):
    scene = last
    h_encounter.report (f"{scene.name} - {scene.description}")
    
    party = h_encounter.run_encounter (scene, party)

    if scene.aftermath:
        h_encounter.report(scene.aftermath)
    
    game_state = "END"
    return game_state, party


def choose_next(options):
    choice = h_actions.choose_options(options)
    return choice if choice else "END"


def scene_100_call(game_state, party):
    scene = scene_100
    h_encounter.report(f"{scene.name} - {scene.description}")

    party = h_encounter.run_encounter(scene, party)

    if scene.aftermath:
        h_encounter.report(scene.aftermath)

    h_actors.apply_boon(party)

    options = {"to the courtyard": "200", "to the walls": "300"}
    game_state = choose_next(options)
    return game_state, party


def scene_200_call(game_state, party):
    scene = scene_200
    h_encounter.report(f"{scene.name} - {scene.description}")

    party = h_encounter.run_encounter(scene, party)

    if scene.aftermath:
        h_encounter.report(scene.aftermath)

    h_actors.apply_boon(party)

    options = {"to the walls": "300", "to the galleries": "400"}
    game_state = choose_next(options)
    return game_state, party


def scene_300_call(game_state, party):
    scene = scene_300
    h_encounter.report(f"{scene.name} - {scene.description}")

    party = h_encounter.run_encounter(scene, party)

    if scene.aftermath:
        h_encounter.report(scene.aftermath)

    h_actors.apply_boon(party)

    options = {"to the galleries": "400", "to the dark halls": "500"}
    game_state = choose_next(options)
    return game_state, party


def scene_400_call(game_state, party):
    scene = scene_400
    h_encounter.report(f"{scene.name} - {scene.description}")

    party = h_encounter.run_encounter(scene, party)

    if scene.aftermath:
        h_encounter.report(scene.aftermath)

    h_actors.apply_boon(party)

    options = {"to the dark halls": "500", "to the pinnacle": "600"}
    game_state = choose_next(options)
    return game_state, party


def scene_500_call(game_state, party):
    scene = scene_500
    h_encounter.report(f"{scene.name} - {scene.description}")

    party = h_encounter.run_encounter(scene, party)

    if scene.aftermath:
        h_encounter.report(scene.aftermath)

    h_actors.apply_boon(party)

    options = {"600": "600"}
    game_state = choose_next(options)
    return game_state, party


def scene_600_call(game_state, party):
    scene = scene_600
    h_encounter.report(f"{scene.name} - {scene.description}")

    party = h_encounter.run_encounter(scene, party)

    h_actors.apply_boon(party)

    game_state = "END"
    return game_state, party

start = Scene ("start")
start.description = "introduction scene"
start.roster = []
start.aftermath = "The hall exhales a cold draft, and the torches gutter as if the stone itself has noticed you."

last = Scene ("last")
last.description = "last scene"
last.roster = []
last.aftermath = "Only the drip of water answers you now. The castle feels older than your fear."

scene_100 = Scene("Entering the gates")
scene_100.description = "A great gate looms before the party, it's open like a gapping maw as if ready to devour them."
scene_100.roster = [h_actors.minion_disruptive, h_actors.minion_aggressive]
scene_100.event = {
    "message": "The party is surprised and slows to react.",
    "effect": "party_slow_first_round",
}
scene_100.aftermath = "They were rail-thin and scar-latticed, fighting like starved dogs. Whatever drives them is older than hunger."

scene_200 = Scene("The courtyard")
scene_200.description = "The vacant courtyard is littered with broken weapons and shattered armor."
scene_200.roster = [h_actors.minion_defensive, h_actors.minion_reactive]
scene_200.event = {
    "message": "The enemy is filled with bloodlust.",
    "effect": "enemy_momentum",
}
scene_200.aftermath = "Half their gear was rust and bone, half was stolen steel. The courtyard is a museum of bad ends."

scene_300 = Scene("Around the walls")
scene_300.description = "Looking around the walls the party sees crumbling battlements and overgrown ramparts."
scene_300.roster = [h_actors.minion_disruptive]
scene_300.event = {
    "message": "A brief calm steels the party's guard.",
    "effect": "party_guard",
}
scene_300.aftermath = "A single fighter held the line like a ritual, not a fight. The stones watch, unmoved."

scene_400 = Scene("The derelict galleries")
scene_400.description = "The galleries are lit by shafts of light from cracks in the ceiling far above."
scene_400.roster = [
    h_actors.minion_aggressive,
    h_actors.minion_defensive,
    h_actors.minion_reactive,
]
scene_400.event = {
    "message": "The foes lock shields and brace themselves.",
    "effect": "enemy_guard",
}
scene_400.aftermath = "Splintered shields, perfect formation. Discipline without hope is a terrible thing to see."

scene_500 = Scene("Descending into the dark")
scene_500.description = "The halls beneath are cold and damp, echoing with the noises of vermin scurrying in the darkness."
scene_500.roster = [
    h_actors.minion_disruptive,
    h_actors.minion_aggressive,
    h_actors.minion_defensive,
    h_actors.minion_reactive,
]
scene_500.event = {
    "message": "A chilling dread leaves the party exposed.",
    "effect": "party_vulnerable",
}
scene_500.aftermath = "They died shivering, not from the cold but from something below. The dark feels awake."

scene_600 = Scene("Reaching the pinnacle")
scene_600.description = "The pinnacle is a narrow spire of stone, overlooking the vast expanse of the mountain king's domain."
scene_600.roster = [
    h_actors.minion_aggressive,
    h_actors.minion_defensive,
    h_actors.minion_reactive,
]
scene_600.event = {
    "message": "At the summit, the enemy surges with momentum.",
    "effect": "enemy_momentum",
}
scene_600.aftermath = "At the height, even the victors looked hollow. This spire drinks more than courage."

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
