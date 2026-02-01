import random
import h_encounter

def stat_test (adder, difficulty):

    roll = random.randint(1,20)
    
    # higher thresholds should be checked first (critical > success)
    total = adder + roll
    if total >= difficulty + 20:
        result = "critical"
    elif total >= difficulty + 10:
        result = "success"
    else:
        result = "failure"

    h_encounter.report(f"{result} - {total} ({difficulty + 10})")
    return result

def choose_options (dictionary):

    options_index = {}
    options_counter = 0

    for key in dictionary:
        options_counter += 1
        text1 = f"{options_counter}.\t"
        text2 = f"{key}"
        text3 = getattr(dictionary[key], "description", "")
        print (text1+text2.center(19)+text3)
        options_index [options_counter] = key
    if options_counter == 0:
        return None

    try:
        choice_index = int(input("choose option."))
    except ValueError:
        choice_index = 1

    if choice_index > options_counter:
        choice_index = options_counter
    elif choice_index < 1:
        choice_index = 1

    choice = options_index[choice_index]

    return dictionary[choice]


def enemy_action_logic (possible_actions):
    # prefer melee fight, then skirmish, then guard; fallback to first available
    choice = None
    if "fight" in possible_actions:
        choice = "fight"
    elif "skirmish" in possible_actions:
        choice = "skirmish"
    elif "guard" in possible_actions:
        choice = "guard"

    if choice is None:
        # return first available action function or None
        return next(iter(possible_actions.values())) if possible_actions else None

    return possible_actions.get(choice)


def filter_actions (actor, encounter_state, action_dict):
    # work on a shallow copy to avoid mutating the original dict
    action_options = dict(action_dict) if action_dict is not None else {}

    if encounter_state["actors"][actor].get("disable") == True:
        action_options.pop("skirmish", None)
        action_options.pop("fight", None)
        action_options.pop("smash", None)
        action_options.pop("trip", None)
        action_options.pop("stab", None)

    if encounter_state["actors"][actor].get("melee") == True:
        action_options.pop("skirmish", None)
        action_options.pop("block", None)

    if encounter_state["actors"][actor].get("melee") == False:
        action_options.pop("retreat", None)
        if encounter_state["actors"][actor].get("pin") == True:
            action_options.pop("fight", None)
            action_options.pop("smash", None)
            action_options.pop("trip", None)
            action_options.pop("stab", None)
            action_options.pop("block", None)

    return action_options

def choose_target (dictionary):

    options_index = {}
    options_counter = 0

    for key in dictionary:
        options_counter += 1
        text1 = f"{options_counter}.\t"
        text2 = f"{key.name}"
        status_text = ""
        for k, v in dictionary[key].items():
            if v == True:
                if k != "active":
                    if k != "party":
                        status_text += f"({k})"
        print (text1+text2.center(19)+status_text)
        options_index [options_counter] = key

    if options_counter == 0:
        return None

    try:
        choice_index = int(input("choose option."))
    except ValueError:
        choice_index = 1

    if choice_index > options_counter:
        choice_index = options_counter
    elif choice_index < 1:
        choice_index = 1

    choice = options_index[choice_index]

    return choice

def logic_target (dictionary):

    options_index = {}
    options_counter = 0

    for key in dictionary:
        options_counter += 1
        options_index [options_counter] = key

    if options_counter == 0:
        return None

    choice_index = random.randint(1, options_counter)
    choice = options_index[choice_index]
    return choice

def filter_targets (actor, encounter_state):

    target_options = encounter_state["actors"]

    target_options = {k:v for k, v in target_options.items() if v["KO"] == False}
    
    target_options = {k:v for k, v in target_options.items() if v["party"] != encounter_state["actors"][actor]["party"]}

    if encounter_state["actors"][actor]["melee"] == True:
        target_options = {k:v for k, v in target_options.items() if v["melee"] == True}
    else:
        blocking_options = {k:v for k, v in target_options.items() if v["block"] == True}
        if blocking_options != {}:
            target_options = blocking_options


    return target_options

def get_target (actor, encounter_state):

    available_targets = filter_targets(actor, encounter_state)

    if not available_targets:
        return None

    if actor.logic is not None:
        target = choose_target(available_targets)
    else:
        target = next(iter(available_targets))

    return target

