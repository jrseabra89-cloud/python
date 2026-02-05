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
# Scenes
# ---------------------------------------------------------------------------


def _resolve_encounter(scene, party):
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
        scene.roster = base_roster

    party = h_encounter.run_encounter(scene, party)

    if scene.aftermath:
        h_encounter.report(scene.aftermath)

    _post_encounter_rewards(party)
    return party


def _resolve_non_encounter(scene, party):
    if scene.aftermath:
        h_encounter.report(scene.aftermath)
    return party


def _post_encounter_rewards(party):
    if not party:
        return

    if random.randint(1, 4) == 1:
        h_actors.apply_boon(party)

    if random.randint(1, 4) == 1:
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
    h_encounter.report(f"{scene.name} - {scene.description}")

    h_encounter.report("Two minions bump into the party. Their eyes reveal their wicked intent.")
    party = h_encounter.run_encounter(scene, party)

    if scene.aftermath:
        h_encounter.report(scene.aftermath)

    h_actors.apply_boon(party)

    game_state = "last"
    return game_state, party


def last_call(game_state, party):
    scene = last
    h_encounter.report(f"{scene.name} - {scene.description}")

    party = h_encounter.run_encounter(scene, party)

    if scene.aftermath:
        h_encounter.report(scene.aftermath)

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
    h_encounter.report(f"{scene.name} - {scene.description}")

    
    party = _resolve_encounter(scene, party)

    options = {
        "to the drowned trench": ("105", "Cold water glints beneath the trench walls."),
        "to the outer wards": ("110", "Torn banners flap in a narrow ward ahead."),
        "to the prayer stones": ("115", "You see stones etched with worn names."),
        "to the threshold": ("150", "A tight passage bends toward deeper halls."),
        "to the sigil arch": ("130", "Faint runes pulse in the archway."),
    }
    game_state = choose_next(options)
    return game_state, party


def scene_105_call(game_state, party):
    scene = scene_105
    h_encounter.report(f"{scene.name} - {scene.description}")

    party = _resolve_encounter(scene, party)

    options = {"to the courtyard": ("200", "You smell open air and rusted steel.")}
    game_state = choose_next(options)
    return game_state, party


def scene_115_call(game_state, party):
    scene = scene_115
    h_encounter.report(f"{scene.name} - {scene.description}")

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
    h_encounter.report(f"{scene.name} - {scene.description}")

    party = _resolve_encounter(scene, party)

    options = {
        "to the kennels": ("120", "A musky corridor of cages yawns ahead."),
        "to the shale steps": ("125", "Loose shale crunches down a sloped stair."),
        "to the courtyard": ("200", "Light opens into the ruined yard."),
    }
    game_state = choose_next(options)
    return game_state, party


def scene_120_call(game_state, party):
    scene = scene_120
    h_encounter.report(f"{scene.name} - {scene.description}")

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
    h_encounter.report(f"{scene.name} - {scene.description}")

    party = _resolve_non_encounter(scene, party)

    options = {"to the courtyard": ("200", "The steps end at the main yard.")}
    game_state = choose_next(options)
    return game_state, party


def scene_130_call(game_state, party):
    scene = scene_130
    h_encounter.report(f"{scene.name} - {scene.description}")

    sigil_options = {"study the sigils": "study", "move on": "move"}
    choice = h_actions.choose_options(sigil_options)
    if choice == "study":
        h_encounter.report("The patterns settle your nerves. A boon stirs within the party.")
        h_actors.apply_boon(party)
    else:
        h_encounter.report("You leave the sigils undisturbed.")

    party = _resolve_non_encounter(scene, party)

    options = {
        "to the sigil crawl": ("135", "A low crawlspace bears scratched prayers."),
        "to the still threshold": ("140", "A silent choke point lies ahead."),
        "to the whispering hall": ("170", "Echoes gather in a long hall."),
        "to the courtyard": ("200", "The passage widens toward the yard."),
    }
    game_state = choose_next(options)
    return game_state, party


def scene_135_call(game_state, party):
    scene = scene_135
    h_encounter.report(f"{scene.name} - {scene.description}")

    party = _resolve_encounter(scene, party)

    options = {"to the courtyard": ("200", "The crawl opens toward the yard.")}
    game_state = choose_next(options)
    return game_state, party


