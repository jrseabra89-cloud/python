import types
import random
import h_actors
import h_encounter
import h_actions

class Scene:
    def __init__(self, name):
        self.name = name
        self.description = ""
        self.roster = []
        self.event = None
        self.aftermath = ""
        self.roster_options = []


# ---------------------------------------------------------------------------
# Scene guide
# ---------------------------------------------------------------------------

"""
Scene guide:

100 -> 110 -> 120
v      ^      v
130 -> 140 -> 200

200 -> 210 -> 220 -> 300
v      v      ^
230 -> 240 -> 250
       v
       400

300 -> 310 -> 320 -> 330
v      ^      v      v
340 -> 350 -> 360 -> 400

400 -> 410 -> 420 -> 500
v             ^
430 -> 440 -> 450
       v
       500

500 -> 510 -> 520
       v      v
       530 -> 540
       v      v
       600 <- 500

100: Entering the gates
110: The outer wards
150: The threshold
190: The red tunnel

200: The courtyard
240: The fallen nave
260: The catacomb stair
285: The beam walk

300: The ramparts
305: The ruined ward
310: The overlook
315: The whisper loft
320: The quiet hall
330: The broken studio
340: The broken loft
350: The reliquary
360: The iron stair
370: The cinder lift
371: The drowned trench
372: The prayer stones
373: The kennels
374: The shale steps
375: The sigil arch
376: The sigil crawl
377: The still threshold
378: The hollow stair
379: The whispering hall
380: The echoing bend

400: The galleries
420: The shattered bridge
430: The soot chapel
450: The sealed library
451: The ash square
452: The sally port
453: The postern shrine
454: The watch landing
455: The gatehouse ring
456: The broken arcade
457: The cracked ossuary
458: The blood shrine
459: The blooded culvert
460: The tomb breach
461: The low passage
462: The undercroft
463: The sinking crypt

500: The dark halls
520: The sinkhole
600: The pinnacle
"""

# ---------------------------------------------------------------------------
# Scenes
# ---------------------------------------------------------------------------


def _resolve_encounter(scene, party, grant_rewards=True):
    if scene.roster_options:
        base_roster = list(random.choice(scene.roster_options))
        extra_pool = [
            h_actors.minion_disruptive,
            h_actors.minion_aggressive,
            h_actors.minion_defensive,
            h_actors.minion_reactive,
            h_actors.minion_cutthroat,
            h_actors.minion_ravager,
            h_actors.minion_banneret,
            h_actors.minion_sentinel,
            h_actors.minion_occultist,
            h_actors.minion_dragoon,
        ]
        base_roster.append(random.choice(extra_pool))
        base_roster.append(random.choice(extra_pool))
        scene.roster = base_roster

    party = h_encounter.run_encounter(scene, party)

    if scene.aftermath:
        h_encounter.major_report(scene.aftermath)

    if grant_rewards:
        _post_encounter_rewards(party)
    return party


def _resolve_non_encounter(scene, party):
    if scene.aftermath:
        h_encounter.major_report(scene.aftermath)
    return party


def _post_encounter_rewards(party, guaranteed=False):
    if not party:
        return

    if guaranteed or random.randint(1, 4) == 1:
        h_actors.apply_boon(party)

    if guaranteed or random.randint(1, 4) == 1:
        consumables = [
            h_actors.Elixir,
            h_actors.FireBomb,
            h_actors.DevilsDust,
            h_actors.SaintsFlesh,
            h_actors.UnicornDust,
        ]
        awarded = random.choice(consumables)
        party_inventory = party[0].inventory if party else None
        if party_inventory and party_inventory.add_item(awarded):
            h_encounter.report(f"The party finds {awarded.name}.")
        else:
            h_encounter.report(f"The party finds {awarded.name}, but has no space to carry it.")


def _restore_party(party, amount):
    for actor in party:
        actor.current_stamina = min(actor.current_stamina + amount, actor.stamina)


def start_call(game_state, party):
    scene = start
    h_encounter.major_report(f"{scene.name} - {scene.description}")

    h_encounter.report("Two minions bump into the party. Their eyes reveal their wicked intent.")
    party = h_encounter.run_encounter(scene, party)

    if scene.aftermath:
        h_encounter.major_report(scene.aftermath)

    h_actors.apply_boon(party)

    game_state = "last"
    return game_state, party


def last_call(game_state, party):
    scene = last
    h_encounter.major_report(f"{scene.name} - {scene.description}")

    party = h_encounter.run_encounter(scene, party)

    if scene.aftermath:
        h_encounter.major_report(scene.aftermath)

    game_state = "END"
    return game_state, party


def choose_next(options):
    formatted = {}
    for label, data in options.items():
        if isinstance(data, dict):
            next_scene = data.get("next")
            desc = data.get("desc", "")
        elif isinstance(data, tuple) and len(data) >= 2:
            next_scene, desc = data[0], data[1]
        else:
            next_scene = data
            desc = "You move onward."

        display = f"{label} - {desc}" if desc else label
        formatted[display] = next_scene

    choice = h_actions.choose_options(formatted)
    return choice if choice else "END"


def scene_100_call(game_state, party):
    scene = scene_100
    h_encounter.major_report(f"{scene.name} - {scene.description}")

    
    party = _resolve_encounter(scene, party)

    options = {
        "to the drowned trench": ("371", "Cold water glints beneath the trench walls."),
        "to the outer wards": ("110", "Torn banners flap in a narrow ward ahead."),
        "to the prayer stones": ("372", "You see stones etched with worn names."),
        "to the threshold": ("150", "A tight passage bends toward deeper halls."),
        "to the sigil arch": ("375", "Faint runes pulse in the archway."),
    }
    game_state = choose_next(options)
    return game_state, party


