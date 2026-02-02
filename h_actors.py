import random
import h_encounter
import h_actions


class Consumable:
    def __init__(self, name, description):
        self.name = name
        self.description = description

    def use(self, actor, encounter_state):
        """Override this method in subclasses"""
        pass


class Inventory:
    def __init__(self):
        self.items = []  # List of consumables, max 3

    def add_item(self, consumable):
        if len(self.items) < 3:
            self.items.append(consumable)
            return True
        return False

    def remove_item(self, index):
        if 0 <= index < len(self.items):
            self.items.pop(index)
            return True
        return False

    def get_items(self):
        return self.items


class Actor:
    def __init__(self, name):
        self.name = name
        self.description = ""
        self.logic = None

        self.current_stamina = 12
        self.current_skill = 10
        self.current_defense = 10
        self.current_fortune = 10
        self.current_power = 1
        self.current_reduction = 0
        self.current_insulation = 0

        self.stamina = 12
        self.skill = 10
        self.defense = 10
        self.fortune = 10
        self.power = 1
        self.reduction = 0
        self.insulation = 0

        self.inventory = Inventory()

        self.damage_type = "blunt"
        self.arms_slot1 = None
        self.arms_slot2 = None
        self.armor = None
        self.headgear = None
        self.speed = "normal"

        self.archetype = None
        self.special_actions = {}
        self.arms_actions = {}
        self.features = []

    def battlecry(self):
        randomizer = random.randint(0, 9)
        battlecry_message = [
            f"Aah!",
            f"Death to you fiend!",
            f"You will fall!",
            f"Die!",
            f"The only cure for fools is death!",
            f"I am your doom!",
            f"Rhhaaaa!",
            f"Your head is mine!",
            f"Taste steel!",
            f"You cur!",
        ]

        print("< < < < < < < > > > > > > >")
        print(f"{self.name}:")
        print(battlecry_message[randomizer])
        print("< < < < < < < > > > > > > >")
        # no interactive pause
        return

    def pain(self):
        randomizer = random.randint(0, 3)
        pain_message = [f"Aaaahh!", f"Curses!", f"Damn you!", f"Ooouff!"]

        print("< < < < < < < > > > > > > >")
        print(f"{self.name}:")
        print(pain_message[randomizer])
        print("< < < < < < < > > > > > > >")
        # no interactive pause
        return

    def feeling(self, encounter_state):
        chance = random.randint(0, 1)
        if chance == 1:
            randomizer = random.randint(0, 3)
            if self.current_stamina < self.stamina // 2 + 1:
                feeling_message = [
                    f"{self.name} spits out blood.",
                    f"{self.name} wipes away the blood and dirt from their face.",
                    f"{self.name} looks distressed.",
                    f"{self.name} has a bad feeling about this.",
                ]
            else:
                if encounter_state["actors"][self]["melee"] == True:
                    feeling_message = [
                        f"{self.name} grits their teeth.",
                        f"{self.name}'s muscles tense up.",
                        f"{self.name} breathes heavily.",
                        f"{self.name} gazes intensely into the eyes of the enemy.",
                    ]
                else:
                    feeling_message = [
                        f"{self.name} holds its weapon tight, the weight of it feels reassuring.",
                        f"{self.name}'s eyes flicker across the field.",
                        f"{self.name} sizes up its enemy.",
                        f"{self.name} senses are alert.",
                    ]
                h_encounter.report(f"{self.name}:\n{feeling_message[randomizer]}")
            return

    def death(self, damage_type="sharp"):
        randomizer = random.randint(0, 3)
        death_message = {
            "blunt": [
                f"{self.name} is beaten to a bloody pulp.",
                f"{self.name}'s skull is cracked open and they die.",
                f"{self.name}'s jaw is torn apart and they collapse.",
                f"{self.name}'s ribcage is crushed.",
            ],
            "sharp": [
                f"{self.name} drops dead in a pool of their own blood.",
                f"{self.name}'s neck is slashed open and they bleed out.",
                f"{self.name} is hacked to pieces.",
                f"{self.name} is decapitated.",
            ],
            "hellfire": [
                f"{self.name}'s flesh melts from their bones as they scream in agony.",
                f"{self.name} body crumbles to cinders and dust.",
                f"{self.name} explodes violently in a shower of gore.",
                f"{self.name} is engulfed by hellfire and turn to ashes.",
            ],
            "pierce": [
                f"{self.name} drops dead in a pool of their own blood.",
                f"{self.name}'s lung is punctured and they collapse.",
                f"{self.name} is pierced through the eye and dies.",
                f"{self.name}'s neck is pierced and they bleed out.",
            ],
        }
        h_encounter.report(f"{death_message[damage_type][randomizer]}")

    def refresh(self):
        self.current_stamina = self.stamina
        self.current_skill = self.skill
        self.current_defense = self.defense
        self.current_fortune = self.fortune
        self.current_power = self.power
        self.current_reduction = self.reduction
        self.current_insulation = self.insulation

    def give_archetype(self, archetype):
        # add archetype's specific stats to the actor
        self.stamina += getattr(archetype, "stamina", 0)
        self.skill += getattr(archetype, "skill", 0)
        self.defense += getattr(archetype, "defense", 0)
        self.power += getattr(archetype, "power", 0)
        self.fortune += getattr(archetype, "fortune", 0)
        self.reduction += getattr(archetype, "reduction", 0)
        self.insulation += getattr(archetype, "insulation", 0)
        self.special_actions = dict(archetype.archetype_actions)
        # ensure features is a list and extend
        self.features += list(archetype.features)
        self.archetype = archetype

    def equip_weapons(self, arms):

        if self.arms_slot1 == None:
            self.skill += arms.skill
            self.defense += arms.defense
            self.power += arms.power
            self.damage_type = arms.damage_type
            self.arms_slot1 = arms
            self.speed = arms.speed
            self.arms_actions = arms.arms_actions
            self.features += list(arms.features)

        else:
            self.skill -= self.arms_slot1.skill
            self.defense -= self.arms_slot1.defense
            self.power -= self.arms_slot1.power
            self.damage_type = "blunt"
            self.speed = "normal"
            self.arms_actions = {}
            # remove features safely
            for item in getattr(self.arms_slot1, "features", []):
                if item in self.features:
                    self.features.remove(item)

            self.arms_slot1 = None
            self.equip_weapons(arms)

    def wear_armor(self, armor):

        if self.armor == None:
            self.skill += armor.skill
            self.defense += armor.defense
            self.fortune += armor.fortune
            self.insulation += armor.insulation
            self.reduction += armor.reduction
            self.power += armor.power
            self.armor = armor

        else:
            self.skill -= self.armor.skill
            self.defense -= self.armor.defense
            self.fortune -= self.armor.fortune
            self.reduction -= self.armor.reduction
            self.insulation -= self.armor.insulation
            self.power -= self.armor.power
            self.armor = None

            self.wear_armor(armor)

    def wear_headgear(self, headgear):

        if self.headgear == None:
            self.skill += headgear.skill
            self.defense += headgear.defense
            self.fortune += headgear.fortune
            self.insulation += headgear.insulation
            self.reduction += headgear.reduction
            self.power += headgear.power
            self.headgear = headgear

        else:
            self.skill -= self.headgear.skill
            self.defense -= self.headgear.defense
            self.fortune -= self.headgear.fortune
            self.reduction -= self.headgear.reduction
            self.insulation -= self.headgear.insulation
            self.power -= self.headgear.power

            for item in getattr(self.headgear, "features", []):
                if item in self.features:
                    self.features.remove(item)

            self.headgear = None

            self.wear_headgear(headgear)

    def swap(self):
        h_encounter.report(
            f"{self.name} sheathes their {self.arms_slot1.name} and equips {self.arms_slot2.name}."
        )
        reserve = self.arms_slot1
        self.equip_weapons(self.arms_slot2)
        self.arms_slot2 = reserve


