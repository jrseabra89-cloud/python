import types
import random
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
        self.roster_options = []

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

    if scene.roster_options:
        scene.roster = random.choice(scene.roster_options)

    party = h_encounter.run_encounter(scene, party)

    if scene.aftermath:
        h_encounter.report(scene.aftermath)

    h_actors.apply_boon(party)

    options = {"to the courtyard": "150", "to the walls": "300"}
    game_state = choose_next(options)
    return game_state, party


def scene_150_call(game_state, party):
    scene = scene_150
    h_encounter.report(f"{scene.name} - {scene.description}")

    if scene.aftermath:
        h_encounter.report(scene.aftermath)

    options = {"to the courtyard": "200"}
    game_state = choose_next(options)
    return game_state, party


def scene_200_call(game_state, party):
    scene = scene_200
    h_encounter.report(f"{scene.name} - {scene.description}")

    if scene.roster_options:
        scene.roster = random.choice(scene.roster_options)

    party = h_encounter.run_encounter(scene, party)

    if scene.aftermath:
        h_encounter.report(scene.aftermath)

    h_actors.apply_boon(party)

    options = {"to the walls": "250", "to the galleries": "400"}
    game_state = choose_next(options)
    return game_state, party


def scene_250_call(game_state, party):
    scene = scene_250
    h_encounter.report(f"{scene.name} - {scene.description}")

    h_encounter.report(
        "A shrine of human sacrifice stands here, its basin crusted dark and old."
    )

    shrine_options = {
        "destroy the shrine": "destroy",
        "spill blood as an offering": "offer",
        "leave it untouched": "leave",
    }
    choice = h_actions.choose_options(shrine_options)

    if choice == "offer":
        h_encounter.report("The offering is accepted. A boon stirs within the party.")
        h_actors.apply_boon(party)
    elif choice == "destroy":
        party_inventory = party[0].inventory if party else None
        items = party_inventory.get_items() if party_inventory else []
        if items:
            lost_index = random.randint(0, len(items) - 1)
            lost_item = items[lost_index]
            party_inventory.remove_item(lost_index)
            h_encounter.report(f"The shrine shatters. {lost_item.name} is lost in the ruin.")
        else:
            h_encounter.report("The shrine collapses into dust. There was nothing to lose.")
    else:
        h_encounter.report("You turn away and let the shrine's silence linger.")

    options = {"to the walls": "300"}
    game_state = choose_next(options)
    return game_state, party


def scene_300_call(game_state, party):
    scene = scene_300
    h_encounter.report(f"{scene.name} - {scene.description}")

    if scene.roster_options:
        scene.roster = random.choice(scene.roster_options)

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

    if scene.roster_options:
        scene.roster = random.choice(scene.roster_options)

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

    if scene.roster_options:
        scene.roster = random.choice(scene.roster_options)

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

    if scene.roster_options:
        scene.roster = random.choice(scene.roster_options)

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
scene_100.roster_options = [
    [h_actors.minion_disruptive, h_actors.minion_aggressive],
    [h_actors.minion_disruptive_2, h_actors.minion_aggressive_2],
    [h_actors.minion_disruptive, h_actors.minion_reactive],
    [h_actors.minion_aggressive, h_actors.minion_reactive_2],
]
scene_100.event = {
    "message": "The party is surprised and slows to react.",
    "effect": "party_slow_first_round",
}
scene_100.aftermath = "They were rail-thin and scar-latticed, fighting like starved dogs. Whatever drives them is older than hunger."

scene_150 = Scene("The threshold")
scene_150.description = "A narrow passage bends toward the courtyard. Someone etched a message here 'stones too can lie'"
scene_150.aftermath = "For a moment the hall is quiet, and your footsteps are the only proof you are not alone."

