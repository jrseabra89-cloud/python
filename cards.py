from dataclasses import dataclass, field, replace
from typing import List, Optional
import random


def announce(message: str) -> None:
	print(f"\n{message}\n")


@dataclass(frozen=True)
class Card:
	name: str
	description: str = ""
	value: int = 0
	card_type: str = "standard"
	presence: int = 0
	domain_value: int = 1
	effect: str = ""
	alignment: str = ""


class Deck:
	def __init__(self, cards: List[Card]):
		self._cards = list(cards)

	def shuffle(self) -> None:
		random.shuffle(self._cards)

	def draw(self) -> Optional[Card]:
		if not self._cards:
			return None
		return self._cards.pop()

	def peek(self, count: int = 1) -> List[Card]:
		if count <= 0:
			return []
		return list(reversed(self._cards[-count:]))

	def __len__(self) -> int:
		return len(self._cards)


@dataclass
class Zone:
	owner: str
	cards: List[Card] = field(default_factory=list)

	def add(self, card: Card) -> None:
		self.cards.append(card)

	def clear(self) -> None:
		self.cards.clear()


@dataclass
class Player:
	name: str
	hand: List[Card] = field(default_factory=list)
	zone: Zone = field(init=False)
	critical: bool = False
	triumph: int = 0
	is_human: bool = True

	def __post_init__(self) -> None:
		self.zone = Zone(owner=self.name)

	def draw(self, deck: Deck, count: int = 1) -> None:
		drawn = 0
		for _ in range(count):
			card = deck.draw()
			if card is not None:
				self.hand.append(card)
				drawn += 1
			else:
				announce(f"{self.name} tries to draw a card, but the deck is empty.")
				break
		if drawn > 0:
			announce(f"{self.name} draws {drawn} card(s).")

	def play_card(self, index: int) -> Optional[Card]:
		if 0 <= index < len(self.hand):
			return self.hand.pop(index)
		return None


