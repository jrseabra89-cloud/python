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


def _apply_stat_bonus(actor, attr, amount):
    current_attr = f"current_{attr}"
    if hasattr(actor, attr):
        setattr(actor, attr, getattr(actor, attr) + amount)
    if hasattr(actor, current_attr):
        setattr(actor, current_attr, getattr(actor, current_attr) + amount)


def _boon_benefits():
    return [
        {"name": "+3 stamina", "apply": lambda a: _apply_stat_bonus(a, "stamina", 3)},
        {"name": "+2 stamina", "apply": lambda a: _apply_stat_bonus(a, "stamina", 2)},
        {"name": "+1 skill", "apply": lambda a: _apply_stat_bonus(a, "skill", 1)},
        {"name": "+2 defense", "apply": lambda a: _apply_stat_bonus(a, "defense", 2)},
        {"name": "+1 defense", "apply": lambda a: _apply_stat_bonus(a, "defense", 1)},
        {"name": "+1 fortune", "apply": lambda a: _apply_stat_bonus(a, "fortune", 1)},
        {"name": "+2 fortune", "apply": lambda a: _apply_stat_bonus(a, "fortune", 2)},
        {"name": "+1 power", "apply": lambda a: _apply_stat_bonus(a, "power", 1)},
        {"name": "+2 power", "apply": lambda a: _apply_stat_bonus(a, "power", 2)},
        {"name": "+1 reduction", "apply": lambda a: _apply_stat_bonus(a, "reduction", 1)},
        {"name": "+1 insulation", "apply": lambda a: _apply_stat_bonus(a, "insulation", 1)},
        {
            "name": "gain riposte",
            "apply": lambda a: a.features.append("riposte") if "riposte" not in a.features else None,
        },
    ]


