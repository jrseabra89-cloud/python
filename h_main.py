#!/usr/bin/env python3

import h_actors
import h_scenario
import h_encounter

def main ():
    show_title_and_intro()
    game_state, party = new_game()
    run_game(game_state, party)

def show_title_and_intro():
    """Display the game title and optional intro text."""
    print("\n" + "="*80)
    print("HALL OF THE MOUNTAIN KING".center(80))
    print("v0.12".center(80))
    print("2026".center(80))
    print("="*80 + "\n")
    input("Press Enter to continue...")
    
    skip = input("Skip intro? (y/n): ")
    
    if skip.lower() != "y":
        intro_lines = [
            "Far away, in a land caught between time and space,",
            "where the secrets of life and death lay,",
            "there is a castle of stone where the mountain king roams.",
            "His deep, dark eyes keep watch on his kingdom,",
            "and the mysteries that sleep safe inside.",
            "His hall, his towers of stone shall not be overthrown for eternity.",
            "It is guarded by the king, insanity and the power that it brings.",
            "But he's not the only one lost inside, forever hidden from the sun.",
            "Madness reigns in the hall of the mountain king.",
        ]
        for line in intro_lines:
            h_encounter.report(line, pause=True)

def new_game():
    game_state = setup_gamestate()
    learn = input("Learn how to play? (y/n): ")
    if learn.lower() == "y":
        show_tutorial()
    party = h_actors.create_party ()
    start_options = ["100", "600"]
    choice = input("Choose starting scene (100, 600): ")
    if choice not in start_options:
        choice = "100"
    game_state["start_scene"] = choice
    return game_state, party

def setup_gamestate():
    game_state = {}
    return game_state

def show_tutorial():
    h_encounter.report(
        "Actor stats:\n"
        "- Stamina: health before KO.\n"
        "- Skill: accuracy and prowess in tests and attacks.\n"
        "- Defense: raises enemy hit difficulty.\n"
        "- Fortune: used for fate tests.\n"
        "- Power: base damage added to attacks.\n"
        "- Reduction: subtracts physical damage.\n"
        "- Insulation: subtracts magical damage.\n"
        "- Speed: sets turn order (fast, normal, slow)."
    )
    h_encounter.report(
        "Encounter structure:\n"
        "- Encounters run in rounds.\n"
        "- Turn order is fast, normal, slow.\n"
        "- Each actor takes one action on their turn.\n"
        "- Upkeep advances the round.\n"
        "- Upkeep resets temporary turn flags.\n"
        "- Encounters end when a side is fully KO."
    )
    h_encounter.report(
        "Actions:\n"
        "- Fight and other attacks use a test.\n"
        "- The test is skill vs target defense.\n"
        "- Guard raises defense.\n"
        "- Block forces attackers to target you first.\n"
        "- Retreat breaks melee.\n"
        "- Swap changes weapons.\n"
        "- Aid supports allies.\n"
        "- Observe reveals foes.\n"
        "- Use item consumes a party item."
    )
    h_encounter.report(
        "Statuses:\n"
        "- Guard: harder to hit.\n"
        "- Block: forces attackers to target you first.\n"
        "- Hide: targeted only if no other non-melee targets exist.\n"
        "- Vulnerable: lowers defense.\n"
        "- Daze: reduces effectiveness in tests.\n"
        "- Pin: limits movement.\n"
        "- Pin: blocks certain actions (like skirmish).\n"
        "- Disable: restricts key actions.\n"
        "- Blind: can only target melee opponents.\n"
        "- Momentum: grants an attack bonus until spent.\n"
        "- Melee: engaged in close combat."
    )
    h_encounter.report(
        "Archetypes & special actions:\n"
        "- Archetypes define a combat role and theme.\n"
        "- Archetypes grant stat bonuses that shape your strengths.\n"
        "- Archetypes grant features that change how you fight.\n"
        "- Archetypes grant unique actions for tactical choices.\n"
        "- Gendarme: armored duelist with riposte and steady defenses.\n"
        "- Furioso: brutal attacker with hack and slash momentum.\n"
        "- Herald: support leader with rally, decisive order, deliverance.\n"
        "- Heathen: skirmisher with prowl and dirty trick.\n"
        "- Diabolist: caster who risks fortune for diablerie."
    )
    h_encounter.report(
        "Special features & equipment:\n"
        "- Features can come from archetypes or gear.\n"
        "- Riposte: if you are Guarding and an enemy attacks you in melee, you may counter-attack.\n"
        "- Mystic aim: attacks use Fortune instead of Skill for tests.\n"
        "- Charge: if you start outside melee and attack a target without Reach, gain +1d4 damage.\n"
        "- Reach: you can attack without entering melee; also blocks enemy charge bonuses.\n"
        "- Resist pin: 75% chance to ignore being pinned.\n"
        "- Quick draw: swapping weapons does not consume your action (you can act again).\n"
        "- Savagery: when below half stamina, become enraged (+2 power, +2 reduction, fast speed, always vulnerable).\n"
        "- Juggernaut: ignores daze effects (also granted temporarily by some spells)."
    )