class Game:
	def __init__(self, players: List[Player], deck: Deck):
		self.players = players
		self.deck = deck
		self.discard_zone = Zone(owner="discard")
		self.round_number = 0
		self.active_player_index = 0
		self.bonus_drawn_players: set[str] = set()

	def start(self, opening_hand_size: int = 5) -> None:
		announce("=== New Game ===")
		self.deck.shuffle()
		for player in self.players:
			player.draw(self.deck, opening_hand_size)

	def next_round(self) -> None:
		self.round_number += 1
		self.active_player_index = 0
		announce(f"=== Round {self.round_number} ===")

	def play_round(self) -> None:
		self.next_round()
		for _ in range(len(self.players)):
			active = self.players[self.active_player_index]
			if active.critical:
				return
			if active.is_human:
				input(f"{active.name}'s turn. Press Enter to continue.")
			self.take_turn(active)
			self.active_player_index = (self.active_player_index + 1) % len(self.players)
		self._end_round_scoring()

	def take_turn(self, player: Player) -> None:
		self._apply_start_of_turn_rituals(player)
		self._apply_start_of_turn_pawns(player)
		player.draw(self.deck, 1)
		if self.round_number == 1 and player is not self.players[0] and player.name not in self.bonus_drawn_players:
			announce(f"{player.name} draws an extra card for going after the first player.")
			player.draw(self.deck, 1)
			self.bonus_drawn_players.add(player.name)
		self._show_board(player)
		domain_value = self._domain_value_total(player)
		print(f"{player.name} domains: {domain_value}")
		print(f"{player.name} triumph: {player.triumph}")
		self._show_hand(player)

		if not player.is_human:
			self._ai_take_turn(player)
			if self._has_ritual(player, "grudge") and self._can_attack(player):
				self._attack(player)
			self._apply_end_of_turn_rituals(player)
			self._enforce_hand_limit(player, limit=7)
			self._update_critical_status(player)
			return

		choice = self._prompt_turn_choice(player)
		if choice == "play":
			announce(f"{player.name} plays a card.")
			self._play_from_hand(player)
			input("Press Enter to continue.")
			if self._has_ritual(player, "grudge") and self._can_attack(player):
				attack_choice = input("Attack as well due to Grudge? (y/n): ").strip().lower()
				if attack_choice == "y":
					announce(f"{player.name} declares an attack.")
					self._attack(player)
					input("Press Enter to continue.")
		elif choice == "draw":
			announce(f"{player.name} draws a second card.")
			player.draw(self.deck, 1)
			input("Press Enter to continue.")
			if self._has_ritual(player, "grudge") and self._can_attack(player):
				attack_choice = input("Attack as well due to Grudge? (y/n): ").strip().lower()
				if attack_choice == "y":
					announce(f"{player.name} declares an attack.")
					self._attack(player)
					input("Press Enter to continue.")
		elif choice == "attack":
			announce(f"{player.name} declares an attack.")
			self._attack(player)
			input("Press Enter to continue.")

		self._apply_end_of_turn_rituals(player)
		self._enforce_hand_limit(player, limit=7)
		self._update_critical_status(player)

	def _show_board(self, player: Player) -> None:
		print("\n--- Board ---")
		for p in self.players:
			print(f"{p.name} zone:")
			if p.zone.cards:
				for card in p.zone.cards:
					print(f"- {card.name}\t{card.description}")
			else:
				print("- (empty)")
			print(f"{p.name} hand: {len(p.hand)} card(s)")
		print("-------------\n")

	def _show_hand(self, player: Player) -> None:
		if not player.is_human:
			return
		print(f"{player.name} hand:")
		if player.hand:
			for card in player.hand:
				print(f"- {card.name}\t{card.description}")
		else:
			print("- (empty)")

	def _prompt_turn_choice(self, player: Player) -> str:
		if not player.hand:
			return "draw"
		can_attack = self._can_attack(player)
		prompt = "Play a card, draw a second card"
		if can_attack:
			prompt += ", or attack"
		choice = input(f"{prompt}? (play/draw/attack): ").strip().lower()
		if choice not in {"play", "draw", "attack"}:
			choice = "play"
		if choice == "attack" and not can_attack:
			choice = "play"
		return choice

	def _play_from_hand(self, player: Player) -> None:
		if not player.hand:
			return
		print("Choose a card to play:")
		playable = [c for c in player.hand if c.card_type != "treason"]
		if not playable:
			print("No playable cards. Treason cards can only be discarded.")
			return
		options_index = {}
		for i, card in enumerate(playable, start=1):
			print(f"{i}.\t{card.name}\t{card.description}")
			options_index[i] = player.hand.index(card)
		try:
			choice_index = int(input("choose card."))
		except ValueError:
			choice_index = 1
		if choice_index > len(playable):
			choice_index = len(playable)
		elif choice_index < 1:
			choice_index = 1
		self._play_card_by_index(player, options_index[choice_index])

	def _play_card_by_index(self, player: Player, index: int) -> None:
		card = player.play_card(index)
		if not card:
			return
		if card.card_type == "treason":
			announce("Treason cards can only be discarded.")
			player.hand.append(card)
			return
		announce(f"{player.name} plays {card.name}.")
		if card.card_type == "power":
			self._resolve_power_card(player, card)
			self.discard_zone.add(card)
		elif card.card_type == "domain":
			player.zone.add(card)
			if card.effect and not self._has_ritual(player, "duress"):
				self._resolve_domain_card(player, card)
		elif card.card_type == "pawn":
			player.zone.add(card)
			if card.effect and not self._has_ritual(player, "duress"):
				self._resolve_pawn_card(player, card)
		elif card.card_type == "ritual":
			if player.is_human:
				target = self._choose_player("Choose a zone to place this ritual:")
				if target is None:
					return
				target.zone.add(card)
			else:
				player.zone.add(card)
		else:
			player.zone.add(card)

	def _ai_take_turn(self, player: Player) -> None:
		if not player.hand:
			player.draw(self.deck, 1)
			return
		if self._can_attack(player) and self._ai_should_attack(player):
			self._attack(player)
			return
		card_index = self._ai_choose_card_index(player)
		if card_index is None:
			player.draw(self.deck, 1)
			return
		self._play_card_by_index(player, card_index)

	def _ai_should_attack(self, player: Player) -> bool:
		attackable = self._get_attackable_opponents(player)
		if not attackable:
			return False
		best_opponent = max(attackable, key=lambda p: self._total_presence(p))
		return self._total_presence(player) >= self._total_presence(best_opponent)

	def _ai_choose_card_index(self, player: Player) -> Optional[int]:
		playable = [c for c in player.hand if c.card_type != "treason"]
		if not playable:
			return None
		opponents = [p for p in self.players if p is not player]
		opponent_has_domain = any(
			c.card_type == "domain" for p in opponents for c in p.zone.cards
		)
		opponent_has_pawn = any(
			c.card_type == "pawn" for p in opponents for c in p.zone.cards
		)
		opponent_has_ritual = any(
			c.card_type == "ritual" for p in opponents for c in p.zone.cards
		)
		presence_one_pawns = any(
			c.card_type == "pawn" and c.presence == 1 for p in opponents for c in p.zone.cards
		)
		opponent_hand_size = max((len(p.hand) for p in opponents), default=0)

		power_priority = [
			("destroy domain", opponent_has_domain),
			("destroy a pawn", opponent_has_pawn),
			("destroy any ritual", opponent_has_ritual),
			("destroy all pawns with presence 1", presence_one_pawns),
			("inheritance", opponent_has_domain),
			("migration", opponent_has_domain),
			("spies", opponent_hand_size > 0),
			("draw 3 cards", len(player.hand) <= 2),
			("any player discards 2 cards", opponent_hand_size >= 2),
		]

		for effect_name, condition in power_priority:
			if not condition:
				continue
			for card in playable:
				if card.card_type == "power" and card.name.strip().lower() == effect_name:
					return player.hand.index(card)

		domain_value = self._domain_value_total(player)
		if domain_value < 4:
			for card in playable:
				if card.card_type == "domain":
					return player.hand.index(card)

		for card in playable:
			if card.card_type == "pawn":
				return player.hand.index(card)

		for card in playable:
			if card.card_type == "ritual":
				return player.hand.index(card)

		return player.hand.index(playable[0])

	def _enforce_hand_limit(self, player: Player, limit: int = 7) -> None:
		while len(player.hand) > limit:
			if not player.is_human:
				discarded = player.play_card(0)
				if discarded:
					self.discard_zone.add(discarded)
					announce(f"{player.name} discards {discarded.name}.")
				continue
			print(f"{player.name} must discard down to {limit} cards.")
			for i, card in enumerate(player.hand, start=1):
				print(f"{i}.\t{card.name}\t{card.description}")
			try:
				choice_index = int(input("choose discard."))
			except ValueError:
				choice_index = 1
			if choice_index > len(player.hand):
				choice_index = len(player.hand)
			elif choice_index < 1:
				choice_index = 1
			discarded = player.play_card(choice_index - 1)
			if discarded:
				self.discard_zone.add(discarded)

	def _resolve_power_card(self, player: Player, card: Card) -> None:
		effect = card.name.strip().lower()
		if effect == "destroy domain":
			target = self._choose_player_for(player, "Choose a player to lose a domain card:")
			if target is None:
				return
			domain_cards = [c for c in target.zone.cards if c.card_type == "domain"]
			if not domain_cards:
				print("No domain cards to destroy.")
				return
			destroyed = domain_cards.pop()
			target.zone.cards.remove(destroyed)
			self.discard_zone.add(destroyed)
			print(f"{target.name} loses a domain card: {destroyed.name}.")
		elif effect == "draw 3 cards":
			player.draw(self.deck, 3)
			print(f"{player.name} draws 3 cards.")
		elif effect == "any player discards 2 cards":
			target = self._choose_player_for(player, "Choose a player to discard 2 cards:")
			if target is None:
				return
			self._discard_cards(target, count=2)
		elif effect == "destroy any ritual":
			target = self._choose_player_for(player, "Choose a player to lose a ritual card:")
			if target is None:
				return
			ritual_cards = [c for c in target.zone.cards if c.card_type == "ritual"]
			if not ritual_cards:
				print("No ritual cards to destroy.")
				return
			destroyed = ritual_cards.pop()
			target.zone.cards.remove(destroyed)
			self.discard_zone.add(destroyed)
			print(f"{target.name} loses a ritual card: {destroyed.name}.")
		elif effect == "destroy a pawn":
			target = self._choose_player_for(player, "Choose a player to lose a pawn card:")
			if target is None:
				return
			pawn_cards = [c for c in target.zone.cards if c.card_type == "pawn"]
			if not pawn_cards:
				print("No pawn cards to destroy.")
				return
			destroyed = pawn_cards.pop()
			target.zone.cards.remove(destroyed)
			self.discard_zone.add(destroyed)
			print(f"{target.name} loses a pawn card: {destroyed.name}.")
		elif effect == "destroy all pawns with presence 1":
			removed = 0
			for target in self.players:
				pawn_cards = [
					c for c in target.zone.cards if c.card_type == "pawn" and c.presence == 1
				]
				for card in pawn_cards:
					target.zone.cards.remove(card)
					self.discard_zone.add(card)
					removed += 1
			if removed == 0:
				print("No presence 1 pawns were destroyed.")
			else:
				print(f"Destroyed {removed} presence 1 pawns across both zones.")
		elif effect == "spies":
			target = self._choose_player_for(player, "Choose a player to reveal their hand:")
			if target is None:
				return
			if target.hand:
				print(f"{target.name} reveals their hand:")
				for card in target.hand:
					print(f"- {card.name}\t{card.description}")
			else:
				print(f"{target.name} has no cards in hand.")
			treason_cards = [c for c in target.hand if c.card_type == "treason"]
			for card in treason_cards:
				target.hand.remove(card)
				self.discard_zone.add(card)
			if treason_cards:
				print(f"{target.name} discards {len(treason_cards)} treason card(s).")
		elif effect == "migration":
			target = self._choose_player_for(player, "Choose a player to return a domain card to hand:")
			if target is None:
				return
			self._return_domain_to_hand(target)
		elif effect == "inheritance":
			target = self._choose_player_for(player, "Choose a player to lose a domain card:")
			if target is None:
				return
			domain_cards = [c for c in target.zone.cards if c.card_type == "domain"]
			if not domain_cards:
				print("No domain cards to take.")
				return
			if player.is_human:
				print("Choose a domain to take:")
				for i, c in enumerate(domain_cards, start=1):
					print(f"{i}.\t{c.name}\t{c.description}")
				try:
					choice_index = int(input("choose domain."))
				except ValueError:
					choice_index = 1
				if choice_index > len(domain_cards):
					choice_index = len(domain_cards)
				elif choice_index < 1:
					choice_index = 1
				chosen = domain_cards[choice_index - 1]
			else:
				chosen = domain_cards[0]
			target.zone.cards.remove(chosen)
			player.zone.add(chosen)
			print(f"{player.name} claims {chosen.name} from {target.name}.")
		elif effect == "uprising":
			removed = 0
			for target in self.players:
				pawn_cards = [c for c in target.zone.cards if c.card_type == "pawn"]
				for pawn in pawn_cards:
					if pawn.name.startswith("Pawn "):
						continue
					target.zone.cards.remove(pawn)
					self.discard_zone.add(pawn)
					removed += 1
			if removed == 0:
				print("No special pawns were destroyed.")
			else:
				print(f"Destroyed {removed} special pawn(s) across both zones.")
		else:
			print(f"{card.name} has no defined power effect.")

	def _has_ritual(self, player: Player, ritual_effect: str) -> bool:
		return any(
			card.card_type == "ritual" and card.effect.strip().lower() == ritual_effect
			for card in player.zone.cards
		)

	def _apply_start_of_turn_rituals(self, player: Player) -> None:
		rituals = [c for c in player.zone.cards if c.card_type == "ritual"]
		for ritual in rituals:
			effect = ritual.effect.strip().lower()
			if effect == "start draw one discard one":
				player.draw(self.deck, 1)
				self._discard_cards(player, count=1)
			elif effect == "deluge":
				if not player.hand:
					player.zone.cards.remove(ritual)
					self.discard_zone.add(ritual)
					print(f"{player.name} removes Deluge from their zone.")
					continue
				if player.is_human:
					choice = input(
						"Deluge: remove from your zone or discard a card to keep it? (remove/discard): "
					).strip().lower()
					if choice == "remove":
						player.zone.cards.remove(ritual)
						self.discard_zone.add(ritual)
						print(f"{player.name} removes Deluge from their zone.")
					else:
						self._discard_cards(player, count=1)
				else:
					discarded = player.play_card(0)
					if discarded:
						self.discard_zone.add(discarded)
						announce(f"{player.name} discards {discarded.name} to keep Deluge.")

	def _apply_start_of_turn_pawns(self, player: Player) -> None:
		saints = [
			c for c in player.zone.cards if c.card_type == "pawn" and c.effect.strip().lower() == "saint"
		]
		if not saints:
			return
		if not player.hand:
			discarded = saints[0]
			player.zone.cards.remove(discarded)
			self.discard_zone.add(discarded)
			print(f"{player.name} discards {discarded.name}.")
			return
		if player.is_human:
			choice = input("Saint: discard a card or discard Saint? (card/saint): ").strip().lower()
			if choice == "saint":
				discarded = saints[0]
				player.zone.cards.remove(discarded)
				self.discard_zone.add(discarded)
				print(f"{player.name} discards {discarded.name}.")
			else:
				self._discard_cards(player, count=1)
			return
		discarded = player.play_card(0)
		if discarded:
			self.discard_zone.add(discarded)
			announce(f"{player.name} discards {discarded.name} to keep Saint.")

	def _apply_end_of_turn_rituals(self, player: Player) -> None:
		rituals = [c for c in player.zone.cards if c.card_type == "ritual"]
		for ritual in rituals:
			effect = ritual.effect.strip().lower()
			if effect == "end return pawn":
				pawn_cards = [c for c in player.zone.cards if c.card_type == "pawn"]
				if not pawn_cards:
					continue
				returned = pawn_cards.pop()
				player.zone.cards.remove(returned)
				player.hand.append(returned)

	def _resolve_domain_card(self, player: Player, card: Card) -> None:
		effect = card.effect.strip().lower()
		if effect == "peek top two":
			peeked = self.deck.peek(2)
			if not peeked:
				print("The deck is empty.")
				return
			print("Top two cards:")
			for c in peeked:
				print(f"- {c.name}\t{c.description}")
		elif effect == "double domain return domain":
			self._return_domain_to_hand(player, exclude=card)
		elif effect == "academy":
			power_cards = [c for c in self.discard_zone.cards if c.card_type == "power"]
			if not power_cards:
				print("No power cards in the discard zone.")
				return
			if not player.is_human:
				chosen = power_cards[0]
				self.discard_zone.cards.remove(chosen)
				player.hand.append(chosen)
				print(f"{player.name} recovers {chosen.name} from the discard zone.")
				return
			print("Choose a power card from the discard zone to return to hand:")
			for i, c in enumerate(power_cards, start=1):
				print(f"{i}.\t{c.name}\t{c.description}")
			try:
				choice_index = int(input("choose power card."))
			except ValueError:
				choice_index = 1
			if choice_index > len(power_cards):
				choice_index = len(power_cards)
			elif choice_index < 1:
				choice_index = 1
			chosen = power_cards[choice_index - 1]
			self.discard_zone.cards.remove(chosen)
			player.hand.append(chosen)
			print(f"{player.name} recovers {chosen.name} from the discard zone.")
		elif effect == "crossroads":
			player.draw(self.deck, 1)
			self._discard_cards(player, count=1)
		else:
			print(f"{card.name} has no defined domain effect.")

	def _resolve_pawn_card(self, player: Player, card: Card) -> None:
		effect = card.effect.strip().lower()
		if effect == "dragon":
			domains = [c for c in player.zone.cards if c.card_type == "domain"]
			if domains:
				destroyed = domains[0]
				player.zone.cards.remove(destroyed)
				self.discard_zone.add(destroyed)
				print(f"{player.name}'s {destroyed.name} is destroyed by the dragon.")
		elif effect == "sage":
			player.draw(self.deck, 1)

	def _return_domain_to_hand(self, player: Player, exclude: Optional[Card] = None) -> None:
		domains = [c for c in player.zone.cards if c.card_type == "domain" and c is not exclude]
		if not domains:
			print(f"{player.name} has no other domain to return.")
			return
		if not player.is_human:
			chosen = domains[0]
			player.zone.cards.remove(chosen)
			player.hand.append(chosen)
			return
		print("Choose a domain to return to hand:")
		for i, card in enumerate(domains, start=1):
			print(f"{i}.\t{card.name}\t{card.description}")
		try:
			choice_index = int(input("choose domain."))
		except ValueError:
			choice_index = 1
		if choice_index > len(domains):
			choice_index = len(domains)
		elif choice_index < 1:
			choice_index = 1
		chosen = domains[choice_index - 1]
		player.zone.cards.remove(chosen)
		player.hand.append(chosen)

	def _choose_player(self, prompt: str) -> Optional[Player]:
		print(prompt)
		for i, p in enumerate(self.players, start=1):
			print(f"{i}.\t{p.name}")
		try:
			choice_index = int(input("choose player."))
		except ValueError:
			choice_index = 1
		if choice_index > len(self.players):
			choice_index = len(self.players)
		elif choice_index < 1:
			choice_index = 1
		return self.players[choice_index - 1]

	def _choose_player_for(self, actor: Player, prompt: str) -> Optional[Player]:
		if actor.is_human:
			return self._choose_player(prompt)
		opponents = [p for p in self.players if p is not actor]
		if not opponents:
			return None
		return max(opponents, key=lambda p: (len(p.zone.cards), len(p.hand)))

	def _discard_cards(self, player: Player, count: int) -> None:
		for _ in range(count):
			if not player.hand:
				announce(f"{player.name} has no cards to discard.")
				return
			if not player.is_human:
				discarded = player.play_card(0)
				if discarded:
					self.discard_zone.add(discarded)
					announce(f"{player.name} discards {discarded.name}.")
				continue
			print(f"{player.name} choose a card to discard:")
			for i, card in enumerate(player.hand, start=1):
				print(f"{i}.\t{card.name}\t{card.description}")
			try:
				choice_index = int(input("choose discard."))
			except ValueError:
				choice_index = 1
			if choice_index > len(player.hand):
				choice_index = len(player.hand)
			elif choice_index < 1:
				choice_index = 1
			discarded = player.play_card(choice_index - 1)
			if discarded:
				self.discard_zone.add(discarded)
				announce(f"{player.name} discards {discarded.name}.")

	def _update_critical_status(self, player: Player) -> None:
		player.critical = self._domain_value_total(player) >= 5

	def _domain_value_total(self, player: Player) -> int:
		if self._has_ritual(player, "deluge"):
			return 0
		other_domains = [
			card
			for card in player.zone.cards
			if card.card_type == "domain" and card.effect.strip().lower() != "outpost"
		]
		outposts = [
			card
			for card in player.zone.cards
			if card.card_type == "domain" and card.effect.strip().lower() == "outpost"
		]
		outpost_value = len(outposts) if other_domains else 0
		return (
			sum(card.domain_value for card in other_domains)
			+ outpost_value
			+ sum(
				card.domain_value
				for card in player.zone.cards
				if card.effect.strip().lower() == "loyalist"
			)
		)

	def _pawn_presence(self, player: Player, pawn: Card) -> int:
		effect = pawn.effect.strip().lower()
		if effect == "mob":
			mob_count = sum(
				1
				for c in player.zone.cards
				if c.card_type == "pawn" and c.effect.strip().lower() == "mob"
			)
			return max(0, mob_count - 1)
		return pawn.presence

	def _total_presence(self, player: Player) -> int:
		return sum(
			self._pawn_presence(player, card)
			for card in player.zone.cards
			if card.card_type == "pawn"
		)

	def _get_attackable_opponents(self, player: Player) -> List[Player]:
		if any(c.card_type == "pawn" and c.effect.strip().lower() == "saint" for c in player.zone.cards):
			return []
		attackable = []
		for opponent in self.players:
			if opponent is player:
				continue
			if self._has_ritual(opponent, "deluge"):
				continue
			if any(
				c.card_type == "pawn" and c.effect.strip().lower() == "saint"
				for c in opponent.zone.cards
			):
				continue
			if opponent.zone.cards:
				attackable.append(opponent)
		return attackable

	def _can_attack(self, player: Player) -> bool:
		if not any(c.card_type == "pawn" for c in player.zone.cards):
			return False
		return bool(self._get_attackable_opponents(player))

	def _attack(self, player: Player) -> None:
		attackable = self._get_attackable_opponents(player)
		if not attackable:
			print("No target to attack.")
			return
		if player.is_human:
			print("Choose a player to attack:")
			for i, opp in enumerate(attackable, start=1):
				print(f"{i}.\t{opp.name}")
			try:
				choice_index = int(input("choose player."))
			except ValueError:
				choice_index = 1
			if choice_index > len(attackable):
				choice_index = len(attackable)
			elif choice_index < 1:
				choice_index = 1
			opponent = attackable[choice_index - 1]
		else:
			opponent = max(attackable, key=lambda p: len(p.zone.cards))
		attacking_pawns = [c for c in player.zone.cards if c.card_type == "pawn"]
		if not attacking_pawns:
			print(f"{player.name} has no pawns to attack with.")
			return

		if player.is_human:
			print("Choose a target card in the opponent's zone:")
			for i, card in enumerate(opponent.zone.cards, start=1):
				print(f"{i}.\t{card.name}\t{card.description}")
			try:
				choice_index = int(input("choose target."))
			except ValueError:
				choice_index = 1
			if choice_index > len(opponent.zone.cards):
				choice_index = len(opponent.zone.cards)
			elif choice_index < 1:
				choice_index = 1
			target_card = opponent.zone.cards[choice_index - 1]
		else:
			domain_targets = [c for c in opponent.zone.cards if c.card_type == "domain"]
			target_card = domain_targets[0] if domain_targets else opponent.zone.cards[0]

		if any(c.card_type == "pawn" and c.effect.strip().lower() == "spymaster" for c in opponent.zone.cards):
			if player.hand:
				print(f"{player.name} reveals their hand:")
				for card in player.hand:
					print(f"- {card.name}\t{card.description}")
			else:
				print(f"{player.name} has no cards in hand.")

		selected_attackers = self._select_pawns(player, "Choose attacking pawns:")
		if not selected_attackers:
			print("No pawns selected. No card is played.")
			return
		attacker_discard = self._discard_any_number(player, "Discard cards to boost attack?")
		attacker_presence = sum(self._pawn_presence(player, c) for c in selected_attackers)
		has_general = any(c.effect.strip().lower() == "general" for c in selected_attackers)
		if has_general:
			attacker_discard *= 2
		attacker_score = attacker_presence + attacker_discard
		if any(c.card_type == "domain" and c.effect.strip().lower() == "workshop" for c in player.zone.cards):
			attacker_score += 1

		selected_defenders = self._select_pawns(opponent, "Choose defending pawns:")
		defender_discard = self._discard_any_number(opponent, "Discard cards to boost defense?")
		defender_presence = sum(self._pawn_presence(opponent, c) for c in selected_defenders)
		defender_score = defender_presence + defender_discard
		if self._has_ritual(opponent, "sanctuary"):
			defender_score += 2

		print(f"Attack score: {attacker_score} | Defense score: {defender_score}")

		self._destroy_pawns(player, selected_attackers)
		self._destroy_pawns(opponent, selected_defenders)

		if attacker_score > defender_score:
			if target_card.card_type == "domain":
				opponent.zone.cards.remove(target_card)
				player.zone.add(target_card)
				print(f"{player.name} captures {target_card.name}.")
			else:
				opponent.zone.cards.remove(target_card)
				self.discard_zone.add(target_card)
				print(f"{target_card.name} is destroyed.")
			player.triumph += 1
			print(f"{player.name} gains 1 triumph (total {player.triumph}).")
		else:
			print("The attack fails to break through.")

	def _select_pawns(self, player: Player, prompt: str) -> List[Card]:
		pawns = [c for c in player.zone.cards if c.card_type == "pawn"]
		if not pawns:
			return []
		if not player.is_human:
			return pawns
		selected: List[Card] = []
		print(prompt)
		while True:
			remaining = [c for c in pawns if c not in selected]
			if not remaining:
				break
			for i, card in enumerate(remaining, start=1):
				print(f"{i}.\t{card.name}\t{card.description}")
			print("0.\tDone")
			try:
				choice_index = int(input("choose pawn."))
			except ValueError:
				choice_index = 0
			if choice_index == 0:
				break
			if choice_index > len(remaining):
				choice_index = len(remaining)
			elif choice_index < 1:
				choice_index = 1
			selected.append(remaining[choice_index - 1])
		return selected

	def _discard_any_number(self, player: Player, prompt: str) -> int:
		if not player.hand:
			return 0
		if not player.is_human:
			return 0
		discarded = 0
		while player.hand:
			choice = input(f"{prompt} (y/n): ").strip().lower()
			if choice != "y":
				break
			print("Choose a card to discard:")
			for i, card in enumerate(player.hand, start=1):
				print(f"{i}.\t{card.name}\t{card.description}")
			try:
				choice_index = int(input("choose discard."))
			except ValueError:
				choice_index = 1
			if choice_index > len(player.hand):
				choice_index = len(player.hand)
			elif choice_index < 1:
				choice_index = 1
			card = player.play_card(choice_index - 1)
			if card:
				self.discard_zone.add(card)
				announce(f"{player.name} discards {card.name}.")
				if card.card_type == "treason":
					discarded += 3
				else:
					discarded += 1
		return discarded

	def _destroy_pawns(self, player: Player, pawns: List[Card]) -> None:
		for pawn in pawns:
			if pawn in player.zone.cards:
				player.zone.cards.remove(pawn)
				self.discard_zone.add(pawn)

	def check_win_conditions(self) -> Optional[Player]:
		for player in self.players:
			has_emperor = any(
				card.card_type == "pawn" and card.effect.strip().lower() == "emperor"
				for card in player.zone.cards
			)
			if has_emperor and self._total_presence(player) >= 5:
				return player
			if player.critical:
				return player
			if player.triumph >= 6:
				return player
		return None

	def _end_round_scoring(self) -> None:
		presence_totals = [
			(
				player,
				sum(
					self._pawn_presence(player, card)
					for card in player.zone.cards
					if card.card_type == "pawn"
				),
			)
			for player in self.players
		]
		max_presence = max(total for _, total in presence_totals)
		leaders = [p for p, total in presence_totals if total == max_presence]

		if max_presence > 0 and len(leaders) == 1:
			leaders[0].triumph += 1
			print(f"{leaders[0].name} gains 1 triumph (total {leaders[0].triumph}).")
		else:
			print("No triumph gained this round.")

		for player in self.players:
			pawn_count = sum(1 for card in player.zone.cards if card.card_type == "pawn")