def scene_105_call(game_state, party):
    scene = scene_105
    h_encounter.major_report(f"{scene.name} - {scene.description}")

    party = _resolve_encounter(scene, party)

    options = {"to the courtyard": ("200", "You smell open air and rusted steel.")}
    game_state = choose_next(options)
    return game_state, party


def scene_115_call(game_state, party):
    scene = scene_115
    h_encounter.major_report(f"{scene.name} - {scene.description}")

    prayer_options = {"leave a quiet offering": "offer", "move on": "move"}
    choice = h_actions.choose_options(prayer_options)
    if choice == "offer":
        h_encounter.report("A hush settles over the party. A boon stirs within the party.")
        h_actors.apply_boon(party)
    else:
        h_encounter.report("You keep your steps light and move on.")

    party = _resolve_non_encounter(scene, party)

    options = {"to the courtyard": ("200", "The path opens toward the main yard.")}
    game_state = choose_next(options)
    return game_state, party


def scene_110_call(game_state, party):
    scene = scene_110
    h_encounter.major_report(f"{scene.name} - {scene.description}")

    party = _resolve_encounter(scene, party)

    options = {
        "to the kennels": ("373", "A musky corridor of cages yawns ahead."),
        "to the shale steps": ("374", "Loose shale crunches down a sloped stair."),
        "to the courtyard": ("200", "Light opens into the ruined yard."),
    }
    game_state = choose_next(options)
    return game_state, party


def scene_120_call(game_state, party):
    scene = scene_120
    h_encounter.major_report(f"{scene.name} - {scene.description}")

    rest_options = {"take a moment": "rest", "press onward": "move"}
    choice = h_actions.choose_options(rest_options)
    if choice == "rest":
        _restore_party(party, 2)
        h_encounter.report("The party steadies their breathing and recovers a little stamina.")
    else:
        h_encounter.report("You press on before the silence can settle.")

    party = _resolve_non_encounter(scene, party)

    options = {"to the courtyard": ("200", "The air clears as the yard opens up.")}
    game_state = choose_next(options)
    return game_state, party


def scene_125_call(game_state, party):
    scene = scene_125
    h_encounter.major_report(f"{scene.name} - {scene.description}")

    party = _resolve_non_encounter(scene, party)

    options = {"to the courtyard": ("200", "The steps end at the main yard.")}
    game_state = choose_next(options)
    return game_state, party


def scene_130_call(game_state, party):
    scene = scene_130
    h_encounter.major_report(f"{scene.name} - {scene.description}")

    sigil_options = {"study the sigils": "study", "move on": "move"}
    choice = h_actions.choose_options(sigil_options)
    if choice == "study":
        h_encounter.report("The patterns settle your nerves. A boon stirs within the party.")
        h_actors.apply_boon(party)
    else:
        h_encounter.report("You leave the sigils undisturbed.")

    party = _resolve_non_encounter(scene, party)

    options = {
        "to the sigil crawl": ("376", "A low crawlspace bears scratched prayers."),
        "to the still threshold": ("377", "A silent choke point lies ahead."),
        "to the whispering hall": ("379", "Echoes gather in a long hall."),
        "to the courtyard": ("200", "The passage widens toward the yard."),
    }
    game_state = choose_next(options)
    return game_state, party


def scene_135_call(game_state, party):
    scene = scene_135
    h_encounter.major_report(f"{scene.name} - {scene.description}")

    party = _resolve_encounter(scene, party)

    options = {"to the courtyard": ("200", "The crawl opens toward the yard.")}
    game_state = choose_next(options)
    return game_state, party


def scene_140_call(game_state, party):
    scene = scene_140
    h_encounter.major_report(f"{scene.name} - {scene.description}")

    party = _resolve_non_encounter(scene, party)

    options = {"to the courtyard": ("200", "The choke point spills into the yard.")}
    game_state = choose_next(options)
    return game_state, party


def scene_150_call(game_state, party):
    scene = scene_150
    h_encounter.major_report(f"{scene.name} - {scene.description}")

    party = _resolve_non_encounter(scene, party)

    options = {
        "to the courtyard": ("200", "Footsteps lead toward the open yard."),
        "to the echoing bend": ("380", "A scuffed bend drops into shadows."),
        "to the hollow stair": ("378", "A hollow stairwell rings below."),
        "to the red tunnel": ("190", "Rust-streaked stone draws you onward."),
    }
    game_state = choose_next(options)
    return game_state, party


def scene_160_call(game_state, party):
    scene = scene_160
    h_encounter.major_report(f"{scene.name} - {scene.description}")

    pause_options = {"catch your breath": "rest", "move on": "move"}
    choice = h_actions.choose_options(pause_options)
    if choice == "rest":
        _restore_party(party, 1)
        h_encounter.report("A brief rest steadies the party.")
    else:
        h_encounter.report("You keep the pace and move on.")

    party = _resolve_non_encounter(scene, party)

    options = {"to the courtyard": ("200", "The stair empties into the yard.")}
    game_state = choose_next(options)
    return game_state, party


def scene_170_call(game_state, party):
    scene = scene_170
    h_encounter.major_report(f"{scene.name} - {scene.description}")

    party = _resolve_non_encounter(scene, party)

    options = {"to the courtyard": ("200", "The hall feeds back toward the yard.")}
    game_state = choose_next(options)
    return game_state, party


def scene_180_call(game_state, party):
    scene = scene_180
    h_encounter.major_report(f"{scene.name} - {scene.description}")

    party = _resolve_non_encounter(scene, party)

    options = {"to the courtyard": ("200", "The bend returns toward the yard.")}
    game_state = choose_next(options)
    return game_state, party


def scene_190_call(game_state, party):
    scene = scene_190
    h_encounter.major_report(f"{scene.name} - {scene.description}")

    party = _resolve_encounter(scene, party)

    options = {"to the broken arcade": ("456", "You glimpse fallen columns beyond.")}
    game_state = choose_next(options)
    return game_state, party