def scene_140_call(game_state, party):
    scene = scene_140
    h_encounter.report(f"{scene.name} - {scene.description}")

    party = _resolve_non_encounter(scene, party)

    options = {"to the courtyard": ("200", "The choke point spills into the yard.")}
    game_state = choose_next(options)
    return game_state, party


def scene_150_call(game_state, party):
    scene = scene_150
    h_encounter.report(f"{scene.name} - {scene.description}")

    party = _resolve_non_encounter(scene, party)

    options = {
        "to the courtyard": ("200", "Footsteps lead toward the open yard."),
        "to the echoing bend": ("180", "A scuffed bend drops into shadows."),
        "to the hollow stair": ("160", "A hollow stairwell rings below."),
        "to the red tunnel": ("190", "Rust-streaked stone draws you onward."),
    }
    game_state = choose_next(options)
    return game_state, party


def scene_160_call(game_state, party):
    scene = scene_160
    h_encounter.report(f"{scene.name} - {scene.description}")

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
    h_encounter.report(f"{scene.name} - {scene.description}")

    party = _resolve_non_encounter(scene, party)

    options = {"to the courtyard": ("200", "The hall feeds back toward the yard.")}
    game_state = choose_next(options)
    return game_state, party


def scene_180_call(game_state, party):
    scene = scene_180
    h_encounter.report(f"{scene.name} - {scene.description}")

    party = _resolve_non_encounter(scene, party)

    options = {"to the courtyard": ("200", "The bend returns toward the yard.")}
    game_state = choose_next(options)
    return game_state, party


def scene_190_call(game_state, party):
    scene = scene_190
    h_encounter.report(f"{scene.name} - {scene.description}")

    party = _resolve_encounter(scene, party)

    options = {"to the broken arcade": ("230", "You glimpse fallen columns beyond.")}
    game_state = choose_next(options)
    return game_state, party


def scene_200_call(game_state, party):
    scene = scene_200
    h_encounter.report(f"{scene.name} - {scene.description}")

    party = _resolve_encounter(scene, party)

    options = {
        "to the ash square": ("205", "A grey square glows with ash."),
        "to the sally port": ("210", "Arrow slits and a low gate beckon."),
        "to the blood shrine": ("250", "A dark altar lies off to one side."),
        "to the broken arcade": ("230", "Collapsed columns frame a passage."),
    }
    game_state = choose_next(options)
    return game_state, party


def scene_205_call(game_state, party):
    scene = scene_205
    h_encounter.report(f"{scene.name} - {scene.description}")

    party = _resolve_encounter(scene, party)

    options = {"to the catacomb stair": ("260", "A stair yawns into stale dark.")}
    game_state = choose_next(options)
    return game_state, party


def scene_210_call(game_state, party):
    scene = scene_210
    h_encounter.report(f"{scene.name} - {scene.description}")

    party = _resolve_encounter(scene, party)

    options = {
        "to the watch landing": ("220", "A slick platform overlooks the yard."),
        "to the postern shrine": ("215", "A small shrine flickers by a side door."),
        "to the gatehouse ring": ("225", "A ring corridor echoes with steps."),
        "to the broken arcade": ("230", "Columns lie shattered in the next hall."),
    }
    game_state = choose_next(options)
    return game_state, party


def scene_215_call(game_state, party):
    scene = scene_215
    h_encounter.report(f"{scene.name} - {scene.description}")

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
    h_encounter.report(f"{scene.name} - {scene.description}")

    party = _resolve_encounter(scene, party)

    options = {"to the ramparts": ("300", "You hear wind and the creak of battlements.")}
    game_state = choose_next(options)
    return game_state, party


def scene_220_call(game_state, party):
    scene = scene_220
    h_encounter.report(f"{scene.name} - {scene.description}")

    party = _resolve_non_encounter(scene, party)

    options = {"to the ramparts": ("300", "The path climbs to the walls.")}
    game_state = choose_next(options)
    return game_state, party