def apply_boon(party):
    eligible = [a for a in party if len(getattr(a, "boons", [])) < 3]
    if not eligible:
        h_encounter.report("No party member can receive more boons.")
        return

    h_encounter.report("Choose one party member to receive a boon.")
    options_index = {}
    options_counter = 0
    for actor in eligible:
        options_counter += 1
        print(f"{options_counter}.\t{actor.name}")
        options_index[options_counter] = actor

    try:
        choice_index = int(input("choose actor."))
    except ValueError:
        choice_index = 1

    if choice_index > options_counter:
        choice_index = options_counter
    elif choice_index < 1:
        choice_index = 1

    chosen_actor = options_index[choice_index]

    benefits = _boon_benefits()
    selected = random.sample(benefits, 2)

    h_encounter.report("Choose a boon:")
    boon_index = {}
    boon_counter = 0
    for boon in selected:
        boon_counter += 1
        print(f"{boon_counter}.\t{boon['name']}")
        boon_index[boon_counter] = boon

    try:
        boon_choice_index = int(input("choose boon."))
    except ValueError:
        boon_choice_index = 1

    if boon_choice_index > boon_counter:
        boon_choice_index = boon_counter
    elif boon_choice_index < 1:
        boon_choice_index = 1

    boon_choice = boon_index[boon_choice_index]
    boon_choice["apply"](chosen_actor)
    chosen_actor.boons.append(boon_choice["name"])
    h_encounter.report(f"{chosen_actor.name} gains boon: {boon_choice['name']}.")


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

        self.inventory = None

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
        self.boons = []

    def _express(self, message):
        header = ("< " * 17).rstrip()
        footer = ("> " * 17).rstrip()
        print(f"{header}\n")
        print(message)
        print(f"\n{footer}")
        input()
        return

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

        self._express(f"{self.name}:\n{battlecry_message[randomizer]}")
        # no interactive pause
        return

    def pain(self):
        randomizer = random.randint(0, 3)
        pain_message = [f"Aaaahh!", f"Curses!", f"Damn you!", f"Ooouff!"]

        self._express(f"{self.name}:\n{pain_message[randomizer]}")
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
                self._express(f"{self.name}:\n{feeling_message[randomizer]}")
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
        self.stamina += random.randint(-3, 3)
        self.skill += random.randint(-3, 3)
        self.defense += random.randint(-3, 3)
        self.fortune += random.randint(-3, 3)
        self.power += random.randint(-3, 3)
        self.current_stamina = self.stamina
        self.current_skill = self.skill
        self.current_defense = self.defense
        self.current_fortune = self.fortune
        self.current_power = self.power

    def battlecry(self):
        # Format matches Actor.battlecry: header, name, messages, footer
        randomizer = random.randint(0, 7)
        messages = [
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
        self._express(f"{self.name}:\n{messages[randomizer]}")
        return


class Master(Actor):
    def __init__(self, name):
        super().__init__(name)
        self.stamina += 6
        self.skill += 3
        self.stamina += random.randint(-3, 3)
        self.skill += random.randint(-3, 3)
        self.defense += random.randint(-3, 3)
        self.fortune += random.randint(-3, 3)
        self.power += random.randint(-3, 3)
        self.current_stamina = self.stamina
        self.current_skill = self.skill
        self.current_defense = self.defense
        self.current_fortune = self.fortune
        self.current_power = self.power

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
        self._express(f"{self.name}:\n{threats[randomizer]}")
        return


class Rowdy(Actor):
    def __init__(self, name):
        super().__init__(name)

    def battlecry(self):
        randomizer = random.randint(0, 7)
        messages = [
            "Oi! Let's make it loud!",
            "Come on then!",
            "Who's first?",
            "Ha! This'll be fun!",
            "I've got a swing to spare!",
            "Make some noise!",
            "Get stuck in!",
            "Break their line!",
        ]
        self._express(f"{self.name}:\n{messages[randomizer]}")
        return

    def pain(self):
        randomizer = random.randint(0, 3)
        messages = ["Oof!", "That all?", "Oi!", "Right in the ribs!"]
        self._express(f"{self.name}:\n{messages[randomizer]}")
        return

    def feeling(self, encounter_state):
        chance = random.randint(0, 1)
        if chance == 1:
            randomizer = random.randint(0, 3)
            if self.current_stamina < self.stamina // 2 + 1:
                messages = [
                    f"{self.name} wipes blood from their mouth and laughs.",
                    f"{self.name} spits and grins through the pain.",
                    f"{self.name} rolls their shoulders and snorts.",
                    f"{self.name} shakes out their arms, still eager.",
                ]
            else:
                messages = [
                    f"{self.name} bounces on their toes, itching for a hit.",
                    f"{self.name} cracks their knuckles with a grin.",
                    f"{self.name} makes a rude gesture at the enemy.",
                    f"{self.name} laughs and charges their stance.",
                ]
            self._express(f"{self.name}:\n{messages[randomizer]}")
            return


class Righteous(Actor):
    def __init__(self, name):
        super().__init__(name)

    def battlecry(self):
        randomizer = random.randint(0, 7)
        messages = [
            "Justice guides my hand.",
            "By oath and honor!",
            "Let righteousness prevail.",
            "Your sins end here.",
            "Stand and be judged.",
            "I am the lawful blade.",
            "In the light, I strike.",
            "No mercy for the wicked.",
        ]
        self._express(f"{self.name}:\n{messages[randomizer]}")
        return

    def pain(self):
        randomizer = random.randint(0, 3)
        messages = ["Faith endures.", "My resolve holds.", "Justice demands more.", "I will not falter."]
        self._express(f"{self.name}:\n{messages[randomizer]}")
        return

    def feeling(self, encounter_state):
        chance = random.randint(0, 1)
        if chance == 1:
            randomizer = random.randint(0, 3)
            if self.current_stamina < self.stamina // 2 + 1:
                messages = [
                    f"{self.name} whispers a vow and steadies.",
                    f"{self.name} sets their jaw, unbroken.",
                    f"{self.name} looks skyward, then refocuses.",
                    f"{self.name} stands firm despite the pain.",
                ]
            else:
                messages = [
                    f"{self.name} lifts their guard in solemn resolve.",
                    f"{self.name} watches the enemy with righteous calm.",
                    f"{self.name} advances, unwavering.",
                    f"{self.name} tightens their grip, certain of purpose.",
                ]
            self._express(f"{self.name}:\n{messages[randomizer]}")
            return


class Confident(Actor):
    def __init__(self, name):
        super().__init__(name)

    def battlecry(self):
        randomizer = random.randint(0, 7)
        messages = [
            "You can't stop me.",
            "Watch and learn.",
            "This ends now.",
            "I was born for this.",
            "Stand aside.",
            "Victory is inevitable.",
            "Try your best.",
            "Not even close.",
        ]
        self._express(f"{self.name}:\n{messages[randomizer]}")
        return

    def pain(self):
        randomizer = random.randint(0, 3)
        messages = ["Tch.", "Is that all?", "Hardly.", "You'll need more."]
        self._express(f"{self.name}:\n{messages[randomizer]}")
        return

    def feeling(self, encounter_state):
        chance = random.randint(0, 1)
        if chance == 1:
            randomizer = random.randint(0, 3)
            if self.current_stamina < self.stamina // 2 + 1:
                messages = [
                    f"{self.name} smirks despite the blood.",
                    f"{self.name} wipes their blade with a knowing grin.",
                    f"{self.name} exhales, unfazed by the pain.",
                    f"{self.name} keeps their gaze steady and sure.",
                ]
            else:
                messages = [
                    f"{self.name} stands tall, utterly sure of victory.",
                    f"{self.name} spins their weapon with practiced ease.",
                    f"{self.name} nods as if the outcome is decided.",
                    f"{self.name} smiles, inviting another challenge.",
                ]
            self._express(f"{self.name}:\n{messages[randomizer]}")
            return


class Anxious(Actor):
    def __init__(self, name):
        super().__init__(name)

    def battlecry(self):
        randomizer = random.randint(0, 7)
        messages = [
            "I can do this...",
            "Stay calm...",
            "Just breathe!",
            "Don't mess this up.",
            "Keep it together.",
            "Please be quick.",
            "Not now...",
            "Here we go.",
        ]
        self._express(f"{self.name}:\n{messages[randomizer]}")
        return

    def pain(self):
        randomizer = random.randint(0, 3)
        messages = ["Ah!", "Ow!", "Too close!", "No, no, no..."]
        self._express(f"{self.name}:\n{messages[randomizer]}")
        return

    def feeling(self, encounter_state):
        chance = random.randint(0, 1)
        if chance == 1:
            randomizer = random.randint(0, 3)
            if self.current_stamina < self.stamina // 2 + 1:
                messages = [
                    f"{self.name} swallows hard, hands trembling.",
                    f"{self.name} glances around, looking for an opening.",
                    f"{self.name} exhales sharply, trying to steady their nerves.",
                    f"{self.name} wipes sweat from their brow.",
                ]
            else:
                messages = [
                    f"{self.name} shifts their footing, uneasy.",
                    f"{self.name} keeps their guard tight, eyes darting.",
                    f"{self.name} forces a deep breath and focuses.",
                    f"{self.name} nods to themself, trying to settle down.",
                ]
            self._express(f"{self.name}:\n{messages[randomizer]}")
            return


class Callous(Actor):
    def __init__(self, name):
        super().__init__(name)

    def battlecry(self):
        randomizer = random.randint(0, 7)
        messages = [
            "Spare me the pleas.",
            "I don't feel a thing.",
            "You've already lost.",
            "Cold work, quick end.",
            "No hesitation.",
            "This is routine.",
            "Another body.",
            "Get on with it.",
        ]
        self._express(f"{self.name}:\n{messages[randomizer]}")
        return

    def pain(self):
        randomizer = random.randint(0, 3)
        messages = ["Irrelevant.", "Noted.", "Still standing.", "You done?"]
        self._express(f"{self.name}:\n{messages[randomizer]}")
        return

    def feeling(self, encounter_state):
        chance = random.randint(0, 1)
        if chance == 1:
            randomizer = random.randint(0, 3)
            if self.current_stamina < self.stamina // 2 + 1:
                messages = [
                    f"{self.name} stares through the pain without flinching.",
                    f"{self.name} wipes a cut with detached focus.",
                    f"{self.name} breathes slow, eyes empty.",
                    f"{self.name} steadies their grip, emotionless.",
                ]
            else:
                messages = [
                    f"{self.name} watches the enemy with cold patience.",
                    f"{self.name} adjusts their stance, indifferent.",
                    f"{self.name} tilts their head, unreadable.",
                    f"{self.name} shifts forward without a word.",
                ]
            self._express(f"{self.name}:\n{messages[randomizer]}")
            return


class Bully(Actor):
    def __init__(self, name):
        super().__init__(name)

    def battlecry(self):
        randomizer = random.randint(0, 7)
        messages = [
            "Back down!",
            "You're outmatched.",
            "I'll crush you.",
            "Kneel, weakling.",
            "I own this ground.",
            "I'll make this hurt.",
            "You're nothing.",
            "Try and stop me!",
        ]
        self._express(f"{self.name}:\n{messages[randomizer]}")
        return

    def pain(self):
        randomizer = random.randint(0, 3)
        messages = ["Gah!", "You'll pay for that!", "Cheap shot!", "I'll break you!"]
        self._express(f"{self.name}:\n{messages[randomizer]}")
        return

    def feeling(self, encounter_state):
        chance = random.randint(0, 1)
        if chance == 1:
            randomizer = random.randint(0, 3)
            if self.current_stamina < self.stamina // 2 + 1:
                messages = [
                    f"{self.name} snarls, anger sharpening their gaze.",
                    f"{self.name} rubs a bruise and glares.",
                    f"{self.name} spits and steps forward.",
                    f"{self.name} shakes off the pain with a scowl.",
                ]
            else:
                messages = [
                    f"{self.name} looms over the field, taunting.",
                    f"{self.name} laughs and points at their foe.",
                    f"{self.name} rolls their shoulders, looking for someone weaker.",
                    f"{self.name} smirks, confident the enemy will fold.",
                ]
            self._express(f"{self.name}:\n{messages[randomizer]}")
            return


class Libertine(Actor):
    def __init__(self, name):
        super().__init__(name)

    def battlecry(self):
        randomizer = random.randint(0, 7)
        messages = [
            "Let the night decide!",
            "No chains, no masters!",
            "To excess and victory!",
            "A toast to danger!",
            "We live for this!",
            "Fortune favors the bold!",
            "Dance with me!",
            "All thrills, no fear!",
        ]
        self._express(f"{self.name}:\n{messages[randomizer]}")
        return

    def pain(self):
        randomizer = random.randint(0, 3)
        messages = ["Ah! Spicy.", "A little sting.", "Worth it.", "What a rush!"]
        self._express(f"{self.name}:\n{messages[randomizer]}")
        return

    def feeling(self, encounter_state):
        chance = random.randint(0, 1)
        if chance == 1:
            randomizer = random.randint(0, 3)
            if self.current_stamina < self.stamina // 2 + 1:
                messages = [
                    f"{self.name} laughs breathlessly, blood on their lips.",
                    f"{self.name} brushes back their hair, still grinning.",
                    f"{self.name} sways, savoring the danger.",
                    f"{self.name} winks as if the pain is a dare.",
                ]
            else:
                messages = [
                    f"{self.name} steps lightly, almost dancing.",
                    f"{self.name} spins their weapon with flair.",
                    f"{self.name} smiles like it's a game.",
                    f"{self.name} raises their chin, fearless and free.",
                ]
            self._express(f"{self.name}:\n{messages[randomizer]}")
            return


class Erudite(Actor):
    def __init__(self, name):
        super().__init__(name)

    def battlecry(self):
        randomizer = random.randint(0, 7)
        messages = [
            "Observe and learn.",
            "A lesson in consequence.",
            "Reason yields to necessity.",
            "Precision over passion.",
            "Your stance is flawed.",
            "Let logic prevail.",
            "Every motion has purpose.",
            "This is inevitable.",
        ]
        self._express(f"{self.name}:\n{messages[randomizer]}")
        return

    def pain(self):
        randomizer = random.randint(0, 3)
        messages = ["Noted.", "Pain is data.", "Unpleasant.", "Adjusting."]
        self._express(f"{self.name}:\n{messages[randomizer]}")
        return

    def feeling(self, encounter_state):
        chance = random.randint(0, 1)
        if chance == 1:
            randomizer = random.randint(0, 3)
            if self.current_stamina < self.stamina // 2 + 1:
                messages = [
                    f"{self.name} exhales, recalculating the odds.",
                    f"{self.name} narrows their eyes, analyzing.",
                    f"{self.name} makes a small correction in footing.",
                    f"{self.name} steadies their breath, focused.",
                ]
            else:
                messages = [
                    f"{self.name} studies the enemy's rhythm.",
                    f"{self.name} tilts their head, evaluating a weak point.",
                    f"{self.name} moves with measured intent.",
                    f"{self.name} remains calm, intent on efficiency.",
                ]
            self._express(f"{self.name}:\n{messages[randomizer]}")
            return


class Downtrodden(Actor):
    def __init__(self, name):
        super().__init__(name)

    def battlecry(self):
        randomizer = random.randint(0, 7)
        messages = [
            "Just let it end.",
            "Nothing to lose.",
            "Do what you must.",
            "I won't beg.",
            "This is all I've got.",
            "Another day, another scar.",
            "Let's finish it.",
            "Go on, then.",
        ]
        self._express(f"{self.name}:\n{messages[randomizer]}")
        return

    def pain(self):
        randomizer = random.randint(0, 3)
        messages = ["Figures.", "Of course.", "I'm used to it.", "Still here."]
        self._express(f"{self.name}:\n{messages[randomizer]}")
        return

    def feeling(self, encounter_state):
        chance = random.randint(0, 1)
        if chance == 1:
            randomizer = random.randint(0, 3)
            if self.current_stamina < self.stamina // 2 + 1:
                messages = [
                    f"{self.name} sags for a moment, then pushes on.",
                    f"{self.name} looks weary, but doesn't stop.",
                    f"{self.name} wipes blood away with a tired hand.",
                    f"{self.name} exhales, resigned but steady.",
                ]
            else:
                messages = [
                    f"{self.name} keeps their head down and fights.",
                    f"{self.name} trudges forward, quiet and grim.",
                    f"{self.name} sets their jaw, accepting the fight.",
                    f"{self.name} stands firm, eyes dulled by hardship.",
                ]
            self._express(f"{self.name}:\n{messages[randomizer]}")
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
        premade_characters = {
            "Valeria": valeria,
            "Sonja": sonja,
            "Bosh": bosh,
            "Thoth": thoth,
            "Sera": sera,
        }

        full_premade = input("Use the full pre-made party? (y/n)")
        if full_premade.lower() == "y":
            party = get_default_party()
            h_encounter.report("Full pre-made party selected.")
        else:
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
            use_premade = input("Use a pre-made character for the next slot? (y/n)")
            if use_premade.lower() == "y":
                premade_characters = {
                    "Valeria": valeria,
                    "Sonja": sonja,
                    "Bosh": bosh,
                    "Thoth": thoth,
                    "Sera": sera,
                }
                available_characters = {k: v for k, v in premade_characters.items() if v not in party}

                if not available_characters:
                    h_encounter.report("No pre-made characters available. Creating a custom character instead.")
                    actor = create_actor()
                    party.append(actor)
                    continue

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
            else:
                actor = create_actor()
                party.append(actor)
        h_encounter.report("Party complete.")

    # Consumable selection
    h_encounter.report("Choose three consumables for your party.")
    selected_consumables = []
    available_consumables = {
        "elixir": Elixir,
        "fire bomb": FireBomb,
        "devil's dust": DevilsDust,
        "saint's flesh": SaintsFlesh,
        "unicorn dust": UnicornDust,
    }
    
    for i in range(3):
        remaining = available_consumables
        
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

    # Assign shared inventory to all party members
    for actor in party:
        actor.inventory = party_inventory


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
        h_encounter.report("Choose personality:")
        personality_options = {
            "standard": Actor,
            "rowdy": Rowdy,
            "righteous": Righteous,
            "confident": Confident,
            "anxious": Anxious,
            "callous": Callous,
            "bully": Bully,
            "libertine": Libertine,
            "erudite": Erudite,
            "downtrodden": Downtrodden,
        }

        options_index = {}
        options_counter = 0
        for key in personality_options:
            options_counter += 1
            text1 = f"{options_counter}.\t"
            text2 = f"{key}"
            print(text1 + text2.center(19))
            options_index[options_counter] = key

        try:
            choice_index = int(input("choose personality."))
        except ValueError:
            choice_index = 1

        if choice_index > options_counter:
            choice_index = options_counter
        elif choice_index < 1:
            choice_index = 1

        choice = options_index[choice_index]
        actor_class = personality_options[choice]
        actor = actor_class(name)

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


class SaintsFlesh(Consumable):
    def __init__(self):
        super().__init__("saint's flesh", "restores 3-6 fortune")

    def use(self, actor, encounter_state):
        fortune_restore = random.randint(3, 6)
        actor.current_fortune = min(actor.current_fortune + fortune_restore, actor.fortune)
        h_encounter.report(
            f"{actor.name} consumes the saint's flesh and restores {fortune_restore} fortune."
        )


class UnicornDust(Consumable):
    def __init__(self):
        super().__init__("unicorn dust", "grants +2 reduction and +1 power for 3 turns")

    def use(self, actor, encounter_state):
        reduction_bonus = 2
        power_bonus = 1

        actor.current_reduction += reduction_bonus
        actor.current_power += power_bonus

        h_encounter.report(
            f"{actor.name}'s skin hardens. +{reduction_bonus} reduction and +{power_bonus} power for 3 turns."
        )

        if "stone_skin_buffs" not in encounter_state:
            encounter_state["stone_skin_buffs"] = {}

        encounter_state["stone_skin_buffs"][actor] = {
            "duration": 3,
            "reduction_bonus": reduction_bonus,
            "power_bonus": power_bonus,
        }


# Create consumable instances
Elixir = Elixir()
FireBomb = FireBomb()
DevilsDust = DevilsDust()
SaintsFlesh = SaintsFlesh()
UnicornDust = UnicornDust()

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

herald = Archetype(
    "herald",
    "stamina +6, skill +2, defense +2, rally, decisive order, deliverance",
)
herald.stamina += 6
herald.skill += 2
herald.defense += 2
herald.archetype_actions = {
    "rally": h_actions.rally,
    "decisive order": h_actions.decisive_order,
    "deliverance": h_actions.deliverance,
}
herald.features = []

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

archetype_list = {
    "gendarme": gendarme,
    "herald": herald,
    "furioso": furioso,
    "heathen": heathen,
    "diabolist": diabolist,
}

# ------------------------------------------------------------------
# Enemies
# ------------------------------------------------------------------


minion_disruptive = Minion("Jinx")
minion_disruptive.logic = "disruptive"
minion_disruptive.equip_weapons(dagger_and_whip)
minion_disruptive.description = "a wiry cutpurse with a hooked whip and darting eyes"
minion_aggressive = Minion("Gnash")
minion_aggressive.logic = "aggressive"
minion_aggressive.equip_weapons(bearded_axe)
minion_aggressive.wear_armor(light_mail)
minion_aggressive.description = "a hulking brute in patched mail, hefting a chipped bearded axe"
minion_defensive = Minion("Bulwark")
minion_defensive.logic = "defensive"
minion_defensive.equip_weapons(shield_and_spear)
minion_defensive.wear_armor(heavy_mail)
minion_defensive.description = "a steady guard in heavy mail, braced behind a spear and battered shield"
minion_reactive = Minion("Skulk")
minion_reactive.logic = "reactive"
minion_reactive.equip_weapons(shield_and_club)
minion_reactive.description = "a lean scrapper lurking behind a club and buckler"

minion_disruptive_2 = Minion("Vex")
minion_disruptive_2.logic = "disruptive"
minion_disruptive_2.equip_weapons(dagger_and_whip)
minion_disruptive_2.wear_armor(light_mail)
minion_disruptive_2.description = "a twitchy raider in light mail, with a barbed whip and a jagged blade"

minion_aggressive_2 = Minion("Raze")
minion_aggressive_2.logic = "aggressive"
minion_aggressive_2.equip_weapons(bastard_sword)
minion_aggressive_2.description = "a broad-shouldered marauder swinging a heavy bastard sword"

minion_defensive_2 = Minion("Ward")
minion_defensive_2.logic = "defensive"
minion_defensive_2.equip_weapons(shield_and_sword)
minion_defensive_2.wear_armor(heavy_mail)
minion_defensive_2.description = "a grim sentinel in heavy mail behind a battered shield and short blade"

minion_reactive_2 = Minion("Mire")
minion_reactive_2.logic = "reactive"
minion_reactive_2.equip_weapons(shield_and_spear)
minion_reactive_2.wear_armor(light_mail)
minion_reactive_2.description = "a watchful lancer in light mail who shifts with every feint"

minion_disruptive_3 = Minion("Snare")
minion_disruptive_3.logic = "disruptive"
minion_disruptive_3.equip_weapons(paired_swords)
minion_disruptive_3.description = "a quick-footed duelist striking from odd angles"

minion_aggressive_3 = Minion("Cleaver")
minion_aggressive_3.logic = "aggressive"
minion_aggressive_3.equip_weapons(bearded_axe)
minion_aggressive_3.description = "a scarred axeman who swings for the bone"

minion_defensive_3 = Minion("Rampart")
minion_defensive_3.logic = "defensive"
minion_defensive_3.equip_weapons(shield_and_club)
minion_defensive_3.wear_armor(heavy_mail)
minion_defensive_3.description = "a stocky bruiser in heavy mail, braced behind a thick buckler"

minion_reactive_3 = Minion("Slink")
minion_reactive_3.logic = "reactive"
minion_reactive_3.equip_weapons(dagger_and_whip)
minion_reactive_3.description = "a patient prowler waiting to counter and cut"


# ------------------------------------------------------------------
# Pre-made Actors
# ------------------------------------------------------------------


valeria = Righteous("Valeria")
valeria.give_archetype(gendarme)
valeria.wear_armor(heavy_mail)
valeria.wear_headgear(winged_helm)
valeria.equip_weapons(shield_and_sword)
valeria.arms_slot2 = polearm

bosh = Rowdy("Bosh")
bosh.give_archetype(furioso)
bosh.wear_armor(light_mail)
bosh.wear_headgear(black_hood)
bosh.equip_weapons(bastard_sword)
bosh.arms_slot2 = shield_and_club

sonja = Confident("Sonja")
sonja.give_archetype(heathen)
sonja.wear_armor(bare)
sonja.wear_headgear(flaming_topknot)
sonja.equip_weapons(paired_swords)
sonja.arms_slot2 = dagger_and_whip

thoth = Erudite("Thoth")
thoth.give_archetype(diabolist)
thoth.wear_armor(cape)
thoth.wear_headgear(moon_circlet)
thoth.equip_weapons(dagger_and_whip)
thoth.arms_slot2 = shield_and_sword

sera = Callous("Sera")
sera.give_archetype(herald)
sera.wear_armor(light_mail)
sera.wear_headgear(winged_helm)
sera.equip_weapons(shield_and_sword)
sera.arms_slot2 = shield_and_spear


def get_default_party():
    """Returns the default party with Valeria, Sonja, Bosh, Thoth, and Sera."""
    return [valeria, sonja, bosh, thoth]