import pygame
import math
import random
import sys
import os
import asyncio
import itertools

# ==========================================
# CONSTANTS & STYLING
# ==========================================
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720

# Colors
COLOR_BG = (12, 13, 16)         # Dark background vignette
COLOR_TEXT = (220, 225, 230)
COLOR_TEXT_MUTED = (110, 115, 125)
COLOR_FELT = (34, 112, 63)       # Dark casino felt green
COLOR_BORDER = (101, 42, 23)     # Rich mahogany wood table trim
COLOR_GOLD = (218, 165, 32)      # Gold accents
COLOR_WHITE = (255, 255, 255)

CARD_NAMES = {2:"2", 3:"3", 4:"4", 5:"5", 6:"6", 7:"7", 8:"8", 9:"9", 10:"10", 11:"J", 12:"Q", 13:"K", 14:"A"}
CARD_PLURALS = {2:"2s", 3:"3s", 4:"4s", 5:"5s", 6:"6s", 7:"7s", 8:"8s", 9:"9s", 10:"10s", 11:"Jacks", 12:"Queens", 13:"Kings", 14:"Aces"}

# ==========================================
# CARD EVALUATION SYSTEM (Texas Hold'em)
# ==========================================
def evaluate_five_card_hand(hand):
    ranks = sorted([c[0] for c in hand], reverse=True)
    suits = [c[1] for c in hand]
    
    is_flush = len(set(suits)) == 1
    
    # Check for straight
    is_straight = False
    straight_high = 0
    if len(set(ranks)) == 5:
        if ranks[0] - ranks[4] == 4:
            is_straight = True
            straight_high = ranks[0]
        elif ranks == [14, 5, 4, 3, 2]:
            is_straight = True
            straight_high = 5
            
    # Rank counts
    counts = {}
    for r in ranks:
        counts[r] = counts.get(r, 0) + 1
        
    # Sort counts descending by frequency, then by rank
    sorted_counts = sorted([(count, r) for r, count in counts.items()], key=lambda x: (x[0], x[1]), reverse=True)
    
    if is_flush and is_straight:
        return (9, straight_high, 0, 0, 0, 0)
    elif sorted_counts[0][0] == 4:
        # Four of a Kind
        four_rank = sorted_counts[0][1]
        kicker = sorted_counts[1][1]
        return (8, four_rank, kicker, 0, 0, 0)
    elif sorted_counts[0][0] == 3 and sorted_counts[1][0] == 2:
        # Full house
        three_rank = sorted_counts[0][1]
        pair_rank = sorted_counts[1][1]
        return (7, three_rank, pair_rank, 0, 0, 0)
    elif is_flush:
        return (6, ranks[0], ranks[1], ranks[2], ranks[3], ranks[4])
    elif is_straight:
        return (5, straight_high, 0, 0, 0, 0)
    elif sorted_counts[0][0] == 3:
        # Three of a Kind
        three_rank = sorted_counts[0][1]
        k0 = sorted_counts[1][1]
        k1 = sorted_counts[2][1]
        return (4, three_rank, k0, k1, 0, 0)
    elif sorted_counts[0][0] == 2 and sorted_counts[1][0] == 2:
        # Two Pair
        p1 = sorted_counts[0][1]
        p2 = sorted_counts[1][1]
        k = sorted_counts[2][1]
        return (3, p1, p2, k, 0, 0)
    elif sorted_counts[0][0] == 2:
        # One Pair
        pair_rank = sorted_counts[0][1]
        k0 = sorted_counts[1][1]
        k1 = sorted_counts[2][1]
        k2 = sorted_counts[3][1]
        return (2, pair_rank, k0, k1, k2, 0)
    else:
        # High Card
        return (1, ranks[0], ranks[1], ranks[2], ranks[3], ranks[4])

def get_best_hand(seven_cards):
    best_score = None
    best_combo = None
    for combo in itertools.combinations(seven_cards, 5):
        score = evaluate_five_card_hand(combo)
        if best_score is None or score > best_score:
            best_score = score
            best_combo = combo
    return best_score, best_combo

def format_hand_name(score):
    if score is None:
        return "No Hand"
    rank = score[0]
    if rank == 9:
        if score[1] == 14:
            return "Royal Flush!"
        return f"Straight Flush, {CARD_NAMES[score[1]]} High"
    elif rank == 8:
        return f"Four of a Kind, {CARD_PLURALS[score[1]]}"
    elif rank == 7:
        return f"Full House, {CARD_PLURALS[score[1]]} over {CARD_PLURALS[score[2]]}"
    elif rank == 6:
        return f"Flush, {CARD_NAMES[score[1]]} High"
    elif rank == 5:
        return f"Straight, {CARD_NAMES[score[1]]} High"
    elif rank == 4:
        return f"Three of a Kind, {CARD_PLURALS[score[1]]}"
    elif rank == 3:
        return f"Two Pair, {CARD_PLURALS[score[1]]} and {CARD_PLURALS[score[2]]}"
    elif rank == 2:
        return f"One Pair of {CARD_PLURALS[score[1]]}"
    else:
        return f"High Card, {CARD_NAMES[score[1]]}"

# ==========================================
# CARD & SUIT PROCEDURAL DRAWING
# ==========================================
def draw_suit_mini(surface, suit, center, color):
    cx, cy = center
    draw_suit_geometry(surface, suit, cx, cy, 10, color)

def draw_suit_large(surface, suit, center, color):
    cx, cy = center
    draw_suit_geometry(surface, suit, cx, cy, 24, color)

