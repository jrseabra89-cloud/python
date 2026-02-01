import random
import h_encounter
import h_actions

class Actor:
    def __init__(self,name):
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

    def battlecry (self):
        randomizer = random.randint(0,9)
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
            f"You cur!"
            ]

        print ("< < < < < < < > > > > > > >")
        print (f"{self.name}:")
        print (battlecry_message[randomizer])
        print ("< < < < < < < > > > > > > >")
        input ("")

    def pain (self):
        randomizer = random.randint(0,3)
        pain_message = [
            f"Aaaahh!",
            f"Curses!",
            f"Damn you!",
            f"Ooouff!"
            ]

        print ("< < < < < < < > > > > > > >")
        print (f"{self.name}:")
        print (pain_message[randomizer])
        print ("< < < < < < < > > > > > > >")
        input ("")
        
    def feeling (self, encounter_state):
        chance = random.randint (0,1)
        if chance == 1:
            randomizer = random.randint(0,3)
            if self.current_stamina < self.stamina // 2 + 1:
                feeling_message = [
                    f"{self.name} spits out blood.",
                    f"{self.name} wipes away the blood and dirt from their face.",
                    f"{self.name} looks distressed.",
                    f"{self.name} has a bad feeling about this."
                ]
            else:
                if encounter_state["actors"][self]["melee"] == True:
                    feeling_message = [
                        f"{self.name} grits their teeth.",
                        f"{self.name}'s muscles tense up.",
                        f"{self.name} breathes heavily.",
                        f"{self.name} gazes intensely into the eyes of the enemy."
                        ]
                else:
        	        feeling_message = [
                        f"{self.name} holds its weapon tight, the weight of it feels reassuring.",
                        f"{self.name}'s eyes flicker across the field.",
                        f"{self.name} sizes up its enemy.",
                        f"{self.name} senses are alert."
                        ]
            h_encounter.report (f"{self.name}:\n{feeling_message[randomizer]}")

    def death (self, damage_type = "sharp"):
        randomizer = random.randint(0,3)
        death_message = {
            "blunt" : [f"{self.name} is beaten to a bloody pulp.", f"{self.name}'s skull is craked open and they die.", f"{self.name}'s jaw is torn appart an they collapse.", f"{self.name}'s' ribcage is crushed."],
            "sharp" : [f"{self.name} drops dead in a pool of their own blood.", f"{self.name}'s neck is slashed open and they bleed out.", f"{self.name} is hacked to pieces.", f"{self.name} is decapitated."],
            "hellfire" : [f"{self.name}'s flesh melts from their bones as they scream in agony.", f"{self.name} body crumbles to cinders and dust.", f"{self.name} explodes violently in a shower of gore.", f"{self.name} is engulfed by hellfire and turn to ashes."],
            "pierce" : [f"{self.name} drops dead in a pool of their own blood.", f"{self.name}'s lung is punctured and they collapse.", f"{self.name} is pierced through the eye and dies.", f"{self.name}'s neck is pierced and they bleed out."]
            }
        h_encounter.report (f"{death_message[damage_type][randomizer]}")

    def refresh (self):
        self.current_stamina = self.stamina
        self.current_skill = self.skill
        self.current_defense = self.defense
        self.current_fortune = self.fortune
        self.current_power = self.power
        self.current_reduction = self.reduction
        self.current_insulation = self.insulation


    def give_archetype (self, archetype):
        
        self.skill += archetype.skill
        self.defense += archetype.skill
        self.power += archetype.skill
        self.fortune += archetype.skill
        self.reduction += archetype.skill
        self.insulation += archetype.skill
        self.special_actions = archetype.archetype_actions
        self.features += archetype.features
        self.archetype = archetype


    def equip_weapons (self, arms):

        if self.arms_slot1 == None:        
            self.skill += arms.skill
            self.defense += arms.defense
            self.power += arms.power
            self.damage = arms.damage_type
            self.arms_slot1 = arms
            self.speed = arms.speed
            self.arms_actions = arms.arms_actions
            self.features += arms.features

        else:
            self.skill -= self.arms_slot1.skill
            self.defense -= self.arms_slot1.defense
            self.power -= self.arms_slot1.power
            self.damage = "blunt"
            self.speed = "normal"
            self.arms_actions = {}
            for item in self.arms_slot1.features:
                self.features.remove(item)

            self.arms_slot1 = None
            self.equip_weapons (arms)

    def wear_armor (self, armor):

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

            self.wear_armor (armor)

    def wear_headgear (self, headgear):

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

            for item in self.headgear.features:
                self.features.remove(item)
            
            self.headgear = None

            self.wear_headgear (headgear)

    def swap (self):
        h_encounter.report (f"{self.name} sheats their {self.arms_slot1.name} and equips {self.arms_slot2.name}.")
        reserve = self.arms_slot1
        self.equip_weapons (self.arms_slot2)
        self.arms_slot2 = reserve


