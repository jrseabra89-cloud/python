import h_actors
import h_scenario
import h_encounter

def main ():

    game_state, party = new_game()
    run_game(game_state, party)

def new_game():
    game_state = setup_gamestate()
    party = h_actors.create_party ()
    return game_state, party

def setup_gamestate():
    game_state = {}
    return game_state

def run_game (game_state, party):
    current = "start"
    while current != "END":
        current, party = h_scenario.scenario_list[current](game_state, party)
    h_encounter.report ("PROGRAM OVER")

# ---------------------------------------------------------------------------
# RUNNING
# ---------------------------------------------------------------------------

main ()