def scene_230_call(game_state, party):
    scene = scene_230
    h_encounter.report(f"{scene.name} - {scene.description}")

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
    h_encounter.report(f"{scene.name} - {scene.description}")

    party = _resolve_non_encounter(scene, party)

    options = {"to the overlook": ("310", "A broken balustrade opens to the valley.")}
    game_state = choose_next(options)
    return game_state, party


def scene_250_call(game_state, party):
    scene = scene_250
    h_encounter.report(f"{scene.name} - {scene.description}")

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
        "to the cracked ossuary": ("245", "Bones clatter in a low vault."),
        "to the blooded culvert": ("255", "A foul culvert runs red."),
        "to the catacomb stair": ("260", "Stale air spills from below."),
        "to the low passage": ("270", "The ceiling drops into a crawl."),
    }
    game_state = choose_next(options)
    return game_state, party


def scene_245_call(game_state, party):
    scene = scene_245
    h_encounter.report(f"{scene.name} - {scene.description}")

    party = _resolve_non_encounter(scene, party)

    options = {"to the ramparts": ("300", "You climb toward the battlements.")}
    game_state = choose_next(options)
    return game_state, party


def scene_255_call(game_state, party):
    scene = scene_255
    h_encounter.report(f"{scene.name} - {scene.description}")

    party = _resolve_encounter(scene, party)

    options = {"to the ramparts": ("300", "A narrow stair climbs to the walls.")}
    game_state = choose_next(options)
    return game_state, party


def scene_260_call(game_state, party):
    scene = scene_260
    h_encounter.report(f"{scene.name} - {scene.description}")

    party = _resolve_encounter(scene, party)

    options = {
        "to the tomb breach": ("265", "A cracked seal yawns open."),
        "to the low passage": ("270", "A low, damp corridor continues."),
        "to the sinking crypt": ("280", "The floor sinks toward graves."),
    }
    game_state = choose_next(options)
    return game_state, party


def scene_265_call(game_state, party):
    scene = scene_265
    h_encounter.report(f"{scene.name} - {scene.description}")

    party = _resolve_encounter(scene, party)

    options = {"to the galleries": ("400", "Faint light shafts mark the galleries.")}
    game_state = choose_next(options)
    return game_state, party


def scene_270_call(game_state, party):
    scene = scene_270
    h_encounter.report(f"{scene.name} - {scene.description}")

    party = _resolve_non_encounter(scene, party)

    options = {
        "to the undercroft": ("275", "Damp pillars loom in the undercroft."),
        "to the galleries": ("400", "Light leaks from high cracks."),
    }
    game_state = choose_next(options)
    return game_state, party


def scene_275_call(game_state, party):
    scene = scene_275
    h_encounter.report(f"{scene.name} - {scene.description}")

    party = _resolve_non_encounter(scene, party)

    options = {"to the galleries": ("400", "You follow the damp toward the galleries.")}
    game_state = choose_next(options)
    return game_state, party


def scene_280_call(game_state, party):
    scene = scene_280
    h_encounter.report(f"{scene.name} - {scene.description}")

    party = _resolve_non_encounter(scene, party)

    options = {
        "to the beam walk": ("285", "A narrow beam spans a drop."),
        "to the galleries": ("400", "A higher passage glows ahead."),
    }
    game_state = choose_next(options)
    return game_state, party


def scene_285_call(game_state, party):
    scene = scene_285
    h_encounter.report(f"{scene.name} - {scene.description}")

    party = _resolve_non_encounter(scene, party)

    options = {"to the galleries": ("400", "You cross toward the galleries.")}
    game_state = choose_next(options)
    return game_state, party


def scene_300_call(game_state, party):
    scene = scene_300
    h_encounter.report(f"{scene.name} - {scene.description}")

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
    h_encounter.report(f"{scene.name} - {scene.description}")

    party = _resolve_encounter(scene, party)

    options = {"to the galleries": ("400", "The wardhouse spills into the galleries.")}
    game_state = choose_next(options)
    return game_state, party


def scene_315_call(game_state, party):
    scene = scene_315
    h_encounter.report(f"{scene.name} - {scene.description}")

    party = _resolve_non_encounter(scene, party)

    options = {"to the galleries": ("400", "The loft slopes toward the galleries.")}
    game_state = choose_next(options)
    return game_state, party