def scene_200_call(game_state, party):
    scene = scene_200
    h_encounter.major_report(f"{scene.name} - {scene.description}")

    party = _resolve_encounter(scene, party)

    options = {
        "to the ash square": ("451", "A grey square glows with ash."),
        "to the sally port": ("452", "Arrow slits and a low gate beckon."),
        "to the blood shrine": ("458", "A dark altar lies off to one side."),
        "to the broken arcade": ("456", "Collapsed columns frame a passage."),
    }
    game_state = choose_next(options)
    return game_state, party


def scene_205_call(game_state, party):
    scene = scene_205
    h_encounter.major_report(f"{scene.name} - {scene.description}")

    party = _resolve_encounter(scene, party)

    options = {"to the catacomb stair": ("260", "A stair yawns into stale dark.")}
    game_state = choose_next(options)
    return game_state, party


def scene_210_call(game_state, party):
    scene = scene_210
    h_encounter.major_report(f"{scene.name} - {scene.description}")

    party = _resolve_encounter(scene, party)

    options = {
        "to the watch landing": ("454", "A slick platform overlooks the yard."),
        "to the postern shrine": ("453", "A small shrine flickers by a side door."),
        "to the gatehouse ring": ("455", "A ring corridor echoes with steps."),
        "to the broken arcade": ("456", "Columns lie shattered in the next hall."),
    }
    game_state = choose_next(options)
    return game_state, party


def scene_215_call(game_state, party):
    scene = scene_215
    h_encounter.major_report(f"{scene.name} - {scene.description}")

    sigil_options = {"touch the ward": "touch", "move on": "move"}
    choice = h_actions.choose_options(sigil_options)
    if choice == "touch":
        _restore_party(party, 1)
        h_encounter.report("A faint warmth lingers in the party's hands.")
    else:
        h_encounter.report("You leave the old ward undisturbed.")

    party = _resolve_non_encounter(scene, party)

    options = {"to the ramparts": ("300", "Wind and height call from the walls.")}
    game_state = choose_next(options)
    return game_state, party


def scene_225_call(game_state, party):
    scene = scene_225
    h_encounter.major_report(f"{scene.name} - {scene.description}")

    party = _resolve_encounter(scene, party)

    options = {"to the ramparts": ("300", "You hear wind and the creak of battlements.")}
    game_state = choose_next(options)
    return game_state, party


def scene_220_call(game_state, party):
    scene = scene_220
    h_encounter.major_report(f"{scene.name} - {scene.description}")

    party = _resolve_non_encounter(scene, party)

    options = {"to the ramparts": ("300", "The path climbs to the walls.")}
    game_state = choose_next(options)
    return game_state, party


def scene_230_call(game_state, party):
    scene = scene_230
    h_encounter.major_report(f"{scene.name} - {scene.description}")

    party = _resolve_encounter(scene, party)

    options = {
        "to the catacomb stair": ("260", "A spiral stair drops into dry dark."),
        "to the fallen nave": ("240", "Broken beams open to the sky."),
        "to the ramparts": ("300", "Stone steps lead up to the walls."),
    }
    game_state = choose_next(options)
    return game_state, party


def scene_240_call(game_state, party):
    scene = scene_240
    h_encounter.major_report(f"{scene.name} - {scene.description}")

    party = _resolve_non_encounter(scene, party)

    options = {"to the overlook": ("310", "A broken balustrade opens to the valley.")}
    game_state = choose_next(options)
    return game_state, party


def scene_250_call(game_state, party):
    scene = scene_250
    h_encounter.major_report(f"{scene.name} - {scene.description}")

    h_encounter.report(
        "A shrine of human sacrifice stands here, its basin crusted dark and old."
    )

    shrine_options = {
        "destroy the shrine": "destroy",
        "spill blood as an offering": "offer",
        "leave it untouched": "leave",
    }
    choice = h_actions.choose_options(shrine_options)

    if choice == "offer":
        h_encounter.report("The offering is accepted. A boon stirs within the party.")
        h_actors.apply_boon(party)
    elif choice == "destroy":
        party_inventory = party[0].inventory if party else None
        items = party_inventory.get_items() if party_inventory else []
        if items:
            lost_index = random.randint(0, len(items) - 1)
            lost_item = items[lost_index]
            party_inventory.remove_item(lost_index)
            h_encounter.report(f"The shrine shatters. {lost_item.name} is lost in the ruin.")
        else:
            h_encounter.report("The shrine collapses into dust. There was nothing to lose.")
    else:
        h_encounter.report("You turn away and let the shrine's silence linger.")

    options = {
        "to the cracked ossuary": ("457", "Bones clatter in a low vault."),
        "to the blooded culvert": ("459", "A foul culvert runs red."),
        "to the catacomb stair": ("260", "Stale air spills from below."),
        "to the low passage": ("461", "The ceiling drops into a crawl."),
    }
    game_state = choose_next(options)
    return game_state, party


def scene_245_call(game_state, party):
    scene = scene_245
    h_encounter.major_report(f"{scene.name} - {scene.description}")

    party = _resolve_non_encounter(scene, party)

    options = {"to the ramparts": ("300", "You climb toward the battlements.")}
    game_state = choose_next(options)
    return game_state, party


def scene_255_call(game_state, party):
    scene = scene_255
    h_encounter.major_report(f"{scene.name} - {scene.description}")

    party = _resolve_encounter(scene, party)

    options = {"to the ramparts": ("300", "A narrow stair climbs to the walls.")}
    game_state = choose_next(options)
    return game_state, party


def scene_260_call(game_state, party):
    scene = scene_260
    h_encounter.major_report(f"{scene.name} - {scene.description}")

    party = _resolve_encounter(scene, party)

    options = {
        "to the tomb breach": ("460", "A cracked seal yawns open."),
        "to the low passage": ("461", "A low, damp corridor continues."),
        "to the sinking crypt": ("463", "The floor sinks toward graves."),
    }
    game_state = choose_next(options)
    return game_state, party


