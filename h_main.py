import h_actors
import h_scenario
import h_encounter

def main ():
    show_title_and_intro()
    game_state, party = new_game()
    run_game(game_state, party)

def show_title_and_intro():
    """Display the game title and optional intro text."""
    print("\n" + "="*60)
    print("HALL OF THE MOUNTAIN KING".center(60))
    print("="*60 + "\n")
    
    skip = input("Skip intro? (y/n): ")
    
    if skip.lower() != "y":
        intro_text = """
Far away, in a land caught between time and space, where the secrets of life and death lay, there is a castle of stone where the mountain king roams.

His deep, dark eyes keep watch on  his kingdom and the mysteries that sleep safe inside.

His hall, his towers of stone shall not be overthrown for eternity. It is guarded by the king, insanity and the power that it brings. 

But he's not the only one lost inside, forever hidden from the sun.

Madness reigns in the hall of the mountain king.
        """
        h_encounter.report(intro_text)

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