def scene_310_call(game_state, party):
    scene = scene_310
    h_encounter.report(f"{scene.name} - {scene.description}")

    party = _resolve_encounter(scene, party)

    options = {
        "to the broken studio": ("330", "Rotted canvases hang beyond."),
        "to the iron stair": ("360", "An iron spiral groans above."),
    }
    game_state = choose_next(options)
    return game_state, party


def scene_320_call(game_state, party):
    scene = scene_320
    h_encounter.report(f"{scene.name} - {scene.description}")

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
    h_encounter.report(f"{scene.name} - {scene.description}")

    party = _resolve_encounter(scene, party)

    options = {
        "to the broken loft": ("340", "Dust sifts from a loft above."),
        "to the galleries": ("400", "The studio opens to the galleries."),
    }
    game_state = choose_next(options)
    return game_state, party


def scene_340_call(game_state, party):
    scene = scene_340
    h_encounter.report(f"{scene.name} - {scene.description}")

    party = _resolve_encounter(scene, party)

    options = {"to the dark halls": ("500", "Cold air pulls toward the deep halls.")}
    game_state = choose_next(options)
    return game_state, party


def scene_350_call(game_state, party):
    scene = scene_350
    h_encounter.report(f"{scene.name} - {scene.description}")

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
    h_encounter.report(f"{scene.name} - {scene.description}")

    party = _resolve_encounter(scene, party)

    options = {
        "to the cinder lift": ("370", "A soot-stained lift sways in the shaft."),
        "to the galleries": ("400", "The stair feeds into the galleries."),
    }
    game_state = choose_next(options)
    return game_state, party


def scene_370_call(game_state, party):
    scene = scene_370
    h_encounter.report(f"{scene.name} - {scene.description}")

    party = _resolve_encounter(scene, party)

    options = {"to the shattered bridge": ("420", "A broken bridge looms ahead.")}
    game_state = choose_next(options)
    return game_state, party


def scene_400_call(game_state, party):
    scene = scene_400
    h_encounter.report(f"{scene.name} - {scene.description}")

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
    h_encounter.report(f"{scene.name} - {scene.description}")

    party = _resolve_encounter(scene, party)

    options = {
        "to the soot chapel": ("430", "A chapel reeks of old smoke."),
        "to the dark halls": ("500", "The path drops into the deep halls."),
    }
    game_state = choose_next(options)
    return game_state, party


def scene_430_call(game_state, party):
    scene = scene_430
    h_encounter.report(f"{scene.name} - {scene.description}")

    party = _resolve_encounter(scene, party)

    options = {"to the dark halls": ("500", "Ash gives way to deeper darkness.")}
    game_state = choose_next(options)
    return game_state, party


def scene_450_call(game_state, party):
    scene = scene_450
    h_encounter.report(f"{scene.name} - {scene.description}")

    party = _resolve_non_encounter(scene, party)

    options = {"to the dark halls": ("500", "The library seals you toward the depths.")}
    game_state = choose_next(options)
    return game_state, party


def scene_500_call(game_state, party):
    scene = scene_500
    h_encounter.report(f"{scene.name} - {scene.description}")

    party = _resolve_encounter(scene, party)

    options = {
        "to the sinkhole": ("520", "Chains sway over a yawning pit."),
        "to the pinnacle": ("600", "A narrow spire rises above."),
    }
    game_state = choose_next(options)
    return game_state, party


def scene_520_call(game_state, party):
    scene = scene_520
    h_encounter.report(f"{scene.name} - {scene.description}")

    party = _resolve_encounter(scene, party)

    options = {"to the pinnacle": ("600", "A final ascent waits above.")}
    game_state = choose_next(options)
    return game_state, party