scene_200 = Scene("The courtyard")
scene_200.description = "The vacant courtyard is littered with broken weapons and shattered armor."
scene_200.roster_options = [
    [h_actors.minion_defensive, h_actors.minion_reactive],
    [h_actors.minion_defensive_2, h_actors.minion_reactive_2],
    [h_actors.minion_defensive, h_actors.minion_aggressive],
    [h_actors.minion_defensive_3, h_actors.minion_reactive_3],
]
scene_200.event = {
    "message": "The enemy is filled with bloodlust.",
    "effect": "enemy_momentum",
}
scene_200.aftermath = "Half their gear was rust and bone, half was stolen steel. The courtyard is a museum of bad ends."

scene_250 = Scene("The blood shrine")
scene_250.description = "Between broken columns lies a crude altar, the stone beneath it stained black."

scene_300 = Scene("Around the walls")
scene_300.description = "Looking around the walls the party sees crumbling battlements and overgrown ramparts."
scene_300.roster_options = [
    [h_actors.minion_disruptive],
    [h_actors.minion_disruptive_2],
    [h_actors.minion_reactive],
    [h_actors.minion_reactive_2],
]
scene_300.event = {
    "message": "A brief calm steels the party's guard.",
    "effect": "party_guard",
}
scene_300.aftermath = "A single fighter held the line like a ritual, not a fight. The stones watch, unmoved."

scene_400 = Scene("The derelict galleries")
scene_400.description = "The galleries are lit by shafts of light from cracks in the ceiling far above."
scene_400.roster_options = [
    [h_actors.minion_aggressive, h_actors.minion_defensive, h_actors.minion_reactive],
    [h_actors.minion_aggressive_2, h_actors.minion_defensive_2, h_actors.minion_reactive_2],
    [h_actors.minion_aggressive_3, h_actors.minion_defensive_3, h_actors.minion_reactive_3],
    [h_actors.minion_aggressive, h_actors.minion_defensive_2, h_actors.minion_reactive_3],
]
scene_400.event = {
    "message": "The foes lock shields and brace themselves.",
    "effect": "enemy_guard",
}
scene_400.aftermath = "Splintered shields, perfect formation. Discipline without hope is a terrible thing to see."

scene_500 = Scene("Descending into the dark")
scene_500.description = "The halls beneath are cold and damp, echoing with the noises of vermin scurrying in the darkness."
scene_500.roster_options = [
    [h_actors.minion_disruptive, h_actors.minion_aggressive, h_actors.minion_defensive, h_actors.minion_reactive],
    [h_actors.minion_disruptive_2, h_actors.minion_aggressive_2, h_actors.minion_defensive_2, h_actors.minion_reactive_2],
    [h_actors.minion_disruptive_3, h_actors.minion_aggressive_3, h_actors.minion_defensive_3, h_actors.minion_reactive_3],
    [h_actors.minion_disruptive, h_actors.minion_aggressive_2, h_actors.minion_defensive_3, h_actors.minion_reactive],
]
scene_500.event = {
    "message": "A chilling dread leaves the party exposed.",
    "effect": "party_vulnerable",
}
scene_500.aftermath = "They died shivering, not from the cold but from something below. The dark feels awake."

scene_600 = Scene("Reaching the pinnacle")
scene_600.description = "The pinnacle is a narrow spire of stone, overlooking the vast expanse of the mountain king's domain."
scene_600.roster_options = [
    [h_actors.minion_aggressive, h_actors.minion_defensive, h_actors.minion_reactive],
    [h_actors.minion_aggressive_2, h_actors.minion_defensive_2, h_actors.minion_reactive_2],
    [h_actors.minion_aggressive_3, h_actors.minion_defensive_3, h_actors.minion_reactive_3],
    [h_actors.minion_aggressive_2, h_actors.minion_defensive, h_actors.minion_reactive_3],
]
scene_600.event = {
    "message": "At the summit, the enemy surges with momentum.",
    "effect": "enemy_momentum",
}
scene_600.aftermath = "At the height, even the victors looked hollow. This spire drinks more than courage."

scenario_list ={
    "start" : start_call,
    "100" : scene_100_call,
    "150" : scene_150_call,
    "200" : scene_200_call,
    "250" : scene_250_call,
    "300" : scene_300_call,
    "400" : scene_400_call,
    "500" : scene_500_call,
    "600" : scene_600_call,
    "last" : last_call
}
