import pygame
import math
import random
import sys
import os
import asyncio

# ==========================================
# CONSTANTS & CONFIGURATION
# ==========================================
# Default window dimensions
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720

# NEW: Higher logical rendering dimensions (More pixels, crisp high fidelity)
GAME_WIDTH = 960
GAME_HEIGHT = 540

# Combat Map boundaries (Expanded)
MAP_WIDTH = 1600
MAP_HEIGHT = 1600

# Colors (Hex / RGB)
COLOR_BG = (12, 13, 16) # Moody dark vignette background
COLOR_TEXT = (220, 225, 230)
COLOR_TEXT_MUTED = (110, 115, 125)
COLOR_GREEN = (46, 204, 113)
COLOR_RED = (231, 76, 60)
COLOR_YELLOW = (241, 196, 15)
COLOR_ORANGE = (230, 126, 34)
COLOR_BLUE = (52, 152, 219)
COLOR_GOLD = (255, 215, 0)
COLOR_CRIT = (155, 89, 182) # Amethyst purple for sniper crits

# High Score persistence file
HIGHSCORE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "highscore.txt")

# ==========================================
# SOUND EFFECTS (SAFE FALLBACK FOR WSL)
# ==========================================
pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()

# Setup audio safely
audio_enabled = False
try:
    pygame.mixer.init()
    audio_enabled = True
except Exception as e:
    print(f"[Warning] Sound initialization failed: {e}. Audio is disabled.")

class SoundManager:
    def __init__(self):
        self.enabled = audio_enabled
        self.sounds = {}
        if self.enabled:
            self.generate_procedural_sounds()

    def generate_procedural_sounds(self):
        """Generate retro synth sounds in-memory so no external assets are needed"""
        try:
            # Helper to create sound from wave data
            def create_synth_sound(freq_func, duration=0.1, volume=0.1):
                sample_rate = 44100
                num_samples = int(sample_rate * duration)
                buffer = bytearray(num_samples * 2) # 16-bit mono
                for i in range(num_samples):
                    t = i / sample_rate
                    freq = freq_func(t)
                    val = int(math.sin(2 * math.pi * freq * t) * 32767 * volume)
                    buffer[i*2] = val & 0xff
                    buffer[i*2+1] = (val >> 8) & 0xff
                return pygame.mixer.Sound(buffer=buffer)

            # Shoot: rapid descending pitch
            self.sounds["shoot"] = create_synth_sound(lambda t: 800 - 600 * (t / 0.12), 0.1, 0.05)
            # Shotgun blast: low crackling
            self.sounds["shotgun"] = create_synth_sound(lambda t: random.randint(150, 450), 0.15, 0.08)
            # Sniper blast: deep heavy crash
            self.sounds["sniper"] = create_synth_sound(lambda t: 300 - 250 * (t / 0.35), 0.3, 0.12)
            # Hit: short white noise-like burst
            self.sounds["hit"] = create_synth_sound(lambda t: random.randint(100, 300), 0.05, 0.08)
            # Death: low pitch explosion
            self.sounds["death"] = create_synth_sound(lambda t: 150 - 100 * (t / 0.3) + random.randint(-20, 20), 0.3, 0.15)
            # Reload: quick beep up-down
            self.sounds["reload"] = create_synth_sound(lambda t: 400 + 300 * math.sin(t * 10), 0.15, 0.05)
            # Unlock / Wave Clear / Powerup
            self.sounds["levelup"] = create_synth_sound(lambda t: 300 + 400 * int(t * 10) / 3, 0.3, 0.08)
            # Skill Activate
            self.sounds["skill"] = create_synth_sound(lambda t: 500 + 600 * (t / 0.2), 0.2, 0.08)
        except Exception as e:
            print(f"[Warning] Failed to generate procedural audio: {e}")
            self.enabled = False

    def play(self, name):
        if self.enabled and name in self.sounds:
            self.sounds[name].play()

sounds = SoundManager()

# ==========================================
# PREMIUM 48x48 PROCEDURAL GRAPHICS
# ==========================================
def generate_player_assault_sprite():
    """Generates detailed 48x48 green military-themed Assault soldier sprite"""
    surf = pygame.Surface((48, 48), pygame.SRCALPHA)
    pygame.draw.circle(surf, (15, 25, 10), (24, 24), 16) # Shadow outline
    pygame.draw.circle(surf, (85, 107, 47), (24, 24), 13) # Tactical camo body
    pygame.draw.rect(surf, (45, 60, 30), (17, 15, 14, 18)) # Plated vest
    pygame.draw.circle(surf, (107, 142, 35), (24, 24), 8) # Helmet
    # M4 Carbine details pointing right
    pygame.draw.rect(surf, (30, 30, 35), (24, 21, 20, 5)) # Barrel
    pygame.draw.rect(surf, (15, 15, 20), (16, 18, 9, 9)) # Receiver
    pygame.draw.rect(surf, (60, 60, 65), (26, 16, 6, 3)) # Scope
    # Flesh hands
    pygame.draw.circle(surf, (230, 190, 150), (33, 24), 3)
    pygame.draw.circle(surf, (230, 190, 150), (20, 25), 3)
    return surf

def generate_player_medic_sprite():
    """Generates detailed 48x48 white/light-gray Medic soldier sprite with red cross"""
    surf = pygame.Surface((48, 48), pygame.SRCALPHA)
    pygame.draw.circle(surf, (25, 30, 35), (24, 24), 16)
    pygame.draw.circle(surf, (160, 175, 185), (24, 24), 13) # Light grey vest body
    pygame.draw.rect(surf, (100, 115, 125), (17, 15, 14, 18))
    pygame.draw.circle(surf, (245, 245, 245), (24, 24), 8) # Pure white helmet
    # Medical Red Cross symbol on helmet
    pygame.draw.rect(surf, (231, 76, 60), (23, 19, 3, 10))
    pygame.draw.rect(surf, (231, 76, 60), (19, 23, 10, 3))
    pygame.draw.rect(surf, (245, 245, 245), (22, 22, 5, 5)) # Center clearing
    pygame.draw.line(surf, (231, 76, 60), (24, 19), (24, 28), 2)
    pygame.draw.line(surf, (231, 76, 60), (19, 24), (28, 24), 2)
    # Tactical Submachine gun pointing right
    pygame.draw.rect(surf, (50, 50, 55), (24, 21, 16, 5))
    pygame.draw.rect(surf, (30, 30, 35), (16, 18, 8, 8))
    # Flesh hands
    pygame.draw.circle(surf, (230, 190, 150), (30, 24), 3)
    pygame.draw.circle(surf, (230, 190, 150), (20, 25), 3)
    return surf

def generate_melee_enemy_sprite():
    """Generates a 48x48 crimson-red cybernetic melee charging zombie soldier"""
    surf = pygame.Surface((48, 48), pygame.SRCALPHA)
    pygame.draw.circle(surf, (30, 10, 10), (24, 24), 16) # Shadow
    pygame.draw.circle(surf, (150, 30, 30), (24, 24), 13) # Red flesh armor
    pygame.draw.rect(surf, (80, 20, 20), (17, 15, 14, 18)) # Rib protection
    pygame.draw.circle(surf, (40, 40, 40), (24, 24), 7) # Masked head
    # Cybernetic glowing visor
    pygame.draw.rect(surf, (255, 0, 50), (22, 21, 6, 3))
    # Dual tactical curved arm blades pointing right
    pygame.draw.polygon(surf, (190, 200, 210), [(24, 20), (40, 14), (28, 24)])
    pygame.draw.polygon(surf, (190, 200, 210), [(24, 28), (40, 34), (28, 24)])
    return surf

def generate_ranged_enemy_sprite():
    """Generates a 48x48 orange-themed desert shooter insurgent with a weapon"""
    surf = pygame.Surface((48, 48), pygame.SRCALPHA)
    pygame.draw.circle(surf, (35, 20, 10), (24, 24), 16)
    pygame.draw.circle(surf, (210, 105, 30), (24, 24), 13) # Chocolate brown body
    pygame.draw.rect(surf, (130, 60, 15), (17, 15, 14, 18)) # Leather ammunition belts
    pygame.draw.circle(surf, (70, 70, 75), (24, 24), 7) # Helmet
    # Orange goggles/headband
    pygame.draw.rect(surf, (230, 126, 34), (21, 21, 7, 3))
    # Long carbine rifle with laser sight
    pygame.draw.rect(surf, (30, 30, 30), (24, 21, 22, 4)) # Gun barrel
    pygame.draw.rect(surf, (100, 50, 20), (16, 18, 9, 7)) # Wood stock
    pygame.draw.rect(surf, (231, 76, 60), (32, 19, 3, 2)) # Red laser module
    # Black gloved hands
    pygame.draw.circle(surf, (20, 20, 20), (32, 24), 3)
    return surf

def generate_crosshair_sprite():
    """Generates high-fidelity high-res green tactical crosshair"""
    surf = pygame.Surface((24, 24), pygame.SRCALPHA)
    color = (46, 204, 113, 240)
    # Center dot
    pygame.draw.rect(surf, color, (11, 11, 2, 2))
    # Outer cross lines
    pygame.draw.rect(surf, color, (11, 3, 2, 5))   # N
    pygame.draw.rect(surf, color, (11, 16, 2, 5))  # S
    pygame.draw.rect(surf, color, (3, 11, 5, 2))   # W
    pygame.draw.rect(surf, color, (16, 11, 5, 2))   # E
    return surf

