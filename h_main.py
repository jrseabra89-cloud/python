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
Far away, in a land caught between time and space, where the secrets of life and death lay,

there is a castle of stone where the mountain king roams.

His deep, dark eyes keep watch on  his kingdom and the mysteries that sleep safe inside.

His hall, his towers of stone shall not be overthrown for eternity.

It is guarded by the king, insanity and the power that it brings. 

But he's not the only one lost inside, forever hidden from the sun.

Madness reigns in the hall of the mountain king.
        """
        h_encounter.report(intro_text)

def new_game():
    game_state = setup_gamestate()
    party = h_actors.create_party ()
    start_options = ["100", "150", "200", "250", "300", "400", "500", "600"]
    choice = input("Choose starting scene (100, 150, 200, 250, 300, 400, 500, 600): ")
    if choice not in start_options:
        choice = "100"
    game_state["start_scene"] = choice
    return game_state, party

def setup_gamestate():
    game_state = {}
    return game_state

def run_game (game_state, party):
    current = game_state.get("start_scene", "100")
    while current != "END":
        reorder = input("Switch party actor order before next scene? (y/n): ")
        if reorder.lower() == "y":
            remaining = list(party)
            new_order = []
            while remaining:
                print("Choose the next party member in line:")
                options_index = {}
                for i, actor in enumerate(remaining, start=1):
                    print(f"{i}.\t{actor.name}")
                    options_index[i] = actor
                try:
                    choice_index = int(input("choose actor."))
                except ValueError:
                    choice_index = 1
                if choice_index > len(remaining):
                    choice_index = len(remaining)
                elif choice_index < 1:
                    choice_index = 1
                chosen = options_index[choice_index]
                new_order.append(chosen)
                remaining.remove(chosen)
            party = new_order
        current, party = h_scenario.scenario_list[current](game_state, party)
    h_encounter.major_report ("PROGRAM OVER".center(40))

# ---------------------------------------------------------------------------
# RUNNING
# ---------------------------------------------------------------------------

main ()