def scene_265_call(game_state, party):
    scene = scene_265
    h_encounter.major_report(f"{scene.name} - {scene.description}")

    party = _resolve_encounter(scene, party)

    options = {"to the galleries": ("400", "Faint light shafts mark the galleries.")}
    game_state = choose_next(options)
    return game_state, party


def scene_270_call(game_state, party):
    scene = scene_270
    h_encounter.major_report(f"{scene.name} - {scene.description}")

    party = _resolve_non_encounter(scene, party)

    options = {
        "to the undercroft": ("462", "Damp pillars loom in the undercroft."),
        "to the galleries": ("400", "Light leaks from high cracks."),
    }
    game_state = choose_next(options)
    return game_state, party


def scene_275_call(game_state, party):
    scene = scene_275
    h_encounter.major_report(f"{scene.name} - {scene.description}")

    party = _resolve_non_encounter(scene, party)

    options = {"to the galleries": ("400", "You follow the damp toward the galleries.")}
    game_state = choose_next(options)
    return game_state, party


def scene_280_call(game_state, party):
    scene = scene_280
    h_encounter.major_report(f"{scene.name} - {scene.description}")

    party = _resolve_non_encounter(scene, party)

    options = {
        "to the beam walk": ("285", "A narrow beam spans a drop."),
        "to the galleries": ("400", "A higher passage glows ahead."),
    }
    game_state = choose_next(options)
    return game_state, party


def scene_285_call(game_state, party):
    scene = scene_285
    h_encounter.major_report(f"{scene.name} - {scene.description}")

    party = _resolve_non_encounter(scene, party)

    options = {"to the galleries": ("400", "You cross toward the galleries.")}
    game_state = choose_next(options)
    return game_state, party


def scene_300_call(game_state, party):
    scene = scene_300
    h_encounter.major_report(f"{scene.name} - {scene.description}")

    party = _resolve_encounter(scene, party)

    options = {
        "to the ruined ward": ("305", "A gutted wardhouse gapes ahead."),
        "to the overlook": ("310", "Wind howls near a broken rail."),
        "to the whisper loft": ("315", "A narrow loft hums above."),
        "to the quiet hall": ("320", "Mosaics lie silent in a hall."),
        "to the galleries": ("400", "Light pours in from the galleries."),
    }
    game_state = choose_next(options)
    return game_state, party


def scene_305_call(game_state, party):
    scene = scene_305
    h_encounter.major_report(f"{scene.name} - {scene.description}")

    party = _resolve_encounter(scene, party)

    options = {"to the galleries": ("400", "The wardhouse spills into the galleries.")}
    game_state = choose_next(options)
    return game_state, party


def scene_315_call(game_state, party):
    scene = scene_315
    h_encounter.major_report(f"{scene.name} - {scene.description}")

    party = _resolve_non_encounter(scene, party)

    options = {"to the galleries": ("400", "The loft slopes toward the galleries.")}
    game_state = choose_next(options)
    return game_state, party


def scene_310_call(game_state, party):
    scene = scene_310
    h_encounter.major_report(f"{scene.name} - {scene.description}")

    party = _resolve_encounter(scene, party)

    options = {
        "to the broken studio": ("330", "Rotted canvases hang beyond."),
        "to the iron stair": ("360", "An iron spiral groans above."),
    }
    game_state = choose_next(options)
    return game_state, party


def scene_320_call(game_state, party):
    scene = scene_320
    h_encounter.major_report(f"{scene.name} - {scene.description}")

    party = _resolve_non_encounter(scene, party)

    options = {
        "to the broken studio": ("330", "A paint-stained studio lies ahead."),
        "to the iron stair": ("360", "The iron stair climbs in the dark."),
        "to the galleries": ("400", "A broader hall leads to the galleries."),
    }
    game_state = choose_next(options)
    return game_state, party


def scene_330_call(game_state, party):
    scene = scene_330
    h_encounter.major_report(f"{scene.name} - {scene.description}")

    party = _resolve_encounter(scene, party)

    options = {
        "to the broken loft": ("340", "Dust sifts from a loft above."),
        "to the galleries": ("400", "The studio opens to the galleries."),
    }
    game_state = choose_next(options)
    return game_state, party


def scene_340_call(game_state, party):
    scene = scene_340
    h_encounter.major_report(f"{scene.name} - {scene.description}")

    party = _resolve_encounter(scene, party)

    options = {"to the dark halls": ("500", "Cold air pulls toward the deep halls.")}
    game_state = choose_next(options)
    return game_state, party


def scene_350_call(game_state, party):
    scene = scene_350
    h_encounter.major_report(f"{scene.name} - {scene.description}")

    relic_options = {"search the reliquary": "search", "move on": "move"}
    choice = h_actions.choose_options(relic_options)
    if choice == "search":
        h_encounter.report("A relic of resolve lingers here. A boon stirs within the party.")
        h_actors.apply_boon(party)
    else:
        h_encounter.report("You leave the relics untouched.")

    party = _resolve_non_encounter(scene, party)

    options = {"to the galleries": ("400", "Relics behind you, the galleries await.")}
    game_state = choose_next(options)
    return game_state, party


def scene_360_call(game_state, party):
    scene = scene_360
    h_encounter.major_report(f"{scene.name} - {scene.description}")

    party = _resolve_encounter(scene, party)

    options = {
        "to the cinder lift": ("370", "A soot-stained lift sways in the shaft."),
        "to the galleries": ("400", "The stair feeds into the galleries."),
    }
    game_state = choose_next(options)
    return game_state, party