def generate_map_background():
    """Generates massive 1600x1600 combat outpost tilemap background surface"""
    surf = pygame.Surface((MAP_WIDTH, MAP_HEIGHT))
    surf.fill((22, 24, 28)) # Dark concrete base
    
    # Draw dark grid floor tiles
    tile_size = 80
    for x in range(0, MAP_WIDTH, tile_size):
        for y in range(0, MAP_HEIGHT, tile_size):
            # Tile border lines
            pygame.draw.rect(surf, (15, 17, 20), (x, y, tile_size, tile_size), 1)
            # Add random concrete scrapes / rubble
            if random.random() < 0.15:
                crack_color = (12, 13, 15)
                cx = x + random.randint(15, 65)
                cy = y + random.randint(15, 65)
                pygame.draw.line(surf, crack_color, (cx, cy), (cx + random.randint(3, 10), cy + random.randint(-6, 6)), 1)
            if random.random() < 0.08:
                dirt_color = (32, 28, 24)
                pygame.draw.circle(surf, dirt_color, (x + random.randint(8, 72), y + random.randint(8, 72)), random.randint(1, 4))

    # Outer concrete fortress walls
    border_thickness = 24
    pygame.draw.rect(surf, (10, 11, 12), (0, 0, MAP_WIDTH, MAP_HEIGHT), border_thickness)
    
    # Draw military warning hazard stripes
    stripe_gap = 40
    for i in range(0, MAP_WIDTH, stripe_gap):
        # Top boundary
        pygame.draw.polygon(surf, (170, 130, 20), [(i, 3), (i + 15, 3), (i + 6, 21), (i - 9, 21)])
        # Bottom boundary
        pygame.draw.polygon(surf, (170, 130, 20), [(i, MAP_HEIGHT - 21), (i + 15, MAP_HEIGHT - 21), (i + 6, MAP_HEIGHT - 3), (i - 9, MAP_HEIGHT - 3)])
    for i in range(0, MAP_HEIGHT, stripe_gap):
        # Left boundary
        pygame.draw.polygon(surf, (170, 130, 20), [(3, i), (3, i + 15), (21, i + 6), (21, i - 9)])
        # Right boundary
        pygame.draw.polygon(surf, (170, 130, 20), [(MAP_WIDTH - 21, i), (MAP_WIDTH - 21, i + 15), (MAP_WIDTH - 3, i + 6), (MAP_WIDTH - 3, i - 9)])
        
    return surf

# Pre-generate core game assets
SPRITE_PLAYER_ASSAULT = generate_player_assault_sprite()
SPRITE_PLAYER_MEDIC = generate_player_medic_sprite()
SPRITE_MELEE_ENEMY = generate_melee_enemy_sprite()
SPRITE_RANGED_ENEMY = generate_ranged_enemy_sprite()
SPRITE_CROSSHAIR = generate_crosshair_sprite()
MAP_BACKGROUND = generate_map_background()

# ==========================================
# WEAPONS SPECS (SURVIVAL LOADOUT)
# ==========================================
WEAPONS = {
    "Assault Rifle": {
        "name": "M4 Carbine",
        "fire_rate": 0.12,
        "ammo_capacity": 30,
        "reload_time": 1.3,
        "bullet_speed": 520,
        "damage": 35,
        "spread": 0.05,
        "burst_count": 1,
        "piercing": False,
        "sound": "shoot",
        "color": (75, 85, 95)
    },
    "Tactical Shotgun": {
        "name": "Remington 870",
        "fire_rate": 0.65,
        "ammo_capacity": 8,
        "reload_time": 1.8,
        "bullet_speed": 450,
        "damage": 22, # per pellet
        "spread": 0.22,
        "burst_count": 5, # Fires 5 pellets in a fan!
        "piercing": False,
        "sound": "shotgun",
        "color": (110, 110, 95)
    },
    "Sniper Rifle": {
        "name": "Barrett .50 Cal",
        "fire_rate": 1.1,
        "ammo_capacity": 5,
        "reload_time": 2.2,
        "bullet_speed": 750,
        "damage": 150, # Massive one-shot hit
        "spread": 0.0,
        "burst_count": 1,
        "piercing": True, # Traverses multiple hostiles!
        "sound": "sniper",
        "color": (120, 140, 150)
    },
    "Tactical Pistol": {
        "name": "Glock-19",
        "fire_rate": 0.25,
        "ammo_capacity": 12,
        "reload_time": 0.9,
        "bullet_speed": 480,
        "damage": 40,
        "spread": 0.02,
        "burst_count": 1,
        "piercing": False,
        "sound": "shoot",
        "color": (160, 140, 110)
    }
}

