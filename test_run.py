import h_actors, h_actions, h_encounter, h_scenario

# Monkeypatch interactive functions to be non-blocking
h_encounter.report = lambda msg: print("REPORT:", msg)
h_encounter.major_report = lambda msg: print("MAJOR:", msg)
h_actors.Actor.battlecry = lambda self: None
h_actors.Actor.pain = lambda self: None
h_actors.Actor.feeling = lambda self, s: None

# Auto-choose first option/target
h_actions.choose_options = lambda d: next(iter(d.values()))
h_actions.choose_target = lambda d: next(iter(d))
h_actions.logic_target = lambda d, *args, **kwargs: next(iter(d))

# Non-blocking party_turn and enemy_turn

def party_turn_nb(actor, encounter_state):
    possible_actions = h_actions.filter_actions(actor, encounter_state, actor.special_actions | actor.arms_actions | h_actions.base_actions)
    user_action = h_actions.choose_options(possible_actions)
    encounter_state = user_action(actor, encounter_state)
    encounter_state["actors"][actor]["active"] = False
    encounter_state["actors"][actor]["done"] = True
    return encounter_state


def enemy_turn_nb(actor, encounter_state):
    possible_actions = h_actions.filter_actions(actor, encounter_state, h_actions.base_actions | actor.special_actions | actor.arms_actions)
    enemy_action = h_actions.enemy_action_logic(actor, encounter_state, possible_actions)
    encounter_state = enemy_action(actor, encounter_state)
    encounter_state["actors"][actor]["active"] = False
    encounter_state["actors"][actor]["done"] = True
    return encounter_state

h_encounter.party_turn = party_turn_nb
h_encounter.enemy_turn = enemy_turn_nb

# Run encounter with default start scene and party
party = [h_actors.valeria, h_actors.bosh]
scene = h_scenario.start

print('Starting non-interactive encounter test...')
result_party = h_encounter.run_encounter(scene, party)
print('Encounter finished. Party status:')
enc_state = h_encounter.new_encounter(scene, party)
for p in party:
    print('-', p.name, 'KO=' , enc_state['actors'][p]['KO'])