def scene_370_call(game_state, party):
    scene = scene_370
    h_encounter.major_report(f"{scene.name} - {scene.description}")

    party = _resolve_encounter(scene, party)

    options = {"to the shattered bridge": ("420", "A broken bridge looms ahead.")}
    game_state = choose_next(options)
    return game_state, party


def scene_400_call(game_state, party):
    scene = scene_400
    h_encounter.major_report(f"{scene.name} - {scene.description}")

    party = _resolve_encounter(scene, party)

    options = {
        "to the shattered bridge": ("420", "A narrow beam crosses the gap."),
        "to the sealed library": ("450", "Chains rattle on a barred door."),
        "to the dark halls": ("500", "Cold air spills from below."),
    }
    game_state = choose_next(options)
    return game_state, party


def scene_420_call(game_state, party):
    scene = scene_420
    h_encounter.major_report(f"{scene.name} - {scene.description}")

    party = _resolve_encounter(scene, party)

    options = {
        "to the soot chapel": ("430", "A chapel reeks of old smoke."),
        "to the dark halls": ("500", "The path drops into the deep halls."),
    }
    game_state = choose_next(options)
    return game_state, party


def scene_430_call(game_state, party):
    scene = scene_430
    h_encounter.major_report(f"{scene.name} - {scene.description}")

    party = _resolve_encounter(scene, party)

    options = {"to the dark halls": ("500", "Ash gives way to deeper darkness.")}
    game_state = choose_next(options)
    return game_state, party


def scene_450_call(game_state, party):
    scene = scene_450
    h_encounter.major_report(f"{scene.name} - {scene.description}")

    party = _resolve_non_encounter(scene, party)

    options = {"to the dark halls": ("500", "The library seals you toward the depths.")}
    game_state = choose_next(options)
    return game_state, party


def scene_500_call(game_state, party):
    scene = scene_500
    h_encounter.major_report(f"{scene.name} - {scene.description}")

    party = _resolve_encounter(scene, party)

    options = {
        "to the sinkhole": ("520", "Chains sway over a yawning pit."),
        "to the pinnacle": ("600", "A narrow spire rises above."),
    }
    game_state = choose_next(options)
    return game_state, party


def scene_520_call(game_state, party):
    scene = scene_520
    h_encounter.major_report(f"{scene.name} - {scene.description}")

    party = _resolve_encounter(scene, party)

    options = {"to the pinnacle": ("600", "A final ascent waits above.")}
    game_state = choose_next(options)
    return game_state, party


def scene_600_call(game_state, party):
    scene = scene_600
    h_encounter.major_report(f"{scene.name} - {scene.description}")

    party = _resolve_encounter(scene, party, grant_rewards=False)
    _post_encounter_rewards(party, guaranteed=True)

    game_state = "END"
    return game_state, party


start = Scene("start")
start.description = "introduction scene"
start.roster = []
start.aftermath = "The hall exhales a cold draft, and the torches gutter as if the stone itself has noticed you."

last = Scene("last")
last.description = "last scene"
last.roster = []
last.aftermath = "Only the drip of water answers you now. The castle feels older than your fear."

scene_100 = Scene("Entering the gates")
scene_100.description = "A sagging stone gate yawns open, its arch cracked and black with age in the lower hall."
scene_100.roster_options = [
    [h_actors.minion_disruptive, h_actors.minion_aggressive, h_actors.minion_reactive],
    [h_actors.minion_disruptive_2, h_actors.minion_aggressive_2, h_actors.minion_reactive_2],
    [h_actors.minion_disruptive, h_actors.minion_reactive, h_actors.minion_cutthroat],
    [h_actors.minion_aggressive, h_actors.minion_reactive_2, h_actors.minion_banneret],
]
scene_100.aftermath = (
    "They were rail-thin and scar-latticed, fighting like starved dogs. "
    "Whatever drives them is older than hunger."
    "High above the walls you see a figure observing you, they linger for a moment then leave."
)

scene_105 = Scene("The drowned trench")
scene_105.description = "A once-grand corridor lies flooded where a skylight collapsed, mosaics submerged under rain." 
scene_105.roster_options = [
    [h_actors.minion_cutthroat, h_actors.minion_reactive, h_actors.minion_disruptive_3],
    [h_actors.minion_disruptive_3, h_actors.minion_aggressive, h_actors.minion_reactive_3],
    [h_actors.minion_ravager, h_actors.minion_aggressive_3],
]
scene_105.aftermath = "Water sloshes in your boots, cold and heavy."

scene_110 = Scene("The outer wards")
scene_110.description = "A narrow ward of bare stone lies choked with rubble; torn banners cling to damp walls."
scene_110.roster_options = [
    [h_actors.minion_cutthroat, h_actors.minion_aggressive, h_actors.minion_reactive],
    [h_actors.minion_disruptive, h_actors.minion_reactive, h_actors.minion_aggressive_2],
    [h_actors.minion_ravager, h_actors.minion_cutthroat],
    [h_actors.minion_disruptive_2, h_actors.minion_aggressive_2, h_actors.minion_reactive_2],
]
scene_110.aftermath = "The ward reeks of wet iron and old ash."

scene_115 = Scene("The prayer stones")
scene_115.description = "Carved marble plinths stand beneath peeling murals, their inscriptions softened by damp." 
scene_115.aftermath = "The stones feel warm despite the chill."

scene_120 = Scene("The kennels")
scene_120.description = "A former hunting gallery lies in ruin, with broken stalls, rotted leashes, and scattered tack." 
scene_120.aftermath = "You hear claws scrabbling somewhere below."

scene_125 = Scene("The shale steps")
scene_125.description = "A marble stair sheds grit from its cracked treads, the balustrade chipped and dull." 
scene_125.aftermath = "Dust hangs in the air after every footfall."

