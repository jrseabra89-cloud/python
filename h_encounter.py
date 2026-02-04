import h_actions
import random

# When True, calls to `report()` and `major_report()` will pause
# and wait for the user to press Enter. Default is False to allow
# non-interactive runs (tests, smoke scripts).
interactive_reports = True


def set_interactive_reports(value: bool):
    """Enable or disable interactive pauses in report functions."""
    global interactive_reports
    interactive_reports = bool(value)


def enable_interactive_reports():
    set_interactive_reports(True)


def disable_interactive_reports():
    set_interactive_reports(False)


def report(message, pause=None):
    print("- - - - - - - - - -\n")
    print(message)
    print("\n- - - - - - - - - -")
    # If pause is None, follow the module-level `interactive_reports` flag.
    if pause is None:
        if interactive_reports:
            input()
    else:
        if pause:
            input()
    return


def major_report(message, pause=None):
    print("* * * * * * * * * *\n")
    print(message)
    print("\n* * * * * * * * * *")
    if pause is None:
        if interactive_reports:
            input()
    else:
        if pause:
            input()
    return

def run_encounter (scene, party):

    encounter_state = new_encounter (scene, party)
    encounter_phase = "round"
    randomizer = random.randint (0,5)
    battle_start_message = [
        "Fate provides another challenge!",
        "Let madness reign!",
        "Let the rivers run red!",
        "The gods are watchful!",
        "Battle on, pawns of the gods!",
        "A meeting with fate!"
    ]
    report (battle_start_message[randomizer])
    
    while encounter_phase != "END":

        encounter_phase, encounter_state = PHASES[encounter_phase] (encounter_phase, encounter_state)

    randomizer = random.randint (0,5)
    battle_end_message = [
        "In the end there is only silence.",
        "The worms feast tonight.",
        "Death claims its due.",
        "The victors remain, unmoved by the death they sow.",
        "Woe to the conquered.",
        "The names of the dead shall not be remembered."
    ]
    report (battle_end_message[randomizer])
    return party

def new_encounter (scene, party):
    encounter_state = {}
    encounter_state["party"] = party
    encounter_state["enemy"] = scene.roster
    encounter_state["round"] = 1
    encounter_state["actors"] = {}


    all_actors = party + scene.roster
    
    for item in all_actors:
        encounter_state["actors"][item] = {
            "party" : False,
            "active" : False,
            "waiting" : False,
            "done" : False,
            "KO" : False,
            "melee" : False,
            "momentum" : False,
            "guard" : False,
            "block" : False,
            "speed" : "normal",
            "vulnerable" : False,
            "daze" : False,
            "blind" : False,
            "pin" : False,
            "disable" : False,
            "enraged" : False
        }

        if item in party:
            encounter_state["actors"][item]["party"] = True

        encounter_state["actors"][item]["speed"] = item.speed
        

    return encounter_state

def round_phase (encounter_phase, encounter_state):

    fast_actors =[]
    regular_actors =[]
    slow_actors =[]

    for k in encounter_state["actors"]:

        encounter_state = h_actions.savagery_trigger (k, encounter_state)

        if encounter_state["actors"][k]["speed"] == "fast":
            fast_actors.append(k)
        elif encounter_state["actors"][k]["speed"] == "slow":
            slow_actors.append(k)
        else:
            regular_actors.append(k)

    for k in fast_actors:
        if encounter_state["actors"][k]["KO"] == False:
            if encounter_state["actors"][k]["done"] == False:
                encounter_state["actors"][k]["active"] = True
                active_actor = k
                encounter_phase = "round"

                # reset soft status
                encounter_state = reset_soft_status (active_actor, encounter_state)

                if active_actor in encounter_state["party"]:
                    encounter_state = party_turn (k, encounter_state)
                else:
                    encounter_state = enemy_turn (k, encounter_state)

                # end condition check
                encounter_phase = check_end_condition (encounter_phase, encounter_state)
                
                # reset hard status
                encounter_state = reset_hard_status (active_actor, encounter_state)
                
                # end melee check
                encounter_state = check_melee_condition (encounter_phase, encounter_state)

                return encounter_phase, encounter_state

    for k in regular_actors:
        if encounter_state["actors"][k]["KO"] == False:
            if encounter_state["actors"][k]["done"] == False:
                encounter_state["actors"][k]["active"] = True
                active_actor = k
                encounter_phase = "round"

                # reset soft status
                encounter_state = reset_soft_status (active_actor, encounter_state)

                if active_actor in encounter_state["party"]:
                    encounter_state = party_turn (k, encounter_state)
                else:
                    encounter_state = enemy_turn (k, encounter_state)

                # end condition check
                encounter_phase = check_end_condition (encounter_phase, encounter_state)
                
                # reset hard status
                encounter_state = reset_hard_status (active_actor, encounter_state)
                
                # end melee check
                encounter_state = check_melee_condition (encounter_phase, encounter_state)

                return encounter_phase, encounter_state

    for k in slow_actors:
        if encounter_state["actors"][k]["KO"] == False:
            if encounter_state["actors"][k]["done"] == False:
                encounter_state["actors"][k]["active"] = True
                active_actor = k
                encounter_phase = "round"

                # reset soft status
                encounter_state = reset_soft_status (active_actor, encounter_state)

                if active_actor in encounter_state["party"]:
                    encounter_state = party_turn (k, encounter_state)
                else:
                    encounter_state = enemy_turn (k, encounter_state)

                # end condition check
                encounter_phase = check_end_condition (encounter_phase, encounter_state)
                
                # reset hard status
                encounter_state = reset_hard_status (active_actor, encounter_state)
                
                # end melee check
                encounter_state = check_melee_condition (encounter_phase, encounter_state)

                return encounter_phase, encounter_state

    encounter_phase = "upkeep"

    # Decrement stone skin buff durations
    if "stone_skin_buffs" in encounter_state:
        actors_to_remove = []
        for buffed_actor in encounter_state["stone_skin_buffs"]:
            encounter_state["stone_skin_buffs"][buffed_actor]["duration"] -= 1
            if encounter_state["stone_skin_buffs"][buffed_actor]["duration"] <= 0:
                # Buff expired, remove bonuses
                bonus_data = encounter_state["stone_skin_buffs"][buffed_actor]
                buffed_actor.current_reduction -= bonus_data["reduction_bonus"]
                buffed_actor.current_power -= bonus_data["power_bonus"]
                report(f"{buffed_actor.name}'s stone skin fades away.")
                actors_to_remove.append(buffed_actor)
        
        # Remove expired buffs
        for actor_to_remove in actors_to_remove:
            del encounter_state["stone_skin_buffs"][actor_to_remove]

    # Decrement devil's dust buff durations
    if "devils_dust_buffs" in encounter_state:
        actors_to_remove = []
        for buffed_actor in encounter_state["devils_dust_buffs"]:
            encounter_state["devils_dust_buffs"][buffed_actor]["duration"] -= 1
            if encounter_state["devils_dust_buffs"][buffed_actor]["duration"] <= 0:
                # Buff expired, remove bonuses
                bonus_data = encounter_state["devils_dust_buffs"][buffed_actor]
                buffed_actor.current_power -= bonus_data["power_bonus"]
                buffed_actor.speed = "normal"
                report(f"{buffed_actor.name}'s devil's dust effect wears off.")
                actors_to_remove.append(buffed_actor)
        
        # Remove expired buffs
        for actor_to_remove in actors_to_remove:
            del encounter_state["devils_dust_buffs"][actor_to_remove]

    return encounter_phase, encounter_state