def create_default_deck() -> Deck:
	cards: List[Card] = []

	for i in range(1, 30):
		if i <= 4:
			cards.append(
				Card(
					name=f"Seer Domain {i}",
					description="When played, look at the top two cards of the deck.",
					card_type="domain",
					effect="peek top two",
				)
			)
		elif i <= 8:
			cards.append(
				Card(
					name=f"Anchor Domain {i}",
					description="Counts as 2 domains. Return a domain you control to your hand.",
					card_type="domain",
					domain_value=2,
					effect="double domain return domain",
				)
			)
		else:
			cards.append(
				Card(
					name=f"Domain {i}",
					description="A steady foothold in contested ground.",
					card_type="domain",
				)
			)

	for i in range(41, 43):
		cards.append(
			Card(
				name=f"Seer Domain {i}",
				description="When played, look at the top two cards of the deck.",
				card_type="domain",
				effect="peek top two",
			)
		)
	for i in range(49, 53):
		cards.append(
			Card(
				name=f"Anchor Domain {i}",
				description="Counts as 2 domains. Return a domain you control to your hand.",
				card_type="domain",
				domain_value=2,
				effect="double domain return domain",
			)
		)

	for i in range(1, 5):
		cards.append(
			Card(
				name=f"Outpost {i}",
				description="Counts as 1 domain only if you control another non-Outpost domain.",
				card_type="domain",
				effect="outpost",
			)
		)

	for i in range(1, 5):
		cards.append(
			Card(
				name=f"Workshop {i}",
				description="While you control this domain, you gain +1 attack score.",
				card_type="domain",
				effect="workshop",
			)
		)

	for i in range(1, 5):
		cards.append(
			Card(
				name=f"Academy {i}",
				description="When played, return a power card from the discard zone to your hand.",
				card_type="domain",
				effect="academy",
			)
		)

	for i in range(1, 5):
		cards.append(
			Card(
				name=f"Crossroads {i}",
				description="When played, draw a card then discard a card.",
				card_type="domain",
				effect="crossroads",
			)
		)

	for i in range(1, 21):
		if i == 1:
			cards.append(
				Card(
					name="Loyalist 1",
					description="Counts as 1 domain.",
					card_type="pawn",
					presence=1,
					domain_value=1,
					effect="loyalist",
				)
			)
		elif i == 2:
			cards.append(
				Card(
					name="Emperor 1",
					description="Presence 1. If you have 7 presence, you win the game.",
					card_type="pawn",
					presence=1,
					effect="emperor",
				)
			)
		elif i == 3 or 7 <= i <= 11:
			cards.append(
				Card(
					name="Mob 1",
					description="Presence 0. +1 presence for each other mob in your zone.",
					card_type="pawn",
					presence=0,
					effect="mob",
				)
			)
		elif i == 4:
			cards.append(
				Card(
					name="Dragon 1",
					description="Presence 4. Destroys a domain in your zone when played.",
					card_type="pawn",
					presence=4,
					effect="dragon",
				)
			)
		elif i == 5:
			cards.append(
				Card(
					name="Sage 1",
					description="Presence 1. Draw a card when played.",
					card_type="pawn",
					presence=1,
					effect="sage",
				)
			)
		elif i == 6:
			cards.append(
				Card(
					name="General 1",
					description="Presence 1. Each card discarded when attacking counts as 2.",
					card_type="pawn",
					presence=1,
					effect="general",
				)
			)
		elif 16 <= i <= 18:
			cards.append(
				Card(
					name=f"Champion Pawn {i}",
					description="An elite force with stronger presence.",
					card_type="pawn",
					presence=2,
				)
			)
		else:
			cards.append(
				Card(
					name=f"Pawn {i}",
					description="A small force that adds presence.",
					card_type="pawn",
					presence=1,
				)
			)

	for i in range(31, 46):
		if i == 31:
			cards.append(
				Card(
					name="Loyalist 2",
					description="Counts as 1 domain.",
					card_type="pawn",
					presence=1,
					domain_value=1,
					effect="loyalist",
				)
			)
		elif i == 32:
			cards.append(
				Card(
					name="Emperor 2",
					description="Presence 1. If you have 7 presence, you win the game.",
					card_type="pawn",
					presence=1,
					effect="emperor",
				)
			)
		elif i == 33 or 37 <= i <= 40:
			cards.append(
				Card(
					name="Mob 2",
					description="Presence 0. +1 presence for each other mob in your zone.",
					card_type="pawn",
					presence=0,
					effect="mob",
				)
			)
		elif i == 34:
			cards.append(
				Card(
					name="Dragon 2",
					description="Presence 4. Destroys a domain in your zone when played.",
					card_type="pawn",
					presence=4,
					effect="dragon",
				)
			)
		elif i == 35:
			cards.append(
				Card(
					name="Sage 2",
					description="Presence 1. Draw a card when played.",
					card_type="pawn",
					presence=1,
					effect="sage",
				)
			)
		elif i == 36:
			cards.append(
				Card(
					name="General 2",
					description="Presence 1. Each card discarded when attacking counts as 2.",
					card_type="pawn",
					presence=1,
					effect="general",
				)
			)
		elif i >= 41:
			cards.append(
				Card(
					name=f"Champion Pawn {i}",
					description="An elite force with stronger presence.",
					card_type="pawn",
					presence=2,
				)
			)

	for i in range(46, 56):
		if i == 46:
			cards.append(
				Card(
					name="Saint 2",
					description=(
						"Presence 0. You cannot attack or be attacked. "
						"Start of your turn: discard a card or discard Saint."
					),
					card_type="pawn",
					presence=0,
					effect="saint",
				)
			)
		elif i == 47:
			cards.append(
				Card(
					name="Spymaster 2",
					description="Presence 1. Enemies reveal their hand when attacking you.",
					card_type="pawn",
					presence=1,
					effect="spymaster",
				)
			)
		elif i == 48:
			cards.append(
				Card(
					name="Saint 1",
					description=(
						"Presence 0. You cannot attack or be attacked. "
						"Start of your turn: discard a card or discard Saint."
					),
					card_type="pawn",
					presence=0,
					effect="saint",
				)
			)
		elif i == 49:
			cards.append(
				Card(
					name="Spymaster 1",
					description="Presence 1. Enemies reveal their hand when attacking you.",
					card_type="pawn",
					presence=1,
					effect="spymaster",
				)
			)
		else:
			cards.append(
				Card(
					name=f"Pawn {i}",
					description="A small force that adds presence.",
					card_type="pawn",
					presence=1,
				)
			)

	for i in range(3):
		cards.append(
			Card(
				name="Destroy Domain",
				description="Destroy a domain card in any player's zone.",
				card_type="power",
			)
		)
		cards.append(
			Card(
				name="Draw 3 Cards",
				description="Draw three cards immediately.",
				card_type="power",
			)
		)
		cards.append(
			Card(
				name="Any Player Discards 2 Cards",
				description="Choose a player to discard two cards.",
				card_type="power",
			)
		)
		cards.append(
			Card(
				name="Destroy a Pawn",
				description="Destroy a pawn card in any player's zone.",
				card_type="power",
			)
		)
		cards.append(
			Card(
				name="Destroy All Pawns with Presence 1",
				description="Destroy all presence 1 pawns in both zones.",
				card_type="power",
			)
		)

	for _ in range(2):
		cards.append(
			Card(
				name="Destroy Any Ritual",
				description="Destroy a ritual card in any player's zone.",
				card_type="power",
			)
		)

	for _ in range(2):
		cards.append(
			Card(
				name="Migration",
				description="Choose a player to return a domain card from their zone to hand.",
				card_type="power",
			)
		)

	for _ in range(2):
		cards.append(
			Card(
				name="Inheritance",
				description="Take a domain from another player's zone and put it into your zone.",
				card_type="power",
			)
		)

	for _ in range(2):
		cards.append(
			Card(
				name="Uprising",
				description="Destroy all non-basic pawn cards in both zones.",
				card_type="power",
			)
		)

	for _ in range(2):
		cards.append(
			Card(
				name="Spies",
				description="Reveal a hand; discard any treason cards from it.",
				card_type="power",
			)
		)

	for i in range(2):
		cards.append(
			Card(
				name="Destroy Domain",
				description="Destroy a domain card in any player's zone.",
				card_type="power",
			)
		)
		cards.append(
			Card(
				name="Draw 3 Cards",
				description="Draw three cards immediately.",
				card_type="power",
			)
		)
		cards.append(
			Card(
				name="Any Player Discards 2 Cards",
				description="Choose a player to discard two cards.",
				card_type="power",
			)
		)
		cards.append(
			Card(
				name="Destroy a Pawn",
				description="Destroy a pawn card in any player's zone.",
				card_type="power",
			)
		)
		cards.append(
			Card(
				name="Destroy All Pawns with Presence 1",
				description="Destroy all presence 1 pawns in both zones.",
				card_type="power",
			)
		)

	for _ in range(1):
		cards.append(
			Card(
				name="Destroy Any Ritual",
				description="Destroy a ritual card in any player's zone.",
				card_type="power",
			)
		)

	for _ in range(2):
		cards.append(
			Card(
				name="Spies",
				description="Reveal a hand; discard any treason cards from it.",
				card_type="power",
			)
		)

	for i in range(1, 2):
		cards.append(
			Card(
				name=f"Ritual of Exchange {i}",
				description="Start of your turn: draw 1 then discard 1.",
				card_type="ritual",
				effect="start draw one discard one",
			)
		)
		cards.append(
			Card(
				name=f"Ritual of Recall {i}",
				description="End of your turn: return a pawn from your zone to your hand.",
				card_type="ritual",
				effect="end return pawn",
			)
		)

	for i in range(1, 3):
		cards.append(
			Card(
				name=f"Ritual of Grudge {i}",
				description="You may attack in addition to playing or drawing a card.",
				card_type="ritual",
				effect="grudge",
			)
		)
		cards.append(
			Card(
				name=f"Ritual of Sanctuary {i}",
				description="When defending, gain +2 presence.",
				card_type="ritual",
				effect="sanctuary",
			)
		)
		if i == 1:
			cards.append(
				Card(
					name=f"Ritual of Deluge {i}",
					description=(
						"You count as having no domains and cannot be attacked. "
						"Start of your turn: remove Deluge or discard a card."
					),
					card_type="ritual",
					effect="deluge",
				)
			)
		cards.append(
			Card(
				name=f"Ritual of Duress {i}",
				description="While this is in a zone, domains and pawns do not trigger when played.",
				card_type="ritual",
				effect="duress",
			)
		)

	for i in range(1, 8):
		cards.append(
			Card(
				name=f"Treason {i}",
				description="Counts as three discarded cards when discarded.",
				card_type="treason",
			)
		)

	alignment_by_name = {
		"pawn": "roots",
		"champion pawn": "elite",
		"treason": "chaos",
		"loyalist": "order",
		"emperor": "elite",
		"mob": "chaos",
		"dragon": "chaos",
		"sage": "reason",
		"general": "elite",
		"saint": "order",
		"spymaster": "cunning",
		"rallying pawn": "roots",
		"shieldbearer pawn": "elite",
		"envoy pawn": "order",
		"bastion domain": "order",
		"harbor domain": "order",
		"outpost": "order",
		"workshop": "order",
		"academy": "reason",
		"crossroads": "reason",
		"seer domain": "reason",
		"anchor domain": "order",
		"domain": "order",
		"ritual of exchange": "reason",
		"ritual of recall": "reason",
		"ritual of grudge": "chaos",
		"ritual of sanctuary": "order",
		"ritual of deluge": "chaos",
		"ritual of duress": "cunning",
		"destroy domain": "chaos",
		"draw 3 cards": "cunning",
		"any player discards 2 cards": "chaos",
		"destroy a pawn": "chaos",
		"destroy all pawns with presence 1": "chaos",
		"destroy any ritual": "cunning",
		"spies": "cunning",
		"migration": "order",
		"inheritance": "elite",
		"uprising": "chaos",
	}

	def _alignment_for_card(card: Card) -> str:
		base_name = card.name.rstrip(" 0123456789").lower()
		if base_name in alignment_by_name:
			return alignment_by_name[base_name]
		if card.card_type == "treason":
			return "chaos"
		if card.card_type == "domain":
			return "order"
		if card.card_type == "ritual":
			return "reason"
		if card.card_type == "power":
			return "cunning"
		if card.card_type == "pawn":
			return "roots"
		return "roots"

	cards = [replace(card, alignment=_alignment_for_card(card)) for card in cards]

	return Deck(cards)