scene_130 = Scene("The sigil arch")
scene_130.description = "A ceremonial arch of stone and brass stands tarnished, its inlay dulled by soot and age." 
scene_130.aftermath = "The runes feel like a stare you cannot return."

scene_135 = Scene("The sigil crawl")
scene_135.description = "A narrow service crawl winds beneath the upper hall, plaster cracked and gilding long faded." 
scene_135.roster_options = [
    [h_actors.minion_occultist, h_actors.minion_reactive_2],
    [h_actors.minion_disruptive, h_actors.minion_cutthroat],
]
scene_135.aftermath = "The air tastes of chalk and old smoke."

scene_140 = Scene("The still threshold")
scene_140.description = "The passage pinches between collapsed columns, quiet and cold beneath the ruined ceiling." 
scene_140.aftermath = "Even your breath sounds too loud here."

scene_150 = Scene("The threshold")
scene_150.description = "A narrow stone passage bends deeper into the lower hall; a warning is etched into the wall."
scene_150.aftermath = "For a moment the hall is quiet, and your footsteps are the only proof you are not alone."

scene_160 = Scene("The hollow stair")
scene_160.description = "A hollow stairwell of stone and brass echoes with each step, its risers chipped and uneven." 
scene_160.aftermath = "The echo fades slowly, like a held breath."

scene_170 = Scene("The whispering hall")
scene_170.description = "A long vaulted hall swallows sound, its once-rich banners rotted and hanging in strips." 
scene_170.aftermath = "It feels like the walls are listening for a name."

scene_180 = Scene("The echoing bend")
scene_180.description = "A tight bend along the gallery wall is scuffed and gouged, the floor worn smooth by passage." 
scene_180.aftermath = "Someone fled through here, and they were not alone."

scene_190 = Scene("The red tunnel")
scene_190.description = "A low stone tunnel is streaked with rust and mineral bleed, the air metallic and stale."
scene_190.roster_options = [
    [h_actors.minion_ravager, h_actors.minion_aggressive_2, h_actors.minion_reactive_2],
    [h_actors.minion_cutthroat, h_actors.minion_disruptive_2, h_actors.minion_aggressive],
]
scene_190.aftermath = "The tunnel seems to remember old blood."

scene_200 = Scene("The courtyard")
scene_200.description = "The salt catacombs open into a hollow of pale rock, its floor strewn with broken weapons and bone."
scene_200.roster_options = [
    [h_actors.minion_defensive, h_actors.minion_reactive, h_actors.minion_banneret],
    [h_actors.minion_defensive_2, h_actors.minion_reactive_2, h_actors.minion_sentinel],
    [h_actors.minion_defensive, h_actors.minion_aggressive, h_actors.minion_reactive_3],
    [h_actors.minion_defensive_3, h_actors.minion_reactive_3, h_actors.minion_cutthroat],
]
scene_200.aftermath = "Half their gear was rust and bone, half was stolen steel. The courtyard is a museum of bad ends."

scene_205 = Scene("The ash square")
scene_205.description = "A broad iron chamber flakes red rust, its floor ringed with corroded hooks and clamps."
scene_205.roster_options = [
    [h_actors.minion_occultist, h_actors.minion_banneret],
    [h_actors.minion_disruptive_3, h_actors.minion_reactive_2],
]
scene_205.aftermath = "The ash coats your sleeves like winter."

scene_210 = Scene("The sally port")
scene_210.description = "A low iron throat narrows like a gatehouse, its lintels blistered and rust-slick."
scene_210.roster_options = [
    [h_actors.minion_sentinel, h_actors.minion_reactive],
    [h_actors.minion_defensive, h_actors.minion_cutthroat],
    [h_actors.minion_defensive_2, h_actors.minion_disruptive],
]
scene_210.aftermath = "The guard post is stripped clean, but the air still tastes of fear."

scene_215 = Scene("The postern shrine")
scene_215.description = "A small shrine of riveted iron is wedged in a niche, its offerings replaced by grim tools."
scene_215.aftermath = "The wax smells faintly of herbs."

scene_225 = Scene("The gatehouse ring")
scene_225.description = "A ring corridor of iron ribs circles the vault, its plates buckled and bleeding rust."
scene_225.roster_options = [
    [h_actors.minion_sentinel, h_actors.minion_aggressive_2],
    [h_actors.minion_banneret, h_actors.minion_reactive],
]
scene_225.aftermath = "Your footsteps echo long after you stop."

scene_220 = Scene("The watch landing")
scene_220.description = "A narrow iron landing overlooks a pit of scrap and bone, slick with rust flakes."
scene_220.aftermath = "The wind carries distant steel on stone."

scene_230 = Scene("The broken arcade")
scene_230.description = "Collapsed iron arches litter the floor, their rivets snapped and their edges corroded."
scene_230.roster_options = [
    [h_actors.minion_aggressive, h_actors.minion_banneret],
    [h_actors.minion_reactive_2, h_actors.minion_ravager],
    [h_actors.minion_defensive_3, h_actors.minion_disruptive_3],
    [h_actors.champion_3, h_actors.minion_defensive_2],
]
scene_230.aftermath = "Dust clings to your skin like cold flour."

scene_240 = Scene("The fallen nave")
scene_240.description = "A collapsed burial chapel slumps into the salt cave, its floor littered with graves and bone."
scene_240.aftermath = "Birds circle above, silent and wary."

scene_250 = Scene("The blood shrine")
scene_250.description = "Between rusted pillars lies a crude altar, stained and surrounded by dull instruments."

scene_245 = Scene("The cracked ossuary")
scene_245.description = "A low iron vault holds racks of bones and tools, its plates cracked and flaking."
scene_245.aftermath = "The bones clack softly in the draft."

scene_255 = Scene("The blooded culvert")
scene_255.description = "A narrow culvert runs with rusty seep, the air sharp with metal and old blood."
scene_255.roster_options = [
    [h_actors.minion_cutthroat, h_actors.minion_disruptive],
    [h_actors.minion_ravager, h_actors.minion_reactive_3],
]
scene_255.aftermath = "The culvert stinks of old rot and rust."