def check_combat_modifiers (actor, encounter_state, target):

    adder = actor.skill
    difficulty = target.defense

    if encounter_state["actors"][actor]["momentum"] == True:
        if "reach" not in target.features:
            adder += 4
        else:
            h_encounter.report (f"{target.name} halts {actor.name}'s momentum.")
    
    if encounter_state["actors"][actor]["daze"] == True:
        adder -= 4    

    if encounter_state["actors"][target]["guard"] == True:
        difficulty += 4    

    if encounter_state["actors"][target]["daze"] == True:
        difficulty -= 4    

    if encounter_state["actors"][target]["vulnerable"] == True:
        difficulty -= 4

    return adder, difficulty


def fight (actor, encounter_state):

    available_targets = filter_targets(actor, encounter_state)

    if actor.logic != None:
        target = logic_target(available_targets)
    else:
        target = choose_target(available_targets)

    attack_damage = actor.current_power + random.randint (1, 4)

    attack_damage = charge_trigger (actor, encounter_state, target, attack_damage)

    if "reach" not in actor.features:
        encounter_state["actors"][actor]["melee"] = True
        encounter_state["actors"][target]["melee"] = True

    h_encounter.report (f"{actor.name} attacks {target.name} in melee.")

    actor.battlecry()

    adder, difficulty = check_combat_modifiers (actor, encounter_state, target)

    result = stat_test (adder, difficulty)

    if result == "success":
        damage (target, encounter_state, attack_damage, target.current_reduction, actor.damage_type)
        encounter_state["actors"][actor]["momentum"] = True
        encounter_state["actors"][target]["momentum"] = False

    elif result == "critical":
        damage (target, encounter_state, attack_damage+4, target.current_reduction, actor.damage_type)
        encounter_state["actors"][actor]["momentum"] = True
        encounter_state["actors"][target]["momentum"] = False

    else:
        h_encounter.report (f"{target.name} deflects the attack.")
        encounter_state["actors"][actor]["momentum"] = False
        riposte_trigger (actor, encounter_state, target)

    return encounter_state

def smash (actor, encounter_state):

    available_targets = filter_targets(actor, encounter_state)

    if actor.logic != None:
        target = logic_target(available_targets)
    else:
        target = choose_target(available_targets)
    
    attack_damage = actor.current_power + random.randint (1, 4)

    attack_damage = charge_trigger (actor, encounter_state, target, attack_damage)

    if "reach" not in actor.features:
        encounter_state["actors"][actor]["melee"] = True
        encounter_state["actors"][target]["melee"] = True

    h_encounter.report (f"{actor.name} winds up for a heavy attack against {target.name}.")

    actor.battlecry()

    adder, difficulty = check_combat_modifiers (actor, encounter_state, target)

    adder -= 4

    result = stat_test (adder, difficulty)

    if result == "success":
        damage (target, encounter_state, attack_damage+2, target.current_reduction, actor.damage_type)
        encounter_state["actors"][actor]["momentum"] = True
        encounter_state["actors"][target]["momentum"] = False
        cause_daze (target, encounter_state)

    elif result == "critical":
        damage (target, encounter_state, attack_damage+6, target.current_reduction, actor.damage_type)
        encounter_state["actors"][actor]["momentum"] = True
        encounter_state["actors"][target]["momentum"] = False
        cause_daze (target, encounter_state)

    else:
        h_encounter.report (f"{target.name} deflects the attack.")
        encounter_state["actors"][actor]["momentum"] = False
        cause_vulnerable (actor, encounter_state)
        riposte_trigger (actor, encounter_state, target)

    return encounter_state

def hack_and_slash (actor, encounter_state):

    available_targets = filter_targets(actor, encounter_state)

    if actor.logic != None:
        target = logic_target(available_targets)
    else:
        target = choose_target(available_targets)
    
    attack_damage = actor.current_power + random.randint (1, 4)

    attack_damage = charge_trigger (actor, encounter_state, target, attack_damage)

    if "reach" not in actor.features:
        encounter_state["actors"][actor]["melee"] = True
        encounter_state["actors"][target]["melee"] = True

    h_encounter.report (f"{actor.name} attacks {target.name} with a flurry of blows.")

    actor.battlecry()

    adder, difficulty = check_combat_modifiers (actor, encounter_state, target)

    adder += 4

    result = stat_test (adder, difficulty)

    if result == "success":
        damage (target, encounter_state, attack_damage, target.current_reduction, actor.damage_type)
        encounter_state["actors"][actor]["momentum"] = True
        encounter_state["actors"][target]["momentum"] = False
        cause_vulnerable (actor, encounter_state)

    elif result == "critical":
        damage (target, encounter_state, attack_damage+4, target.current_reduction, actor.damage_type)
        encounter_state["actors"][actor]["momentum"] = True
        encounter_state["actors"][target]["momentum"] = False
        cause_vulnerable (actor, encounter_state)

    else:
        h_encounter.report (f"{target.name} deflects the attack.")
        encounter_state["actors"][actor]["momentum"] = False
        cause_vulnerable (actor, encounter_state)
        riposte_trigger (actor, encounter_state, target)

    return encounter_state