class Minion(Actor):
    def __init__(self, name):
        super().__init__(name)

    def battlecry(self):
        # Format matches Actor.battlecry: header, name, messages, footer
        randomizer = random.randint(0, 7)
        messages = [
            "mE mInIoN, hUnGrY",
            "SqUeAk wE gO",
            "fOlLoW lEaDeR mAyBe",
            "MaNy BiTeInGs",
            "sMaLl tOoThS eVeRyWhErE",
            "rUn rUn NO sToP",
            "FoR sWaRm nOw!",
            "wIn mAyBe nOt",
        ]

        print("< < < < < < < > > > > > > >")
        print(f"{self.name}:")
        print(messages[randomizer])
        print("< < < < < < < > > > > > > >")
        return


class Master(Actor):
    def __init__(self, name):
        super().__init__(name)

    def battlecry(self):
        # Imposing, threatening multi-line battlecry for Master actors
        randomizer = random.randint(0, 7)
        threats = [
            "Fall now; I will crush you.",
            "I will break every bone you own.",
            "No mercy, no respite.",
            "Kneel or die beneath my shadow.",
            "I will rip your ranks to pieces.",
            "No plea will save your breath.",
            "I will hunt you down, one by one.",
            "This world ends when I command it.",
        ]

        print("< < < < < < < > > > > > > >")
        print(f"{self.name}:")
        print(threats[randomizer])
        print("< < < < < < < > > > > > > >")
        return