scene_260 = Scene("The catacomb stair")
scene_260.description = "Salt-stone steps spiral down into a stale dark, their edges worn to powder."
scene_260.roster_options = [
    [h_actors.minion_occultist, h_actors.minion_reactive],
    [h_actors.minion_aggressive_2, h_actors.minion_defensive_2],
    [h_actors.minion_cutthroat, h_actors.minion_disruptive_3],
]
scene_260.aftermath = "The stair smells of dust, tallow, and old whispers."

scene_265 = Scene("The tomb breach")
scene_265.description = "A cracked iron seal yawns open, cold air spilling from a sealed chamber of rusted racks."
scene_265.roster_options = [
    [h_actors.minion_occultist, h_actors.minion_disruptive_2],
    [h_actors.minion_defensive_2, h_actors.minion_reactive_2],
]
scene_265.aftermath = "The seal stones feel slick with frost."

scene_270 = Scene("The low passage")
scene_270.description = "The iron ceiling drops low, forcing a crouch through flaking plates and dangling chains."
scene_270.aftermath = "Your shoulders ache from the slow crawl."

scene_275 = Scene("The undercroft")
scene_275.description = "An undercroft of iron ribs opens into a narrow chamber, its floor littered with morbid tools."
scene_275.aftermath = "Water beads on the stone like sweat."

scene_280 = Scene("The sinking crypt")
scene_280.description = "A sagging iron crypt dips into a shallow sink, its platforms warped and stained."
scene_280.aftermath = "Somewhere below, a stone rolls and never stops."

scene_285 = Scene("The beam walk")
scene_285.description = "A narrow beam crosses a salt-hewn drop, the depths below littered with graves and bones."
scene_285.aftermath = "You can feel the depth beneath every step."

scene_300 = Scene("Around the walls")
scene_300.description = "The upper hall opens into a once-lavish promenade, its gilding flaked and tapestries rotted."
scene_300.roster_options = [
    [h_actors.minion_disruptive],
    [h_actors.minion_disruptive_2],
    [h_actors.minion_reactive],
    [h_actors.minion_reactive_2],
    [h_actors.minion_cutthroat],
]
scene_300.aftermath = "A single fighter held the line like a ritual, not a fight. The stones watch, unmoved."

scene_305 = Scene("The ruined ward")
scene_305.description = "A grand wardroom sits gutted, its carved doors sagging and its marble floor cracked."
scene_305.roster_options = [
    [h_actors.minion_sentinel, h_actors.minion_aggressive],
    [h_actors.minion_defensive_3, h_actors.minion_cutthroat],
]
scene_305.aftermath = "The wardhouse smells of ash and damp leather."

scene_310 = Scene("The overlook")
scene_310.description = "A broken balustrade frames a rain-grey vista; salt-stained frescoes peel above it."
scene_310.roster_options = [
    [h_actors.minion_ravager, h_actors.minion_aggressive_3],
    [h_actors.minion_dragoon],
    [h_actors.minion_defensive_2, h_actors.minion_cutthroat],
    [h_actors.champion_2, h_actors.minion_reactive],
]
scene_310.aftermath = "The wind steals your breath, and the vista offers no comfort."

scene_315 = Scene("The whisper loft")
scene_315.description = "A narrow loft of dark beams hums with wind, its once-rich paneling warped and split."
scene_315.aftermath = "The hum fades when you stop moving."

scene_320 = Scene("The quiet hall")
scene_320.description = "A mosaic hall lies silent, its inlaid tiles cracked and dulled by dust and time."
scene_320.aftermath = "A mosaic of a crowned figure has been scraped away."

scene_330 = Scene("The broken studio")
scene_330.description = "A painter's studio sits abandoned, canvases rotted and frames gilt with tarnish."
scene_330.roster_options = [
    [h_actors.minion_occultist, h_actors.minion_banneret],
    [h_actors.minion_aggressive_3, h_actors.minion_defensive_3, h_actors.minion_reactive_3],
]
scene_330.aftermath = "The pigments smell of oil and rust."

scene_340 = Scene("The broken loft")
scene_340.description = "The loft above the studio groans underfoot, its velvet drapes reduced to ragged strips."
scene_340.roster_options = [
    [h_actors.minion_dragoon, h_actors.minion_reactive_3],
    [h_actors.minion_ravager, h_actors.minion_disruptive_2],
]
scene_340.aftermath = "Dust falls in slow sheets."

scene_350 = Scene("The reliquary")
scene_350.description = "A reliquary chamber lies plundered, its velvet-lined cases overturned and tarnished."
scene_350.aftermath = "The relics feel too cold to touch."

scene_360 = Scene("The iron stair")
scene_360.description = "An ornate iron stair twists upward, rusted and groaning beneath faded heraldry."
scene_360.roster_options = [
    [h_actors.minion_sentinel, h_actors.minion_aggressive_2],
    [h_actors.minion_dragoon, h_actors.minion_reactive_2],
    [h_actors.champion_1, h_actors.minion_defensive],
]
scene_360.aftermath = "The iron sings when struck, like a low warning."

scene_370 = Scene("The cinder lift")
scene_370.description = "A soot-stained lift hangs by a chain, its brass fittings dulled and blackened."
scene_370.roster_options = [
    [h_actors.minion_banneret, h_actors.minion_defensive_2],
    [h_actors.minion_cutthroat, h_actors.minion_aggressive_3],
]
scene_370.aftermath = "The chain groans, but it holds."