def scene_600_call(game_state, party):
    scene = scene_600
    h_encounter.report(f"{scene.name} - {scene.description}")

    party = _resolve_encounter(scene, party)

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
scene_100.description = "A great gate looms before the party, it's open like a gapping maw as if ready to devour them."
scene_100.roster_options = [
    [h_actors.minion_disruptive, h_actors.minion_aggressive],
    [h_actors.minion_disruptive_2, h_actors.minion_aggressive_2],
    [h_actors.minion_disruptive, h_actors.minion_reactive],
    [h_actors.minion_aggressive, h_actors.minion_reactive_2],
]
scene_100.event = {
    "message": "The party is surprised and slows to react.",
    "effect": "party_slow_first_round",
}
scene_100.aftermath = (
    "They were rail-thin and scar-latticed, fighting like starved dogs. "
    "Whatever drives them is older than hunger."
)

scene_105 = Scene("The drowned trench")
scene_105.description = "A trench half-full of rainwater hides broken pikes and slick stones."
scene_105.roster_options = [
    [h_actors.minion_cutthroat, h_actors.minion_reactive],
    [h_actors.minion_disruptive_3, h_actors.minion_aggressive],
    [h_actors.minion_ravager],
]
scene_105.aftermath = "Water sloshes in your boots, cold and heavy."

scene_110 = Scene("The outer wards")
scene_110.description = "Brambles scrape stone and old banners hang in tatters over a narrow ward."
scene_110.roster_options = [
    [h_actors.minion_cutthroat, h_actors.minion_aggressive],
    [h_actors.minion_disruptive, h_actors.minion_reactive],
    [h_actors.minion_ravager],
    [h_actors.minion_disruptive_2, h_actors.minion_aggressive_2],
]
scene_110.aftermath = "The ward reeks of wet iron and old ash."

scene_115 = Scene("The prayer stones")
scene_115.description = "Three stones stand in a line, each etched with names worn smooth."
scene_115.aftermath = "The stones feel warm despite the chill."

scene_120 = Scene("The kennels")
scene_120.description = "Broken cages line the corridor, the air sharp with animal musk and rot."
scene_120.aftermath = "You hear claws scrabbling somewhere below."

scene_125 = Scene("The shale steps")
scene_125.description = "Loose shale crunches underfoot; each step sends a small slide down the slope."
scene_125.aftermath = "Dust hangs in the air after every footfall."

scene_130 = Scene("The sigil arch")
scene_130.description = "A stone arch is etched with warding sigils that pulse in the corner of your eye."
scene_130.aftermath = "The runes feel like a stare you cannot return."

scene_135 = Scene("The sigil crawl")
scene_135.description = "A low crawlspace is lined with fading sigils and scratched prayers."
scene_135.roster_options = [
    [h_actors.minion_occultist, h_actors.minion_reactive_2],
    [h_actors.minion_disruptive, h_actors.minion_cutthroat],
]
scene_135.aftermath = "The air tastes of chalk and old smoke."

scene_140 = Scene("The still threshold")
scene_140.description = "The corridor narrows to a choke point, silent and cold."
scene_140.aftermath = "Even your breath sounds too loud here."

scene_150 = Scene("The threshold")
scene_150.description = "A narrow passage bends toward the courtyard. Someone etched a message here 'stones too can lie'"
scene_150.aftermath = "For a moment the hall is quiet, and your footsteps are the only proof you are not alone."

scene_160 = Scene("The hollow stair")
scene_160.description = "A hollowed stairwell rings with each footstep, as if it hides a second hall below."
scene_160.aftermath = "The echo fades slowly, like a held breath."

scene_170 = Scene("The whispering hall")
scene_170.description = "Your voices carry strangely, as if the hall answers a heartbeat late."
scene_170.aftermath = "It feels like the walls are listening for a name."

scene_180 = Scene("The echoing bend")
scene_180.description = "A tight turn is scuffed with boot prints, all of them moving at speed."
scene_180.aftermath = "Someone fled through here, and they were not alone."

scene_190 = Scene("The red tunnel")
scene_190.description = "Rust stains the stones in streaks, and the air tastes metallic."
scene_190.roster_options = [
    [h_actors.minion_ravager, h_actors.minion_aggressive_2],
    [h_actors.minion_cutthroat, h_actors.minion_disruptive_2],
]
scene_190.aftermath = "The tunnel seems to remember old blood."