# ------------------------------------------------------------------
# Party
# ------------------------------------------------------------------


def create_party():
    h_encounter.report("Create a new party.")
    party = []

    answer = input("Use a pre-made party? (y/n)")

    if answer.lower() == "y":
        # Pre-made character selection
        premade_characters = {"Valeria": valeria, "Sonja": sonja, "Bosh": bosh, "Thoth": thoth}
        
        h_encounter.report("Select pre-made characters for your party:")
        while len(party) < 4:
            available_characters = {k: v for k, v in premade_characters.items() if v not in party}
            
            if not available_characters:
                h_encounter.report("All available characters have been selected.")
                break
            
            options_index = {}
            options_counter = 0
            
            for key in available_characters:
                options_counter += 1
                text1 = f"{options_counter}.\t"
                text2 = f"{key}"
                print(text1 + text2.center(19))
                options_index[options_counter] = key
            
            try:
                choice_index = int(input("choose character."))
            except ValueError:
                choice_index = 1
            
            if choice_index > options_counter:
                choice_index = options_counter
            elif choice_index < 1:
                choice_index = 1
            
            choice = options_index[choice_index]
            actor = premade_characters[choice]
            
            # Display character stats for confirmation
            print("\n" + "="*50)
            print(f"CHARACTER SUMMARY: {actor.name}")
            print("="*50)
            print(f"Archetype: {actor.archetype.name}")
            print(f"Armor: {actor.armor.name if actor.armor else 'None'}")
            print(f"Headgear: {actor.headgear.name if actor.headgear else 'None'}")
            print(f"Main Weapon: {actor.arms_slot1.name if actor.arms_slot1 else 'None'}")
            print(f"Secondary Weapon: {actor.arms_slot2.name if actor.arms_slot2 else 'None'}")
            print("-"*50)
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
            print("="*50 + "\n")
            
            confirm = input("Add this character to your party? (y/n)")
            if confirm.lower() == "y":
                party.append(actor)
                h_encounter.report(f"{choice} added to party.")
            else:
                h_encounter.report("Character not added. Choose another character.")
        
        h_encounter.report("Party complete.")
    else:
        # Custom character creation
        while len(party) < 4:
            actor = create_actor()
            party.append(actor)
        h_encounter.report("Party complete.")

    # Consumable selection
    h_encounter.report("Choose three consumables for your party.")
    selected_consumables = []
    available_consumables = {"elixir": elixir, "fire bomb": fire_bomb, "devil's dust": devils_dust}
    
    for i in range(3):
        remaining = {k: v for k, v in available_consumables.items() if v not in selected_consumables}
        
        if not remaining:
            h_encounter.report("No more consumables available.")
            break
        
        options_index = {}
        options_counter = 0
        
        for key in remaining:
            options_counter += 1
            text1 = f"{options_counter}.\t"
            text2 = f"{key}"
            print(text1 + text2.center(19))
            options_index[options_counter] = key
        
        try:
            choice_index = int(input("choose consumable."))
        except ValueError:
            choice_index = 1
        
        if choice_index > options_counter:
            choice_index = options_counter
        elif choice_index < 1:
            choice_index = 1
        
        choice = options_index[choice_index]
        consumable = remaining[choice]
        selected_consumables.append(consumable)
        h_encounter.report(f"{choice.title()} selected.")
    
    # Create shared party inventory with selected consumables
    party_inventory = Inventory()
    for consumable in selected_consumables:
        party_inventory.add_item(consumable)
        h_encounter.report(f"{consumable.name} added to party inventory.")
    
    # Attach inventory to party list for later access
    #party._inventory = party_inventory


    # refresh party stats
    for actor in party:
        actor.refresh()

    return party