def main() -> None:
	choice = input("Start a new game or see the card list? (play/list): ").strip().lower()
	if choice == "list":
		deck = create_default_deck()
		groups = {}
		for card in deck._cards:
			base_name = card.name.rstrip(" 0123456789")
			key = (
				base_name,
				card.card_type,
				card.description,
				card.value,
				card.presence,
				card.domain_value,
				card.effect,
				card.alignment,
			)
			if key not in groups:
				groups[key] = {"count": 0, "card": card, "name": base_name}
			groups[key]["count"] += 1
		for entry in groups.values():
			card = entry["card"]
			print(
				f"- {entry['name']} (x{entry['count']})\t{card.description}\t[{card.alignment}]"
			)
		return

	while True:
		try:
			player_count = int(input("How many players? (2-6): "))
		except ValueError:
			player_count = 2
		if 2 <= player_count <= 6:
			break
		print("Please choose a number between 2 and 6.")
	while True:
		try:
			human_count = int(input(f"How many human players? (0-{player_count}): "))
		except ValueError:
			human_count = 0
		if 0 <= human_count <= player_count:
			break
		print("Please choose a valid number of human players.")
	players: List[Player] = []
	for i in range(player_count):
		default_name = f"Player {i + 1}"
		name = input(f"Name for {default_name}: ").strip() or default_name
		players.append(Player(name, is_human=i < human_count))

	deck = create_default_deck()
	game = Game(players, deck)
	game.start(opening_hand_size=3)

	while True:
		game.play_round()
		winner = game.check_win_conditions()
		if winner is not None:
			print(f"{winner.name} wins the game!")
			break


if __name__ == "__main__":
	main()