def draw_suit_geometry(surface, suit, cx, cy, size, color):
    if suit == 'H':  # Hearts
        r = size // 4
        r = max(1, r)
        pygame.draw.circle(surface, color, (cx - r, cy - r // 2), r)
        pygame.draw.circle(surface, color, (cx + r, cy - r // 2), r)
        pts = [(cx - size // 2, cy), (cx + size // 2, cy), (cx, cy + size // 2 + 1)]
        pygame.draw.polygon(surface, color, pts)
    elif suit == 'D':  # Diamonds
        pts = [(cx, cy - size // 2), (cx + size // 2, cy), (cx, cy + size // 2), (cx - size // 2, cy)]
        pygame.draw.polygon(surface, color, pts)
    elif suit == 'S':  # Spades
        r = size // 4
        r = max(1, r)
        pygame.draw.circle(surface, color, (cx - r, cy + r // 2), r)
        pygame.draw.circle(surface, color, (cx + r, cy + r // 2), r)
        pts = [(cx - size // 2, cy), (cx + size // 2, cy), (cx, cy - size // 2 - 1)]
        pygame.draw.polygon(surface, color, pts)
        # Stem
        stem_pts = [(cx, cy), (cx - r, cy + size // 2), (cx + r, cy + size // 2)]
        pygame.draw.polygon(surface, color, stem_pts)
    elif suit == 'C':  # Clubs
        r = size // 5
        r = max(1, r)
        pygame.draw.circle(surface, color, (cx, cy - r), r)
        pygame.draw.circle(surface, color, (cx - r, cy + r // 2), r)
        pygame.draw.circle(surface, color, (cx + r, cy + r // 2), r)
        # Stem
        stem_pts = [(cx, cy), (cx - r, cy + size // 2), (cx + r, cy + size // 2)]
        pygame.draw.polygon(surface, color, stem_pts)

# ==========================================
# RETRO POLISHED INTERACTIVE ELEMENTS
# ==========================================
class CardSprite:
    def __init__(self, card, start_pos, target_pos, face_up=True, delay=0.0):
        self.card = card  # (rank, suit)
        self.x, self.y = start_pos
        self.tx, self.ty = target_pos
        self.face_up = face_up
        self.delay = delay
        self.width = 74
        self.height = 110
        self.active = False

    def update(self, dt):
        if self.delay > 0:
            self.delay -= dt
            return
        
        self.active = True
        # Frame-rate independent slide interpolation
        rate = 1.0 - math.exp(-12.0 * dt)
        self.x += (self.tx - self.x) * rate
        self.y += (self.ty - self.y) * rate

    def draw(self, surface, font, showdown_revealed=False):
        if not self.active:
            return

        cx, cy = int(self.x), int(self.y)
        rect = pygame.Rect(cx, cy, self.width, self.height)
        shadow_rect = pygame.Rect(cx + 3, cy + 3, self.width, self.height)

        # Draw Shadow
        pygame.draw.rect(surface, (15, 20, 18), shadow_rect, border_radius=6)

        visible = self.face_up or showdown_revealed

        if visible:
            # White elegant card body
            pygame.draw.rect(surface, (252, 252, 250), rect, border_radius=6)
            pygame.draw.rect(surface, (180, 180, 185), rect, width=1, border_radius=6)

            rank, suit = self.card
            color = (230, 50, 50) if suit in ['H', 'D'] else (30, 30, 30)

            rank_str = {11: 'J', 12: 'Q', 13: 'K', 14: 'A'}.get(rank, str(rank))

            # Corner Rank Letters
            r_surf = font.render(rank_str, True, color)
            surface.blit(r_surf, (cx + 6, cy + 6))
            draw_suit_mini(surface, suit, (cx + 12, cy + 30), color)

            # Bottom Right Letter
            surface.blit(r_surf, (cx + self.width - 6 - r_surf.get_width(), cy + self.height - 6 - r_surf.get_height()))
            draw_suit_mini(surface, suit, (cx + self.width - 12, cy + self.height - 30), color)

            # Center Suit Accent
            draw_suit_large(surface, suit, (cx + self.width // 2, cy + self.height // 2), color)
        else:
            # Blue card back pattern
            pygame.draw.rect(surface, (23, 54, 93), rect, border_radius=6)
            pygame.draw.rect(surface, (218, 165, 32), rect, width=3, border_radius=6)
            pygame.draw.rect(surface, (250, 250, 250), rect.inflate(-10, -10), width=1, border_radius=4)
            
            # Center golden diamond
            center_x, center_y = cx + self.width // 2, cy + self.height // 2
            pygame.draw.polygon(surface, (218, 165, 32), [
                (center_x, center_y - 20),
                (center_x + 14, center_y),
                (center_x, center_y + 20),
                (center_x - 14, center_y)
            ], width=2)


class Button:
    def __init__(self, x, y, w, h, text, color, hover_color, text_color=(255, 255, 255), enabled=True):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.enabled = enabled

    def draw(self, surface, font):
        if not self.enabled:
            # Disabled state (slate-grayed)
            pygame.draw.rect(surface, (45, 48, 52), self.rect, border_radius=6)
            txt = font.render(self.text, True, (95, 100, 105))
        else:
            mouse_pos = pygame.mouse.get_pos()
            color = self.hover_color if self.rect.collidepoint(mouse_pos) else self.color
            pygame.draw.rect(surface, color, self.rect, border_radius=6)
            pygame.draw.rect(surface, (255, 255, 255), self.rect, width=1, border_radius=6)
            txt = font.render(self.text, True, self.text_color)
        
        surface.blit(txt, (self.rect.centerx - txt.get_width() // 2, self.rect.centery - txt.get_height() // 2))

    def is_clicked(self, event):
        if not self.enabled:
            return False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
        return False


class ChipParticle:
    def __init__(self, start_pos, target_pos, color):
        self.x, self.y = start_pos
        self.tx, self.ty = target_pos
        self.color = color
        self.life = 0.5
        self.max_life = 0.5
        # Quadratic bezier curve control point to arc upwards!
        self.cx = (start_pos[0] + target_pos[0]) // 2
        self.cy = min(start_pos[1], target_pos[1]) - random.randint(70, 150)
        
    def update(self, dt):
        self.life -= dt
        
    def draw(self, surface):
        if self.life <= 0:
            return
        t = 1.0 - (self.life / self.max_life)
        mt = 1.0 - t
        # Bezier curve formula B(t)
        x = mt*mt*self.x + 2*mt*t*self.cx + t*t*self.tx
        y = mt*mt*self.y + 2*mt*t*self.cy + t*t*self.ty
        
        pygame.draw.circle(surface, (10, 10, 10), (int(x), int(y)), 9)
        pygame.draw.circle(surface, self.color, (int(x), int(y)), 7)
        pygame.draw.circle(surface, (255, 255, 255), (int(x), int(y)), 4, 1)


class Confetti:
    def __init__(self):
        self.x = random.randint(0, WINDOW_WIDTH)
        self.y = random.randint(-50, 0)
        self.vx = random.uniform(-40, 40)
        self.vy = random.uniform(110, 260)
        self.color = (random.randint(70, 255), random.randint(70, 255), random.randint(70, 255))
        self.w = random.randint(6, 12)
        self.h = random.randint(6, 12)
        self.rot = random.uniform(0, 360)
        self.rot_speed = random.uniform(100, 300)
        
    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.rot += self.rot_speed * dt
        
    def draw(self, surface):
        rad = math.radians(self.rot)
        c, s = math.cos(rad), math.sin(rad)
        hw, hh = self.w / 2, self.h / 2
        pts = [
            (self.x + (-hw*c - -hh*s), self.y + (-hw*s + -hh*c)),
            (self.x + (hw*c - -hh*s), self.y + (hw*s + -hh*c)),
            (self.x + (hw*c - hh*s), self.y + (hw*s + hh*c)),
            (self.x + (-hw*c - hh*s), self.y + (-hw*s + hh*c))
        ]
        pygame.draw.polygon(surface, self.color, pts)

# ==========================================
# MAIN GAME MACHINE
# ==========================================
class Game:
    def __init__(self):
        pygame.mixer.pre_init(44100, -16, 2, 512)
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("High-Stakes Texas Hold'em Poker")
        self.clock = pygame.time.Clock()
        
        # Audio Initialization Safely
        self.audio_enabled = False
        try:
            pygame.mixer.init()
            self.audio_enabled = True
        except Exception as e:
            print(f"[Warning] Mixer failed to init: {e}")
            
        self.sounds = {}
        if self.audio_enabled:
            self.generate_sounds()
            
        # Standard Fonts
        self.font_large = pygame.font.Font(None, 46)
        self.font_medium = pygame.font.Font(None, 30)
        self.font_small = pygame.font.Font(None, 24)
        self.font_card = pygame.font.Font(None, 26)
        
        self.reset_game_state(full_reset=True)

    def generate_sounds(self):
        try:
            # Waveform buffer synth helper
            def create_synth_sound(freq_func, duration=0.1, volume=0.1):
                sample_rate = 44100
                num_samples = int(sample_rate * duration)
                buffer = bytearray(num_samples * 2)
                for i in range(num_samples):
                    t = i / sample_rate
                    freq = freq_func(t)
                    val = int(math.sin(2 * math.pi * freq * t) * 32767 * volume)
                    buffer[i*2] = val & 0xff
                    buffer[i*2+1] = (val >> 8) & 0xff
                return pygame.mixer.Sound(buffer=buffer)

            # Sound specs
            self.sounds["deal"] = create_synth_sound(lambda t: 800 - 600 * t, 0.1, 0.04)
            self.sounds["chip"] = create_synth_sound(lambda t: 1800 - 1200 * (t/0.04) if t < 0.04 else 450, 0.07, 0.03)
            self.sounds["check"] = create_synth_sound(lambda t: 140 if (t < 0.03 or 0.05 < t < 0.08) else 0, 0.09, 0.07)
            self.sounds["raise"] = create_synth_sound(lambda t: 950 if (t < 0.06 or 0.1 < t < 0.15) else 0, 0.18, 0.04)
            self.sounds["win"] = create_synth_sound(lambda t: 450 + 250 * int(t * 15) / 3, 0.35, 0.06)
            self.sounds["lose"] = create_synth_sound(lambda t: 300 - 180 * t, 0.5, 0.06)
            self.sounds["fold"] = create_synth_sound(lambda t: 450 - 350 * t, 0.22, 0.04)
        except Exception as e:
            print(f"[Warning] Failed to generate procedural audio: {e}")
            self.audio_enabled = False
            
    def play_sound(self, name):
        if self.audio_enabled and name in self.sounds:
            self.sounds[name].play()

    def reset_game_state(self, full_reset=True):
        if full_reset:
            self.player_chips = 1000
            self.ai_chips = 1000
            self.dealer_button = 'player'
            self.game_state = "MENU"
        
        self.deck = []
        self.player_cards = []
        self.ai_cards = []
        self.community_cards = []
        
        self.pot = 0
        self.current_bet = 0
        self.player_round_bet = 0
        self.ai_round_bet = 0
        self.action_count = 0
        self.all_in_active = False
        self.whose_turn = 'player'
        
        self.card_sprites = []
        self.particles = []
        self.confetti = []
        self.ai_thinking_timer = 0.0
        self.ai_status_message = ""
        self.hand_outcome_text = ""
        self.winner = None
        self.showdown_revealed = False
        
        self.raise_amount = 40
        self.betting_ended = False
        self.all_in_deal_timer = 0.0
        
        self.init_buttons()

    def init_buttons(self):
        self.btn_menu_start = Button(540, 450, 200, 50, "PLAY GAME", (34, 139, 34), (46, 204, 113))
        self.btn_restart = Button(540, 450, 200, 50, "PLAY AGAIN", (34, 139, 34), (46, 204, 113))
        
        self.btn_check_call = Button(950, 560, 130, 40, "Check", (52, 152, 219), (41, 128, 185))
        self.btn_fold = Button(1100, 560, 130, 40, "Fold", (231, 76, 60), (192, 57, 43))
        
        self.btn_raise_minus = Button(950, 610, 50, 40, "-$50", (127, 140, 141), (149, 165, 166))
        self.btn_raise_plus = Button(1010, 610, 50, 40, "+$50", (127, 140, 141), (149, 165, 166))
        self.btn_raise_min = Button(1070, 610, 70, 40, "Min", (44, 62, 80), (52, 73, 94))
        self.btn_raise_allin = Button(1150, 610, 80, 40, "All-In", (230, 126, 34), (211, 84, 0))
        
        self.btn_raise_execute = Button(950, 660, 280, 45, "Raise", (46, 204, 113), (39, 174, 96))
        self.btn_next_hand = Button(540, 600, 200, 50, "NEXT HAND", (241, 196, 15), (243, 156, 18), (44, 62, 80))

    def start_new_hand(self):
        if self.player_chips <= 0 or self.ai_chips <= 0:
            self.game_state = "GAME_OVER"
            self.winner = "ai" if self.player_chips <= 0 else "player"
            self.play_sound("lose" if self.winner == "ai" else "win")
            return
            
        if self.game_state != "MENU":
            self.dealer_button = 'ai' if self.dealer_button == 'player' else 'player'
            
        self.deck = [(rank, suit) for rank in range(2, 15) for suit in ['H', 'D', 'C', 'S']]
        random.shuffle(self.deck)
        
        self.player_cards = []
        self.ai_cards = []
        self.community_cards = []
        self.card_sprites = []
        self.particles = []
        self.confetti = []
        self.ai_status_message = ""
        self.hand_outcome_text = ""
        self.winner = None
        self.showdown_revealed = False
        self.pot = 0
        self.player_round_bet = 0
        self.ai_round_bet = 0
        self.current_bet = 0
        self.action_count = 0
        self.all_in_active = False
        self.betting_ended = False
        self.all_in_deal_timer = 0.0
        
        sb = 10
        bb = 20
        
        if self.dealer_button == 'player':
            actual_sb = min(sb, self.player_chips)
            actual_bb = min(bb, self.ai_chips)
            self.player_chips -= actual_sb
            self.player_round_bet = actual_sb
            self.ai_chips -= actual_bb
            self.ai_round_bet = actual_bb
            self.current_bet = actual_bb
            self.whose_turn = 'player'
        else:
            actual_sb = min(sb, self.ai_chips)
            actual_bb = min(bb, self.player_chips)
            self.ai_chips -= actual_sb
            self.ai_round_bet = actual_sb
            self.player_chips -= actual_bb
            self.player_round_bet = actual_bb
            self.current_bet = actual_bb
            self.whose_turn = 'ai'
            self.ai_thinking_timer = 1.0
            
        if self.player_chips == 0 or self.ai_chips == 0:
            self.all_in_active = True
            
        p1 = self.deck.pop()
        p2 = self.deck.pop()
        a1 = self.deck.pop()
        a2 = self.deck.pop()
        
        self.player_cards = [p1, p2]
        self.ai_cards = [a1, a2]
        
        # Sequence cards onto the table
        self.card_sprites.append(CardSprite(p1, (640, -100), (570, 500), face_up=True, delay=0.0))
        self.card_sprites.append(CardSprite(a1, (640, -100), (570, 80), face_up=False, delay=0.2))
        self.card_sprites.append(CardSprite(p2, (640, -100), (670, 500), face_up=True, delay=0.4))
        self.card_sprites.append(CardSprite(a2, (640, -100), (670, 80), face_up=False, delay=0.6))
        
        self.play_sound("deal")
        
        self.raise_amount = max(bb, self.current_bet * 2)
        self.game_state = "PRE_FLOP"
        self.check_betting_round_complete()

    def deal_community_cards(self, num_cards):
        start_idx = len(self.community_cards)
        for i in range(num_cards):
            card = self.deck.pop()
            self.community_cards.append(card)
            idx = start_idx + i
            tx = 450 + idx * 95
            ty = 290
            self.card_sprites.append(CardSprite(card, (640, -100), (tx, ty), face_up=True, delay=i*0.2))
        self.play_sound("deal")

    def advance_betting_round(self):
        self.pot += self.player_round_bet + self.ai_round_bet
        self.player_round_bet = 0
        self.ai_round_bet = 0
        self.current_bet = 0
        self.action_count = 0
        
        if self.player_chips == 0 or self.ai_chips == 0:
            self.all_in_active = True
            
        if self.all_in_active:
            self.betting_ended = True
            self.all_in_deal_timer = 1.0
            return

        if self.game_state == "PRE_FLOP":
            self.game_state = "FLOP"
            self.deal_community_cards(3)
            self.whose_turn = 'ai' if self.dealer_button == 'player' else 'player'
        elif self.game_state == "FLOP":
            self.game_state = "TURN"
            self.deal_community_cards(1)
            self.whose_turn = 'ai' if self.dealer_button == 'player' else 'player'
        elif self.game_state == "TURN":
            self.game_state = "RIVER"
            self.deal_community_cards(1)
            self.whose_turn = 'ai' if self.dealer_button == 'player' else 'player'
        elif self.game_state == "RIVER":
            self.trigger_showdown()
            
        if self.whose_turn == 'ai':
            self.ai_thinking_timer = 1.2
            
        self.raise_amount = self.get_min_raise()

    def trigger_showdown(self):
        self.game_state = "SHOWDOWN"
        self.showdown_revealed = True
        
        p_score, p_combo = get_best_hand(self.player_cards + self.community_cards)
        a_score, a_combo = get_best_hand(self.ai_cards + self.community_cards)
        
        p_name = format_hand_name(p_score)
        a_name = format_hand_name(a_score)
        
        if p_score > a_score:
            self.winner = 'player'
            self.player_chips += self.pot
            self.hand_outcome_text = f"You Win ${self.pot} with {p_name}!"
            self.play_sound("win")
            self.spawn_confetti(120)
            self.spawn_bet_particles((640, 225), (200, 560), self.pot)
        elif a_score > p_score:
            self.winner = 'ai'
            self.ai_chips += self.pot
            self.hand_outcome_text = f"AI Wins ${self.pot} with {a_name}!"
            self.play_sound("lose")
            self.spawn_bet_particles((640, 225), (200, 140), self.pot)
        else:
            self.winner = 'split'
            half_pot = self.pot // 2
            self.player_chips += half_pot
            self.ai_chips += half_pot
            self.hand_outcome_text = f"Split Pot! Both have {p_name}."
            self.play_sound("win")
            self.spawn_bet_particles((640, 225), (200, 560), half_pot)
            self.spawn_bet_particles((640, 225), (200, 140), half_pot)
            
        self.pot = 0

    def trigger_fold(self, folder):
        self.game_state = "SHOWDOWN"
        self.showdown_revealed = False
        
        self.pot += self.player_round_bet + self.ai_round_bet
        self.player_round_bet = 0
        self.ai_round_bet = 0
        
        if folder == 'player':
            self.winner = 'ai'
            self.ai_chips += self.pot
            self.hand_outcome_text = f"You Fold. AI Wins ${self.pot}!"
            self.play_sound("fold")
            self.spawn_bet_particles((640, 225), (200, 140), self.pot)
        else:
            self.winner = 'player'
            self.player_chips += self.pot
            self.hand_outcome_text = f"AI Folds. You Win ${self.pot}!"
            self.play_sound("win")
            self.spawn_confetti(60)
            self.spawn_bet_particles((640, 225), (200, 560), self.pot)
            
        self.pot = 0

    def spawn_confetti(self, count):
        for _ in range(count):
            self.confetti.append(Confetti())

    def spawn_bet_particles(self, from_pos, to_pos, amount):
        colors = []
        if amount >= 100:
            colors.append((30, 30, 30))
        if amount >= 25:
            colors.append((46, 204, 113))
        if amount >= 10:
            colors.append((52, 152, 219))
        if not colors:
            colors.append((231, 76, 60))
            
        for color in colors:
            for _ in range(random.randint(2, 4)):
                sp = (from_pos[0] + random.randint(-15, 15), from_pos[1] + random.randint(-15, 15))
                tp = (to_pos[0] + random.randint(-20, 20), to_pos[1] + random.randint(-20, 20))
                self.particles.append(ChipParticle(sp, tp, color))

    def get_min_raise(self):
        max_possible = self.player_round_bet + self.player_chips
        if self.current_bet == 0:
            return min(20, max_possible)
        diff = max(20, self.current_bet)
        return min(self.current_bet + diff, max_possible)

    def execute_ai_turn(self):
        to_call = self.player_round_bet - self.ai_round_bet
        if to_call < 0:
            to_call = 0
            
        action, amount = self.get_ai_decision(to_call)
        
        if action == "FOLD":
            self.ai_status_message = "AI folds"
            self.trigger_fold('ai')
        elif action == "CHECK":
            self.ai_status_message = "AI checks"
            self.play_sound("check")
            self.action_count += 1
            self.whose_turn = 'player'
            self.check_betting_round_complete()
        elif action == "CALL":
            call_cost = to_call
            if call_cost >= self.ai_chips:
                call_cost = self.ai_chips
                self.ai_chips = 0
                self.ai_round_bet += call_cost
                self.all_in_active = True
                self.ai_status_message = "AI calls ALL-IN!"
            else:
                self.ai_chips -= call_cost
                self.ai_round_bet += call_cost
                self.ai_status_message = f"AI calls ${call_cost}"
                
            self.play_sound("chip")
            self.spawn_bet_particles((200, 140), (640, 225), call_cost)
            self.action_count += 1
            self.whose_turn = 'player'
            self.check_betting_round_complete()
        elif action == "RAISE":
            raise_target = amount
            raise_cost = raise_target - self.ai_round_bet
            
            if raise_cost >= self.ai_chips:
                raise_target = self.ai_round_bet + self.ai_chips
                self.ai_chips = 0
                self.ai_round_bet = raise_target
                self.all_in_active = True
                self.ai_status_message = "AI raises ALL-IN!"
            else:
                self.ai_chips -= raise_cost
                self.ai_round_bet = raise_target
                self.ai_status_message = f"AI raises to ${raise_target}"
                
            self.current_bet = raise_target
            self.play_sound("raise")
            self.spawn_bet_particles((200, 140), (640, 225), raise_cost)
            self.action_count += 1
            self.whose_turn = 'player'
            self.check_betting_round_complete()

    def get_ai_decision(self, to_call):
        if len(self.community_cards) == 0:
            # Simple preflop calculation
            r1, s1 = self.ai_cards[0]
            r2, s2 = self.ai_cards[1]
            max_r = max(r1, r2)
            min_r = min(r1, r2)
            is_pair = (r1 == r2)
            is_suited = (s1 == s2)
            is_connected = (abs(r1 - r2) == 1)
            
            if is_pair:
                rating = 80 + max_r
            elif is_suited and is_connected:
                rating = 60 + max_r
            elif is_suited:
                rating = 45 + max_r
            elif is_connected:
                rating = 40 + max_r
            else:
                rating = max_r * 2 + min_r
                
            if rating >= 85:
                strength = "excellent"
            elif rating >= 65:
                strength = "great"
            elif rating >= 45:
                strength = "medium"
            else:
                strength = "weak"
        else:
            score, combo = get_best_hand(self.ai_cards + self.community_cards)
            rank = score[0] if score is not None else 1
            if rank >= 3:
                strength = "excellent"
            elif rank == 2:
                pair_rank = score[1] if score is not None else 2
                strength = "great" if pair_rank >= 10 else "medium"
            else:
                strength = "weak"

        # Intercept if Player is All-In (cannot raise)
        if self.player_chips == 0:
            if strength in ["excellent", "great"]:
                return "CALL", 0
            elif strength == "medium" and to_call <= self.ai_chips * 0.4:
                return "CALL", 0
            return "FOLD", 0

        bluff = (random.random() < 0.10)
        total_pot = self.pot + self.player_round_bet + self.ai_round_bet
        
        if to_call == 0:
            if strength == "excellent":
                if random.random() < 0.8:
                    return "RAISE", self.calculate_bet_size(0.6, total_pot)
                return "CHECK", 0
            elif strength == "great":
                if random.random() < 0.4:
                    return "RAISE", self.calculate_bet_size(0.4, total_pot)
                return "CHECK", 0
            elif strength == "medium":
                return "CHECK", 0
            else:
                if bluff:
                    return "RAISE", self.calculate_bet_size(0.5, total_pot)
                return "CHECK", 0
        else:
            if strength == "excellent":
                if random.random() < 0.7:
                    raise_amount = self.player_round_bet + self.calculate_bet_size(0.75, total_pot)
                    min_r = self.player_round_bet + max(20, self.player_round_bet)
                    return "RAISE", max(raise_amount, min_r)
                return "CALL", 0
            elif strength == "great":
                if random.random() < 0.3:
                    raise_amount = self.player_round_bet + self.calculate_bet_size(0.5, total_pot)
                    min_r = self.player_round_bet + max(20, self.player_round_bet)
                    return "RAISE", max(raise_amount, min_r)
                return "CALL", 0
            elif strength == "medium":
                if to_call <= self.ai_chips * 0.3:
                    return "CALL", 0
                return "FOLD", 0
            else:
                if bluff and to_call <= self.ai_chips * 0.2:
                    raise_amount = self.player_round_bet + self.calculate_bet_size(0.6, total_pot)
                    min_r = self.player_round_bet + max(20, self.player_round_bet)
                    return "RAISE", max(raise_amount, min_r)
                return "FOLD", 0

    def calculate_bet_size(self, pct, total_pot):
        raw = int(total_pot * pct)
        rounded = ((raw + 4) // 5) * 5
        return max(20, min(rounded, self.ai_chips))

    def check_betting_round_complete(self):
        is_all_in_complete = False
        if self.all_in_active:
            if self.player_chips == 0 and self.ai_chips == 0:
                is_all_in_complete = True
            elif self.player_chips == 0 and self.ai_round_bet >= self.player_round_bet:
                is_all_in_complete = True
            elif self.ai_chips == 0 and self.player_round_bet >= self.ai_round_bet:
                is_all_in_complete = True
                
        if is_all_in_complete:
            self.advance_betting_round()
        elif self.action_count >= 2 and self.player_round_bet == self.ai_round_bet:
            self.advance_betting_round()

    def update_buttons(self):
        is_p_turn = (self.whose_turn == 'player' and 
                     not self.betting_ended and 
                     self.game_state in ["PRE_FLOP", "FLOP", "TURN", "RIVER"])
        
        if is_p_turn:
            to_call = self.current_bet - self.player_round_bet
            if to_call == 0:
                self.btn_check_call.text = "Check"
            else:
                self.btn_check_call.text = f"Call ${min(to_call, self.player_chips)}"
            
            self.btn_check_call.enabled = True
            self.btn_fold.enabled = True
            
            min_r = self.get_min_raise()
            max_r = self.player_round_bet + self.player_chips
            
            if self.ai_chips == 0:
                self.btn_raise_minus.enabled = False
                self.btn_raise_plus.enabled = False
                self.btn_raise_min.enabled = False
                self.btn_raise_allin.enabled = False
                self.btn_raise_execute.enabled = False
            else:
                self.btn_raise_minus.enabled = (self.raise_amount - 50 >= min_r)
                self.btn_raise_plus.enabled = (self.raise_amount + 50 <= max_r)
                self.btn_raise_min.enabled = (max_r >= min_r)
                self.btn_raise_allin.enabled = True
                
                self.raise_amount = max(min_r, min(self.raise_amount, max_r))
                
                if self.raise_amount == max_r:
                    self.btn_raise_execute.text = "Raise ALL-IN!"
                elif self.current_bet == 0:
                    self.btn_raise_execute.text = f"Bet ${self.raise_amount}"
                else:
                    self.btn_raise_execute.text = f"Raise to ${self.raise_amount}"
                    
                self.btn_raise_execute.enabled = (max_r >= min_r)
        else:
            self.btn_check_call.enabled = False
            self.btn_fold.enabled = False
            self.btn_raise_minus.enabled = False
            self.btn_raise_plus.enabled = False
            self.btn_raise_min.enabled = False
            self.btn_raise_allin.enabled = False
            self.btn_raise_execute.enabled = False

    def handle_events(self, event):
        if self.game_state == "MENU":
            if self.btn_menu_start.is_clicked(event):
                self.start_new_hand()
        elif self.game_state == "SHOWDOWN":
            if self.btn_next_hand.is_clicked(event):
                self.start_new_hand()
        elif self.game_state == "GAME_OVER":
            if self.btn_restart.is_clicked(event):
                self.reset_game_state(full_reset=True)
                self.game_state = "MENU"
        else:
            # Active Betting State & Player's Turn
            is_p_turn = (self.whose_turn == 'player' and 
                         not self.betting_ended and 
                         self.game_state in ["PRE_FLOP", "FLOP", "TURN", "RIVER"])
            if is_p_turn:
                if self.btn_check_call.is_clicked(event):
                    to_call = self.current_bet - self.player_round_bet
                    call_amount = min(to_call, self.player_chips)
                    self.player_chips -= call_amount
                    self.player_round_bet += call_amount
                    
                    if self.player_chips == 0:
                        self.all_in_active = True
                        
                    self.action_count += 1
                    if to_call == 0:
                        self.play_sound("check")
                        self.ai_status_message = "You check"
                    else:
                        self.play_sound("chip")
                        self.spawn_bet_particles((200, 560), (640, 225), call_amount)
                        self.ai_status_message = f"You call ${call_amount}"
                        
                    self.whose_turn = 'ai'
                    self.ai_thinking_timer = 1.2
                    self.check_betting_round_complete()
                    
                elif self.btn_fold.is_clicked(event):
                    self.trigger_fold('player')
                    
                elif self.btn_raise_minus.is_clicked(event):
                    self.raise_amount = max(self.raise_amount - 50, self.get_min_raise())
                    self.play_sound("chip")
                    
                elif self.btn_raise_plus.is_clicked(event):
                    max_r = self.player_round_bet + self.player_chips
                    self.raise_amount = min(self.raise_amount + 50, max_r)
                    self.play_sound("chip")
                    
                elif self.btn_raise_min.is_clicked(event):
                    self.raise_amount = self.get_min_raise()
                    self.play_sound("chip")
                    
                elif self.btn_raise_allin.is_clicked(event):
                    self.raise_amount = self.player_round_bet + self.player_chips
                    self.play_sound("chip")
                    
                elif self.btn_raise_execute.is_clicked(event):
                    raise_cost = self.raise_amount - self.player_round_bet
                    self.player_chips -= raise_cost
                    self.player_round_bet = self.raise_amount
                    
                    if self.player_chips == 0:
                        self.all_in_active = True
                        
                    self.current_bet = self.raise_amount
                    self.action_count += 1
                    self.play_sound("raise")
                    self.spawn_bet_particles((200, 560), (640, 225), raise_cost)
                    
                    if self.player_chips == 0:
                        self.ai_status_message = "You raise ALL-IN!"
                    else:
                        self.ai_status_message = f"You raise to ${self.raise_amount}"
                        
                    self.whose_turn = 'ai'
                    self.ai_thinking_timer = 1.2
                    self.check_betting_round_complete()

    def update(self, dt):
        # Update Card Sprites
        for s in self.card_sprites:
            s.update(dt)
            
        # Update Particles
        alive_particles = []
        for p in self.particles:
            p.update(dt)
            if p.life > 0:
                alive_particles.append(p)
        self.particles = alive_particles
        
        # Update Confetti
        for c in self.confetti:
            c.update(dt)
        self.confetti = [c for c in self.confetti if c.y < 750]
        
        # Handle all-in automatic card sweeps
        if self.betting_ended and self.game_state != "SHOWDOWN":
            self.all_in_deal_timer -= dt
            if self.all_in_deal_timer <= 0:
                self.all_in_deal_timer = 1.0
                num_comm = len(self.community_cards)
                if num_comm == 0:
                    self.deal_community_cards(3)
                elif num_comm in [3, 4]:
                    self.deal_community_cards(1)
                elif num_comm == 5:
                    self.trigger_showdown()
                    
        # Update buttons enabled-states
        self.update_buttons()
        
        # Handle AI Turn Timers
        if (self.whose_turn == 'ai' and 
            not self.betting_ended and 
            self.game_state in ["PRE_FLOP", "FLOP", "TURN", "RIVER"]):
            self.ai_thinking_timer -= dt
            if self.ai_thinking_timer <= 0:
                self.execute_ai_turn()

    def draw_chip_stack(self, surface, x, y, amount):
        denoms = [(100, (30, 30, 30)), (25, (46, 204, 113)), (10, (52, 152, 219)), (5, (231, 76, 60))]
        rem = amount
        stacks = []
        for val, color in denoms:
            count = rem // val
            if count > 0:
                stacks.append((count, color))
                rem %= val
                
        if not stacks:
            return
            
        num_stacks = len(stacks)
        spacing = 30
        start_x = x - (num_stacks - 1) * spacing // 2
        
        for idx, (count, color) in enumerate(stacks):
            stack_x = start_x + idx * spacing
            draw_count = min(count, 8)
            for i in range(draw_count):
                cy = y - i * 4
                # Black base rim
                pygame.draw.circle(surface, (10, 10, 12), (stack_x, cy), 14)
                pygame.draw.circle(surface, color, (stack_x, cy), 12)
                # Radial ticks
                for angle in range(0, 360, 45):
                    rad = math.radians(angle)
                    px = stack_x + int(math.cos(rad) * 11)
                    py = cy + int(math.sin(rad) * 11)
                    pygame.draw.line(surface, COLOR_WHITE, (stack_x + int(math.cos(rad)*8), cy + int(math.sin(rad)*8)), (px, py), 1)
                pygame.draw.circle(surface, COLOR_WHITE, (stack_x, cy), 6, 1)

    def draw(self):
        self.screen.fill(COLOR_BG)
        
        # DRAW CLASSIC OVAL CASINO TABLE
        # 1. Mahogany thick frame
        pygame.draw.ellipse(self.screen, COLOR_BORDER, pygame.Rect(140, 60, 1000, 480))
        # 2. Golden rim highlight
        pygame.draw.ellipse(self.screen, COLOR_GOLD, pygame.Rect(150, 70, 980, 460), 2)
        # 3. Rich green velvet felt
        pygame.draw.ellipse(self.screen, COLOR_FELT, pygame.Rect(155, 75, 970, 450))
        
        # Draw central golden lines
        pygame.draw.ellipse(self.screen, (28, 90, 50), pygame.Rect(340, 180, 600, 240), 2)
        
        # DRAW DEALER BUTTONS
        if self.game_state not in ["MENU", "GAME_OVER"]:
            # Player Dealer Button
            if self.dealer_button == 'player':
                pygame.draw.circle(self.screen, COLOR_GOLD, (540, 470), 12)
                pygame.draw.circle(self.screen, COLOR_WHITE, (540, 470), 12, 1)
                b_txt = self.font_small.render("D", True, COLOR_BG)
                self.screen.blit(b_txt, (540 - b_txt.get_width() // 2, 470 - b_txt.get_height() // 2))
            else: # AI Dealer Button
                pygame.draw.circle(self.screen, COLOR_GOLD, (540, 110), 12)
                pygame.draw.circle(self.screen, COLOR_WHITE, (540, 110), 12, 1)
                b_txt = self.font_small.render("D", True, COLOR_BG)
                self.screen.blit(b_txt, (540 - b_txt.get_width() // 2, 110 - b_txt.get_height() // 2))
                
        # DRAW POT & STACKS
        if self.pot > 0:
            self.draw_chip_stack(self.screen, 640, 215, self.pot)
            pot_txt = self.font_medium.render(f"POT: ${self.pot}", True, COLOR_GOLD)
            self.screen.blit(pot_txt, (640 - pot_txt.get_width() // 2, 230))
            
        # DRAW CHIP STACKS FOR CURRENT ROUND BETS
        if self.player_round_bet > 0:
            self.draw_chip_stack(self.screen, 640, 440, self.player_round_bet)
            pbet_txt = self.font_small.render(f"${self.player_round_bet}", True, COLOR_WHITE)
            self.screen.blit(pbet_txt, (640 - pbet_txt.get_width() // 2, 455))
            
        if self.ai_round_bet > 0:
            self.draw_chip_stack(self.screen, 640, 175, self.ai_round_bet)
            abet_txt = self.font_small.render(f"${self.ai_round_bet}", True, COLOR_WHITE)
            self.screen.blit(abet_txt, (640 - abet_txt.get_width() // 2, 140))
            
        # DRAW PLAYER AND AI HUD (Left Side of screen)
        # Player Stats Box
        pygame.draw.rect(self.screen, (22, 25, 30), pygame.Rect(30, 540, 300, 150), border_radius=8)
        pygame.draw.rect(self.screen, COLOR_GOLD if self.whose_turn == 'player' and self.game_state not in ["MENU", "SHOWDOWN", "GAME_OVER"] else (50, 55, 60), pygame.Rect(30, 540, 300, 150), width=2, border_radius=8)
        
        title_p = self.font_medium.render("PLAYER (YOU)", True, COLOR_GOLD)
        self.screen.blit(title_p, (45, 555))
        chips_p = self.font_large.render(f"${self.player_chips}", True, COLOR_WHITE)
        self.screen.blit(chips_p, (45, 585))
        
        # Display player's current hand rank description if postflop
        if self.game_state in ["FLOP", "TURN", "RIVER", "SHOWDOWN"] and len(self.player_cards + self.community_cards) >= 5:
            score, combo = get_best_hand(self.player_cards + self.community_cards)
            rank_p_txt = self.font_small.render(format_hand_name(score), True, COLOR_TEXT_MUTED)
            self.screen.blit(rank_p_txt, (45, 640))
            
        # AI Stats Box
        pygame.draw.rect(self.screen, (22, 25, 30), pygame.Rect(30, 30, 300, 150), border_radius=8)
        pygame.draw.rect(self.screen, COLOR_GOLD if self.whose_turn == 'ai' and self.game_state not in ["MENU", "SHOWDOWN", "GAME_OVER"] else (50, 55, 60), pygame.Rect(30, 30, 300, 150), width=2, border_radius=8)
        
        title_a = self.font_medium.render("AI OPPONENT", True, COLOR_GOLD)
        self.screen.blit(title_a, (45, 45))
        chips_a = self.font_large.render(f"${self.ai_chips}", True, COLOR_WHITE)
        self.screen.blit(chips_a, (45, 75))
        
        # Display AI hand description during showdown only
        if self.game_state == "SHOWDOWN" and self.showdown_revealed and len(self.ai_cards + self.community_cards) >= 5:
            score, combo = get_best_hand(self.ai_cards + self.community_cards)
            rank_a_txt = self.font_small.render(format_hand_name(score), True, COLOR_TEXT_MUTED)
            self.screen.blit(rank_a_txt, (45, 130))
            
        # DRAW CARD SPRITES
        for s in self.card_sprites:
            s.draw(self.screen, self.font_card, showdown_revealed=self.showdown_revealed)
            
        # DRAW FLYING CHIP PARTICLES
        for p in self.particles:
            p.draw(self.screen)
            
        # DRAW WINNING CONFETTI
        for c in self.confetti:
            c.draw(self.screen)
            
        # DRAW PLAYER INTERACTIVE CONTROLS
        # Raise Amount Display
        if self.btn_raise_execute.enabled:
            ra_txt = self.font_medium.render(f"Bet/Raise amount: ${self.raise_amount}", True, COLOR_GOLD)
            self.screen.blit(ra_txt, (950, 525))
            
        self.btn_check_call.draw(self.screen, self.font_medium)
        self.btn_fold.draw(self.screen, self.font_medium)
        self.btn_raise_minus.draw(self.screen, self.font_small)
        self.btn_raise_plus.draw(self.screen, self.font_small)
        self.btn_raise_min.draw(self.screen, self.font_small)
        self.btn_raise_allin.draw(self.screen, self.font_small)
        self.btn_raise_execute.draw(self.screen, self.font_medium)
        
        # DRAW RUNNING AI THOUGHTS / GENERAL GAME NOTIFICATION TEXT ON FELT
        if self.game_state not in ["MENU", "GAME_OVER", "SHOWDOWN"]:
            msg = self.ai_status_message
            if not msg:
                if self.whose_turn == 'player':
                    msg = "Your Turn to Act"
                else:
                    msg = "AI is thinking..."
                    
            status_surf = self.font_medium.render(msg, True, COLOR_WHITE)
            self.screen.blit(status_surf, (640 - status_surf.get_width() // 2, 410))
            
        # DRAW STATE OVERLAYS (MENU, SHOWDOWN, GAME_OVER)
        if self.game_state == "MENU":
            # Transparent screen filter
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 200))
            self.screen.blit(overlay, (0, 0))
            
            # Title banner
            title = self.font_large.render("HIGH-STAKES TEXAS HOLD'EM POKER", True, COLOR_GOLD)
            self.screen.blit(title, (WINDOW_WIDTH // 2 - title.get_width() // 2, 220))
            
            desc_1 = self.font_medium.render("Put your skills to the test in classic 1-on-1 heads-up Poker.", True, COLOR_WHITE)
            desc_2 = self.font_medium.render("Blinds: $10 / $20. Win by bankrupting the AI opponent.", True, COLOR_WHITE)
            desc_3 = self.font_small.render("Controls: Use mouse to click betting buttons. Press SPACE to start.", True, COLOR_TEXT_MUTED)
            
            self.screen.blit(desc_1, (WINDOW_WIDTH // 2 - desc_1.get_width() // 2, 290))
            self.screen.blit(desc_2, (WINDOW_WIDTH // 2 - desc_2.get_width() // 2, 330))
            self.screen.blit(desc_3, (WINDOW_WIDTH // 2 - desc_3.get_width() // 2, 380))
            
            self.btn_menu_start.draw(self.screen, self.font_medium)
            
        elif self.game_state == "SHOWDOWN":
            # Draw semi-transparent center banner for results
            banner_rect = pygame.Rect(0, 260, WINDOW_WIDTH, 180)
            pygame.draw.rect(self.screen, (15, 17, 21, 230), banner_rect)
            pygame.draw.rect(self.screen, COLOR_GOLD, banner_rect, width=2)
            
            result_txt = self.font_large.render(self.hand_outcome_text, True, COLOR_GOLD)
            self.screen.blit(result_txt, (WINDOW_WIDTH // 2 - result_txt.get_width() // 2, 290))
            
            sub_txt = self.font_medium.render("Press SPACE or click below for Next Hand", True, COLOR_WHITE)
            self.screen.blit(sub_txt, (WINDOW_WIDTH // 2 - sub_txt.get_width() // 2, 350))
            
            self.btn_next_hand.draw(self.screen, self.font_medium)
            
        elif self.game_state == "GAME_OVER":
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 210))
            self.screen.blit(overlay, (0, 0))
            
            go_title = self.font_large.render("MATCH COMPLETED", True, COLOR_GOLD)
            self.screen.blit(go_title, (WINDOW_WIDTH // 2 - go_title.get_width() // 2, 220))
            
            if self.winner == "player":
                msg = "CONGRATULATIONS! You took all the AI's chips and won the match!"
                color = (46, 204, 113)
            else:
                msg = "BANKRUPT! The AI wiped out your stack. Try again!"
                color = (231, 76, 60)
                
            res_txt = self.font_medium.render(msg, True, color)
            self.screen.blit(res_txt, (WINDOW_WIDTH // 2 - res_txt.get_width() // 2, 290))
            
            self.btn_restart.draw(self.screen, self.font_medium)
            
        pygame.display.flip()

    async def run(self):
        running = True
        while running:
            dt = min(0.1, self.clock.tick(60) / 1000.0)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_SPACE:
                        if self.game_state == "MENU":
                            self.start_new_hand()
                        elif self.game_state == "SHOWDOWN":
                            self.start_new_hand()
                        elif self.game_state == "GAME_OVER":
                            self.reset_game_state(full_reset=True)
                            self.game_state = "MENU"
                
                self.handle_events(event)
                
            self.update(dt)
            self.draw()
            
            await asyncio.sleep(0)
            
        pygame.quit()
        sys.exit()


async def main():
    game = Game()
    await game.run()


if __name__ == "__main__":
    asyncio.run(main())