scene_200 = Scene("The courtyard")
scene_200.description = "The vacant courtyard is littered with broken weapons and shattered armor."
scene_200.roster_options = [
    [h_actors.minion_defensive, h_actors.minion_reactive],
    [h_actors.minion_defensive_2, h_actors.minion_reactive_2],
    [h_actors.minion_defensive, h_actors.minion_aggressive],
    [h_actors.minion_defensive_3, h_actors.minion_reactive_3],
]
scene_200.event = {
    "message": "The enemy is filled with bloodlust.",
    "effect": "enemy_momentum",
}
scene_200.aftermath = "Half their gear was rust and bone, half was stolen steel. The courtyard is a museum of bad ends."

scene_205 = Scene("The ash square")
scene_205.description = "An open square is dusted in ash, with a circle scraped clean at its center."
scene_205.roster_options = [
    [h_actors.minion_occultist, h_actors.minion_banneret],
    [h_actors.minion_disruptive_3, h_actors.minion_reactive_2],
]
scene_205.aftermath = "The ash coats your sleeves like winter."

scene_210 = Scene("The sally port")
scene_210.description = "A low gatehouse guard post hides arrow slits and a splintered portcullis."
scene_210.roster_options = [
    [h_actors.minion_sentinel, h_actors.minion_reactive],
    [h_actors.minion_defensive, h_actors.minion_cutthroat],
    [h_actors.minion_defensive_2, h_actors.minion_disruptive],
]
scene_210.aftermath = "The guard post is stripped clean, but the air still tastes of fear."

scene_215 = Scene("The postern shrine")
scene_215.description = "A small shrine is wedged beside the postern door, its candle melted to stone."
scene_215.aftermath = "The wax smells faintly of herbs."

scene_225 = Scene("The gatehouse ring")
scene_225.description = "A ring corridor circles the gatehouse, echoing with the clatter of steps."
scene_225.roster_options = [
    [h_actors.minion_sentinel, h_actors.minion_aggressive_2],
    [h_actors.minion_banneret, h_actors.minion_reactive],
]
scene_225.aftermath = "Your footsteps echo long after you stop."

scene_220 = Scene("The watch landing")
scene_220.description = "A narrow platform overlooks the yard, slick with rainwater and ash."
scene_220.aftermath = "The wind carries distant steel on stone."

scene_230 = Scene("The broken arcade")
scene_230.description = "Columns lie like felled trees, their tops carved with half-ruined saints."
scene_230.roster_options = [
    [h_actors.minion_aggressive, h_actors.minion_banneret],
    [h_actors.minion_reactive_2, h_actors.minion_ravager],
    [h_actors.minion_defensive_3, h_actors.minion_disruptive_3],
    [h_actors.champion_3, h_actors.minion_defensive_2],
]
scene_230.aftermath = "Dust clings to your skin like cold flour."

scene_240 = Scene("The fallen nave")
scene_240.description = "A collapsed chapel opens to the sky, its beams broken and mossy."
scene_240.aftermath = "Birds circle above, silent and wary."

scene_250 = Scene("The blood shrine")
scene_250.description = "Between broken columns lies a crude altar, the stone beneath it stained black."

scene_245 = Scene("The cracked ossuary")
scene_245.description = "A low vault packed with bones has cracked open to the elements."
scene_245.aftermath = "The bones clack softly in the draft."

scene_255 = Scene("The blooded culvert")
scene_255.description = "A culvert runs red with old grime and water, the air thick with iron."
scene_255.roster_options = [
    [h_actors.minion_cutthroat, h_actors.minion_disruptive],
    [h_actors.minion_ravager, h_actors.minion_reactive_3],
]
scene_255.aftermath = "The culvert stinks of old rot and rust."

scene_260 = Scene("The catacomb stair")
scene_260.description = "Stone steps spiral into a dry, stale dark."
scene_260.roster_options = [
    [h_actors.minion_occultist, h_actors.minion_reactive],
    [h_actors.minion_aggressive_2, h_actors.minion_defensive_2],
    [h_actors.minion_cutthroat, h_actors.minion_disruptive_3],
]
scene_260.aftermath = "The stair smells of dust, tallow, and old whispers."

