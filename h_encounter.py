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
    print("- "*30 + "\n")
    print(message.center(60))
    print("\n" + "- "*30)
    # If pause is None, follow the module-level `interactive_reports` flag.
    if pause is None:
        if interactive_reports:
            input()
    else:
        if pause:
            input()
    return


def major_report(message, pause=None):
    print("= "*30 + "\n")
    print(message.center(60))
    print("\n" + "= "*30)
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

    if scene.roster:
        descriptions = []
        for actor in scene.roster:
            desc = getattr(actor, "description", "")
            descriptions.append(desc if desc else actor.name)
        formatted = "\n\n".join(descriptions)
        report(f"The party encounters:\n\n{formatted}.")

    if getattr(scene, "event", None):
        event = scene.event
        event_message = event.get("message")
        if event_message:
            report(event_message)
        apply_scene_event(encounter_state, event)

    randomizer = random.randint (0,5)
    battle_start_message = [
        "Fate provides another challenge!",
        "Let madness reign!",
        "Let the rivers run red!",
        "The gods are watchful!",
        "Battle on, pawns of the gods!",
        "A meeting with fate!"
    ]
    major_report(battle_start_message[randomizer].center(60))
    report(f"Round: {encounter_state['round']}".center(60) )
    
    while encounter_phase != "END":

        encounter_phase, encounter_state = PHASES[encounter_phase] (encounter_phase, encounter_state)

    randomizer = random.randint (0,5)
    battle_end_message = [
        "In the end there is only silence.",
        "A feast for worms.",
        "Death claims its due.",
        "Only the victors remain, unmoved by the death they sow.",
        "Woe to the conquered.",
        "The names of the dead shall not be remembered."
    ]
    major_report(battle_end_message[randomizer].center(60))

    for enemy in scene.roster:
        enemy.refresh()

    party = [actor for actor in party if encounter_state["actors"].get(actor, {}).get("KO") != True]
    for actor in party:
        stamina_restore = random.randint(3, 6)
        fortune_restore = random.randint(1, 4)
        actor.current_stamina = min(actor.current_stamina + stamina_restore, actor.stamina)
        actor.current_fortune = min(actor.current_fortune + fortune_restore, actor.fortune)
        report(
            f"{actor.name} recovers {stamina_restore} stamina and {fortune_restore} fortune after the encounter."
        )
    return party


def apply_scene_event(encounter_state, event):
    effect = event.get("effect")

    if effect == "party_slow_first_round":
        speed_overrides = {}
        for actor in encounter_state.get("party", []):
            speed_overrides[actor] = encounter_state["actors"][actor]["speed"]
            encounter_state["actors"][actor]["speed"] = "slow"
        encounter_state["speed_overrides"] = speed_overrides
        encounter_state["restore_speeds_round"] = encounter_state["round"] + 1

    elif effect == "enemy_momentum":
        for actor in encounter_state.get("enemy", []):
            encounter_state["actors"][actor]["momentum"] = True

    elif effect == "enemy_guard":
        for actor in encounter_state.get("enemy", []):
            encounter_state["actors"][actor]["guard"] = True

    elif effect == "party_guard":
        for actor in encounter_state.get("party", []):
            encounter_state["actors"][actor]["guard"] = True

    elif effect == "party_vulnerable":
        for actor in encounter_state.get("party", []):
            encounter_state["actors"][actor]["vulnerable"] = True

    return encounter_state

def new_encounter (scene, party):
    encounter_state = {}
    encounter_state["party"] = party
    encounter_state["enemy"] = scene.roster
    encounter_state["round"] = 1
    encounter_state["actors"] = {}

    party_inventory = None
    if party:
        party_inventory = party[0].inventory
    encounter_state["party_inventory"] = party_inventory

    if party_inventory is not None:
        for actor in party:
            actor.inventory = party_inventory


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
            "hide" : False,
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

                # reset hard status
                encounter_state = reset_hard_status (active_actor, encounter_state)
                
                # end melee check
                encounter_state = check_melee_condition (encounter_phase, encounter_state)
                
                # end condition check
                encounter_phase = check_end_condition (encounter_phase, encounter_state)

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
                if bonus_data.get("juggernaut") == True and "juggernaut" in buffed_actor.features:
                    buffed_actor.features.remove("juggernaut")
                if encounter_state["actors"].get(buffed_actor, {}).get("KO") != True:
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
                if encounter_state["actors"].get(buffed_actor, {}).get("KO") != True:
                    report(f"{buffed_actor.name}'s devil's dust effect wears off.")
                actors_to_remove.append(buffed_actor)
        
        # Remove expired buffs
        for actor_to_remove in actors_to_remove:
            del encounter_state["devils_dust_buffs"][actor_to_remove]

    return encounter_phase, encounter_state

