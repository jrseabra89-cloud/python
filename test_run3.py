import builtins
builtins.input = lambda *a, **k: ""

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

print('Starting non-interactive encounter test (builtins.input patched)...')
party = [h_actors.valeria, h_actors.bosh]
scene = h_scenario.start
result_party = h_encounter.run_encounter(scene, party)
print('Encounter finished. Party status:')
enc_state = h_encounter.new_encounter(scene, party)
for p in party:
    print('-', p.name, 'KO=' , enc_state['actors'][p]['KO'])