scene_265 = Scene("The tomb breach")
scene_265.description = "A cracked seal yawns open, and cold air spills from the tomb beyond."
scene_265.roster_options = [
    [h_actors.minion_occultist, h_actors.minion_disruptive_2],
    [h_actors.minion_defensive_2, h_actors.minion_reactive_2],
]
scene_265.aftermath = "The seal stones feel slick with frost."

scene_270 = Scene("The low passage")
scene_270.description = "The ceiling drops low enough to force a crouch; the stone sweats cold."
scene_270.aftermath = "Your shoulders ache from the slow crawl."

scene_275 = Scene("The undercroft")
scene_275.description = "An undercroft opens into a narrow chamber of damp pillars."
scene_275.aftermath = "Water beads on the stone like sweat."

scene_280 = Scene("The sinking crypt")
scene_280.description = "Graves slump into a shallow sinkhole. The earth feels loose underfoot."
scene_280.aftermath = "Somewhere below, a stone rolls and never stops."

scene_285 = Scene("The beam walk")
scene_285.description = "A narrow beam spans a drop, forcing a careful, single-file crossing."
scene_285.aftermath = "You can feel the depth beneath every step."

scene_300 = Scene("Around the walls")
scene_300.description = "Looking around the walls the party sees crumbling battlements and overgrown ramparts."
scene_300.roster_options = [
    [h_actors.minion_disruptive],
    [h_actors.minion_disruptive_2],
    [h_actors.minion_reactive],
    [h_actors.minion_reactive_2],
    [h_actors.minion_cutthroat],
]
scene_300.event = {
    "message": "A brief calm steels the party's guard.",
    "effect": "party_guard",
}
scene_300.aftermath = "A single fighter held the line like a ritual, not a fight. The stones watch, unmoved."

scene_305 = Scene("The ruined ward")
scene_305.description = "A wardhouse lies gutted, its doors hanging on iron hinges."
scene_305.roster_options = [
    [h_actors.minion_sentinel, h_actors.minion_aggressive],
    [h_actors.minion_defensive_3, h_actors.minion_cutthroat],
]
scene_305.aftermath = "The wardhouse smells of ash and damp leather."

scene_310 = Scene("The overlook")
scene_310.description = "A broken balustrade reveals the valley, grey and distant through rain."
scene_310.roster_options = [
    [h_actors.minion_ravager, h_actors.minion_aggressive_3],
    [h_actors.minion_dragoon],
    [h_actors.minion_defensive_2, h_actors.minion_cutthroat],
    [h_actors.champion_2, h_actors.minion_reactive],
]
scene_310.aftermath = "The wind steals your breath, and the vista offers no comfort."

scene_315 = Scene("The whisper loft")
scene_315.description = "A narrow loft catches the wind, and the beams hum with a low tone."
scene_315.aftermath = "The hum fades when you stop moving."

scene_320 = Scene("The quiet hall")
scene_320.description = "A hall of cracked mosaics lies silent. The quiet feels deliberate."
scene_320.aftermath = "A mosaic of a crowned figure has been scraped away."

scene_330 = Scene("The broken studio")
scene_330.description = "Rotted canvases line the walls, each painting a faceless court."
scene_330.roster_options = [
    [h_actors.minion_occultist, h_actors.minion_banneret],
    [h_actors.minion_aggressive_3, h_actors.minion_defensive_3, h_actors.minion_reactive_3],
]
scene_330.aftermath = "The pigments smell of oil and rust."

scene_340 = Scene("The broken loft")
scene_340.description = "The loft above the studio shakes with every footstep and every breath."
scene_340.roster_options = [
    [h_actors.minion_dragoon, h_actors.minion_reactive_3],
    [h_actors.minion_ravager, h_actors.minion_disruptive_2],
]
scene_340.aftermath = "Dust falls in slow sheets."

scene_350 = Scene("The reliquary")
scene_350.description = "A toppled case of relics lies open, its velvet lining soaked dark."
scene_350.aftermath = "The relics feel too cold to touch."

scene_360 = Scene("The iron stair")
scene_360.description = "A spiral of iron groans with every step, the bolts long rusted."
scene_360.roster_options = [
    [h_actors.minion_sentinel, h_actors.minion_aggressive_2],
    [h_actors.minion_dragoon, h_actors.minion_reactive_2],
    [h_actors.champion_1, h_actors.minion_defensive],
]
scene_360.aftermath = "The iron sings when struck, like a low warning."

