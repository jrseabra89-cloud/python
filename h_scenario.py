import types
import h_actors
import h_encounter

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
    
    party = h_encounter.run_encounter (scene, party)
    
    game_state = "last"
    return game_state, party

def last_call (game_state, party):
    scene = last
    h_encounter.report (f"{scene.name} - {scene.description}")
    
    party = h_encounter.run_encounter (scene, party)
    
    game_state = "END"
    return game_state, party

start = Scene ("start")
start.description = "introduction scene"
start.roster = [h_actors.minion, h_actors.grunt]

last = Scene ("last")
last.description = "last scene"
last.roster = [h_actors.nemesis]

scenario_list ={
    "start" : start_call,
    "last" : last_call
}