def trip (actor, encounter_state):

    available_targets = filter_targets(actor, encounter_state)

    if actor.logic != None:
        target = logic_target(available_targets)
    else:
        target = choose_target(available_targets)

    if "reach" not in actor.features:
        encounter_state["actors"][actor]["melee"] = True
        encounter_state["actors"][target]["melee"] = True

    h_encounter.report (f"{actor.name} looks for an openning against {target.name}.")

    actor.battlecry()

    adder, difficulty = check_combat_modifiers (actor, encounter_state, target)

    adder += 4

    result = stat_test (adder, difficulty)

    if result == "success":
        encounter_state["actors"][actor]["momentum"] = True
        encounter_state["actors"][target]["momentum"] = False
        cause_daze (target, encounter_state)

    elif result == "critical":
        encounter_state["actors"][actor]["momentum"] = True
        encounter_state["actors"][target]["momentum"] = False
        cause_daze (target, encounter_state)
        cause_disable (target, encounter_state)

    else:
        h_encounter.report (f"{target.name} deflects the attack.")
        encounter_state["actors"][actor]["momentum"] = False
        riposte_trigger (actor, encounter_state, target)

    return encounter_state


def dirty_trick(actor, encounter_state):
    # Dirty trick: can only be used in melee; actor loses melee status after use
    if encounter_state["actors"][actor]["melee"] != True:
        h_encounter.report(f"{actor.name} is not in melee and cannot use dirty trick.")
        return encounter_state

    available_targets = filter_targets(actor, encounter_state)

    if actor.logic != None:
        target = logic_target(available_targets)
    else:
        target = choose_target(available_targets)

    if not target:
        return encounter_state

    # ensure target is in melee (dirty trick only in melee)
    if encounter_state["actors"][target]["melee"] != True:
        h_encounter.report(f"{actor.name} cannot use dirty trick on non-melee target.")
        return encounter_state

    h_encounter.report(f"{actor.name} attempts a dirty trick on {target.name}.")

    actor.battlecry()

    adder, difficulty = check_combat_modifiers (actor, encounter_state, target)

    adder += 4

    result = stat_test (adder, difficulty)

    # actor loses melee status when using dirty trick
    encounter_state["actors"][actor]["melee"] = False

    if result == "success":
        encounter_state["actors"][actor]["momentum"] = True
        encounter_state["actors"][target]["momentum"] = False
        cause_daze (target, encounter_state)

    elif result == "critical":
        encounter_state["actors"][actor]["momentum"] = True
        encounter_state["actors"][target]["momentum"] = False
        cause_daze (target, encounter_state)
        cause_disable (target, encounter_state)

    else:
        h_encounter.report (f"{target.name} deflects the attack.")
        encounter_state["actors"][actor]["momentum"] = False
        riposte_trigger (actor, encounter_state, target)

    return encounter_state


def prowl(actor, encounter_state):
    # Prowl: similar to fight but does NOT set actor into melee.
    # If actor is not in melee, it may target any enemy (including blockers).
    if encounter_state["actors"][actor]["melee"] == False:
        # allow any enemy target (KO==False and opposite party)
        available_targets = {k: v for k, v in encounter_state["actors"].items() if v["KO"] == False and v["party"] != encounter_state["actors"][actor]["party"]}
        if not available_targets:
            return encounter_state
        if actor.logic != None:
            target = logic_target(available_targets)
        else:
            target = choose_target(available_targets)
    else:
        # behave like a normal fight selection
        available_targets = filter_targets(actor, encounter_state)
        if actor.logic != None:
            target = logic_target(available_targets)
        else:
            target = choose_target(available_targets)

    if not target:
        return encounter_state

    attack_damage = actor.current_power + random.randint(1, 4)

    # bonus damage if target is in melee while actor is not
    if encounter_state["actors"][target]["melee"] == True and encounter_state["actors"][actor]["melee"] == False:
        attack_damage += random.randint(1, 4)

    # prowling action does not set melee flags
    h_encounter.report (f"{actor.name} prowls toward {target.name}.")

    actor.battlecry()

    adder, difficulty = check_combat_modifiers (actor, encounter_state, target)

    result = stat_test (adder, difficulty)

    if result == "success":
        damage (target, encounter_state, attack_damage, target.current_reduction, actor.damage_type)
        encounter_state["actors"][actor]["momentum"] = True
        encounter_state["actors"][target]["momentum"] = False

    elif result == "critical":
        damage (target, encounter_state, attack_damage+4, target.current_reduction, actor.damage_type)
        encounter_state["actors"][actor]["momentum"] = True
        encounter_state["actors"][target]["momentum"] = False

    else:
        h_encounter.report (f"{target.name} deflects the attack.")
        encounter_state["actors"][actor]["momentum"] = False
        riposte_trigger (actor, encounter_state, target)

    return encounter_state