def create_actor():
    confirmed = False
    
    while not confirmed:
        try:
            name = input("Type character name.")
        except ValueError:
            name = "Nameless"
        actor = Actor(name)

        h_encounter.report("Choose archetype:")
        archetype_choice = h_actions.choose_options(archetype_list)
        actor.give_archetype(archetype_choice)

        h_encounter.report("Choose armor:")
        armor_choice = h_actions.choose_options(armor_list)
        actor.wear_armor(armor_choice)

        h_encounter.report("Choose headgear:")
        headgear_choice = h_actions.choose_options(headgear_list)
        actor.wear_headgear(headgear_choice)

        h_encounter.report("Choose main weapon:")
        arms_choice = h_actions.choose_options(arms_list)
        actor.equip_weapons(arms_choice)

        h_encounter.report("Choose secondary weapon:")
        arms_choice = h_actions.choose_options(arms_list)
        actor.arms_slot2 = arms_choice

        actor.refresh()

        # Display character stats
        print("\n" + "="*50)
        print(f"CHARACTER SUMMARY: {actor.name}")
        print("="*50)
        print(f"Archetype: {actor.archetype.name}")
        print(f"Armor: {actor.armor.name if actor.armor else 'None'}")
        print(f"Headgear: {actor.headgear.name if actor.headgear else 'None'}")
        print(f"Main Weapon: {actor.arms_slot1.name if actor.arms_slot1 else 'None'}")
        print(f"Secondary Weapon: {actor.arms_slot2.name if actor.arms_slot2 else 'None'}")
        print("-"*50)
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
        print("="*50 + "\n")
        
        confirm = input("Confirm this character? (y/n)")
        if confirm.lower() == "y":
            confirmed = True
            h_encounter.report("Character complete.")
        else:
            h_encounter.report("Starting character creation over...")

    return actor


# ------------------------------------------------------------------
# Equipment
# ------------------------------------------------------------------


class Arms:
    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.skill = 0
        self.defense = 0
        self.power = 0
        self.fortune = 0
        self.damage_type = "blunt"
        self.speed = "normal"
        self.arms_actions = {}
        self.features = []


shield_and_sword = Arms(
    "shield and sword", "slashing, skill +2, defense +2, stab, resist pinning."
)
shield_and_sword.skill += 1
shield_and_sword.defense += 2
shield_and_sword.damage_type = "sharp"
shield_and_sword.arms_actions = {"stab": h_actions.stab}
shield_and_sword.features = ["resist pin"]

bearded_axe = Arms("bearded axe", "slashing, power +3, defense -2, charge, slow.")
bearded_axe.power += 3
bearded_axe.defense -= 2
bearded_axe.speed = "slow"
bearded_axe.damage_type = "sharp"
bearded_axe.arms_actions = {"smash": h_actions.smash}
bearded_axe.features = ["charge"]

shield_and_spear = Arms(
    "shield and spear", "piercing, defense +2, charge, reach, resist pinning."
)
shield_and_spear.defense += 2
shield_and_spear.damage_type = "pierce"
shield_and_spear.features = ["resist pin", "reach", "charge"]

dagger_and_whip = Arms("dagger and whip", "slashing, skill +2, stab, reach, fast.")
dagger_and_whip.skill += 2
dagger_and_whip.speed = "fast"
dagger_and_whip.damage_type = "sharp"
dagger_and_whip.arms_actions = {"stab": h_actions.stab}
dagger_and_whip.features = ["reach"]

shield_and_club = Arms(
    "shield and club", "blunt, power +1, defense +2, resist pinning."
)
shield_and_club.power += 1
shield_and_club.defense += 2
shield_and_club.damage_type = "blunt"
shield_and_club.arms_actions = {"smash": h_actions.smash}
shield_and_club.features = ["resist pin"]

paired_swords = Arms("paired swords", "slashing, skill +1, power +1, stab, fast")
paired_swords.skill += 1
paired_swords.power += 1
paired_swords.speed = "fast"
paired_swords.damage_type = "sharp"
paired_swords.arms_actions = {"stab": h_actions.stab}