# ==========================================
# BOUNCING POPUP DAMAGE INDICATORS (20 Mins style)
# ==========================================
class DamageNumber:
    """A floating, bouncing physics damage number popup"""
    def __init__(self, x, y, text, color=(255, 230, 100)):
        self.pos = pygame.math.Vector2(x, y)
        self.text = text
        self.color = color
        # Physics arc trajectory: burst up and expand sideways
        self.vel = pygame.math.Vector2(random.uniform(-40, 40), -120)
        self.life = 0.65  # Quick transient lifespan
        self.max_life = 0.65

    def update(self, dt):
        self.pos += self.vel * dt
        # Gravity accelerates downwards creating a bounce arc
        self.vel.y += 240 * dt
        self.life -= dt

    def draw(self, surface, camera, font):
        if self.life <= 0:
            return
        # Calculate fade out ratio
        alpha = int(255 * (self.life / self.max_life))
        rendered = font.render(self.text, True, self.color)
        
        # Draw translucent faded surfaces
        temp_surf = rendered.convert_alpha()
        temp_surf.fill((255, 255, 255, alpha), special_flags=pygame.BLEND_RGBA_MULT)
        
        screen_pos = self.pos - camera
        surface.blit(temp_surf, (screen_pos.x - temp_surf.get_width() // 2, screen_pos.y - temp_surf.get_height() // 2))


# ==========================================
# LOOT DROP CRATE CLASS
# ==========================================
class WeaponCrate:
    """Blown-off crate containing fresh weapon lockpick items"""
    def __init__(self, x, y, weapon_type):
        self.pos = pygame.math.Vector2(x, y)
        self.weapon_type = weapon_type
        self.radius = 12.0
        self.bob_timer = random.uniform(0, 100) # Floating math wave offsets
        self.color = WEAPONS[weapon_type]["color"]

    def update(self, dt):
        self.bob_timer += 6.0 * dt

    def draw(self, surface, camera, font):
        # Sine wave bobbing vertical offsets
        bob_y = math.sin(self.bob_timer) * 4.0
        screen_pos = self.pos - camera + pygame.math.Vector2(0, bob_y)
        
        # Draw crate square box outline (military supply chest)
        rect = pygame.Rect(screen_pos.x - 10, screen_pos.y - 10, 20, 20)
        pygame.draw.rect(surface, (15, 15, 18), (rect.x - 2, rect.y - 2, 24, 24)) # Outline shadow
        pygame.draw.rect(surface, self.color, rect)
        pygame.draw.rect(surface, COLOR_GOLD, rect, 2) # Golden lining frame
        
        # Draw dynamic medical/supplies tactical tape crosses
        pygame.draw.line(surface, COLOR_GOLD, (rect.x + 3, rect.y + 10), (rect.right - 3, rect.y + 10), 2)
        pygame.draw.line(surface, COLOR_GOLD, (rect.x + 10, rect.y + 3), (rect.x + 10, rect.bottom - 3), 2)

        # Overhead text descriptor
        text_label = font.render(self.weapon_type.upper(), True, COLOR_GOLD)
        surface.blit(text_label, (screen_pos.x - text_label.get_width() // 2, screen_pos.y - 24))


# ==========================================
# PARTICLE SYSTEMS (JUICE)
# ==========================================
class Particle:
    """Represents a chunky retro particle for blood, sparks, or smoke"""
    def __init__(self, x, y, vx, vy, color, size, life, is_blood=False):
        self.pos = pygame.math.Vector2(x, y)
        self.vel = pygame.math.Vector2(vx, vy)
        self.color = color
        self.size = size
        self.life = life
        self.max_life = life
        self.is_blood = is_blood

    def update(self, dt, bg_surface):
        self.pos += self.vel * dt
        # Friction/drag (particles slow down over time)
        self.vel *= (1.0 - 2.5 * dt)
        self.life -= dt
        
        # When blood particle dies, paint a permanent bloodstain on the map floor!
        if self.life <= 0 and self.is_blood:
            stain_radius = random.randint(1, 4)
            stain_color = (
                max(50, min(self.color[0] + random.randint(-15, 15), 180)),
                max(4, min(self.color[1] + random.randint(-3, 3), 15)),
                max(4, min(self.color[2] + random.randint(-3, 3), 15))
            )
            pygame.draw.circle(bg_surface, stain_color, (int(self.pos.x), int(self.pos.y)), stain_radius)

    def draw(self, surface, camera):
        if self.life <= 0:
            return
        # Calculate dynamic size based on remaining life ratio (shrink as it decays)
        current_size = max(1.0, self.size * (self.life / self.max_life))
        screen_pos = self.pos - camera
        rect = pygame.Rect(
            screen_pos.x - current_size / 2, 
            screen_pos.y - current_size / 2, 
            current_size, 
            current_size
        )
        pygame.draw.rect(surface, self.color, rect)


class EffectManager:
    def __init__(self):
        self.particles = []

    def spawn_blood_splatter(self, x, y, count=12):
        """Creates a burst of red blood particles when hostiles are shot"""
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(40, 160)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            life = random.uniform(0.15, 0.45)
            # Tactical crimson to dark red shade
            r = random.randint(130, 200)
            g = random.randint(10, 25)
            b = random.randint(10, 25)
            self.particles.append(Particle(x, y, vx, vy, (r, g, b), random.uniform(3.0, 5.0), life, is_blood=True))

    def spawn_wall_sparks(self, x, y, count=5):
        """Creates bullet ricochet sparks off walls"""
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(60, 200)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            life = random.uniform(0.1, 0.25)
            # High intensity amber/yellow spark color
            color = (255, random.randint(150, 230), random.randint(20, 60))
            self.particles.append(Particle(x, y, vx, vy, color, random.uniform(1.5, 3.5), life, is_blood=False))

    def spawn_muzzle_flash_particles(self, x, y, angle_rad, count=4):
        """Spawns directional gun muzzle exhaust gas"""
        for _ in range(count):
            spread_angle = angle_rad + random.uniform(-0.3, 0.3)
            speed = random.uniform(80, 150)
            vx = math.cos(spread_angle) * speed
            vy = math.sin(spread_angle) * speed
            life = random.uniform(0.05, 0.12)
            color = (255, random.randint(180, 255), 100)
            self.particles.append(Particle(x, y, vx, vy, color, random.uniform(2.0, 4.0), life, is_blood=False))

    def spawn_powerup_sparks(self, x, y, color, count=22):
        """Spawns a dramatic expanding ring of color sparks on skill trigger"""
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(60, 140)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            life = random.uniform(0.25, 0.55)
            self.particles.append(Particle(x, y, vx, vy, color, random.uniform(3.0, 6.0), life, is_blood=False))

    def spawn_aura_spark(self, x, y, color):
        """Spawns a single rising particle to signify an active stat buff"""
        vx = random.uniform(-10, 10)
        vy = random.uniform(-25, -60) # float upwards on screen
        life = random.uniform(0.35, 0.65)
        self.particles.append(Particle(x + random.randint(-12, 12), y + random.randint(-12, 12), vx, vy, color, random.uniform(1.5, 3.5), life, is_blood=False))

    def update_and_draw(self, dt, logical_surface, camera, bg_surface):
        # Update and clean up dead particles
        alive_particles = []
        for p in self.particles:
            p.update(dt, bg_surface)
            if p.life > 0:
                p.draw(logical_surface, camera)
                alive_particles.append(p)
        self.particles = alive_particles


# ==========================================
# PROJECTILE CLASS
# ==========================================
class Bullet:
    """Represents a flying projectile fired from a weapons model"""
    def __init__(self, x, y, angle_rad, speed, damage, piercing=False, is_player_bullet=True):
        self.pos = pygame.math.Vector2(x, y)
        self.speed = speed
        self.velocity = pygame.math.Vector2(math.cos(angle_rad), math.sin(angle_rad)) * self.speed
        self.radius = 2.0 if is_player_bullet else 3.5 # Hostile orbs are thicker/larger
        self.is_player = is_player_bullet
        self.damage = damage
        self.piercing = piercing
        self.life = 2.0  # Seconds of active range
        
        # Piercing track (remembers who it hit so it doesn't double-hit the same target)
        self.hit_targets = []

    def update(self, dt):
        self.pos += self.velocity * dt
        self.life -= dt

    def draw(self, surface, camera):
        start_pos = self.pos - camera
        
        if self.is_player:
            # Player glowing yellow tracer trails
            trail_len = 12.0
            vel_norm = self.velocity.normalize() if self.velocity.length() > 0 else pygame.math.Vector2(0, 0)
            end_pos = start_pos - vel_norm * trail_len
            pygame.draw.line(surface, (255, 255, 220), start_pos, end_pos, 2)
            pygame.draw.circle(surface, COLOR_YELLOW, start_pos, self.radius)
        else:
            # Hostile neon red plasma energy balls
            pygame.draw.circle(surface, (255, 100, 100), start_pos, self.radius + 1.5)
            pygame.draw.circle(surface, COLOR_RED, start_pos, self.radius)


# ==========================================
# BASE CHARACTER CLASS (PLAYER)
# ==========================================
class Player:
    """Base Character Class representing the controllable user soldier"""
    def __init__(self, x, y):
        self.pos = pygame.math.Vector2(x, y)
        self.speed = 130.0 # Pixels per second (WASD)
        self.radius = 12.0
        self.angle = 0.0 # In degrees, aiming direction
        
        # 20 Mins walk bobbing timers
        self.walk_timer = 0.0
        self.bob_y = 0.0

        # Common Stats
        self.max_health = 100.0
        self.health = 100.0
        self.score = 0
        
        # Weapon Inventories System
        self.weapons = {k: v["ammo_capacity"] for k, v in WEAPONS.items()} # Tracks active magazine ammo levels
        self.unlocked_weapons = ["Tactical Pistol", "Assault Rifle"] # Starts with two weapons
        self.current_weapon_name = "Assault Rifle"
        
        self.shoot_cooldown = 0.0
        self.reloading = False
        self.reload_timer = 0.0
        
        # Cooldown Systems
        self.skill_cooldown_max = 10.0
        self.skill_cooldown = 0.0
        self.class_name = "Recruit"
        self.skill_name = "None"
        
        # Overlays
        self.muzzle_flash_timer = 0.0
        self.damage_flash_timer = 0.0

    @property
    def current_weapon_spec(self):
        return WEAPONS[self.current_weapon_name]

    def take_damage(self, amount):
        if self.health > 0:
            self.health -= amount
            self.damage_flash_timer = 0.12 # Red flash on HUD
            sounds.play("hit")
            if self.health <= 0:
                self.health = 0
                sounds.play("death")

    def start_reload(self):
        spec = self.current_weapon_spec
        cur_ammo = self.weapons[self.current_weapon_name]
        if not self.reloading and cur_ammo < spec["ammo_capacity"]:
            self.reloading = True
            self.reload_timer = spec["reload_time"]
            sounds.play("reload")

    def cycle_weapon(self, direction):
        """Rotates index of weapon inventory scroll"""
        if len(self.unlocked_weapons) <= 1:
            return
        current_idx = self.unlocked_weapons.index(self.current_weapon_name)
        next_idx = (current_idx + direction) % len(self.unlocked_weapons)
        self.current_weapon_name = self.unlocked_weapons[next_idx]
        
        # Cancel any active reload upon changing gun models
        self.reloading = False
        self.reload_timer = 0.0
        sounds.play("reload")

    def activate_skill(self, effect_mgr):
        """To be overridden by subclasses"""
        pass

    def update(self, dt, mouse_world_pos, bullet_list, effect_mgr):
        spec = self.current_weapon_spec
        
        # Update cooldowns
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= dt
        if self.muzzle_flash_timer > 0:
            self.muzzle_flash_timer -= dt
        if self.damage_flash_timer > 0:
            self.damage_flash_timer -= dt
        if self.skill_cooldown > 0:
            self.skill_cooldown -= dt

        # Handle active weapon reloading timers
        if self.reloading:
            self.reload_timer -= dt
            if self.reload_timer <= 0:
                self.weapons[self.current_weapon_name] = spec["ammo_capacity"]
                self.reloading = False

        # ----------------------------------
        # 8-Way Movement Handling (WASD)
        # ----------------------------------
        dx = 0
        dy = 0
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dy -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy += 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx += 1

        move_vec = pygame.math.Vector2(dx, dy)
        moving = move_vec.length_squared() > 0
        if moving:
            move_vec = move_vec.normalize()
            self.pos += move_vec * self.speed * dt
            # Advance bobbing walks animation wave
            self.walk_timer += 14.0 * dt
            self.bob_y = math.sin(self.walk_timer) * 3.5 # swaying bob height
        else:
            # Slowly decay bobbing animation back to zero if stationary
            self.bob_y *= (1.0 - 15.0 * dt)
            self.walk_timer = 0.0

        # Enforce tactical compound borders limits
        wall_offset = 24.0
        self.pos.x = max(wall_offset, min(self.pos.x, MAP_WIDTH - wall_offset))
        self.pos.y = max(wall_offset, min(self.pos.y, MAP_HEIGHT - wall_offset))

        # ----------------------------------
        # Rotation & Aiming towards Cursor
        # ----------------------------------
        aim_direction = mouse_world_pos - self.pos
        if aim_direction.length_squared() > 0:
            angle_rad = math.atan2(aim_direction.y, aim_direction.x)
            self.angle = math.degrees(angle_rad)
        else:
            angle_rad = 0.0

        # ----------------------------------
        # Shooting Weapons Implementation
        # ----------------------------------
        mouse_pressed = pygame.mouse.get_pressed()
        if mouse_pressed[0]: # Left click fires active gun model
            if not self.reloading:
                active_ammo = self.weapons[self.current_weapon_name]
                if active_ammo > 0:
                    if self.shoot_cooldown <= 0:
                        # Fires a single bullet or multi-projectile blast (e.g. shotgun)
                        for _ in range(spec["burst_count"]):
                            # Apply unique weapon spreads accuracy ratios
                            spread = random.uniform(-spec["spread"], spec["spread"])
                            final_angle = angle_rad + spread
                            
                            # Barrel spawn offset coordinates
                            barrel_offset = 24.0
                            bullet_spawn_x = self.pos.x + math.cos(angle_rad) * barrel_offset
                            bullet_spawn_y = self.pos.y + math.sin(angle_rad) * barrel_offset
                            
                            bullet_list.append(Bullet(
                                bullet_spawn_x, bullet_spawn_y, final_angle,
                                spec["bullet_speed"], spec["damage"],
                                piercing=spec["piercing"], is_player_bullet=True
                            ))
                            
                        # Spend ammunition and trigger recoil cooldowns
                        self.weapons[self.current_weapon_name] -= 1
                        self.shoot_cooldown = self.shoot_rate if self.class_name == "Assault" and self.skill_active else spec["fire_rate"]
                        self.muzzle_flash_timer = 0.05
                        sounds.play(spec["sound"])
                        
                        # Spark flares
                        effect_mgr.spawn_muzzle_flash_particles(self.pos.x + math.cos(angle_rad) * barrel_offset, self.pos.y + math.sin(angle_rad) * barrel_offset, angle_rad)
                else:
                    self.start_reload()

    def draw(self, surface, camera):
        # Rotate pre-rendered soldier sprite based on aiming angle
        rotated_sprite = pygame.transform.rotate(self.sprite, -self.angle)
        
        # Offset Y drawing position using walking sine wave bobbing logic (20 Mins style)
        screen_y = self.pos.y - camera.y + self.bob_y
        rect = rotated_sprite.get_rect(center=(self.pos.x - camera.x, screen_y))
        
        # Flash visual feedback indicators on damage impact
        if self.damage_flash_timer > 0:
            pygame.draw.circle(surface, COLOR_RED, (int(self.pos.x - camera.x), int(screen_y)), int(self.radius + 1))
            
        surface.blit(rotated_sprite, rect.topleft)

        # Draw active reloading progress meters overhead
        if self.reloading:
            percent = max(0.0, self.reload_timer / self.current_weapon_spec["reload_time"])
            progress_width = 32
            bar_x = int(self.pos.x - camera.x - progress_width / 2)
            bar_y = int(screen_y - 24)
            
            # Progress frame
            pygame.draw.rect(surface, (0, 0, 0), (bar_x, bar_y, progress_width, 3))
            pygame.draw.rect(surface, COLOR_YELLOW, (bar_x, bar_y, int(progress_width * (1.0 - percent)), 3))


# ==========================================
# PLAYABLE SUBCLASSES
# ==========================================
class Assault(Player):
    """Heavy offense soldier with temporal hyper fire rates"""
    def __init__(self, x, y):
        super().__init__(x, y)
        self.class_name = "Assault"
        self.sprite = SPRITE_PLAYER_ASSAULT
        self.skill_name = "Rapid Fire"
        self.skill_cooldown_max = 12.0 # 12s cooldown
        
        # Active Skill parameters
        self.skill_active = False
        self.skill_duration_max = 4.0 # 4s buff duration
        self.skill_timer = 0.0

    def activate_skill(self, effect_mgr):
        if self.skill_cooldown <= 0 and not self.skill_active:
            self.skill_active = True
            self.skill_timer = self.skill_duration_max
            # Substantially cuts firing rate intervals by half!
            self.shoot_rate = 0.06
            sounds.play("skill")
            
            # Spawn golden aura visual sparks around soldier
            effect_mgr.spawn_powerup_sparks(self.pos.x, self.pos.y, COLOR_GOLD, count=24)

    def update(self, dt, mouse_world_pos, bullet_list, effect_mgr):
        if self.skill_active:
            self.skill_timer -= dt
            
            # Spawn golden aura float sparks
            if random.random() < 0.35:
                effect_mgr.spawn_aura_spark(self.pos.x, self.pos.y, COLOR_GOLD)
                
            if self.skill_timer <= 0:
                self.skill_active = False
                self.skill_cooldown = self.skill_cooldown_max
                
        super().update(dt, mouse_world_pos, bullet_list, effect_mgr)


class Medic(Player):
    """Support defensive medic capable of instant health injection"""
    def __init__(self, x, y):
        super().__init__(x, y)
        self.class_name = "Medic"
        self.sprite = SPRITE_PLAYER_MEDIC
        self.skill_name = "Self Heal"
        self.skill_cooldown_max = 8.0 # 8s cooldown

    def activate_skill(self, effect_mgr):
        if self.skill_cooldown <= 0 and self.health < self.max_health:
            heal_amount = 40.0
            self.health = min(self.max_health, self.health + heal_amount)
            self.skill_cooldown = self.skill_cooldown_max
            sounds.play("skill")
            
            # Spawn healing green sparks energy rings
            effect_mgr.spawn_powerup_sparks(self.pos.x, self.pos.y, COLOR_GREEN, count=24)


# ==========================================
# GRID-BASED INVENTORY SYSTEM (TARKOVOV)
# ==========================================
class Item:
    """An inventory piece occupying width x height block shapes in a 2D grid"""
    def __init__(self, name, width, height, color):
        self.name = name
        self.width = width
        self.height = height
        self.color = color
        self.grid_x = None
        self.grid_y = None


class Inventory:
    """2D Grid layout containing military survival gear"""
    def __init__(self, cols=10, rows=6):
        self.cols = cols
        self.rows = rows
        self.grid = [[None for _ in range(cols)] for _ in range(rows)]
        self.items = []

    def can_fit(self, item, x, y, ignore_item=None):
        if x < 0 or y < 0 or (x + item.width) > self.cols or (y + item.height) > self.rows:
            return False
        
        for r in range(y, y + item.height):
            for c in range(x, x + item.width):
                cell_item = self.grid[r][c]
                if cell_item is not None and cell_item is not ignore_item:
                    return False
        return True

    def add_item(self, item, x, y):
        if self.can_fit(item, x, y):
            item.grid_x = x
            item.grid_y = y
            for r in range(y, y + item.height):
                for c in range(x, x + item.width):
                    self.grid[r][c] = item
            if item not in self.items:
                self.items.append(item)
            return True
        return False

    def remove_item(self, item):
        if item.grid_x is not None and item.grid_y is not None:
            for r in range(item.grid_y, item.grid_y + item.height):
                for c in range(item.grid_x, item.grid_x + item.width):
                    self.grid[r][c] = None
            item.grid_x = None
            item.grid_y = None


# ==========================================
# ENEMY CLASS (WITH SHOTER AND MELEE CLASSIFICATIONS)
# ==========================================
class Enemy:
    """Rushing zombie or defensive shooter insurgent (20 Mins walk style)"""
    def __init__(self, x, y, wave_number, enemy_type="melee"):
        self.pos = pygame.math.Vector2(x, y)
        self.type = enemy_type # "melee" or "ranged"
        
        # Distinct parameters depending on type
        if self.type == "melee":
            self.sprite = SPRITE_MELEE_ENEMY
            base_speed = random.uniform(65.0, 85.0)
            self.radius = 11.0
            self.max_health = 100.0 + (wave_number - 1) * 10.0
            self.contact_damage = 35.0 # Damage/sec in contact
        else:
            self.sprite = SPRITE_RANGED_ENEMY
            base_speed = random.uniform(45.0, 60.0) # Shooters travel slower
            self.radius = 12.0
            self.max_health = 80.0 + (wave_number - 1) * 8.0
            self.contact_damage = 15.0
            # Shooter weapons parameters
            self.fire_rate = max(1.0, 2.0 - wave_number * 0.05) # shoots quicker as waves advance
            self.fire_cooldown = random.uniform(0.5, self.fire_rate)
            self.shoot_range = 220.0
            self.bullet_speed = 180.0
            self.bullet_damage = 15.0

        self.speed = min(120.0, base_speed + (wave_number * 1.5))
        self.health = self.max_health
        self.angle = 0.0
        self.flash_timer = 0.0
        
        # Bobbing walking sway timers
        self.walk_timer = random.uniform(0, 100)
        self.bob_y = 0.0

    def take_damage(self, amount, effect_mgr):
        self.health -= amount
        self.flash_timer = 0.08
        sounds.play("hit")
        effect_mgr.spawn_blood_splatter(self.pos.x, self.pos.y, count=8)

    def update(self, dt, player, other_enemies, bullet_list, effect_mgr):
        if self.flash_timer > 0:
            self.flash_timer -= dt

        # Vector leading directly to targeted player position
        dir_to_player = player.pos - self.pos
        dist = dir_to_player.length()

        if dist > 0:
            dir_norm = dir_to_player.normalize()
            self.angle = math.degrees(math.atan2(dir_to_player.y, dir_to_player.x))

            # Bobbing walk animation values
            self.walk_timer += 12.0 * dt
            self.bob_y = math.sin(self.walk_timer) * 2.5

            # ----------------------------------
            # Mutual Steering Separation
            # ----------------------------------
            sep_vector = pygame.math.Vector2(0, 0)
            for other in other_enemies:
                if other is not self:
                    gap = self.pos.distance_to(other.pos)
                    overlap_threshold = 24.0
                    if gap < overlap_threshold and gap > 0:
                        push_force = (overlap_threshold - gap) / overlap_threshold
                        sep_vector += (self.pos - other.pos).normalize() * push_force * 1.8

            # RANGED SHOOTER BEHAVIOR ALGORITHM
            if self.type == "ranged":
                # Shoot at player if within combat limits
                self.fire_cooldown -= dt
                if dist <= self.shoot_range and self.fire_cooldown <= 0:
                    # Fire red orb bullet at player
                    aim_angle = math.atan2(dir_to_player.y, dir_to_player.x)
                    bullet_list.append(Bullet(
                        self.pos.x + math.cos(aim_angle) * 16.0,
                        self.pos.y + math.sin(aim_angle) * 16.0,
                        aim_angle, self.bullet_speed, self.bullet_damage,
                        piercing=False, is_player_bullet=False
                    ))
                    self.fire_cooldown = self.fire_rate
                    sounds.play("shoot") # basic shoot trigger
                
                # Stand ground or retreat slightly if player is too close
                if dist < 170.0:
                    # Back off slowly
                    final_heading = (-dir_norm + sep_vector).normalize()
                    self.pos += final_heading * (self.speed * 0.6) * dt
                elif dist > self.shoot_range - 20.0:
                    # Move closer
                    final_heading = (dir_norm + sep_vector).normalize()
                    self.pos += final_heading * self.speed * dt
                else:
                    # Maintain positions, only apply minor flocking adjustments
                    if sep_vector.length_squared() > 0:
                        self.pos += sep_vector.normalize() * (self.speed * 0.4) * dt
            
            # STANDARD CHARGER MELEE BEHAVIOR
            else:
                final_heading = (dir_norm + sep_vector).normalize()
                self.pos += final_heading * self.speed * dt

            # Enforce map bounds limit
            wall_offset = 24.0
            self.pos.x = max(wall_offset, min(self.pos.x, MAP_WIDTH - wall_offset))
            self.pos.y = max(wall_offset, min(self.pos.y, MAP_HEIGHT - wall_offset))

            # Melee damage collision with player (deal damage over time)
            if dist < (self.radius + player.radius):
                player.take_damage(self.contact_damage * dt)

    def draw(self, surface, camera):
        # Apply walk bobbing vertical sway to final rendering
        screen_y = self.pos.y - camera.y + self.bob_y
        rotated_sprite = pygame.transform.rotate(self.sprite, -self.angle)
        rect = rotated_sprite.get_rect(center=(self.pos.x - camera.x, screen_y))
        
        surface.blit(rotated_sprite, rect.topleft)

        # White impact outline flash overlay
        if self.flash_timer > 0:
            pygame.draw.circle(surface, (255, 255, 255), (int(self.pos.x - camera.x), int(screen_y)), int(self.radius - 2))


# ==========================================
# MAIN GAME COORDINATOR
# ==========================================
class Game:
    def __init__(self):
        # Set up resizable hardware monitor display
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("SpecOps: Tactical Outpost (Pixel Shooter)")
        
        # High resolution logical scratchpad surface
        self.logical_surf = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))
        
        # Load local high score safely
        self.high_score = self.load_high_score()
        
        self.clock = pygame.time.Clock()
        self.font_main = pygame.font.Font(None, 24)
        self.font_large = pygame.font.Font(None, 40)
        self.font_hud = pygame.font.Font(None, 18)
        self.font_tiny = pygame.font.Font(None, 12)
        self.font_damage = pygame.font.Font(None, 16) # Smaller bouncy popups

        # Active player class type defaults
        self.selected_class_type = "Assault"

        # Grid Inventory state variables
        self.inventory_open = False
        self.dragged_item = None
        self.drag_offset_x = 0
        self.drag_offset_y = 0
        self.last_valid_grid_x = 0
        self.last_valid_grid_y = 0
        self.slot_size = 24 # Adjusted visual slot scale

        # HUD feedback popups
        self.hud_popup_timer = 0.0
        self.hud_popup_msg = ""

        # Game states: 'START', 'PLAYING', 'GAMEOVER'
        self.state = 'START'
        self.reset_game_state()

    def load_high_score(self):
        try:
            if os.path.exists(HIGHSCORE_FILE):
                with open(HIGHSCORE_FILE, 'r') as f:
                    return int(f.read().strip())
        except Exception:
            pass
        return 0

    def save_high_score(self):
        try:
            with open(HIGHSCORE_FILE, 'w') as f:
                f.write(str(self.high_score))
        except Exception:
            pass

    def reset_game_state(self):
        """Reset player class, inventory, and setup combat parameters"""
        spawn_x, spawn_y = MAP_WIDTH // 2, MAP_HEIGHT // 2
        
        # Instantiate correct chosen subclass
        if self.selected_class_type == "Assault":
            self.player = Assault(spawn_x, spawn_y)
        else:
            self.player = Medic(spawn_x, spawn_y)
            
        self.bullets = []
        self.enemies = []
        self.effect_mgr = EffectManager()
        self.damage_popups = [] # Floating bouncy numbers list
        self.dropped_crates = [] # Drops on combat floor
        
        # Instantiate 10x6 grid backpack inventory
        self.inventory = Inventory(10, 6)
        self.inventory_open = False
        self.dragged_item = None
        self.populate_default_inventory()
        
        # Reset dynamic persistent ground layer (wipes old bloodstains)
        self.persistent_ground = MAP_BACKGROUND.copy()
        
        # Wave tracking system
        self.wave_number = 0
        self.enemies_spawned_count = 0
        self.enemies_remaining_to_spawn = 0
        self.spawn_timer = 0.0
        self.spawn_interval = 1.2
        
        # Screen shake intensity
        self.screen_shake_intensity = 0.0
        
        # Post-wave Intermission counter
        self.intermission_active = False
        self.intermission_timer = 0.0
        
        # HUD triggers
        self.hud_popup_timer = 0.0
        self.hud_popup_msg = ""
        
        # Start immediately at Wave 1
        self.advance_to_next_wave()

    def show_hud_popup(self, text, duration=2.5):
        self.hud_popup_msg = text
        self.hud_popup_timer = duration

    def populate_default_inventory(self):
        """Fills player grid inventory pack with some military items of distinct sizes"""
        self.inventory.add_item(Item("M4 Carbine", 3, 2, (75, 85, 95)), 0, 0)
        self.inventory.add_item(Item("Glock-19", 2, 1, (120, 110, 95)), 4, 0)
        self.inventory.add_item(Item("IFAK Medkit", 2, 2, (180, 40, 40)), 0, 3)
        self.inventory.add_item(Item("HE Grenade", 1, 1, (40, 80, 50)), 3, 3)
        self.inventory.add_item(Item("5.56 Ammo", 2, 1, (190, 150, 40)), 7, 0)
        self.inventory.add_item(Item("Camo Vest", 3, 3, (65, 80, 55)), 4, 2)

    def swap_player_class(self):
        """Swaps player class dynamically during gameplay for testing! (Saves core progress stats)"""
        current_x, current_y = self.player.pos.x, self.player.pos.y
        current_health = self.player.health
        current_score = self.player.score
        unlocked = self.player.unlocked_weapons.copy()
        cur_weapon = self.player.current_weapon_name
        weapons_ammo = self.player.weapons.copy()
        
        # Alternate class type
        if self.player.class_name == "Assault":
            self.selected_class_type = "Medic"
            self.player = Medic(current_x, current_y)
        else:
            self.selected_class_type = "Assault"
            self.player = Assault(current_x, current_y)
            
        # Re-apply matching stats
        self.player.health = current_health
        self.player.score = current_score
        self.player.unlocked_weapons = unlocked
        self.player.current_weapon_name = cur_weapon
        self.player.weapons = weapons_ammo
        
        sounds.play("levelup")
        self.effect_mgr.spawn_powerup_sparks(current_x, current_y, COLOR_BLUE, count=15)
        self.show_hud_popup(f"CLASS SWAPPED TO {self.player.class_name.upper()}!")

    def advance_to_next_wave(self):
        """Starts the next wave difficulty setting"""
        self.wave_number += 1
        # E.g., Wave 1: 7 enemies, Wave 2: 10, Wave 3: 13
        self.enemies_remaining_to_spawn = 4 + (self.wave_number * 3) 
        self.enemies_spawned_count = 0
        self.spawn_timer = 0.5
        self.intermission_active = False
        sounds.play("levelup")
        
        # Wave clear bonus: heal player slightly as tactical supplies arrive
        if self.wave_number > 1:
            self.player.health = min(self.player.max_health, self.player.health + 20)
            # Full resupply ammo for all weapons
            for k in self.player.weapons:
                self.player.weapons[k] = WEAPONS[k]["ammo_capacity"]
            self.show_hud_popup(f"WAVE {self.wave_number} DEPLOYED - GEAR RESUPPLIED!")

    def spawn_wave_hostile(self):
        """Spawns an enemy outside of camera view boundaries but inside combat outpost"""
        cam_x = max(0, min(self.player.pos.x - GAME_WIDTH / 2, MAP_WIDTH - GAME_WIDTH))
        cam_y = max(0, min(self.player.pos.y - GAME_HEIGHT / 2, MAP_HEIGHT - GAME_HEIGHT))
        
        # Try up to 50 times to locate a suitable off-screen coordinate inside walls
        for _ in range(50):
            rx = random.uniform(40, MAP_WIDTH - 40)
            ry = random.uniform(40, MAP_HEIGHT - 40)
            
            # Ensure spawning outside logical camera viewport + 40px padding
            padding = 40.0
            on_screen = (cam_x - padding <= rx <= cam_x + GAME_WIDTH + padding) and \
                        (cam_y - padding <= ry <= cam_y + GAME_HEIGHT + padding)
            
            if not on_screen:
                # 35% chance to spawn a Ranged Shooter insurgent, 65% standard Melee Charger
                enemy_type = "ranged" if random.random() < 0.35 else "melee"
                self.enemies.append(Enemy(rx, ry, self.wave_number, enemy_type))
                self.enemies_spawned_count += 1
                break

    def get_viewport_rect(self):
        """Computes a centered letterbox destination rect maintaining 16:9 aspect ratio"""
        screen_w, screen_h = self.screen.get_size()
        target_aspect = GAME_WIDTH / GAME_HEIGHT # 1.777 (16:9)
        screen_aspect = screen_w / screen_h
        
        if screen_aspect > target_aspect:
            # Letterbox margins on left & right sides
            new_h = screen_h
            new_w = int(new_h * target_aspect)
            x_offset = (screen_w - new_w) // 2
            y_offset = 0
        else:
            # Letterbox margins on top & bottom sides
            new_w = screen_w
            new_h = int(new_w / target_aspect)
            x_offset = 0
            y_offset = (screen_h - new_h) // 2
            
        return pygame.Rect(x_offset, y_offset, new_w, new_h)

    def get_logical_mouse_pos(self):
        """Translates system cursor coords to matched low-res logical space boundaries"""
        mx, my = pygame.mouse.get_pos()
        viewport = self.get_viewport_rect()
        
        # Subtract viewport screen offset, then multiply by logical aspect multiplier ratios
        rx = (mx - viewport.x) / viewport.width * GAME_WIDTH
        ry = (my - viewport.y) / viewport.height * GAME_HEIGHT
        return pygame.math.Vector2(rx, ry)

    def handle_inventory_clicks(self, event):
        """Processes grid pickup and dropping triggers"""
        logical_mouse = self.get_logical_mouse_pos()
        logical_mx, logical_my = logical_mouse.x, logical_mouse.y
        
        # Calculate grid boundary layout anchor positions
        grid_width = self.inventory.cols * self.slot_size
        grid_height = self.inventory.rows * self.slot_size
        grid_left = GAME_WIDTH // 2 - grid_width // 2
        grid_top = GAME_HEIGHT // 2 - grid_height // 2 + 10

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: # Left Click
            # Iterate through placed items to verify hover pickup click
            for item in self.inventory.items:
                ix = grid_left + item.grid_x * self.slot_size
                iy = grid_top + item.grid_y * self.slot_size
                iw = item.width * self.slot_size
                ih = item.height * self.slot_size
                
                # Check click coordinates
                if ix <= logical_mx < ix + iw and iy <= logical_my < iy + ih:
                    # Pick up item
                    self.dragged_item = item
                    self.last_valid_grid_x = item.grid_x
                    self.last_valid_grid_y = item.grid_y
                    self.inventory.remove_item(item)
                    # Track relative drag offsets
                    self.drag_offset_x = logical_mx - ix
                    self.drag_offset_y = logical_my - iy
                    sounds.play("hit")
                    break

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1: # Left Release
            if self.dragged_item is not None:
                # Estimate which cell coordinates the cursor represents relative to offsets
                item_top_left_x = logical_mx - self.drag_offset_x
                item_top_left_y = logical_my - self.drag_offset_y
                
                cell_x = int(round((item_top_left_x - grid_left) / self.slot_size))
                cell_y = int(round((item_top_left_y - grid_top) / self.slot_size))
                
                # Attempt lock placements
                if self.inventory.can_fit(self.dragged_item, cell_x, cell_y):
                    self.inventory.add_item(self.dragged_item, cell_x, cell_y)
                    sounds.play("reload")
                else:
                    # Snaps back into original valid orientation coordinates
                    self.inventory.add_item(self.dragged_item, self.last_valid_grid_x, self.last_valid_grid_y)
                    sounds.play("hit")
                self.dragged_item = None

    def auto_place_looted_weapon_item(self, item):
        """Finds first available free block in 10x6 inventory grid for incoming weapons"""
        for r in range(self.inventory.rows - item.height + 1):
            for c in range(self.inventory.cols - item.width + 1):
                if self.inventory.can_fit(item, c, r):
                    self.inventory.add_item(item, c, r)
                    return True
        return False

    def update(self, dt):
        # 1. Decay Screen Shake Effect
        if self.screen_shake_intensity > 0:
            self.screen_shake_intensity -= 15.0 * dt
            if self.screen_shake_intensity < 0:
                self.screen_shake_intensity = 0

        # Pause standard combat updates if inventory is toggled open!
        if self.inventory_open:
            return

        # Calculate logical mouse world coordinates
        mouse_logical_pos = self.get_logical_mouse_pos()
        cam_x = max(0, min(self.player.pos.x - GAME_WIDTH / 2, MAP_WIDTH - GAME_WIDTH))
        cam_y = max(0, min(self.player.pos.y - GAME_HEIGHT / 2, MAP_HEIGHT - GAME_HEIGHT))
        camera = pygame.math.Vector2(cam_x, cam_y)
        mouse_world_pos = mouse_logical_pos + camera

        # Decay popup banner timers
        if self.hud_popup_timer > 0:
            self.hud_popup_timer -= dt

        # ----------------------------------
        # STATE: PLAYING UPDATES
        # ----------------------------------
        if self.state == 'PLAYING':
            # Update player actions
            self.player.update(dt, mouse_world_pos, self.bullets, self.effect_mgr)
            
            # Check player status
            if self.player.health <= 0:
                self.state = 'GAMEOVER'
                self.effect_mgr.spawn_blood_splatter(self.player.pos.x, self.player.pos.y, count=40)
                if self.player.score > self.high_score:
                    self.high_score = self.player.score
                    self.save_high_score()

            # Handle Wave Enemy Spawning Tick
            if self.enemies_spawned_count < self.enemies_remaining_to_spawn:
                if not self.intermission_active:
                    self.spawn_timer -= dt
                    if self.spawn_timer <= 0:
                        self.spawn_wave_hostile()
                        self.spawn_timer = max(0.3, self.spawn_interval - (self.wave_number * 0.05))
            
            # Check if all wave hostiles are neutralized to trigger next wave
            elif len(self.enemies) == 0 and not self.intermission_active:
                self.intermission_active = True
                self.intermission_timer = 2.5 # Intermission timer countdown

            # Update Wave transition Intermission timer
            if self.intermission_active:
                self.intermission_timer -= dt
                if self.intermission_timer <= 0:
                    self.advance_to_next_wave()

            # Update weapon crates floating animations
            for crate in self.dropped_crates:
                crate.update(dt)
                # Player proximity walkover detection
                if self.player.pos.distance_to(crate.pos) < (self.player.radius + crate.radius):
                    # Picked up weapon!
                    weapon_type = crate.weapon_type
                    if weapon_type not in self.player.unlocked_weapons:
                        # Unlock!
                        self.player.unlocked_weapons.append(weapon_type)
                        # Add item into grid backpack
                        if weapon_type == "Tactical Shotgun":
                            new_inv_item = Item("Remington", 2, 2, WEAPONS[weapon_type]["color"])
                        else:
                            new_inv_item = Item("Barrett .50", 4, 1, WEAPONS[weapon_type]["color"])
                            
                        fits = self.auto_place_looted_weapon_item(new_inv_item)
                        if fits:
                            self.show_hud_popup(f"CRATE LOOTED: SECURED {weapon_type.upper()}!")
                        else:
                            self.show_hud_popup(f"CRATE LOOTED: SECURED {weapon_type.upper()} (BACKPACK FULL)!")
                    else:
                        # If already unlocked, grant full ammo reload bonus and high score pts!
                        self.player.weapons[weapon_type] = WEAPONS[weapon_type]["ammo_capacity"]
                        self.player.score += 500
                        self.show_hud_popup(f"SUPPLY RESUPPLIED: {weapon_type.upper()} (+500 SCORE)!")
                        
                    sounds.play("levelup")
                    self.dropped_crates.remove(crate)

            # Update active Projectiles
            alive_bullets = []
            for b in self.bullets:
                b.update(dt)
                
                # Check projectile collision with tactical border concrete walls
                border_limit = 24.0
                hit_wall = (b.pos.x <= border_limit or b.pos.x >= MAP_WIDTH - border_limit or
                            b.pos.y <= border_limit or b.pos.y >= MAP_HEIGHT - border_limit)
                
                if hit_wall:
                    self.effect_mgr.spawn_wall_sparks(b.pos.x, b.pos.y, count=5)
                    sounds.play("hit")
                    continue
                
                # COLLISION RESOLUTION (PLAYER PROJECTILE VS ENEMY HOSTILES)
                if b.is_player:
                    bullet_active = True
                    for e in self.enemies:
                        if e in b.hit_targets:
                            continue # Already pierced this target
                            
                        distance = b.pos.distance_to(e.pos)
                        if distance < (b.radius + e.radius):
                            # Impact! Damage and sparks visual effects
                            e.take_damage(b.damage, self.effect_mgr)
                            self.effect_mgr.spawn_wall_sparks(b.pos.x, b.pos.y, count=3)
                            
                            # Pop up bouncing damage indicator (20 Mins style!)
                            self.damage_popups.append(DamageNumber(
                                e.pos.x, e.pos.y - 12.0,
                                f"{int(b.damage)}",
                                COLOR_GOLD if b.damage > 50 else COLOR_YELLOW
                            ))
                            
                            self.screen_shake_intensity = min(self.screen_shake_intensity + 1.2, 5.0)
                            
                            # Piercing logic
                            if b.piercing:
                                b.hit_targets.append(e) # Remember target
                                # Bullet retains speed but drops kinetic energy slightly
                                b.damage = max(10, int(b.damage * 0.75))
                            else:
                                bullet_active = False # Die on contact
                            
                            # Check neutralizations
                            if e.health <= 0:
                                self.enemies.remove(e)
                                self.player.score += 100
                                sounds.play("death")
                                self.screen_shake_intensity = min(self.screen_shake_intensity + 3.0, 7.0)
                                
                                # ENEMY LOOT ITEM DROPS CHANCE: 15% chance to drop weapons!
                                if random.random() < 0.15:
                                    # Pick a weapon not currently fully stocked or unlockable (Shotgun or Sniper)
                                    drop_type = "Tactical Shotgun" if random.random() < 0.55 else "Sniper Rifle"
                                    self.dropped_crates.append(WeaponCrate(e.pos.x, e.pos.y, drop_type))
                                break
                    
                    if bullet_active and b.life > 0:
                        alive_bullets.append(b)
                
                # COLLISION RESOLUTION (HOSTILE SHOOTER BULLETS VS PLAYER TARGET)
                else:
                    distance = b.pos.distance_to(self.player.pos)
                    if distance < (b.radius + self.player.radius):
                        self.player.take_damage(b.damage)
                        # Pop up bouncy damage indicator over player (red/crimson text)
                        self.damage_popups.append(DamageNumber(
                            self.player.pos.x, self.player.pos.y - 12.0,
                            f"-{int(b.damage)}", COLOR_RED
                        ))
                        self.screen_shake_intensity = min(self.screen_shake_intensity + 4.0, 8.0)
                    elif b.life > 0:
                        alive_bullets.append(b)
                        
            self.bullets = alive_bullets

            # Update individual active Enemy movements & shoot algorithms
            for e in self.enemies:
                e.update(dt, self.player, self.enemies, self.bullets, self.effect_mgr)

            # Update bouncing popups list
            alive_popups = []
            for dp in self.damage_popups:
                dp.update(dt)
                if dp.life > 0:
                    alive_popups.append(dp)
            self.damage_popups = alive_popups

        # ----------------------------------
        # STATE: START SCREEN UPDATES
        # ----------------------------------
        elif self.state == 'START':
            keys = pygame.key.get_pressed()
            if keys[pygame.K_1]:
                self.selected_class_type = "Assault"
            elif keys[pygame.K_2]:
                self.selected_class_type = "Medic"

    def draw(self):
        # Clear logical scratchpad surface
        self.logical_surf.fill((10, 11, 14)) # Dark moody base

        # Calculate camera center matrix positions
        cam_x = max(0, min(self.player.pos.x - GAME_WIDTH / 2, MAP_WIDTH - GAME_WIDTH))
        cam_y = max(0, min(self.player.pos.y - GAME_HEIGHT / 2, MAP_HEIGHT - GAME_HEIGHT))
        camera = pygame.math.Vector2(cam_x, cam_y)

        # 1. Draw static grid tile background terrain
        self.logical_surf.blit(self.persistent_ground, (-camera.x, -camera.y))

        # 2. Draw loot chests drops on the floor
        for crate in self.dropped_crates:
            crate.draw(self.logical_surf, camera, self.font_tiny)

        # 3. Draw blood, fire, and muzzle blast particle systems
        anim_dt = 0.0 if self.inventory_open else (self.clock.get_time() / 1000.0)
        self.effect_mgr.update_and_draw(anim_dt, self.logical_surf, camera, self.persistent_ground)

        # 4. Draw active flying projectiles
        for b in self.bullets:
            b.draw(self.logical_surf, camera)

        # 5. Draw active hostiles
        for e in self.enemies:
            e.draw(self.logical_surf, camera)

        # 6. Draw player (if alive)
        if self.player.health > 0:
            self.player.draw(self.logical_surf, camera)

        # 7. Draw bouncing damage numbers
        for dp in self.damage_popups:
            dp.draw(self.logical_surf, camera, self.font_damage)



        # ----------------------------------
        # DRAW GAME HUD & INTERFACE OVERLAYS
        # ----------------------------------
        if self.state == 'PLAYING':
            # A. Draw Tactical Health Bar (Top-Left)
            hb_x, hb_y = 16, 16
            hb_width, hb_height = 120, 10
            pygame.draw.rect(self.logical_surf, (0, 0, 0), (hb_x - 1, hb_y - 1, hb_width + 2, hb_height + 2), 1)
            pygame.draw.rect(self.logical_surf, (50, 10, 10), (hb_x, hb_y, hb_width, hb_height))
            health_percentage = self.player.health / self.player.max_health
            pygame.draw.rect(self.logical_surf, COLOR_GREEN, (hb_x, hb_y, int(hb_width * health_percentage), hb_height))
            
            text_hp = self.font_hud.render(f"HP: {int(self.player.health)}% [{self.player.class_name.upper()}]", True, COLOR_TEXT)
            self.logical_surf.blit(text_hp, (hb_x, hb_y + 13))

            # B. Draw Class Active Skill Bar & Cooldowns
            sb_x, sb_y = 16, 44
            if self.player.class_name == "Assault" and self.player.skill_active:
                skill_percentage = self.player.skill_timer / self.player.skill_duration_max
                pygame.draw.rect(self.logical_surf, (0, 0, 0), (sb_x - 1, sb_y - 1, hb_width + 2, 4), 1)
                pygame.draw.rect(self.logical_surf, COLOR_GOLD, (sb_x, sb_y, int(hb_width * skill_percentage), 2))
                text_skill = self.font_hud.render(f"[SPACE] RAPID FIRE: ACTIVE ({self.player.skill_timer:.1f}s)", True, COLOR_GOLD)
                self.logical_surf.blit(text_skill, (sb_x, sb_y + 6))
            else:
                if self.player.skill_cooldown > 0:
                    cooldown_percentage = self.player.skill_cooldown / self.player.skill_cooldown_max
                    pygame.draw.rect(self.logical_surf, (0, 0, 0), (sb_x - 1, sb_y - 1, hb_width + 2, 4), 1)
                    pygame.draw.rect(self.logical_surf, COLOR_ORANGE, (sb_x, sb_y, int(hb_width * cooldown_percentage), 2))
                    text_skill = self.font_hud.render(f"{self.player.skill_name.upper()}: CD ({self.player.skill_cooldown:.1f}s)", True, COLOR_TEXT_MUTED)
                else:
                    text_skill = self.font_hud.render(f"[SPACE] {self.player.skill_name.upper()}: READY", True, COLOR_GREEN)
                self.logical_surf.blit(text_skill, (sb_x, sb_y + 6))

            # C. Draw Weapons Loadouts Status Indicators (Bottom-Left HUD)
            w_start_y = GAME_HEIGHT - 65
            w_spec = self.player.current_weapon_spec
            cur_ammo = self.player.weapons[self.player.current_weapon_name]
            
            # Cycle/Active weapon title
            text_cw = self.font_main.render(w_spec["name"].upper(), True, COLOR_GOLD)
            self.logical_surf.blit(text_cw, (16, w_start_y))
            
            # Ammo count text
            ammo_lbl = f"{cur_ammo} / {w_spec['ammo_capacity']}"
            if self.player.reloading:
                ammo_lbl = "RELOADING..."
            text_ammo = self.font_hud.render(f"AMMO: {ammo_lbl}", True, COLOR_YELLOW if cur_ammo < (w_spec['ammo_capacity'] * 0.3) else COLOR_TEXT)
            self.logical_surf.blit(text_ammo, (16, w_start_y + 20))
            
            # Controls help hints HUD overlay
            help_msg = "[C] Class  |  [Scroll Wheel] Cycle Weapons  |  [TAB] Backpack Inventory"
            text_help = self.font_hud.render(help_msg, True, COLOR_TEXT_MUTED)
            self.logical_surf.blit(text_help, (16, w_start_y + 36))

            # D. Draw Combat Wave Counters (Top-Right)
            hostiles_count = len(self.enemies) + self.enemies_remaining_to_spawn - self.enemies_spawned_count
            wave_info = f"WAVE: {self.wave_number}  |  HOSTILES LEFT: {hostiles_count}"
            text_wave = self.font_hud.render(wave_info, True, COLOR_TEXT)
            self.logical_surf.blit(text_wave, (GAME_WIDTH - text_wave.get_width() - 16, 16))

            # E. Score Counters (Top-Center)
            text_score = self.font_hud.render(f"SCORE: {self.player.score}", True, COLOR_TEXT)
            self.logical_surf.blit(text_score, (GAME_WIDTH // 2 - text_score.get_width() // 2, 16))

            # F. Global HUD Popup Alerts Banner
            if self.hud_popup_timer > 0:
                p_rendered = self.font_main.render(self.hud_popup_msg, True, COLOR_GOLD)
                p_x = GAME_WIDTH // 2 - p_rendered.get_width() // 2
                self.logical_surf.blit(p_rendered, (p_x, GAME_HEIGHT - 45))

            # G. Wave Clear Intermission Banner
            if self.intermission_active:
                inter_text = f"WAVE COMPLETED! OUTPOST RESUPPLIED... NEXT WAVE IN {math.ceil(self.intermission_timer)}s"
                text_inter = self.font_main.render(inter_text, True, COLOR_YELLOW)
                self.logical_surf.blit(text_inter, (GAME_WIDTH // 2 - text_inter.get_width() // 2, GAME_HEIGHT // 2 - 30))

            # ----------------------------------
            # GRID INVENTORY VISUAL CASE (TAB OVERLAY)
            # ----------------------------------
            if self.inventory_open:
                inv_overlay = pygame.Surface((GAME_WIDTH, GAME_HEIGHT), pygame.SRCALPHA)
                inv_overlay.fill((10, 11, 14, 185)) # dim dims overlay background
                self.logical_surf.blit(inv_overlay, (0, 0))

                grid_width = self.inventory.cols * self.slot_size
                grid_height = self.inventory.rows * self.slot_size
                box_w = grid_width + 32
                box_h = grid_height + 64
                box_x = GAME_WIDTH // 2 - box_w // 2
                box_y = GAME_HEIGHT // 2 - box_h // 2 + 10
                
                # Draw metal tactical grid lock container frame
                pygame.draw.rect(self.logical_surf, (15, 17, 20), (box_x, box_y, box_w, box_h))
                pygame.draw.rect(self.logical_surf, COLOR_GREEN, (box_x, box_y, box_w, box_h), 1)
                
                # Header Title
                hdr_txt = self.font_hud.render("=== OPERATIONAL SUPPLY INVENTORY GRID ===", True, COLOR_GREEN)
                self.logical_surf.blit(hdr_txt, (box_x + 16, box_y + 12))

                # Draw empty 2D slots blocks
                grid_left = GAME_WIDTH // 2 - grid_width // 2
                grid_top = box_y + 36
                for r in range(self.inventory.rows):
                    for c in range(self.inventory.cols):
                        slot_rect = pygame.Rect(grid_left + c * self.slot_size, grid_top + r * self.slot_size, self.slot_size, self.slot_size)
                        pygame.draw.rect(self.logical_surf, (25, 27, 32), slot_rect) # slot base
                        pygame.draw.rect(self.logical_surf, (40, 44, 50), slot_rect, 1) # borders
                
                # Fetch matched logical mouse coordinates
                logical_mouse = self.get_logical_mouse_pos()
                logical_mx, logical_my = logical_mouse.x, logical_mouse.y

                # Highlight placement shadow preview if dragging gear items
                if self.dragged_item is not None:
                    item_top_left_x = logical_mx - self.drag_offset_x
                    item_top_left_y = logical_my - self.drag_offset_y
                    cell_x = int(round((item_top_left_x - grid_left) / self.slot_size))
                    cell_y = int(round((item_top_left_y - grid_top) / self.slot_size))
                    
                    in_range = (0 <= cell_x <= self.inventory.cols - self.dragged_item.width) and \
                               (0 <= cell_y <= self.inventory.rows - self.dragged_item.height)
                    
                    if in_range:
                        if self.inventory.can_fit(self.dragged_item, cell_x, cell_y):
                            shadow_color = (46, 204, 113, 95)
                        else:
                            shadow_color = (231, 76, 60, 95)
                            
                        # Draw shadow block overlay on grid cells
                        shadow_surf = pygame.Surface((self.dragged_item.width * self.slot_size, self.dragged_item.height * self.slot_size), pygame.SRCALPHA)
                        shadow_surf.fill(shadow_color)
                        self.logical_surf.blit(shadow_surf, (grid_left + cell_x * self.slot_size, grid_top + cell_y * self.slot_size))

                # Render placed items inside the slots
                for item in self.inventory.items:
                    if item is self.dragged_item:
                        continue
                    
                    ix = grid_left + item.grid_x * self.slot_size
                    iy = grid_top + item.grid_y * self.slot_size
                    iw = item.width * self.slot_size - 1
                    ih = item.height * self.slot_size - 1
                    
                    pygame.draw.rect(self.logical_surf, item.color, (ix + 1, iy + 1, iw - 1, ih - 1))
                    pygame.draw.rect(self.logical_surf, (min(255, item.color[0] + 40), min(255, item.color[1] + 40), min(255, item.color[2] + 40)), (ix, iy, iw, ih), 1)
                    
                    # Centered text labels inside container block
                    text_label = self.font_tiny.render(item.name, True, COLOR_TEXT)
                    text_x = ix + iw // 2 - text_label.get_width() // 2
                    text_y = iy + ih // 2 - text_label.get_height() // 2
                    if text_label.get_width() < iw - 2:
                        self.logical_surf.blit(text_label, (text_x, text_y))

                # Render the actively dragged piece following cursor positions
                if self.dragged_item is not None:
                    ix = logical_mx - self.drag_offset_x
                    iy = logical_my - self.drag_offset_y
                    iw = self.dragged_item.width * self.slot_size - 1
                    ih = self.dragged_item.height * self.slot_size - 1
                    
                    drag_surf = pygame.Surface((iw, ih), pygame.SRCALPHA)
                    drag_surf.fill((self.dragged_item.color[0], self.dragged_item.color[1], self.dragged_item.color[2], 200))
                    pygame.draw.rect(drag_surf, (255, 255, 255, 220), (0, 0, iw, ih), 1)
                    
                    text_label = self.font_tiny.render(self.dragged_item.name, True, (255, 255, 255))
                    if text_label.get_width() < iw:
                        drag_surf.blit(text_label, (iw // 2 - text_label.get_width() // 2, ih // 2 - text_label.get_height() // 2))
                        
                    self.logical_surf.blit(drag_surf, (ix, iy))

                # Drawer footer guidelines
                footer_txt = self.font_hud.render("[TAB] Resume Outpost  |  [L-Click + Drag] Sort Weapons & Gear", True, COLOR_TEXT_MUTED)
                self.logical_surf.blit(footer_txt, (box_x + 16, box_y + box_h - 22))

            # H. Render custom high-visibility cursor crosshair at logical position (Only if inventory is closed!)
            if not self.inventory_open:
                # Note: mouse scaling is automatically handled dynamically on hardware scaling!
                logical_mouse = self.get_logical_mouse_pos()
                self.logical_surf.blit(SPRITE_CROSSHAIR, (logical_mouse.x - 12, logical_mouse.y - 12))

        # ----------------------------------
        # DRAW STATE: START SCREEN OVERLAYS
        # ----------------------------------
        elif self.state == 'START':
            overlay = pygame.Surface((GAME_WIDTH, GAME_HEIGHT), pygame.SRCALPHA)
            overlay.fill((10, 11, 14, 230))
            self.logical_surf.blit(overlay, (0, 0))

            title = self.font_large.render("SPECOPS: DARKNESS OUTPOST", True, COLOR_GREEN)
            sub_title = self.font_main.render("PRESS [ SPACE ] TO DEPLOY COVERT OPs", True, COLOR_TEXT)
            class_select_title = self.font_hud.render("=== CHOOSE COVERT CLASS (Press [1] or [2]) ===", True, COLOR_GOLD)
            
            self.logical_surf.blit(title, (GAME_WIDTH // 2 - title.get_width() // 2, 45))
            self.logical_surf.blit(sub_title, (GAME_WIDTH // 2 - sub_title.get_width() // 2, 85))
            self.logical_surf.blit(class_select_title, (GAME_WIDTH // 2 - class_select_title.get_width() // 2, 125))

            # Render Class Options Side-by-Side
            # ASSAULT Class Panel (Left)
            assault_x = GAME_WIDTH // 4 - 30
            is_assault_selected = (self.selected_class_type == "Assault")
            pygame.draw.rect(self.logical_surf, COLOR_GREEN if is_assault_selected else (40, 40, 45), (assault_x, 155, 200, 110), 1)
            if is_assault_selected:
                pygame.draw.rect(self.logical_surf, (15, 35, 20), (assault_x + 1, 156, 198, 108))
            self.logical_surf.blit(SPRITE_PLAYER_ASSAULT, (assault_x + 10, 162))
            text_assault_lbl = self.font_main.render("[1] ASSAULT", True, COLOR_GREEN if is_assault_selected else COLOR_TEXT)
            self.logical_surf.blit(text_assault_lbl, (assault_x + 65, 172))
            text_assault_skill = self.font_hud.render("SKILL: Rapid Fire (Space)", True, COLOR_GOLD)
            text_assault_desc = self.font_hud.render("Cuts M4 Carbine firing delay", True, COLOR_TEXT_MUTED)
            text_assault_desc2 = self.font_hud.render("from 120ms to 60ms for 4s", True, COLOR_TEXT_MUTED)
            self.logical_surf.blit(text_assault_skill, (assault_x + 10, 212))
            self.logical_surf.blit(text_assault_desc, (assault_x + 10, 228))
            self.logical_surf.blit(text_assault_desc2, (assault_x + 10, 244))

            # MEDIC Class Panel (Right)
            medic_x = (GAME_WIDTH // 4) * 3 - 170
            is_medic_selected = (self.selected_class_type == "Medic")
            pygame.draw.rect(self.logical_surf, COLOR_GREEN if is_medic_selected else (40, 40, 45), (medic_x, 155, 200, 110), 1)
            if is_medic_selected:
                pygame.draw.rect(self.logical_surf, (15, 35, 20), (medic_x + 1, 156, 198, 108))
            self.logical_surf.blit(SPRITE_PLAYER_MEDIC, (medic_x + 10, 162))
            text_medic_lbl = self.font_main.render("[2] MEDIC", True, COLOR_GREEN if is_medic_selected else COLOR_TEXT)
            self.logical_surf.blit(text_medic_lbl, (medic_x + 65, 172))
            text_medic_skill = self.font_hud.render("SKILL: Self Heal (Space)", True, COLOR_GOLD)
            text_medic_desc = self.font_hud.render("Injects stimpack to instantly", True, COLOR_TEXT_MUTED)
            text_medic_desc2 = self.font_hud.render("restore +40 HP health ratio", True, COLOR_TEXT_MUTED)
            self.logical_surf.blit(text_medic_skill, (medic_x + 10, 212))
            self.logical_surf.blit(text_medic_desc, (medic_x + 10, 228))
            self.logical_surf.blit(text_medic_desc2, (medic_x + 10, 244))

            # Controls section
            controls_title = self.font_hud.render("=== STRATEGIC FIELD INTEL ===", True, COLOR_TEXT_MUTED)
            ctrl_wasd = self.font_hud.render("[WASD] Movement  |  [Mouse Aim] Aiming Line of Sight  |  [Scroll Wheel] Cycle Weapons", True, COLOR_TEXT)
            ctrl_space = self.font_hud.render("[Left Click] Shoot  |  [R] Reload  |  [SPACEBAR] Trigger Class Skill", True, COLOR_TEXT)
            ctrl_game_type = self.font_hud.render("[TAB] Backpack Case  |  [Enemies Drop Crate] Walkover Loot unlocks Shotguns & Snipers!", True, COLOR_YELLOW)
            ctrl_resizing = self.font_hud.render("[Resize Window] Outpost maintains Aspect Ratio & Mouse Scales dynamically!", True, COLOR_BLUE)
            
            high_score_txt = self.font_hud.render(f"TOP OUTPOST RECORD: {self.high_score}", True, COLOR_GOLD)

            start_y = 295
            self.logical_surf.blit(controls_title, (GAME_WIDTH // 2 - controls_title.get_width() // 2, start_y))
            self.logical_surf.blit(ctrl_wasd, (GAME_WIDTH // 2 - ctrl_wasd.get_width() // 2, start_y + 18))
            self.logical_surf.blit(ctrl_space, (GAME_WIDTH // 2 - ctrl_space.get_width() // 2, start_y + 34))
            self.logical_surf.blit(ctrl_game_type, (GAME_WIDTH // 2 - ctrl_game_type.get_width() // 2, start_y + 50))
            self.logical_surf.blit(ctrl_resizing, (GAME_WIDTH // 2 - ctrl_resizing.get_width() // 2, start_y + 66))
            
            self.logical_surf.blit(high_score_txt, (GAME_WIDTH // 2 - high_score_txt.get_width() // 2, start_y + 95))

        # ----------------------------------
        # DRAW STATE: GAMEOVER OVERLAYS
        # ----------------------------------
        elif self.state == 'GAMEOVER':
            overlay = pygame.Surface((GAME_WIDTH, GAME_HEIGHT), pygame.SRCALPHA)
            overlay.fill((30, 5, 5, 235)) # Deep red vignette overlay
            self.logical_surf.blit(overlay, (0, 0))

            title = self.font_large.render("OUTPOST OVERRUN!", True, COLOR_RED)
            sub_title = self.font_main.render("YOU WERE ELIMINATED IN ACTION", True, COLOR_TEXT)
            restart_hint = self.font_hud.render("PRESS [ SPACE ] TO REDEPLOY AN AGENT", True, COLOR_TEXT_MUTED)

            stats_score = self.font_hud.render(f"FINAL COMBAT SCORE: {self.player.score}", True, COLOR_TEXT)
            stats_wave = self.font_hud.render(f"FINAL SURVIVED WAVE: {self.wave_number}", True, COLOR_TEXT)
            high_score_txt = self.font_hud.render(f"TOP RECORD: {self.high_score}", True, COLOR_GOLD)

            self.logical_surf.blit(title, (GAME_WIDTH // 2 - title.get_width() // 2, 110))
            self.logical_surf.blit(sub_title, (GAME_WIDTH // 2 - sub_title.get_width() // 2, 155))
            
            self.logical_surf.blit(stats_score, (GAME_WIDTH // 2 - stats_score.get_width() // 2, 200))
            self.logical_surf.blit(stats_wave, (GAME_WIDTH // 2 - stats_wave.get_width() // 2, 220))
            self.logical_surf.blit(high_score_txt, (GAME_WIDTH // 2 - high_score_txt.get_width() // 2, 250))
            
            self.logical_surf.blit(restart_hint, (GAME_WIDTH // 2 - restart_hint.get_width() // 2, 310))

        # ----------------------------------
        # NEW: ADAPTIVE SCREEN VIEWPORT BLITTING (Letterbox Scaling)
        # ----------------------------------
        viewport = self.get_viewport_rect()
        # Smoothly scale low-res logical surface to centered letterboxed hardware viewport aspect
        scaled_backbuffer = pygame.transform.smoothscale(self.logical_surf, (viewport.width, viewport.height))
        
        # Apply Screen Shake Displacement Vectors
        shake_x = 0
        shake_y = 0
        if self.screen_shake_intensity > 0:
            viewport_scale = viewport.width / GAME_WIDTH
            shake_x = random.uniform(-self.screen_shake_intensity, self.screen_shake_intensity) * viewport_scale
            shake_y = random.uniform(-self.screen_shake_intensity, self.screen_shake_intensity) * viewport_scale

        # Paint letterbox black borders
        self.screen.fill((10, 11, 13))
        # Draw game viewport inside centered margins with screen shakes
        self.screen.blit(scaled_backbuffer, (viewport.x + shake_x, viewport.y + shake_y))
        pygame.display.flip()

    async def run(self):
        pygame.mouse.set_visible(False)
        
        running = True
        while running:
            dt = min(0.1, self.clock.tick(60) / 1000.0)

            # Polling events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.VIDEORESIZE:
                    # Update hardware window dimensions cleanly upon resizing
                    self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.state == 'PLAYING':
                        if self.inventory_open:
                            self.handle_inventory_clicks(event)
                        else:
                            # Scroll wheel cycles active weapon slot inventories
                            if event.button == 4: # Scroll Up
                                self.player.cycle_weapon(1)
                            elif event.button == 5: # Scroll Down
                                self.player.cycle_weapon(-1)
                elif event.type == pygame.MOUSEBUTTONUP:
                    if self.state == 'PLAYING' and self.inventory_open:
                        self.handle_inventory_clicks(event)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_r:
                        if self.state == 'PLAYING' and not self.inventory_open:
                            self.player.start_reload()
                    elif event.key == pygame.K_c:
                        if self.state == 'PLAYING' and not self.inventory_open:
                            self.swap_player_class()
                    elif event.key == pygame.K_TAB:
                        if self.state == 'PLAYING':
                            self.inventory_open = not self.inventory_open
                            self.dragged_item = None # Clear drag pieces
                            sounds.play("reload")
                            pygame.mouse.set_visible(self.inventory_open)
                    elif event.key == pygame.K_SPACE:
                        if self.state == 'PLAYING' and not self.inventory_open:
                            self.player.activate_skill(self.effect_mgr)
                        elif self.state == 'START':
                            self.reset_game_state()
                            self.state = 'PLAYING'
                        elif self.state == 'GAMEOVER':
                            self.reset_game_state()
                            self.state = 'PLAYING'
            
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