def stab (actor, encounter_state):

    available_targets = filter_targets(actor, encounter_state)

    if actor.logic != None:
        target = logic_target(available_targets)
    else:
        target = choose_target(available_targets)

    
    attack_damage = actor.current_power + random.randint (1, 4)

    attack_damage = charge_trigger (actor, encounter_state, target, attack_damage)

    encounter_state["actors"][actor]["melee"] = True
    encounter_state["actors"][target]["melee"] = True

    h_encounter.report (f"{actor.name} aims at {target.name} weak points.")

    actor.battlecry()

    adder, difficulty = check_combat_modifiers (actor, encounter_state, target)
    
    adder -= 4

    result = stat_test (adder, difficulty)

    if result == "success":
        damage (target, encounter_state, attack_damage + random.randint (1, 4), 0, "pierce")
        encounter_state["actors"][actor]["momentum"] = True
        encounter_state["actors"][target]["momentum"] = False

    elif result == "critical":
        damage (target, encounter_state, attack_damage + 4, 0, "pierce")
        encounter_state["actors"][actor]["momentum"] = True
        encounter_state["actors"][target]["momentum"] = False

    else:
        h_encounter.report (f"{target.name} deflects the attack.")
        encounter_state["actors"][actor]["momentum"] = False
        riposte_trigger (actor, encounter_state, target)

    return encounter_state

def skirmish (actor, encounter_state):

    available_targets = filter_targets(actor, encounter_state)

    if actor.logic != None:
        target = logic_target(available_targets)
    else:
        target = choose_target(available_targets)

    attack_damage = random.randint (1, 6)

    h_encounter.report (f"{actor.name} takes aims at {target.name} and attacks from a distance.")

    encounter_state["actors"][actor]["momentum"] = False
    
    adder, difficulty = check_combat_modifiers (actor, encounter_state, target)

    result = stat_test (adder, difficulty)

    if result == "success":
        damage (target, encounter_state, attack_damage, target.current_reduction, "pierce")
        encounter_state["actors"][target]["momentum"] = False
        cause_pin (target, encounter_state)

    elif result == "critical":
        damage (target, encounter_state, attack_damage+4, target.current_reduction, "pierce")
        encounter_state["actors"][target]["momentum"] = False
        cause_pin (target, encounter_state)

    else:
        h_encounter.report (f"{actor.name} misses.")
        encounter_state["actors"][actor]["momentum"] = False

    return encounter_state

def guard (actor, encounter_state):

    encounter_state["actors"][actor]["guard"] = True
    h_encounter.report (f"{actor.name} raises their guard.")

    return encounter_state

def block (actor, encounter_state):

    encounter_state["actors"][actor]["block"] = True
    encounter_state["actors"][actor]["guard"] = True
    h_encounter.report (f"{actor.name} stands ready to intercept attackers.")

    return encounter_state

def retreat (actor, encounter_state):

    encounter_state["actors"][actor]["melee"] = False
    encounter_state["actors"][actor]["momentum"] = False
    h_encounter.report (f"{actor.name} retreats from melee.")

    return encounter_state

def swap_arms (actor, encounter_state): 
    if actor.arms_slot2 != None:
        actor.swap()
    else:
        h_encounter.report (f"{actor.name} has no other weapons.")
        # nothing to swap
    
    encounter_state["actors"][actor]["momentum"] = False

    return encounter_state

base_actions = {
    "fight" : fight,
    "smash" : smash,
    "trip" : trip,
    "skirmish" : skirmish,
    "guard" : guard,
    "block" : block,
    "retreat" : retreat,
    "swap" : swap_arms
}