polearm = Arms("polearm", "piercing, power +2, charge, reach, slow.")
polearm.power += 2
polearm.speed = "slow"
polearm.damage_type = "pierce"
polearm.arms_actions = {"smash": h_actions.smash}
polearm.features = ["charge", "reach"]

bastard_sword = Arms("bastard sword", "slashing, power +2, stab.")
bastard_sword.power += 2
bastard_sword.damage_type = "sharp"
bastard_sword.arms_actions = {"stab": h_actions.stab}

arms_list = {
    "shield and sword": shield_and_sword,
    "shield and club": shield_and_club,
    "bearded axe": bearded_axe,
    "shield and spear": shield_and_spear,
    "dagger and whip": dagger_and_whip,
    "paired swords": paired_swords,
    "polearm": polearm,
    "bastard sword": bastard_sword,
}

# ------------------------------------------------------------------
# armor
# ------------------------------------------------------------------


class Armor:
    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.skill = 0
        self.defense = 0
        self.power = 0
        self.fortune = 0
        self.reduction = 0
        self.insulation = 0


bare = Armor("bare", "defense +2.")
bare.defense += 2

cape = Armor("cape", "fortune +1, insulation +1.")
cape.insulation += 1
cape.fortune += 1

light_mail = Armor("light mail", "damage reduction +1")
light_mail.reduction += 1

heavy_mail = Armor("heavy mail", "damage reduction +2, -2 insulation")
heavy_mail.reduction += 2
heavy_mail.insulation -= 2

suit_of_plate = Armor("suit of plate", "damage reduction +3, -2 skill, -2 insulation")
suit_of_plate.reduction += 3
suit_of_plate.skill -= 2
suit_of_plate.insulation -= 2

armor_list = {
    "bare": bare,
    "cape": cape,
    "light mail": light_mail,
    "heavy mail": heavy_mail,
    "suit of plate": suit_of_plate,
}

# ------------------------------------------------------------------
# headgear
# ------------------------------------------------------------------


class Headgear:
    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.skill = 0
        self.defense = 0
        self.power = 0
        self.fortune = 0
        self.reduction = 0
        self.insulation = 0
        self.features = []


winged_helm = Headgear("winged helm", "defense +1, insulation -1.")
winged_helm.defense += 1
winged_helm.insulation -= 1

moon_circlet = Headgear("moon circlet", "fortune +1, defense -1.")
moon_circlet.fortune += 1
moon_circlet.defense -= 1

stag_helm = Headgear("stag helm", "damage reduction +1, skill -2.")
stag_helm.reduction += 1
stag_helm.skill -= 2

black_hood = Headgear("black hood", "skill +1, fortune -1.")
black_hood.skill += 1
black_hood.fortune -= 1

flaming_topknot = Headgear("flaming topknot", "resist pinning, defense -1.")
flaming_topknot.features = ["resist pin"]
flaming_topknot.defense -= 1


headgear_list = {
    "winged helm": winged_helm,
    "stag helm": stag_helm,
    "moon circlet": moon_circlet,
    "black hood": black_hood,
    "flaming topknot": flaming_topknot,
}

# ------------------------------------------------------------------
# Consumables
# ------------------------------------------------------------------


class Elixir(Consumable):
    def __init__(self):
        super().__init__("elixir", "restores 7-12 stamina")
    
    def use(self, actor, encounter_state):
        stamina_restore = random.randint(7, 12)
        actor.current_stamina = min(actor.current_stamina + stamina_restore, actor.stamina)
        h_encounter.report(f"{actor.name} drinks the elixir and restores {stamina_restore} stamina.")


class FireBomb(Consumable):
    def __init__(self):
        super().__init__("fire bomb", "deals 7-12 hellfire damage (always hits)")
    
    def use(self, actor, encounter_state):
        # Select a target
        available_targets = h_actions.filter_targets(actor, encounter_state)
        
        if actor.logic != None:
            target = h_actions.logic_target(available_targets)
        else:
            target = h_actions.choose_target(available_targets)
        
        if not target:
            h_encounter.report(f"No target available for {actor.name}'s fire bomb.")
            return
        
        damage_dealt = random.randint(7, 12)
        h_encounter.report(f"{actor.name}'s fire bomb explodes on {target.name}!")
        h_actions.damage(target, encounter_state, damage_dealt, target.current_insulation, "hellfire")


