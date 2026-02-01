import h_actions

def report (message):
    print ("- - - - - - - - - -")
    print (message)
    print ("- - - - - - - - - -")
    input("")

def major_report (message):
    print ("* * * * * * * * * *")
    print (message)
    print ("* * * * * * * * * *")
    input("")

def run_encounter (scene, party):

    encounter_state = new_encounter (scene, party)
    encounter_phase = "round"
    
    while encounter_phase != "END":

        encounter_phase, encounter_state = PHASES[encounter_phase] (encounter_phase, encounter_state)

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
            "momemtum" : False,
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
        

    major_report(f"Round: {encounter_state['round']}")

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

    return encounter_phase, encounter_state

def party_turn (actor, encounter_state):

    actor.feeling (encounter_state)

    print (f"{actor.name}'s turn")
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
    
    return encounter_state