#------------------------------------------------------------------
# Damage and status
#------------------------------------------------------------------

def damage (actor, encounter_state, power = 0, reduction = 0, damage_type = "blunt"):

    final_damage = power - reduction

    if final_damage < 0:
        final_damage = 0

    actor.current_stamina -= final_damage

    actor.pain ()

    h_encounter.report (f"{actor.name} takes {final_damage} damage.")

    if actor.current_stamina < 1:
        actor.current_stamina = 0
        encounter_state["actors"][actor]["KO"] = True
        encounter_state["actors"][actor]["melee"] = False

        actor.death (damage_type)

    return encounter_state


def charge_trigger (actor, encounter_state, target, attack_damage):

    if encounter_state["actors"][actor]["melee"] == False:
        if "charge" in actor.features:
            if "reach" not in target.features:
                attack_damage += random.randint (1, 4)
                h_encounter.report (f"{actor.name} charges furiously into battle.")
            else:
                h_encounter.report (f"{target.name} staggers {actor.name}'s charge.")

    return attack_damage

def riposte_trigger (actor, encounter_state, target):
    if encounter_state["actors"][target]["guard"] == True: 
        if "riposte" in target.features:
            
            h_encounter.report (f"{target.name} siezes the moment and counter-attacks.")

            attack_damage = target.current_power + random.randint (1, 4)

            target.battlecry()

            adder, difficulty = check_combat_modifiers (target, encounter_state, actor)

            result = stat_test (adder, difficulty)

            if result == "success":
                damage (actor, encounter_state, attack_damage, actor.current_reduction, target.damage_type)
                encounter_state["actors"][actor]["momentum"] = False

            elif result == "critical":
                damage (actor, encounter_state, attack_damage+4, actor.current_reduction, target.damage_type)
                encounter_state["actors"][actor]["momentum"] = False

            else:
                h_encounter.report (f"{target.name} misses.")

def savagery_trigger (actor, encounter_state):
    if "savagery" in actor.features:
        if actor.current_stamina < actor.stamina // 2 +1:
            if encounter_state["actors"][actor]["enraged"] == False:
                h_encounter.report (f"{actor.name} is enraged and grows stronger from their wounds.")
                actor.current_power += 2
                actor.current_reduction += 2
                encounter_state["actors"][actor]["enraged"] = True
                encounter_state["actors"][actor]["speed"] = "fast"

    return encounter_state

def cause_status (actor, encounter_state, status, message):
    if encounter_state["actors"][actor][status] == False:
        encounter_state["actors"][actor][status] = True
        h_encounter.report (message)

def remove_status (actor, encounter_state, status, message):
    if encounter_state["actors"][actor][status] == True:
        encounter_state["actors"][actor][status] = False
        h_encounter.report (message)

def cause_daze (actor, encounter_state):
    status = "daze"
    message = f"{actor.name} is dazed."
    cause_status (actor, encounter_state, status, message)

def cause_vulnerable (actor, encounter_state):
    status = "vulnerable"
    message = f"{actor.name} is vulnerable."
    cause_status (actor, encounter_state, status, message)

def cause_disable (actor, encounter_state):
    status = "disable"
    message = f"{actor.name} is disabled."
    cause_status (actor, encounter_state, status, message)

def cause_pin (actor, encounter_state):
    status = "pin"
    message = f"{actor.name} is pinned."
    if "resist pin" not in actor.features:
        cause_status (actor, encounter_state, status, message)
    else:
        h_encounter.report (f"{actor.name} resists being pinned.")

def remove_guard (actor, encounter_state):
    status = "guard"
    message = f"{actor.name} is no longer guarding."
    remove_status (actor, encounter_state, status, message)

def remove_block (actor, encounter_state):
    status = "block"
    message = f"{actor.name} is no longer blocking."
    remove_status (actor, encounter_state, status, message)

def remove_daze (actor, encounter_state):
    status = "daze"
    message = f"{actor.name} is no longer dazed."
    remove_status (actor, encounter_state, status, message)

def remove_vulnerable (actor, encounter_state):
    status = "vulnerable"
    message = f"{actor.name} is no longer vulnerable."
    remove_status (actor, encounter_state, status, message)

def remove_disable (actor, encounter_state):
    status = "disable"
    message = f"{actor.name} is no longer disabled."
    remove_status (actor, encounter_state, status, message)

def remove_pin (actor, encounter_state):
    status = "pin"
    message = f"{actor.name} is no longer pinned."
    remove_status (actor, encounter_state, status, message)