class DevilsDust(Consumable):
    def __init__(self):
        super().__init__("devil's dust", "increases power by 2 and speed to fast for 4 turns")
    
    def use(self, actor, encounter_state):
        actor.current_power += 2
        actor.speed = "fast"
        h_encounter.report(f"{actor.name} inhales the devil's dust and feels more powerful!")
        h_encounter.report(f"{actor.name} gains +2 power and fast speed for 4 turns.")
        
        # Track the buff duration
        if "devils_dust_buffs" not in encounter_state:
            encounter_state["devils_dust_buffs"] = {}
        
        encounter_state["devils_dust_buffs"][actor] = {
            "duration": 4,
            "power_bonus": 2
        }


# Create consumable instances
elixir = Elixir()
fire_bomb = FireBomb()
devils_dust = DevilsDust()

# ------------------------------------------------------------------
# Archetype
# ------------------------------------------------------------------


class Archetype:
    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.stamina = 0
        self.skill = 0
        self.defense = 0
        self.power = 0
        self.fortune = 0
        self.reduction = 0
        self.insulation = 0
        self.archetype_actions = {}
        self.features = []


gendarme = Archetype("gendarme", "stamina +6, skill +4, defense + 4, riposte")
gendarme.stamina += 6
gendarme.skill += 4
gendarme.defense += 4
gendarme.features = ["riposte"]

furioso = Archetype(
    "furioso", "stamina +12, skill +2, defense + 2, hack and slash, savagery"
)
furioso.stamina += 12
furioso.skill += 2
furioso.defense += 2
furioso.archetype_actions = {"hack and slash": h_actions.hack_and_slash}
furioso.features = ["savagery"]


# New archetype: heathen
# As `gendarme` but with 3 fewer stamina and no riposte; grants
# special actions `prowl` and `dirty trick`.
heathen = Archetype("heathen", "stamina +3, skill +4, defense +4, prowl, dirty trick")
heathen.stamina += 3
heathen.skill += 4
heathen.defense += 4
heathen.archetype_actions = {"prowl": h_actions.prowl, "dirty trick": h_actions.dirty_trick}
heathen.features = []

# New archetype: diabolist
# Grants +3 fortune and the special action 'diablerie'.
diabolist = Archetype("diabolist", "fortune +3, diablerie")
diabolist.fortune += 3
diabolist.archetype_actions = {"diablerie": h_actions.diablerie}
diabolist.features = []

archetype_list = {"gendarme": gendarme, "furioso": furioso, "heathen": heathen, "diabolist": diabolist}

# ------------------------------------------------------------------
# Actors
# ------------------------------------------------------------------


minion = Minion("Skitter")
minion.logic = "minion logic"
minion.speed = "slow"
grunt = Minion("Chitter")
grunt.logic = "grunt logic"
nemesis = Actor("nemesis")
nemesis.logic = "nemesis logic"

valeria = Actor("Valeria")
valeria.give_archetype(gendarme)
valeria.wear_armor(heavy_mail)
valeria.wear_headgear(winged_helm)
valeria.equip_weapons(shield_and_sword)
valeria.arms_slot2 = polearm

bosh = Actor("Bosh")
bosh.give_archetype(furioso)
bosh.wear_armor(light_mail)
bosh.wear_headgear(black_hood)
bosh.equip_weapons(bastard_sword)
bosh.arms_slot2 = shield_and_club

sonja = Actor("Sonja")
sonja.give_archetype(heathen)
sonja.wear_armor(bare)
sonja.wear_headgear(flaming_topknot)
sonja.equip_weapons(paired_swords)
sonja.arms_slot2 = dagger_and_whip

thoth = Actor("Thoth")
thoth.give_archetype(diabolist)
thoth.wear_armor(cape)
thoth.wear_headgear(moon_circlet)
thoth.equip_weapons(dagger_and_whip)
thoth.arms_slot2 = shield_and_sword


def get_default_party():
    """Returns the default party with Valeria, Sonja, Bosh, and Thoth."""
    return [valeria, sonja, bosh, thoth]