#------------------------------------------------------------------
# Party
#------------------------------------------------------------------

def create_party ():
    h_encounter.report ("Create a new party.")
    party = []

    answer = input ("Use default party? (y/n)")

    if answer == "n":
        while len(party) <2:
            actor = create_actor ()
            
            party.append(actor)
        h_encounter.report ("Party complete.")
    else:
        party = [valeria, bosh]

    return party

def create_actor ():
    try:
        name = input ("Type character name.")
    except ValueError:
        name = "Nameless"
    actor = Actor (name)
    
    h_encounter.report ("Choose archetype:")
    archetype_choice = h_actions.choose_options (archetype_list)
    actor.give_archetype(archetype_choice)
    
    h_encounter.report ("Choose armor:")
    armor_choice = h_actions.choose_options (armor_list)
    actor.wear_armor(armor_choice)
    
    h_encounter.report ("Choose headgear:")
    headgear_choice = h_actions.choose_options (headgear_list)
    actor.wear_headgear(headgear_choice)
    
    h_encounter.report ("Choose main weapon:")
    arms_choice = h_actions.choose_options (arms_list)
    actor.equip_weapons (arms_choice)
    
    h_encounter.report ("Choose secondary weapon:")
    arms_choice = h_actions.choose_options (arms_list)
    actor.arms_slot2 = arms_choice

    actor.refresh ()

    h_encounter.report ("Character complete.")
    return actor


#------------------------------------------------------------------
# Equipment
#------------------------------------------------------------------

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

shield_and_sword = Arms ("shield and sword", "slashing, skill +2, defense +2, stab, resist pinning.")
shield_and_sword.skill += 1
shield_and_sword.defense += 2
shield_and_sword.damage_type = "sharp"
shield_and_sword.arms_actions = {"stab" : h_actions.stab}
shield_and_sword.features = ["resist pin"]

bearded_axe = Arms ("bearded axe", "slashing, power +3, defense -2, charge, slow.")
bearded_axe.power += 3
bearded_axe.defense -= 2
bearded_axe.speed = "slow"
bearded_axe.damage_type = "sharp"
bearded_axe.features = ["charge"]

shield_and_spear = Arms ("shield and spear", "piercing, defense +2, charge, reach, resist pinning.")
shield_and_spear.defense += 2
shield_and_spear.damage_type = "pierce"
shield_and_spear.features = ["resist pin", "reach", "charge"]

dagger_and_whip = Arms ("dagger and whip", "slashing, skill +2, stab, reach, fast.")
dagger_and_whip.skill += 2
dagger_and_whip.speed = "fast"
dagger_and_whip.damage_type = "sharp"
dagger_and_whip.arms_actions = {"stab" : h_actions.stab}
dagger_and_whip.features = ["reach"]

shield_and_club = Arms ("shield and club", "blunt, power +1, defense +2, resist pinning.")
shield_and_club.power += 1
shield_and_club.defense += 2
shield_and_club.damage_type = "blunt"
shield_and_club.features = ["resist pin"]

paired_swords = Arms ("paired swords", "slashing, skill +1, power +1, stab, fast")
paired_swords.skill += 1
paired_swords.power += 1
paired_swords.speed = "fast"
paired_swords.damage_type = "sharp"
paired_swords.arms_actions = {"stab" : h_actions.stab}

polearm = Arms ("polearm", "piercing, power +2, charge, reach, slow.")
polearm.power += 2
polearm.speed = "slow"
polearm.damage_type = "pierce"
polearm.features = ["charge", "reach"]