scene_400 = Scene("The derelict galleries")
scene_400.description = "The rust vault opens into a flaking iron gallery, its beams bleeding red and streaked with rust."
scene_400.roster_options = [
    [h_actors.minion_aggressive, h_actors.minion_defensive, h_actors.minion_reactive],
    [h_actors.minion_aggressive_2, h_actors.minion_defensive_2, h_actors.minion_reactive_2],
    [h_actors.minion_aggressive_3, h_actors.minion_defensive_3, h_actors.minion_reactive_3],
    [h_actors.minion_aggressive, h_actors.minion_defensive_2, h_actors.minion_reactive_3],
    [h_actors.minion_banneret, h_actors.minion_ravager, h_actors.minion_cutthroat],
]
scene_400.aftermath = "Splintered shields, perfect formation. Discipline without hope is a terrible thing to see."

scene_420 = Scene("The shattered bridge")
scene_420.description = "A collapsed iron span leaves only a narrow girder to cross, pitted and flaking with rust."
scene_420.roster_options = [
    [h_actors.minion_occultist, h_actors.minion_disruptive_2],
    [h_actors.minion_banneret, h_actors.minion_defensive, h_actors.minion_reactive_2],
    [h_actors.champion_4, h_actors.minion_cutthroat],
]
scene_420.aftermath = "The drop below eats every sound."

scene_430 = Scene("The soot chapel")
scene_430.description = "A morbid iron chapel holds corroded instruments on altars, the air metallic and bitter."
scene_430.roster_options = [
    [h_actors.minion_ravager, h_actors.minion_defensive_3],
    [h_actors.minion_cutthroat, h_actors.minion_disruptive_2, h_actors.minion_reactive],
]
scene_430.aftermath = "Ash drifts like thin snow across the floor."

scene_450 = Scene("The sealed library")
scene_450.description = "A chained iron archive seals off racks of surgical tools and morbid implements gone dull with rust."
scene_450.aftermath = "The knowledge here has been burned away."

scene_500 = Scene("Descending into the dark")
scene_500.description = "The halls beneath are cold and damp, echoing with the noises of vermin scurrying in the darkness."
scene_500.roster_options = [
    [h_actors.minion_disruptive, h_actors.minion_aggressive, h_actors.minion_defensive, h_actors.minion_reactive],
    [h_actors.minion_disruptive_2, h_actors.minion_aggressive_2, h_actors.minion_defensive_2, h_actors.minion_reactive_2],
    [h_actors.minion_disruptive_3, h_actors.minion_aggressive_3, h_actors.minion_defensive_3, h_actors.minion_reactive_3],
    [h_actors.minion_disruptive, h_actors.minion_aggressive_2, h_actors.minion_defensive_3, h_actors.minion_reactive],
    [h_actors.minion_occultist, h_actors.minion_ravager, h_actors.minion_banneret],
    [h_actors.champion_1, h_actors.minion_ravager, h_actors.minion_banneret],
]
scene_500.aftermath = "They died shivering, not from the cold but from something below. The dark feels awake."

scene_520 = Scene("The sinkhole")
scene_520.description = "A yawning sinkhole opens into a chamber of broken stairs and hanging chains."
scene_520.roster_options = [
    [h_actors.minion_dragoon, h_actors.minion_banneret],
    [h_actors.minion_ravager, h_actors.minion_occultist],
]
scene_520.aftermath = "Chains sway without wind, like a warning."

scene_600 = Scene("Reaching the pinnacle")
scene_600.description = "The pinnacle is a narrow spire of stone, overlooking the vast expanse of the mountain king's domain."
scene_600.roster_options = [
    [h_actors.minion_aggressive, h_actors.minion_defensive, h_actors.minion_reactive],
    [h_actors.minion_aggressive_2, h_actors.minion_defensive_2, h_actors.minion_reactive_2],
    [h_actors.minion_aggressive_3, h_actors.minion_defensive_3, h_actors.minion_reactive_3],
    [h_actors.minion_aggressive_2, h_actors.minion_defensive, h_actors.minion_reactive_3],
    [h_actors.minion_dragoon, h_actors.minion_ravager],
    [h_actors.champion_2, h_actors.champion_3],
    [h_actors.champion_4, h_actors.minion_defensive_3],
]
scene_600.aftermath = "At the height, there is no king to await you - you are all that is left.\n\nBroken by the weight of truth you now roam the halls,\n\nwith deep, dark eyes, insanity and the power that it brings.\n\nThe secret of life and death is finnally yours to keep."

scenario_list = {
    "start": start_call,
    "100": scene_100_call,
    "110": scene_110_call,
    "150": scene_150_call,
    "190": scene_190_call,
    "200": scene_200_call,
    "240": scene_240_call,
    "260": scene_260_call,
    "285": scene_285_call,
    "300": scene_300_call,
    "305": scene_305_call,
    "310": scene_310_call,
    "315": scene_315_call,
    "320": scene_320_call,
    "330": scene_330_call,
    "340": scene_340_call,
    "350": scene_350_call,
    "360": scene_360_call,
    "370": scene_370_call,
    "371": scene_105_call,
    "372": scene_115_call,
    "373": scene_120_call,
    "374": scene_125_call,
    "375": scene_130_call,
    "376": scene_135_call,
    "377": scene_140_call,
    "378": scene_160_call,
    "379": scene_170_call,
    "380": scene_180_call,
    "400": scene_400_call,
    "420": scene_420_call,
    "430": scene_430_call,
    "450": scene_450_call,
    "451": scene_205_call,
    "452": scene_210_call,
    "453": scene_215_call,
    "454": scene_220_call,
    "455": scene_225_call,
    "456": scene_230_call,
    "457": scene_245_call,
    "458": scene_250_call,
    "459": scene_255_call,
    "460": scene_265_call,
    "461": scene_270_call,
    "462": scene_275_call,
    "463": scene_280_call,
    "500": scene_500_call,
    "520": scene_520_call,
    "600": scene_600_call,
    "last": last_call,
}