def party_turn (actor, encounter_state):

    actor.feeling (encounter_state)

    print (f"{actor.name}'s turn")
    weapon_name = actor.arms_slot1.name if actor.arms_slot1 else "None"
    print(
        f"Stamina: {actor.current_stamina}/{actor.stamina} | Fortune: {actor.current_fortune}/{actor.fortune} | Weapon: {weapon_name}"
    )
    status_text = "Status: "
    for key, value in encounter_state["actors"][actor].items():
        if value == True:
            if key != "active":
                if key != "party":
                    status_text += f"({key})"
    print(status_text)
    input()

    encounter_state["actors"][actor].pop("hide_blocked", None)

    while True:
        possible_actions = h_actions.filter_actions (actor, encounter_state, actor.special_actions | actor.arms_actions | h_actions.base_actions)

        user_action = h_actions.choose_options (possible_actions)

        if user_action == h_actions.observe:
            encounter_state = user_action(actor, encounter_state)
            continue

        encounter_state = user_action (actor, encounter_state)
        if encounter_state.pop("action_failed", False):
            continue
        break

    encounter_state["actors"][actor]["active"] = False
    encounter_state["actors"][actor]["done"] = True

    #print(actor.name, encounter_state["actors"][actor])

    return encounter_state

def enemy_turn (actor, encounter_state):
    print (f"{actor.name}'s turn")
    weapon_name = actor.arms_slot1.name if actor.arms_slot1 else "None"
    print(
        f"Stamina: {actor.current_stamina}/{actor.stamina} | Fortune: {actor.current_fortune}/{actor.fortune} | Weapon: {weapon_name}"
    )
    status_text = "Status: "
    for key, value in encounter_state["actors"][actor].items():
        if value == True:
            if key != "active":
                status_text += f"({key})"
    print(status_text)
    input()

    encounter_state["actors"][actor].pop("hide_blocked", None)

    while True:
        possible_actions = h_actions.filter_actions (actor, encounter_state, h_actions.base_actions | actor.special_actions | actor.arms_actions)

        enemy_action = h_actions.enemy_action_logic(actor, encounter_state, possible_actions)
        if enemy_action is None:
            break

        encounter_state = enemy_action (actor, encounter_state)
        if encounter_state.pop("action_failed", False):
            continue
        break

    encounter_state["actors"][actor]["active"] = False
    encounter_state["actors"][actor]["done"] = True
    #print(actor.name, encounter_state["actors"][actor])
    return encounter_state

def upkeep_phase (encounter_phase, encounter_state):
    #major_report(f"Round {encounter_state['round']} upkeep".center(60))
    #input()
    encounter_state["round"] += 1
    major_report(f"Round {encounter_state['round']}")

    if encounter_state.get("restore_speeds_round") == encounter_state["round"]:
        for actor, speed in encounter_state.get("speed_overrides", {}).items():
            encounter_state["actors"][actor]["speed"] = speed
        encounter_state.pop("speed_overrides", None)
        encounter_state.pop("restore_speeds_round", None)
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
        #major_report("The battle is over.".center(60))
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
    
    if party_melee or enemy_melee:
        report ("No melee.")

    return encounter_state

def reset_soft_status (actor, encounter_state):

    h_actions.remove_guard (actor, encounter_state)
    h_actions.remove_block (actor, encounter_state)
    h_actions.remove_hide (actor, encounter_state)
    h_actions.remove_vulnerable (actor, encounter_state)

    return encounter_state

def reset_hard_status (actor, encounter_state):
    
    h_actions.remove_daze (actor, encounter_state)
    h_actions.remove_disable (actor, encounter_state)
    h_actions.remove_pin (actor, encounter_state)
    h_actions.remove_blind (actor, encounter_state)
    
    return encounter_state