scene_370 = Scene("The cinder lift")
scene_370.description = "A soot-stained lift platform hangs by a chain, swaying with each step."
scene_370.roster_options = [
    [h_actors.minion_banneret, h_actors.minion_defensive_2],
    [h_actors.minion_cutthroat, h_actors.minion_aggressive_3],
]
scene_370.aftermath = "The chain groans, but it holds."

scene_400 = Scene("The derelict galleries")
scene_400.description = "The galleries are lit by shafts of light from cracks in the ceiling far above."
scene_400.roster_options = [
    [h_actors.minion_aggressive, h_actors.minion_defensive, h_actors.minion_reactive],
    [h_actors.minion_aggressive_2, h_actors.minion_defensive_2, h_actors.minion_reactive_2],
    [h_actors.minion_aggressive_3, h_actors.minion_defensive_3, h_actors.minion_reactive_3],
    [h_actors.minion_aggressive, h_actors.minion_defensive_2, h_actors.minion_reactive_3],
    [h_actors.minion_banneret, h_actors.minion_ravager, h_actors.minion_cutthroat],
]
scene_400.event = {
    "message": "The foes lock shields and brace themselves.",
    "effect": "enemy_guard",
}
scene_400.aftermath = "Splintered shields, perfect formation. Discipline without hope is a terrible thing to see."

scene_420 = Scene("The shattered bridge")
scene_420.description = "A collapsed bridge leaves only a narrow beam of stone to cross."
scene_420.roster_options = [
    [h_actors.minion_occultist, h_actors.minion_disruptive_2],
    [h_actors.minion_banneret, h_actors.minion_defensive, h_actors.minion_reactive_2],
    [h_actors.champion_4, h_actors.minion_cutthroat],
]
scene_420.aftermath = "The drop below eats every sound."

scene_430 = Scene("The soot chapel")
scene_430.description = "A chapel of char and soot still smells of old smoke."
scene_430.roster_options = [
    [h_actors.minion_ravager, h_actors.minion_defensive_3],
    [h_actors.minion_cutthroat, h_actors.minion_disruptive_2, h_actors.minion_reactive],
]
scene_430.aftermath = "Ash drifts like thin snow across the floor."

scene_450 = Scene("The sealed library")
scene_450.description = "A chained door bars a library of rotted shelves and blank pages."
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
scene_500.event = {
    "message": "A chilling dread leaves the party exposed.",
    "effect": "party_vulnerable",
}
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
scene_600.event = {
    "message": "At the summit, the enemy surges with momentum.",
    "effect": "enemy_momentum",
}
scene_600.aftermath = "At the height, there is no king to await you - you are all that is left.\nThe secret of life and death is finnally yours to keep.\nNow you shall roam this hall for eternity with insanity and the power that it brings."

scenario_list = {
    "start": start_call,
    "100": scene_100_call,
    "105": scene_105_call,
    "110": scene_110_call,
    "115": scene_115_call,
    "120": scene_120_call,
    "125": scene_125_call,
    "130": scene_130_call,
    "135": scene_135_call,
    "140": scene_140_call,
    "150": scene_150_call,
    "160": scene_160_call,
    "170": scene_170_call,
    "180": scene_180_call,
    "190": scene_190_call,
    "200": scene_200_call,
    "205": scene_205_call,
    "210": scene_210_call,
    "215": scene_215_call,
    "220": scene_220_call,
    "225": scene_225_call,
    "230": scene_230_call,
    "240": scene_240_call,
    "245": scene_245_call,
    "250": scene_250_call,
    "255": scene_255_call,
    "260": scene_260_call,
    "265": scene_265_call,
    "270": scene_270_call,
    "275": scene_275_call,
    "280": scene_280_call,
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
    "400": scene_400_call,
    "420": scene_420_call,
    "430": scene_430_call,
    "450": scene_450_call,
    "500": scene_500_call,
    "520": scene_520_call,
    "600": scene_600_call,
    "last": last_call,
}
