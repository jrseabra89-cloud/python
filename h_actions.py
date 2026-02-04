import random
import h_encounter

SPELLS = {
    "inferno": {
        "rank": 8,
        "min_damage": 7,
        "max_damage": 12,
        "damage_type": "hellfire",
        "description": "inferno: call hellfire to scorch an enemy.",
    },
    "wail": {
        "rank": 8,
        "description": "wail: an unholy wail that pins and risks dazing multiple targets.",
    },
    "locust swarm": {
        "rank": 8,
        "description": "locust swarm: a plague of locusts blinds and ends all melee.",
    },
    "stone skin": {
        "rank": 8,
        "description": "stone skin: harden the caster's skin for protection (rank 8)",
    }
} 

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


def enemy_action_logic(actor, encounter_state, possible_actions):
    if not possible_actions:
        return None

    logic = getattr(actor, "logic", None)
    actor_state = encounter_state["actors"][actor]
    targets = {
        k: v
        for k, v in encounter_state["actors"].items()
        if v["KO"] == False and v["party"] != actor_state["party"]
    }

    low_stamina_targets = [
        t for t in targets if t.current_stamina <= max(1, t.stamina // 2)
    ]
    high_stamina_targets = [
        t for t in targets if t.current_stamina > max(1, t.stamina // 2)
    ]
    not_in_melee_targets = [t for t, v in targets.items() if v.get("melee") == False]
    guard_block_targets = [
        t for t, v in targets.items() if v.get("guard") == True or v.get("block") == True
    ]
    soft_targets = [
        t
        for t, v in targets.items()
        if v.get("daze") == True or v.get("vulnerable") == True
    ]

    actor_melee = actor_state.get("melee") == True
    actor_momentum = actor_state.get("momentum") == True

    choice = None

    if logic == "disruptive":
        if actor_melee and "retreat" in possible_actions:
            choice = "retreat"
        elif "skirmish" in possible_actions:
            choice = "skirmish"
        elif "trip" in possible_actions:
            choice = "trip"
        elif "smash" in possible_actions:
            choice = "smash"
        elif "fight" in possible_actions:
            choice = "fight"

    elif logic == "aggressive":
        for action_name in ["fight", "smash", "stab", "hack and slash", "trip", "skirmish"]:
            if action_name in possible_actions:
                choice = action_name
                break

    elif logic == "defensive":
        if "block" in possible_actions:
            choice = "block"
        elif "guard" in possible_actions:
            choice = "guard"
        else:
            for action_name in ["fight", "smash", "stab", "skirmish", "trip"]:
                if action_name in possible_actions:
                    choice = action_name
                    break

    elif logic == "reactive":
        if actor_melee and not actor_momentum and "retreat" in possible_actions:
            choice = "retreat"
        elif not_in_melee_targets and "skirmish" in possible_actions:
            choice = "skirmish"
        elif guard_block_targets and "trip" in possible_actions:
            choice = "trip"
        elif actor_melee and (low_stamina_targets or soft_targets):
            for action_name in ["fight", "smash", "stab", "trip", "hack and slash"]:
                if action_name in possible_actions:
                    choice = action_name
                    break
        elif "guard" in possible_actions:
            choice = "guard"
        elif "block" in possible_actions:
            choice = "block"

    if choice is None:
        if "fight" in possible_actions:
            choice = "fight"
        elif "skirmish" in possible_actions:
            choice = "skirmish"
        elif "guard" in possible_actions:
            choice = "guard"

    if choice is None:
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

def logic_target(dictionary, actor=None, encounter_state=None):
    options = list(dictionary.keys())

    if not options:
        return None

    if actor is None or getattr(actor, "logic", None) is None:
        return random.choice(options)

    logic = actor.logic

    if logic == "disruptive":
        preferred = [
            t for t in options if dictionary[t].get("melee") == False and dictionary[t].get("pin") == False
        ]
        if preferred:
            return random.choice(preferred)

    elif logic == "aggressive":
        return min(options, key=lambda t: t.current_stamina / max(1, t.stamina))

    elif logic == "defensive":
        return max(options, key=lambda t: t.current_stamina / max(1, t.stamina))

    elif logic == "reactive":
        preferred = [
            t
            for t in options
            if dictionary[t].get("daze") == True
            or dictionary[t].get("vulnerable") == True
            or t.current_stamina <= max(1, t.stamina // 2)
        ]
        if preferred:
            return random.choice(preferred)

    return random.choice(options)

def filter_targets (actor, encounter_state):

    target_options = encounter_state["actors"]

    target_options = {k:v for k, v in target_options.items() if v["KO"] == False}
    
    target_options = {k:v for k, v in target_options.items() if v["party"] != encounter_state["actors"][actor]["party"]}

    # Blind actors can only target enemies in melee
    if encounter_state["actors"][actor].get("blind") == True:
        if encounter_state["actors"][actor]["melee"] == True:
            target_options = {k:v for k, v in target_options.items() if v["melee"] == True}
        else:
            # Blind and not in melee = cannot target anyone
            return {}

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
        target = logic_target(available_targets, actor, encounter_state)
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
        target = logic_target(available_targets, actor, encounter_state)
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
        target = logic_target(available_targets, actor, encounter_state)
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
        target = logic_target(available_targets, actor, encounter_state)
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
        target = logic_target(available_targets, actor, encounter_state)
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


def diablerie(actor, encounter_state):
    """Diablerie: summon a demon to cast a spell. Uses actor.current_fortune as adder
    and the spell's rank as the difficulty. On a failed roll the caster suffers
    1-4 backlash damage reduced by their insulation and the spell fails."""

    # Rank mapping: lord (8), count (10), duke (12)
    rank_names = {8: "summon lord", 10: "summon count", 12: "summon duke"}
    rank_values = [8, 10, 12]

    # choose a spell
    if actor.logic != None:
        spell_name = random.choice(list(SPELLS.keys()))
    else:
        spells_list = list(SPELLS.items())
        options_index = {}
        for i, (k, v) in enumerate(spells_list, start=1):
            text1 = f"{i}.\t"
            text2 = f"{k}"
            text3 = f"{v.get('description','')}"
            print(text1 + text2.center(19) + text3)
            options_index[i] = k
        try:
            choice_index = int(input("choose spell."))
        except ValueError:
            choice_index = 1
        if choice_index > len(spells_list):
            choice_index = len(spells_list)
        elif choice_index < 1:
            choice_index = 1
        spell_name = options_index[choice_index]

    # choose rank
    if actor.logic != None:
        rank = random.choice(rank_values)
    else:
        rank_index = {}
        for i, rv in enumerate(rank_values, start=1):
            print(f"{i}.\t{rank_names[rv]}")
            rank_index[i] = rv
        try:
            rank_choice = int(input("choose rank for the summoning."))
        except ValueError:
            rank_choice = 1
        if rank_choice > len(rank_values):
            rank_choice = len(rank_values)
        elif rank_choice < 1:
            rank_choice = 1
        rank = rank_index[rank_choice]

    spell = dict(SPELLS[spell_name])
    spell["rank"] = rank
    base_rank = SPELLS[spell_name]["rank"]
    rank_steps = max(0, (rank - base_rank) // 2)

    h_encounter.report(f"{actor.name} summons a {rank_names[rank]} of hell to cast {spell_name}.")

    # Fortune test: adder = actor.current_fortune, difficulty = spell rank
    result = stat_test(actor.current_fortune, spell["rank"])

    if result == "failure":
        h_encounter.report(f"the {rank_names[rank]} resists the summons and lashes out at {actor.name}")
        backlash = random.randint(1, 4) + 2
        # backlash reduced by caster insulation
        damage(actor, encounter_state, backlash, actor.current_insulation, spell.get("damage_type", "hellfire"))
        return encounter_state

    # On success, deduct 1 fortune and report
    actor.current_fortune = max(0, actor.current_fortune - 1)
    h_encounter.report(f"{actor.name}'s fortune is bound to the spell ({actor.current_fortune} remaining).")

    # On success, resolve the spell
    if spell_name == "inferno":
        available_targets = filter_targets(actor, encounter_state)
        if actor.logic != None:
            target = logic_target(available_targets, actor, encounter_state)
        else:
            target = choose_target(available_targets)
        if not target:
            return encounter_state
        power = random.randint(spell["min_damage"], spell["max_damage"]) + (3 * rank_steps)
        h_encounter.report(f"the {rank_names[rank]} unleashes inferno upon {target.name}!")
        # damage reduced by target insulation, damage type is hellfire
        damage(target, encounter_state, power, target.current_insulation, spell.get("damage_type", "hellfire"))

    elif spell_name == "wail":
        # Determine targets: if caster not in melee -> all enemies; if in melee -> all actors in melee
        if encounter_state["actors"][actor]["melee"] == False:
            targets = {k: v for k, v in encounter_state["actors"].items() if v["KO"] == False and v["party"] != encounter_state["actors"][actor]["party"]}
        else:
            targets = {k: v for k, v in encounter_state["actors"].items() if v["KO"] == False and v.get("melee") == True}

        if not targets:
            return encounter_state

        h_encounter.report(f"the {rank_names[rank]} releases a soul-wail that rends the field!")

        # Difficulty increases by 2 per rank step above base
        base_difficulty = 15
        difficulty = base_difficulty + (2 * rank_steps)

        for t in targets:
            # Remove melee, momentum and guard
            encounter_state["actors"][t]["melee"] = False
            encounter_state["actors"][t]["momentum"] = False
            encounter_state["actors"][t]["guard"] = False

            # Apply pin (respects resist pin feature)
            cause_pin(t, encounter_state)

            # Each affected actor takes a fortune test
            ft_result = stat_test(t.current_fortune, difficulty)
            if ft_result == "failure":
                cause_daze(t, encounter_state)

            # Rank 10+ applies disable status
            if rank >= 10:
                cause_disable(t, encounter_state)

    elif spell_name == "locust swarm":
        # Determine targets: if caster not in melee -> all enemies; if in melee -> all actors in melee
        if encounter_state["actors"][actor]["melee"] == False:
            targets = {k: v for k, v in encounter_state["actors"].items() if v["KO"] == False and v["party"] != encounter_state["actors"][actor]["party"]}
        else:
            targets = {k: v for k, v in encounter_state["actors"].items() if v["KO"] == False and v.get("melee") == True}

        if not targets:
            return encounter_state

        h_encounter.report(f"the {rank_names[rank]} unleashes a locust swarm!")

        # End melee for ALL actors
        for actor_key in encounter_state["actors"]:
            encounter_state["actors"][actor_key]["melee"] = False

        # Difficulty increases by 2 per rank step above base
        base_difficulty = 15
        difficulty = base_difficulty + (2 * rank_steps)

        for t in targets:
            # Remove momentum and guard
            encounter_state["actors"][t]["momentum"] = False
            encounter_state["actors"][t]["guard"] = False

            # Each affected actor takes a fortune test
            ft_result = stat_test(t.current_fortune, difficulty)
            if ft_result == "failure":
                cause_blind(t, encounter_state)

            # Rank 10+ applies disable status
            if rank >= 10:
                cause_disable(t, encounter_state)

    elif spell_name == "stone skin":
        # Stone skin buffs the caster
        h_encounter.report(f"the {rank_names[rank]} cloaks {actor.name} in hardened skin!")
        
        # Base reduction bonus: +3
        reduction_bonus = 3
        power_bonus = 0
        
        # +1 reduction and power per rank step above base
        reduction_bonus += rank_steps
        power_bonus = rank_steps
        
        # Apply bonuses temporarily
        actor.current_reduction += reduction_bonus
        actor.current_power += power_bonus
        
        h_encounter.report(f"{actor.name} gains +{reduction_bonus} reduction and +{power_bonus} power for 4 turns.")
        
        # Track the buff duration in encounter_state (if not already initialized)
        if "stone_skin_buffs" not in encounter_state:
            encounter_state["stone_skin_buffs"] = {}
        
        # Set duration to 4 turns
        encounter_state["stone_skin_buffs"][actor] = {
            "duration": 4,
            "reduction_bonus": reduction_bonus,
            "power_bonus": power_bonus
        }

    return encounter_state


diablerie.description = "Call a demon from hell to cast spells."


def prowl(actor, encounter_state):
    # Prowl: similar to fight but does NOT set actor into melee.
    # If actor is not in melee, it may target any enemy (including blockers).
    if encounter_state["actors"][actor]["melee"] == False:
        # allow any enemy target (KO==False and opposite party)
        available_targets = {k: v for k, v in encounter_state["actors"].items() if v["KO"] == False and v["party"] != encounter_state["actors"][actor]["party"]}
        if not available_targets:
            return encounter_state
        if actor.logic != None:
            target = logic_target(available_targets, actor, encounter_state)
        else:
            target = choose_target(available_targets)
    else:
        # behave like a normal fight selection
        available_targets = filter_targets(actor, encounter_state)
        if actor.logic != None:
            target = logic_target(available_targets, actor, encounter_state)
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
        target = logic_target(available_targets, actor, encounter_state)
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
        target = logic_target(available_targets, actor, encounter_state)
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

def aid(actor, encounter_state):
    available_targets = {
        k: v
        for k, v in encounter_state["actors"].items()
        if v["KO"] == False
        and v["party"] == encounter_state["actors"][actor]["party"]
        and k != actor
    }

    if not available_targets:
        h_encounter.report(f"{actor.name} has no ally to aid.")
        return encounter_state

    if actor.logic != None:
        target = logic_target(available_targets, actor, encounter_state)
    else:
        target = choose_target(available_targets)

    if not target:
        return encounter_state

    target_state = encounter_state["actors"][target]
    if target_state.get("vulnerable") == True or target_state.get("daze") == True:
        if target_state.get("vulnerable") == True:
            remove_vulnerable(target, encounter_state)
        if target_state.get("daze") == True:
            remove_daze(target, encounter_state)
        h_encounter.report(f"{actor.name} aids {target.name}, steadying them.")
    else:
        target_state["momentum"] = True
        h_encounter.report(f"{actor.name} aids {target.name}, granting momentum.")

    encounter_state["actors"][actor]["momentum"] = False
    return encounter_state

def rally(actor, encounter_state):
    if "rally_used" not in encounter_state:
        encounter_state["rally_used"] = True
    else:
        if random.randint(0, 1) == 0:
            h_encounter.report(f"{actor.name}'s rally falters.")
            encounter_state["actors"][actor]["momentum"] = False
            return encounter_state

    allies = [
        k
        for k, v in encounter_state["actors"].items()
        if v["KO"] == False
        and v["party"] == encounter_state["actors"][actor]["party"]
        and k != actor
    ]

    if not allies:
        h_encounter.report(f"{actor.name} rallies, but no allies respond.")
        return encounter_state

    for ally in allies:
        ally_state = encounter_state["actors"][ally]
        if ally_state.get("vulnerable") == True or ally_state.get("daze") == True:
            if ally_state.get("vulnerable") == True:
                remove_vulnerable(ally, encounter_state)
            if ally_state.get("daze") == True:
                remove_daze(ally, encounter_state)
        else:
            ally_state["momentum"] = True

    h_encounter.report(f"{actor.name} rallies the party.")
    encounter_state["actors"][actor]["momentum"] = False
    return encounter_state

def decisive_order(actor, encounter_state):
    if encounter_state.get("decisive_order_used") == True:
        h_encounter.report(f"{actor.name} has already issued a decisive order this encounter.")
        encounter_state["actors"][actor]["momentum"] = False
        return encounter_state

    allies = {
        k: v
        for k, v in encounter_state["actors"].items()
        if v["KO"] == False
        and v["party"] == encounter_state["actors"][actor]["party"]
        and k != actor
    }

    if not allies:
        h_encounter.report(f"{actor.name} has no ally to command.")
        encounter_state["actors"][actor]["momentum"] = False
        return encounter_state

    if actor.logic != None:
        target = logic_target(allies, actor, encounter_state)
    else:
        target = choose_target(allies)

    if not target:
        encounter_state["actors"][actor]["momentum"] = False
        return encounter_state

    possible = filter_actions(
        target,
        encounter_state,
        {"fight": fight, "skirmish": skirmish, "retreat": retreat},
    )

    if not possible:
        h_encounter.report(f"{target.name} cannot act on the decisive order.")
        encounter_state["actors"][actor]["momentum"] = False
        return encounter_state

    if actor.logic != None:
        ordered_action = enemy_action_logic(target, encounter_state, possible)
    else:
        ordered_action = choose_options(possible)

    if ordered_action:
        h_encounter.report(f"{actor.name} issues a decisive order to {target.name}.")
        encounter_state = ordered_action(target, encounter_state)

    encounter_state["decisive_order_used"] = True
    encounter_state["actors"][actor]["momentum"] = False
    return encounter_state

def deliverance(actor, encounter_state):
    if encounter_state.get("deliverance_used") == True:
        h_encounter.report(f"{actor.name} has already used deliverance this encounter.")
        encounter_state["actors"][actor]["momentum"] = False
        return encounter_state

    allies = {
        k: v
        for k, v in encounter_state["actors"].items()
        if v["KO"] == False
        and v["party"] == encounter_state["actors"][actor]["party"]
        and k != actor
    }

    if not allies:
        h_encounter.report(f"{actor.name} has no ally to aid with deliverance.")
        encounter_state["actors"][actor]["momentum"] = False
        return encounter_state

    if actor.logic != None:
        target = logic_target(allies, actor, encounter_state)
    else:
        target = choose_target(allies)

    if not target:
        encounter_state["actors"][actor]["momentum"] = False
        return encounter_state

    restore = random.randint(7, 12)
    target.current_stamina = min(target.current_stamina + restore, target.stamina)

    remove_vulnerable(target, encounter_state)
    remove_daze(target, encounter_state)
    remove_pin(target, encounter_state)
    remove_disable(target, encounter_state)

    h_encounter.report(f"{actor.name} delivers salvation to {target.name}, restoring {restore} stamina.")
    encounter_state["deliverance_used"] = True
    encounter_state["actors"][actor]["momentum"] = False
    return encounter_state

def swap_arms (actor, encounter_state): 
    if actor.arms_slot2 != None:
        actor.swap()
    else:
        h_encounter.report (f"{actor.name} has no other weapons.")
        # nothing to swap
    
    encounter_state["actors"][actor]["momentum"] = False

    return encounter_state

def use_item (actor, encounter_state):
    # Access shared party inventory from encounter_state
    party_inventory = encounter_state.get("party_inventory")
    
    if party_inventory is None:
        h_encounter.report(f"No party inventory available.")
        return encounter_state
    
    items = party_inventory.get_items()
    
    if not items:
        h_encounter.report(f"The party has no items to use.")
        return encounter_state
    
    # Display items and prompt for choice
    options_index = {}
    for i, item in enumerate(items, start=1):
        print(f"{i}.\t{item.name}")
        options_index[i] = i - 1  # Store 0-indexed position
    
    try:
        choice_index = int(input("choose item."))
    except ValueError:
        choice_index = 1
    
    if choice_index > len(items):
        choice_index = len(items)
    elif choice_index < 1:
        choice_index = 1
    
    item_index = options_index[choice_index]
    consumable = items[item_index]
    
    h_encounter.report(f"{actor.name} uses {consumable.name}.")
    
    # Use the consumable
    consumable.use(actor, encounter_state)
    
    # Remove from shared inventory
    party_inventory.remove_item(item_index)
    
    encounter_state["actors"][actor]["momentum"] = False
    
    return encounter_state

def observe(actor, encounter_state):
    enemies = [e for e in encounter_state.get("enemy", []) if encounter_state["actors"][e]["KO"] == False]
    if not enemies:
        h_encounter.report("There are no enemies to observe.")
        return encounter_state

    descriptions = []
    for enemy in enemies:
        desc = getattr(enemy, "description", "")
        descriptions.append(desc if desc else enemy.name)

    h_encounter.report(f"You observe: {', '.join(descriptions)}.")
    return encounter_state

#use_item.description = "Use an item from inventory"

base_actions = {
    "fight" : fight,
    "trip" : trip,
    "skirmish" : skirmish,
    "guard" : guard,
    "block" : block,
    "retreat" : retreat,
    "aid" : aid,
    "swap" : swap_arms,
    "use item" : use_item,
    "observe" : observe
}


#------------------------------------------------------------------
# Damage and status
#------------------------------------------------------------------

def damage (actor, encounter_state, power = 0, reduction = 0, damage_type = "blunt"):

    final_damage = power - reduction

    if final_damage < 0:
        final_damage = 0

    fate_check = final_damage >= actor.current_stamina

    ft_result = None
    # If this damage would drop the actor to 0 or below, attempt a fortune test
    if fate_check:
        # Fortune test: adder = actor.current_fortune, difficulty = 10 + damage
        ft_result = stat_test(actor.current_fortune, 10 + final_damage)

    actor.current_stamina -= final_damage

    actor.pain ()

    h_encounter.report (f"{actor.name} takes {final_damage} damage.")

    if fate_check:
        h_encounter.report(f"{actor.name}'s fate is about to be decided.")
        if ft_result == "success" or ft_result == "critical":
            # Survives by fortune: restore to 1 stamina and skip death
            actor.current_stamina = 1
            h_encounter.report(f"{actor.name} is spared by fortune and clings to life.")
            return encounter_state

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
                # Enraged actors are always vulnerable
                encounter_state["actors"][actor]["vulnerable"] = True

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
    # Enraged actors cannot be disabled
    if encounter_state["actors"][actor].get("enraged") == True:
        h_encounter.report (f"{actor.name}'s rage prevents them from being disabled.")
    else:
        cause_status (actor, encounter_state, status, message)

def cause_pin (actor, encounter_state):
    status = "pin"
    message = f"{actor.name} is pinned."
    # Enraged actors cannot be pinned
    if encounter_state["actors"][actor].get("enraged") == True:
        h_encounter.report (f"{actor.name}'s rage prevents them from being pinned.")
    elif "resist pin" not in actor.features:
        cause_status (actor, encounter_state, status, message)
    else:
        # Resist pin has 75% chance to prevent pinning
        if random.randint(1, 4) <= 3:
            h_encounter.report (f"{actor.name} resists being pinned.")
        else:
            cause_status (actor, encounter_state, status, message)

def cause_blind (actor, encounter_state):
    status = "blind"
    message = f"{actor.name} is blinded."
    cause_status (actor, encounter_state, status, message)

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

def remove_blind (actor, encounter_state):
    status = "blind"
    message = f"{actor.name} is no longer blinded."
    remove_status (actor, encounter_state, status, message)