def run_game (game_state, party):

    h_encounter.report(f"You've made your way to the halls of the mountain king.\n\nYou stand in the feeble sun before the bleached walls lined with faded murals, their stories lost to time.\n\nWhy have you come?\n\nPerhaps it doesn't matter now...")

    current = game_state.get("start_scene", "100")
    while current != "END":
        manage = input("Manage party before next scene? (y/n): ")
        if manage.lower() == "y":
            party = manage_party(party)
        current, party = h_scenario.scenario_list[current](game_state, party)
    h_encounter.major_report ("MADNESS REIGNS IN THE HALL OF THE MOUNTAIN KING.")


def manage_party(party):
    while True:
        print("\nParty management:")
        print("1.\tReorder party")
        print("2.\tSwap weapon set")
        print("3.\tCheck stats")
        print("4.\tDone")
        try:
            choice = int(input("Choose option: "))
        except ValueError:
            choice = 4

        if choice == 1:
            remaining = list(party)
            new_order = []
            while remaining:
                print("Choose the next party member in line:")
                options_index = {}
                for i, actor in enumerate(remaining, start=1):
                    print(f"{i}.\t{actor.name}")
                    options_index[i] = actor
                try:
                    choice_index = int(input("Choose actor: "))
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

        elif choice == 2:
            print("Choose a party member to swap weapon set:")
            options_index = {}
            for i, actor in enumerate(party, start=1):
                print(f"{i}.\t{actor.name}")
                options_index[i] = actor
            try:
                choice_index = int(input("Choose actor: "))
            except ValueError:
                choice_index = 1
            if choice_index > len(party):
                choice_index = len(party)
            elif choice_index < 1:
                choice_index = 1
            chosen = options_index[choice_index]
            if chosen.arms_slot2 is None:
                h_encounter.report(f"{chosen.name} has no secondary weapon to swap.")
            else:
                chosen.swap()

        elif choice == 3:
            print("\nParty stats:")
            for actor in party:
                print("\n" + "=" * 60)
                print(f"CHARACTER SUMMARY: {actor.name}")
                print("=" * 60)
                print(f"Archetype: {actor.archetype.name if actor.archetype else 'None'}")
                print(f"Armor: {actor.armor.name if actor.armor else 'None'}")
                print(f"Headgear: {actor.headgear.name if actor.headgear else 'None'}")
                print(f"Main Weapon: {actor.arms_slot1.name if actor.arms_slot1 else 'None'}")
                print(f"Secondary Weapon: {actor.arms_slot2.name if actor.arms_slot2 else 'None'}")
                print("-" * 60)
                print(f"Stamina: {actor.stamina}")
                print(f"Skill: {actor.skill}")
                print(f"Defense: {actor.defense}")
                print(f"Fortune: {actor.fortune}")
                print(f"Power: {actor.power}")
                print(f"Reduction: {actor.reduction}")
                print(f"Insulation: {actor.insulation}")
                print(f"Speed: {actor.speed}")
                print(f"Damage Type: {actor.damage_type}")
                if actor.features:
                    print(f"Features: {', '.join(actor.features)}")
            print("\n" + "=" * 60)

        else:
            return party

# ---------------------------------------------------------------------------
# RUNNING
# ---------------------------------------------------------------------------

main ()