bastard_sword = Arms ("bastard sword", "slashing, power +2, stab.")
bastard_sword.power += 2
bastard_sword.damage_type = "sharp"
bastard_sword.arms_actions = {"stab" : h_actions.stab}

arms_list = {
    "shield and sword" : shield_and_sword,
    "shield and club" : shield_and_club,
    "bearded axe" : bearded_axe,
    "shield and spear" : shield_and_spear,
    "dagger and whip" : dagger_and_whip,
    "paired swords" : paired_swords,
    "polearm" : polearm,
    "bastard sword" : bastard_sword
}

#------------------------------------------------------------------
# armor
#------------------------------------------------------------------

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

bare = Armor ("bare", "defense +2.")
bare.defense += 2

cape = Armor ("cape", "fortune +1, insulation +1.")
cape.insulation += 1
cape.fortune += 1

light_mail = Armor ("light mail", "damage reduction +1")
light_mail.reduction += 1

heavy_mail = Armor ("heavy mail", "damage reduction +2, -2 insulation")
heavy_mail.reduction += 2
heavy_mail.insulation -= 2

suit_of_plate = Armor ("suit of plate", "damage reduction +3, -2 skill, -2 insulation")
suit_of_plate.reduction += 3
suit_of_plate.skill -= 2
suit_of_plate.insulation -= 2

armor_list = {
    "bare" : bare,
    "cape" : cape,
    "light mail" : light_mail,
    "heavy mail" : heavy_mail,
    "suit of plate" : suit_of_plate
    }

#------------------------------------------------------------------
# headgear
#------------------------------------------------------------------

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

winged_helm = Headgear ("winged helm", "defense +1, insulation -1.")
winged_helm.defense += 1
winged_helm.insulation -= 1

moon_circlet = Headgear ("moon circlet", "fortune +1, defense -1.")
moon_circlet.fortune += 1
moon_circlet.defense -= 1

stag_helm = Headgear ("stag helm", "damage reduction +1, skill -2.")
stag_helm.reduction += 1
stag_helm.skill -= 2

black_hood = Headgear ("black hood", "skill +1, fortune -1.")
black_hood.skill += 1
black_hood.fortune -= 1

flaming_topknot = Headgear ("flaming topknot", "resist pinning, defense -1.")
flaming_topknot.features = "resist pinning"
flaming_topknot.defense -= 1


headgear_list = {
    "winged helm" : winged_helm,
    "stag helm" : stag_helm,
    "moon circlet" : moon_circlet,
    "black hood" : black_hood,
    "flaming topknot" : flaming_topknot
    }

#------------------------------------------------------------------
# Archetype
#------------------------------------------------------------------

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

gendarme = Archetype ("gendarme", "stamina +6, skill +4, defense + 4, riposte")
gendarme.stamina += 6
gendarme.skill += 4
gendarme.defense += 4
gendarme.features = ["riposte"]

furioso = Archetype ("furioso", "stamina +12, skill +2, defense + 2, hack and slash, savagery")
furioso.stamina += 12
furioso.skill += 2
furioso.defense += 2
furioso.archetype_actions = {"hack and slash" : h_actions.hack_and_slash}
furioso.features = ["savagery"]


archetype_list = {
    "gendarme" : gendarme,
    "furioso" : furioso
    }

#------------------------------------------------------------------
# Actors
#------------------------------------------------------------------


minion = Actor ("minion")
minion.logic = "minion logic"
minion.speed = "slow"
grunt = Actor ("grunt")
grunt.logic = "grunt logic"
nemesis = Actor ("nemesis")
nemesis.logic = "nemesis logic"


valeria = Actor ("Valeria")
valeria.give_archetype(gendarme)
valeria.wear_armor(heavy_mail)
valeria.wear_headgear(winged_helm)
valeria.equip_weapons (shield_and_sword)
valeria.arms_slot2 = polearm

bosh = Actor ("Bosh")
bosh.give_archetype(furioso)
bosh.wear_armor(light_mail)
bosh.wear_headgear(flaming_topknot)
bosh.equip_weapons (bastard_sword)
bosh.arms_slot2 = bearded_axe