def party_turn (actor, encounter_state):

    actor.feeling (encounter_state)

    print (f"{actor.name}'s turn")
    print(f"Stamina: {actor.current_stamina}/{actor.stamina} | Fortune: {actor.current_fortune}/{actor.fortune}")
    status_text = "Status: "
    for key, value in encounter_state["actors"][actor].items():
        if value == True:
            if key != "active":
                if key != "party":
                    status_text += f"({key})"
    print(status_text)
    input()

    possible_actions = h_actions.filter_actions (actor, encounter_state, actor.special_actions | actor.arms_actions | h_actions.base_actions)

    user_action = h_actions.choose_options (possible_actions)

    encounter_state = user_action (actor, encounter_state)

    encounter_state["actors"][actor]["active"] = False
    encounter_state["actors"][actor]["done"] = True

    #print(actor.name, encounter_state["actors"][actor])

    return encounter_state

def enemy_turn (actor, encounter_state):
    print (f"{actor.name}'s turn")
    print(f"Stamina: {actor.current_stamina}/{actor.stamina} | Fortune: {actor.current_fortune}/{actor.fortune}")
    status_text = "Status: "
    for key, value in encounter_state["actors"][actor].items():
        if value == True:
            if key != "active":
                status_text += f"({key})"
    print(status_text)
    input()

    possible_actions = h_actions.filter_actions (actor, encounter_state, h_actions.base_actions | actor.special_actions | actor.arms_actions)

    enemy_action = h_actions.enemy_action_logic (possible_actions)

    encounter_state = enemy_action (actor, encounter_state)    

    encounter_state["actors"][actor]["active"] = False
    encounter_state["actors"][actor]["done"] = True
    #print(actor.name, encounter_state["actors"][actor])
    return encounter_state

def upkeep_phase (encounter_phase, encounter_state):
    report(f"Round {encounter_state['round']} upkeep")
    input()
    encounter_state["round"] += 1
    major_report(f"Round {encounter_state['round']}")
    for k in encounter_state["actors"]:
        encounter_state["actors"][k]["done"] = False
        encounter_state["actors"][k]["active"] = False

    encounter_phase = "round"

    return encounter_phase, encounter_state

PHASES = {
    "round" : round_phase,
    "upkeep" : upkeep_phase
}

def check_end_condition (encounter_phase, encounter_state):

    party_KO = True
    enemy_KO = True

    for item in encounter_state["party"]:
        if encounter_state["actors"][item]["KO"] == False:
            party_KO = False

    for item in encounter_state["enemy"]:
        if encounter_state["actors"][item]["KO"] == False:
            enemy_KO = False

    if party_KO == True or enemy_KO == True:
        report ("Encounter over.")
        encounter_phase = "END"

    return encounter_phase

def check_melee_condition (encounter_phase, encounter_state):

    party_melee = False
    enemy_melee = False

    for item in encounter_state["actors"]:
        if encounter_state["actors"][item]["party"] == True:
            if encounter_state["actors"][item]["melee"] == True:
                party_melee = True
        else:
            if encounter_state["actors"][item]["melee"] == True:
                enemy_melee = True

    if party_melee == True:
        if enemy_melee == True:
            return encounter_state
        
    for item in encounter_state["actors"]:
        encounter_state["actors"][item]["melee"] = False
    
    report ("No melee.")

    return encounter_state

def reset_soft_status (actor, encounter_state):

    h_actions.remove_guard (actor, encounter_state)
    h_actions.remove_block (actor, encounter_state)
    h_actions.remove_vulnerable (actor, encounter_state)

    return encounter_state

def reset_hard_status (actor, encounter_state):
    
    h_actions.remove_daze (actor, encounter_state)
    h_actions.remove_disable (actor, encounter_state)
    h_actions.remove_pin (actor, encounter_state)
    h_actions.remove_blind (actor, encounter_state)
    
    return encounter_state
