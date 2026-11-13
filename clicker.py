# ============================================================================
# CLICKER SIM - inside gyakorlas/ folder ONLY
# Refactored: tiered upgrades, dynamic pricing, scrollable UI, save/load
# Uses bgp.webp (background) and clickPIC.jpg (clickable picture)
# Run:  python clicker.py   (from inside the gyakorlas folder)
# ============================================================================

import os
import sys
import json
import random
import pygame

# ----------------------------------------------------------------------------
# STEP 0: INITIALIZE PYGAME
# ----------------------------------------------------------------------------
pygame.init()

def format_num(n):
    if n < 0:
        return "-" + format_num(-n)
    if n < 1_000:
        return str(int(n))
    suffixes = ["k", "M", "B", "T", "Qa", "Qi", "Sx", "Sp", "Oc", "No", "Dc"]
    for i in range(len(suffixes) - 1, -1, -1):
        threshold = 1000 ** (i + 1)
        if n >= threshold:
            value = n / threshold
            formatted = f"{value:.1f}".rstrip("0").rstrip(".")
            return f"{formatted}{suffixes[i]}"
    return str(int(n))

# ----------------------------------------------------------------------------
DEFAULT_W, DEFAULT_H = 1000, 700
MIN_W, MIN_H = 900, 620
BASE = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE, "settings.json")
RESOLUTION_OPTIONS = [(1280, 720), (1600, 900), (1920, 1080)]
FPS_OPTIONS = [30, 60, 120, 144, "Unlimited"]
DEFAULT_SETTINGS = {
    "volume": 80,
    "resolution_index": 0,  # index in RESOLUTION_OPTIONS
    "fullscreen": False,
    "fps_index": 1,         # 60
}


def load_settings():
    cfg = DEFAULT_SETTINGS.copy()
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            cfg["volume"] = max(0, min(100, int(data.get("volume", cfg["volume"]))))
            ri = int(data.get("resolution_index", cfg["resolution_index"]))
            if 0 <= ri < len(RESOLUTION_OPTIONS):
                cfg["resolution_index"] = ri
            cfg["fullscreen"] = bool(data.get("fullscreen", cfg["fullscreen"]))
            fi = int(data.get("fps_index", cfg["fps_index"]))
            if 0 <= fi < len(FPS_OPTIONS):
                cfg["fps_index"] = fi
    except Exception:
        pass
    return cfg


def save_settings(cfg):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2)
    except Exception as e:
        print(f"[CLICKER] Settings save failed: {e}")


def effective_fps(cfg):
    val = FPS_OPTIONS[cfg["fps_index"]]
    return 0 if val == "Unlimited" else int(val)


settings = load_settings()
_draft_settings = settings.copy()
audio_volume = settings["volume"] / 100.0
try:
    if pygame.mixer.get_init():
        pygame.mixer.music.set_volume(audio_volume)
except Exception:
    pass

win_w, win_h = RESOLUTION_OPTIONS[settings["resolution_index"]]
SCREEN_W, SCREEN_H = win_w, win_h
_display_flags = pygame.FULLSCREEN if settings["fullscreen"] else pygame.RESIZABLE
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H), _display_flags)
pygame.display.set_caption("Clicker Sim - Upgrades & Rebirth")
clock = pygame.time.Clock()
FPS_CAP = effective_fps(settings)

# ----------------------------------------------------------------------------
# STEP 2: COLORS
# ----------------------------------------------------------------------------
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
BLUE = (0, 120, 255)
DARK_BLUE = (0, 90, 200)
RED = (200, 50, 50)
DARK_RED = (150, 40, 40)
YELLOW = (255, 220, 0)
GREEN = (0, 200, 0)
DARK_GREEN = (0, 140, 0)
PINK = pygame.Color("pink")
PANEL_BG = (40, 40, 60)
PANEL_BORDER = WHITE
OVERLAY = (0, 0, 0, 170)
TEXT_BG = (20, 20, 35)
CARD_BG = (55, 55, 80)

# ----------------------------------------------------------------------------
# STEP 3: FONTS
# ----------------------------------------------------------------------------
font_big = pygame.font.SysFont(None, 48)
font_med = pygame.font.SysFont(None, 32)
font_small = pygame.font.SysFont(None, 24)
font_tiny = pygame.font.SysFont(None, 20)

# ----------------------------------------------------------------------------
# STEP 4: LOAD IMAGES FROM THIS FOLDER (gyakorlas/)
# ----------------------------------------------------------------------------

def load_background(size):
    w, h = size
    try:
        img = pygame.image.load(os.path.join(BASE, "bgp.webp")).convert()
        return pygame.transform.scale(img, (w, h))
    except (pygame.error, FileNotFoundError):
        surf = pygame.Surface((w, h))
        surf.fill((30, 30, 50))
        return surf

def load_click_source():
    try:
        img = pygame.image.load(os.path.join(BASE, "clickPIC.jpg")).convert_alpha()
        print("[CLICKER] Loaded click picture: clickPIC.jpg")
        return img
    except (pygame.error, FileNotFoundError):
        print("[CLICKER] clickPIC.jpg not found, using fallback color.")
        surf = pygame.Surface((256, 256), pygame.SRCALPHA)
        surf.fill(GREEN)
        return surf

bg_img = load_background((SCREEN_W, SCREEN_H))
click_source_img = load_click_source()
clicker_img = pygame.transform.smoothscale(click_source_img, (180, 180))
clicker_rect = clicker_img.get_rect(center=(SCREEN_W // 2 + 40, SCREEN_H // 2 + 40))

def apply_display_settings(cfg):
    global screen, SCREEN_W, SCREEN_H, bg_img, FPS_CAP
    FPS_CAP = effective_fps(cfg)
    if cfg["fullscreen"]:
        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    else:
        w, h = RESOLUTION_OPTIONS[cfg["resolution_index"]]
        w = max(MIN_W, w)
        h = max(MIN_H, h)
        screen = pygame.display.set_mode((w, h), pygame.RESIZABLE)
    SCREEN_W, SCREEN_H = screen.get_size()
    bg_img = load_background((SCREEN_W, SCREEN_H))

# Skins
SKIN_FILES = {
    "Szomszéd": "mezodeafult.jpg",
    "UtcaRéme": "mezo2.jpg",
    "SuliFélelme": "mezo3.jpg",
    "PacekMező": "mezo4.webp",
    "Cicafül": "mezo5.jpg",
    "Osztályföni": "mezo6.jpg",
    "Vicces": "mezo7.jpg",
    "Mosoly": "mezo8.png",
    "'Mi'?": "mezo9.png",
    "Vigyor": "mezo10.png",
    "'MivanItt'": "mezo11.png",
    "4km-re": "mezo12.gif",
    "ShyMezo": "mezo13.png",
}

SKIN_MULTIPLIERS = {name: round(1.0 + i * 0.15, 2) for i, name in enumerate(SKIN_FILES.keys())}

def load_skin_image(name):
    path = os.path.join(BASE, SKIN_FILES[name])
    try:
        img = pygame.image.load(path).convert_alpha()
        return img
    except (pygame.error, FileNotFoundError):
        print(f"[CLICKER] skin {name} not found")
        surf = pygame.Surface((180, 180))
        surf.fill((random.randint(50, 200), random.randint(50, 200), random.randint(50, 200)))
        txt = font_small.render(name, True, WHITE)
        surf.blit(txt, txt.get_rect(center=(90, 90)))
        return surf

skin_source_images = {name: load_skin_image(name) for name in SKIN_FILES}
skin_images = {}  # resized responsively in relayout_ui()

# ----------------------------------------------------------------------------
# STEP 5: UPGRADE CATALOG (categories, per-upgrade levels, shared scaling)
# ----------------------------------------------------------------------------
# Within a category, buying ANY upgrade increases that category's shared price
# multiplier, so every upgrade in the category becomes more expensive. Each
# upgrade still has its own base cost, per-level growth, and individual price
# multiplier so tiered prices remain distinct.
UPGRADE_CATALOG = {
    "click_power": {
        "label": "Click Power",
        "color": (70, 130, 220),
        "shared_scale": 1.12,
        "upgrades": [
            {"id": "finger_training", "name": "Finger Training", "desc": "+1 click power / level", "base_cost": 15, "level_growth": 1.15, "individual_scale": 1.04, "effect": {"type": "click_add", "value": 1}},
            {"id": "reinforced_mouse", "name": "Reinforced Mouse", "desc": "+5 click power / level", "base_cost": 120, "level_growth": 1.16, "individual_scale": 1.05, "effect": {"type": "click_add", "value": 5}},
            {"id": "power_gauntlet", "name": "Power Gauntlet", "desc": "+25 click power / level", "base_cost": 900, "level_growth": 1.17, "individual_scale": 1.06, "effect": {"type": "click_add", "value": 25}},
            {"id": "hydraulic_press", "name": "Hydraulic Press", "desc": "+50 click power / level", "base_cost": 3_200, "level_growth": 1.18, "individual_scale": 1.06, "effect": {"type": "click_add", "value": 50}},
            {"id": "titanium_stylus", "name": "Titanium Stylus", "desc": "+100 click power / level", "base_cost": 11_000, "level_growth": 1.18, "individual_scale": 1.07, "effect": {"type": "click_add", "value": 100}},
            {"id": "cybernetic_hand", "name": "Cybernetic Hand", "desc": "+250 click power / level", "base_cost": 45_000, "level_growth": 1.19, "individual_scale": 1.07, "effect": {"type": "click_add", "value": 250}},
            {"id": "plasma_cursor", "name": "Plasma Cursor", "desc": "+500 click power / level", "base_cost": 160_000, "level_growth": 1.19, "individual_scale": 1.08, "effect": {"type": "click_add", "value": 500}},
            {"id": "sonic_tapper", "name": "Sonic Tapper", "desc": "+1k click power / level", "base_cost": 550_000, "level_growth": 1.20, "individual_scale": 1.08, "effect": {"type": "click_add", "value": 1_000}},
            {"id": "quantum_switch", "name": "Quantum Switch", "desc": "+2.5k click power / level", "base_cost": 2_200_000, "level_growth": 1.20, "individual_scale": 1.09, "effect": {"type": "click_add", "value": 2_500}},
            {"id": "gravity_hammer", "name": "Gravity Hammer", "desc": "+5k click power / level", "base_cost": 8_000_000, "level_growth": 1.21, "individual_scale": 1.09, "effect": {"type": "click_add", "value": 5_000}},
            {"id": "laser_pointer", "name": "Orbital Laser", "desc": "+10k click power / level", "base_cost": 28_000_000, "level_growth": 1.21, "individual_scale": 1.10, "effect": {"type": "click_add", "value": 10_000}},
            {"id": "neutron_finger", "name": "Neutron Finger", "desc": "+25k click power / level", "base_cost": 115_000_000, "level_growth": 1.22, "individual_scale": 1.10, "effect": {"type": "click_add", "value": 25_000}},
            {"id": "antimatter_click", "name": "Antimatter Click", "desc": "+50k click power / level", "base_cost": 420_000_000, "level_growth": 1.22, "individual_scale": 1.11, "effect": {"type": "click_add", "value": 50_000}},
            {"id": "tachyon_pulse", "name": "Tachyon Pulse", "desc": "+100k click power / level", "base_cost": 1_500_000_000, "level_growth": 1.23, "individual_scale": 1.11, "effect": {"type": "click_add", "value": 100_000}},
            {"id": "star_forged_glove", "name": "Star-Forged Glove", "desc": "+250k click power / level", "base_cost": 6_000_000_000, "level_growth": 1.23, "individual_scale": 1.12, "effect": {"type": "click_add", "value": 250_000}},
            {"id": "void_touch", "name": "Void Touch", "desc": "+500k click power / level", "base_cost": 22_000_000_000, "level_growth": 1.24, "individual_scale": 1.12, "effect": {"type": "click_add", "value": 500_000}},
            {"id": "god_hand", "name": "Hand of Creation", "desc": "+1M click power / level", "base_cost": 85_000_000_000, "level_growth": 1.25, "individual_scale": 1.13, "effect": {"type": "click_add", "value": 1_000_000}},
        ],
    },
    "auto_income": {
        "label": "Auto-Income",
        "color": (60, 170, 110),
        "shared_scale": 1.13,
        "upgrades": [
            {"id": "intern", "name": "Intern", "desc": "+1 / sec passive income", "base_cost": 40, "level_growth": 1.15, "individual_scale": 1.04, "effect": {"type": "passive_add", "value": 1}},
            {"id": "workshop", "name": "Workshop", "desc": "+8 / sec passive income", "base_cost": 350, "level_growth": 1.16, "individual_scale": 1.05, "effect": {"type": "passive_add", "value": 8}},
            {"id": "factory", "name": "Factory", "desc": "+40 / sec passive income", "base_cost": 2_500, "level_growth": 1.17, "individual_scale": 1.06, "effect": {"type": "passive_add", "value": 40}},
            {"id": "assembly_line", "name": "Auto-Assembly Line", "desc": "+150 / sec passive income", "base_cost": 14_000, "level_growth": 1.18, "individual_scale": 1.06, "effect": {"type": "passive_add", "value": 150}},
            {"id": "server_farm", "name": "Server Farm", "desc": "+600 / sec passive income", "base_cost": 75_000, "level_growth": 1.18, "individual_scale": 1.07, "effect": {"type": "passive_add", "value": 600}},
            {"id": "mega_corp", "name": "Mega Corporation", "desc": "+2.5k / sec passive income", "base_cost": 420_000, "level_growth": 1.19, "individual_scale": 1.07, "effect": {"type": "passive_add", "value": 2_500}},
            {"id": "ai_cluster", "name": "AI Trading Cluster", "desc": "+10k / sec passive income", "base_cost": 2_200_000, "level_growth": 1.20, "individual_scale": 1.08, "effect": {"type": "passive_add", "value": 10_000}},
            {"id": "fusion_plant", "name": "Fusion Power Plant", "desc": "+45k / sec passive income", "base_cost": 12_000_000, "level_growth": 1.20, "individual_scale": 1.08, "effect": {"type": "passive_add", "value": 45_000}},
            {"id": "orbital_mine", "name": "Asteroid Mine", "desc": "+200k / sec passive income", "base_cost": 68_000_000, "level_growth": 1.21, "individual_scale": 1.09, "effect": {"type": "passive_add", "value": 200_000}},
            {"id": "lunar_colony", "name": "Lunar Foundry", "desc": "+850k / sec passive income", "base_cost": 380_000_000, "level_growth": 1.21, "individual_scale": 1.09, "effect": {"type": "passive_add", "value": 850_000}},
            {"id": "dyson_swarm", "name": "Dyson Swarm", "desc": "+3.5M / sec passive income", "base_cost": 2_100_000_000, "level_growth": 1.22, "individual_scale": 1.10, "effect": {"type": "passive_add", "value": 3_500_000}},
            {"id": "wormhole_port", "name": "Wormhole Trade Port", "desc": "+15M / sec passive income", "base_cost": 11_500_000_000, "level_growth": 1.23, "individual_scale": 1.11, "effect": {"type": "passive_add", "value": 15_000_000}},
            {"id": "galaxy_bank", "name": "Galactic Reserve", "desc": "+75M / sec passive income", "base_cost": 65_000_000_000, "level_growth": 1.24, "individual_scale": 1.12, "effect": {"type": "passive_add", "value": 75_000_000}},
        ],
    },
    "multipliers": {
        "label": "Multipliers",
        "color": (160, 85, 220),
        "shared_scale": 1.25,
        "upgrades": [
            {"id": "coffee_break", "name": "Espresso Shot", "desc": "+10% all income / level", "base_cost": 500, "level_growth": 1.35, "individual_scale": 1.15, "effect": {"type": "global_mult", "value": 0.10}},
            {"id": "overclock", "name": "System Overclock", "desc": "+25% click power / level", "base_cost": 3_000, "level_growth": 1.40, "individual_scale": 1.18, "effect": {"type": "click_mult", "value": 0.25}},
            {"id": "automation_ai", "name": "Workflow AI", "desc": "+25% auto-income / level", "base_cost": 7_500, "level_growth": 1.40, "individual_scale": 1.18, "effect": {"type": "passive_mult", "value": 0.25}},
            {"id": "golden_touch", "name": "Midas Protocol", "desc": "+50% all income / level", "base_cost": 100_000, "level_growth": 1.50, "individual_scale": 1.22, "effect": {"type": "global_mult", "value": 0.50}},
            {"id": "quantum_compound", "name": "Quantum Compounding", "desc": "x1.5 total income / level", "base_cost": 5_000_000, "level_growth": 1.75, "individual_scale": 1.30, "effect": {"type": "global_mult_exp", "value": 1.50}},
        ],
    },
    "critical": {
        "label": "Critical Hits",
        "color": (220, 120, 50),
        "shared_scale": 1.20,
        "upgrades": [
            {"id": "lucky_charm", "name": "Lucky Coin", "desc": "+2% crit chance / level", "base_cost": 250, "level_growth": 1.30, "individual_scale": 1.12, "max_level": 25, "effect": {"type": "crit_chance", "value": 0.02}},
            {"id": "precision_lens", "name": "Precision Lens", "desc": "+0.5x crit damage / level", "base_cost": 800, "level_growth": 1.28, "individual_scale": 1.10, "effect": {"type": "crit_mult", "value": 0.5}},
            {"id": "overload_cap", "name": "Capacitor Discharge", "desc": "+3% crit chance / level", "base_cost": 25_000, "level_growth": 1.35, "individual_scale": 1.15, "max_level": 15, "effect": {"type": "crit_chance", "value": 0.03}},
            {"id": "supernova_crit", "name": "Supernova Strike", "desc": "+2.0x crit damage / level", "base_cost": 150_000, "level_growth": 1.35, "individual_scale": 1.15, "effect": {"type": "crit_mult", "value": 2.0}},
        ],
    },
    "multipliers": {
        "label": "Multipliers",
        "color": (170, 120, 60),
        "shared_scale": 1.15,
        "upgrades": [
            {"id": "focus_brew", "name": "Focus Brew", "desc": "+5% global earnings / level", "base_cost": 200, "level_growth": 1.22, "individual_scale": 1.06, "effect": {"type": "mult_add", "value": 0.05}},
            {"id": "momentum", "name": "Momentum", "desc": "+12% global earnings / level", "base_cost": 1200, "level_growth": 1.24, "individual_scale": 1.09, "effect": {"type": "mult_add", "value": 0.12}},
            {"id": "overclock", "name": "Overclock", "desc": "+25% global earnings / level", "base_cost": 6000, "level_growth": 1.27, "individual_scale": 1.12, "effect": {"type": "mult_add", "value": 0.25}},
        ],
    },
    "critical_chance": {
        "label": "Critical Chance",
        "color": (180, 80, 140),
        "shared_scale": 1.14,
        "upgrades": [
            {"id": "sharp_eye", "name": "Sharp Eye", "desc": "+1% crit chance / level (cap 75%)", "base_cost": 150, "level_growth": 1.20, "individual_scale": 1.05, "effect": {"type": "crit_chance", "value": 0.01}},
            {"id": "deadly_precision", "name": "Deadly Precision", "desc": "+0.25x crit multiplier / level", "base_cost": 500, "level_growth": 1.22, "individual_scale": 1.08, "effect": {"type": "crit_mult", "value": 0.25}},
            {"id": "auto_turret", "name": "Auto Turret", "desc": "+1 auto-click / sec / level", "base_cost": 1000, "level_growth": 1.23, "individual_scale": 1.10, "effect": {"type": "auto_cps", "value": 1.0}},
        ],
    },
}
CATEGORY_ORDER = ["click_power", "auto_income", "multipliers", "critical_chance"]
UPGRADE_BY_ID = {u["id"]: (cat_id, u) for cat_id, cat in UPGRADE_CATALOG.items() for u in cat["upgrades"]}

# ----------------------------------------------------------------------------
# STEP 6: GAME STATE (encapsulated in a class)
# ----------------------------------------------------------------------------
class GameState:
    """Holds all mutable game progress so we don't rely on scattered globals."""

    def __init__(self):
        self.score = 0
        self.click_power = 1
        self.clicks_total = 0
        self.click_speed = 0
        self.global_multiplier_bonus = 0.0  # additive bonus from multiplier upgrades
        self.crit_chance = 0.0
        self.crit_multiplier = 2.0
        self.auto_clicker_count = 0        # derived as auto-cps (can be fractional)
        self.auto_clicker_interval = 1.0    # legacy/display
        self.auto_clicker_timer = 0.0

        # Per-upgrade levels and per-category shared price scale
        self.upgrade_levels = {uid: 0 for uid in UPGRADE_BY_ID}
        self.category_scale = {cid: 1.0 for cid in UPGRADE_CATALOG}

        # Rebirth system
        self.rebirth_count = 0
        self.rebirth_cost = 1000
        self.rebirth_multiplier = 1.0

        # Skins
        self.current_skin = "Szomszéd"
        self.owned_skins = ["Szomszéd"]
        self.skin_multiplier = SKIN_MULTIPLIERS.get(self.current_skin, 1.0)
        self.gamble_timer = 0
        self.gamble_result = None

        # Legacy fields kept for migration
        self._legacy = {}

    def _migrate_legacy(self, d):
        # Best-effort migration from old tier-based save format.
        def _add(uid, levels):
            if levels and uid in self.upgrade_levels:
                self.upgrade_levels[uid] += int(levels)
        _add("finger_training", d.get("tier_click_power", 0))
        _add("intern", d.get("tier_passive_income", 0))
        _add("auto_turret", d.get("tier_auto_speed", 0))
        spent = (d.get("spent_click_power", 0) or 0) + (d.get("spent_passive_income", 0) or 0) + (d.get("spent_auto_speed", 0) or 0)
        # approximate shared scale pressure from prior spending
        if spent > 0:
            for cid in self.category_scale:
                self.category_scale[cid] = max(self.category_scale[cid], 1.0 + min(spent / 50000.0, 2.0))
        self.recompute_stats()

    def recompute_stats(self):
        self.click_power = 1
        self.click_speed = 0
        self.global_multiplier_bonus = 0.0
        self.crit_chance = 0.0
        self.crit_multiplier = 2.0
        self.auto_clicker_count = 0.0
        for uid, lvl in self.upgrade_levels.items():
            if lvl <= 0 or uid not in UPGRADE_BY_ID:
                continue
            _, udef = UPGRADE_BY_ID[uid]
            eff = udef["effect"]
            etype = eff["type"]
            val = eff["value"] * lvl
            if etype == "click_add":
                self.click_power += val
            elif etype == "passive_add":
                self.click_speed += val
            elif etype == "mult_add":
                self.global_multiplier_bonus += val
            elif etype == "crit_chance":
                self.crit_chance += val
            elif etype == "crit_mult":
                self.crit_multiplier += val
            elif etype == "auto_cps":
                self.auto_clicker_count += val
        self.crit_chance = min(0.75, max(0.0, self.crit_chance))
        self.crit_multiplier = max(1.0, self.crit_multiplier)
        if self.auto_clicker_count > 0:
            self.auto_clicker_interval = 1.0 / self.auto_clicker_count
        else:
            self.auto_clicker_interval = 1.0

    def total_multiplier(self):
        return self.rebirth_multiplier * self.skin_multiplier * (1.0 + self.global_multiplier_bonus)

    def get_upgrade_level(self, upgrade_id):
        return self.upgrade_levels.get(upgrade_id, 0)

    def get_upgrade_price(self, upgrade_id):
        cat_id, udef = UPGRADE_BY_ID[upgrade_id]
        lvl = self.get_upgrade_level(upgrade_id)
        cat_scale = self.category_scale.get(cat_id, 1.0)
        base = udef["base_cost"]
        growth = udef["level_growth"]
        indiv = udef["individual_scale"]
        # Distinct per-upgrade base/growth/individual scaling, plus shared category scale.
        price = base * (growth ** lvl) * (indiv ** lvl) * cat_scale
        return max(1, int(price))

    def buy_upgrade(self, upgrade_id):
        if upgrade_id not in UPGRADE_BY_ID:
            return False
        price = self.get_upgrade_price(upgrade_id)
        if self.score < price:
            return False
        cat_id, _ = UPGRADE_BY_ID[upgrade_id]
        self.score -= price
        self.upgrade_levels[upgrade_id] = self.get_upgrade_level(upgrade_id) + 1
        # Buying in a category increases shared cost of ALL upgrades in that category.
        self.category_scale[cat_id] = self.category_scale.get(cat_id, 1.0) * UPGRADE_CATALOG[cat_id]["shared_scale"]
        self.recompute_stats()
        return True

    def to_dict(self):
        return {
            "score": self.score,
            "clicks_total": self.clicks_total,
            "upgrade_levels": self.upgrade_levels,
            "category_scale": self.category_scale,
            "rebirth_count": self.rebirth_count,
            "rebirth_cost": self.rebirth_cost,
            "rebirth_multiplier": self.rebirth_multiplier,
            "current_skin": self.current_skin,
            "owned_skins": self.owned_skins,
            "skin_multiplier": self.skin_multiplier,
            "gamble_timer": self.gamble_timer,
            "gamble_result": self.gamble_result,
        }

    @classmethod
    def from_dict(cls, d):
        s = cls()
        s.score = d.get("score", 0)
        s.clicks_total = d.get("clicks_total", 0)
        s.rebirth_count = d.get("rebirth_count", 0)
        s.rebirth_cost = d.get("rebirth_cost", 1000)
        s.rebirth_multiplier = d.get("rebirth_multiplier", 1.0)
        s.current_skin = d.get("current_skin", "Szomszéd")
        s.owned_skins = d.get("owned_skins", ["Szomszéd"])
        s.skin_multiplier = d.get("skin_multiplier", SKIN_MULTIPLIERS.get(s.current_skin, 1.0))
        s.gamble_timer = d.get("gamble_timer", 0)
        s.gamble_result = d.get("gamble_result", None)

        if "upgrade_levels" in d:
            levels = d.get("upgrade_levels", {}) or {}
            for uid in s.upgrade_levels:
                try:
                    s.upgrade_levels[uid] = max(0, int(levels.get(uid, 0)))
                except Exception:
                    s.upgrade_levels[uid] = 0
            scales = d.get("category_scale", {}) or {}
            for cid in s.category_scale:
                try:
                    s.category_scale[cid] = max(1.0, float(scales.get(cid, 1.0)))
                except Exception:
                    s.category_scale[cid] = 1.0
            s.recompute_stats()
        else:
            # migrate legacy save
            s._migrate_legacy(d)
        return s


# ----------------------------------------------------------------------------
# STEP 7: SAVE / LOAD SYSTEM
# ----------------------------------------------------------------------------
SAVE_FILE = os.path.join(BASE, "clicker_save.json")


def save_game(state):
    try:
        with open(SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump(state.to_dict(), f, indent=2)
    except Exception as e:
        print(f"[CLICKER] Save failed: {e}")


def load_game():
    try:
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            d = json.load(f)
        print("[CLICKER] Save file loaded.")
        return GameState.from_dict(d)
    except (FileNotFoundError, json.JSONDecodeError, Exception) as e:
        print(f"[CLICKER] No save file found, starting fresh. ({e})")
        return GameState()


# ----------------------------------------------------------------------------
# STEP 8: UPGRADE CLASS (per-upgrade levels, category-linked dynamic pricing)
# ----------------------------------------------------------------------------
class Upgrade:
    def __init__(self, category_id, upgrade_def):
        self.category_id = category_id
        self.id = upgrade_def["id"]
        self.name = upgrade_def["name"]
        self.desc = upgrade_def["desc"]
        self.effect = upgrade_def["effect"]
        self.rect = pygame.Rect(0, 0, 280, 96)
        self.is_hovered = False

    @property
    def category(self):
        return UPGRADE_CATALOG[self.category_id]

    def get_level(self, state):
        return state.get_upgrade_level(self.id)

    def get_price(self, state):
        return state.get_upgrade_price(self.id)

    def can_afford(self, state):
        return state.score >= self.get_price(state)

    def apply(self, state):
        return state.buy_upgrade(self.id)

    def update(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def effect_text(self, lvl):
        e = self.effect
        t = e["type"]; v = e["value"]
        if t == "click_add":
            return f"+{int(v*lvl)} click (next +{int(v)})"
        if t == "passive_add":
            return f"+{int(v*lvl)}/s (next +{int(v)})"
        if t == "mult_add":
            return f"+{int(v*lvl*100)}% total (next +{int(v*100)}%)"
        if t == "crit_chance":
            return f"+{v*lvl*100:.1f}% crit (next +{v*100:.1f}%)"
        if t == "crit_mult":
            return f"+{v*lvl:.2f}x crit (next +{v:.2f}x)"
        if t == "auto_cps":
            return f"+{v*lvl:.0f}/s auto (next +{v:.0f})"
        return ""

    def draw(self, surf, state):
        price = self.get_price(state)
        lvl = self.get_level(state)
        affordable = state.score >= price
        base = self.category["color"]
        if not affordable:
            color = (80, 80, 95)
        elif self.is_hovered:
            color = tuple(min(255, c + 35) for c in base)
        else:
            color = base

        pygame.draw.rect(surf, color, self.rect, border_radius=10)
        pygame.draw.rect(surf, WHITE, self.rect, width=2, border_radius=10)

        pad = 10
        x = self.rect.x + pad
        y = self.rect.y + 8
        right = self.rect.right - pad

        name_surf = font_small.render(self.name, True, WHITE)
        lvl_surf = font_small.render(f"Lvl {lvl}", True, YELLOW)
        # trim name if overlapping level badge
        max_name_w = self.rect.w - lvl_surf.get_width() - pad * 3
        if name_surf.get_width() > max_name_w:
            nm = self.name
            while nm and font_tiny.render(nm + "…", True, WHITE).get_width() > max_name_w:
                nm = nm[:-1]
            name_surf = font_tiny.render(nm + "…", True, WHITE)
        surf.blit(name_surf, (x, y))
        surf.blit(lvl_surf, lvl_surf.get_rect(topright=(right, y)))

        desc_surf = font_tiny.render(self.desc, True, (235, 235, 245))
        if desc_surf.get_width() > self.rect.w - pad * 2:
            d = self.desc
            while d and font_tiny.render(d + "…", True, WHITE).get_width() > self.rect.w - pad * 2:
                d = d[:-1]
            desc_surf = font_tiny.render(d + "…", True, (235, 235, 245))
        surf.blit(desc_surf, (x, y + 22))

        eff_surf = font_tiny.render(self.effect_text(lvl), True, (210, 235, 210) if lvl > 0 else (200, 200, 215))
        if eff_surf.get_width() > self.rect.w - pad * 2:
            eff_surf = font_tiny.render(self.effect_text(lvl)[:28] + "…", True, (210, 235, 210))
        surf.blit(eff_surf, (x, y + 42))

        cost_surf = font_small.render(f"Cost: {format_num(price)}", True, YELLOW if affordable else (220, 220, 220))
        surf.blit(cost_surf, (x, self.rect.bottom - cost_surf.get_height() - 8))

    def is_clicked(self, event):
        return (
            event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and self.rect.collidepoint(event.pos)
        )


# ----------------------------------------------------------------------------
# STEP 9: BUILD ALL UPGRADE INSTANCES
# ----------------------------------------------------------------------------
PANEL_W = 360
PANEL_X = 0
PANEL_Y = 150

def build_upgrades():
    upgrades = []
    for cat_id in CATEGORY_ORDER:
        for udef in UPGRADE_CATALOG[cat_id]["upgrades"]:
            upgrades.append(Upgrade(cat_id, udef))
    return upgrades

all_upgrades = build_upgrades()


class CloseButton:
    """Small X button at top-right of the upgrades panel."""

    def __init__(self, x, y, w, h):
        self.rect = pygame.Rect(x, y, w, h)
        self.is_hovered = False

    def update(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def draw(self, surf):
        color = DARK_RED if self.is_hovered else RED
        pygame.draw.rect(surf, color, self.rect, border_radius=8)
        pygame.draw.rect(surf, WHITE, self.rect, width=2, border_radius=8)
        x_surf = font_med.render("X", True, WHITE)
        surf.blit(x_surf, x_surf.get_rect(center=self.rect.center))

    def is_clicked(self, event):
        return (
            event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and self.rect.collidepoint(event.pos)
        )


btn_close_upgrades = CloseButton(PANEL_W - 55, PANEL_Y + 10, 40, 40)

# ----------------------------------------------------------------------------
# STEP 10: SCROLLABLE PANEL LOGIC
# ----------------------------------------------------------------------------
scroll_offset = 0
max_scroll = 0
PANEL_CONTENT_H = 0
upgrade_layout = []  # (type, category_id|upgrade, rect)


def get_visible_upgrades():
    """Return (upgrade, draw_rect) pairs for upgrades that overlap the panel."""
    visible = []
    view_top = PANEL_Y + 70
    view_bottom = SCREEN_H - 12
    for kind, obj, rect in upgrade_layout:
        if kind != "upgrade":
            continue
        draw_rect = rect.copy()
        draw_rect.y -= scroll_offset
        if draw_rect.bottom > view_top and draw_rect.top < view_bottom:
            visible.append((obj, draw_rect))
    return visible


def get_visible_layout_items():
    items = []
    view_top = PANEL_Y + 70
    view_bottom = SCREEN_H - 12
    for kind, obj, rect in upgrade_layout:
        draw_rect = rect.copy()
        draw_rect.y -= scroll_offset
        if draw_rect.bottom > view_top and draw_rect.top < view_bottom:
            items.append((kind, obj, draw_rect))
    return items


# ----------------------------------------------------------------------------
# STEP 10b: UI HELPERS
# ----------------------------------------------------------------------------
def clamp_scroll(value, maximum):
    return max(0, min(value, maximum))


def clamp_text_rect(rect, container, padding=10):
    r = rect.copy()
    r.x = max(container.left + padding, min(r.x, container.right - r.w - padding))
    r.y = max(container.top + padding, min(r.y, container.bottom - r.h - padding))
    return r


def draw_text_pill(surf, text_surf, center, padding_x=14, padding_y=8, bg=TEXT_BG, border=WHITE):
    rect = text_surf.get_rect(center=center)
    pill = pygame.Rect(0, 0, rect.w + padding_x * 2, rect.h + padding_y * 2)
    pill.center = center
    pill = clamp_text_rect(pill, pygame.Rect(0, 0, SCREEN_W, SCREEN_H), padding=4)
    pygame.draw.rect(surf, bg, pill, border_radius=10)
    pygame.draw.rect(surf, border, pill, width=2, border_radius=10)
    surf.blit(text_surf, text_surf.get_rect(center=pill.center))
    return pill


def draw_button(surf, rect, label, mouse_pos, bg, hover_bg=None, text_color=WHITE, border=WHITE, font=font_med, enabled=True):
    if not enabled:
        color = GRAY
    else:
        color = hover_bg if (hover_bg and rect.collidepoint(mouse_pos)) else bg
    pygame.draw.rect(surf, color, rect, border_radius=10)
    pygame.draw.rect(surf, border, rect, width=3, border_radius=10)
    txt = font.render(label, True, text_color)
    surf.blit(txt, txt.get_rect(center=rect.center))


def next_rebirth_multiplier(state):
    return state.rebirth_multiplier * 2.0


def get_rebirth_info(state):
    progress = 0.0 if state.rebirth_cost <= 0 else min(1.0, state.score / state.rebirth_cost)
    return {
        "current": state.score,
        "required": state.rebirth_cost,
        "progress": progress,
        "percent": int(progress * 100),
        "count": state.rebirth_count + 1,
        "multiplier": next_rebirth_multiplier(state),
    }


def draw_rebirth_popup(surf, state, mouse_pos):
    overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
    overlay.fill(OVERLAY)
    surf.blit(overlay, (0, 0))

    box = pygame.Rect(0, 0, min(560, SCREEN_W - 40), min(460, SCREEN_H - 40))
    box.center = (SCREEN_W // 2, SCREEN_H // 2)
    pygame.draw.rect(surf, PANEL_BG, box, border_radius=16)
    pygame.draw.rect(surf, PANEL_BORDER, box, width=3, border_radius=16)

    info = get_rebirth_info(state)
    title = font_big.render(f"Rebirth #{info['count']}", True, YELLOW)
    surf.blit(title, title.get_rect(centerx=box.centerx, y=box.y + 18))
    subtitle = font_small.render("Reset progress for a permanent multiplier boost.", True, WHITE)
    surf.blit(subtitle, subtitle.get_rect(centerx=box.centerx, y=box.y + 62))

    rows = [
        ("Current Money", f"${format_num(info['current'])}"),
        ("Required Money", f"${format_num(info['required'])}"),
        ("Progress", f"{info['percent']}% (${format_num(min(info['current'], info['required']))}/${format_num(info['required'])})"),
        ("Rebirth Count", f"#{info['count']}"),
        ("Rebirth Rewards", f"x{info['multiplier']:.1f} total multiplier (permanent), reset upgrades/progress"),
    ]
    row_y = box.y + 100
    for label, value in rows:
        card = pygame.Rect(box.x + 24, row_y, box.w - 48, 44)
        pygame.draw.rect(surf, CARD_BG, card, border_radius=8)
        pygame.draw.rect(surf, (90, 90, 120), card, width=1, border_radius=8)
        ltxt = font_small.render(label, True, (220, 220, 235))
        vtxt = font_small.render(value, True, WHITE)
        surf.blit(ltxt, (card.x + 12, card.y + 12))
        vrect = vtxt.get_rect(midright=(card.right - 12, card.centery))
        if vrect.w > card.w - 180:
            vtxt = font_tiny.render(value, True, WHITE)
            vrect = vtxt.get_rect(midright=(card.right - 12, card.centery))
        vrect = clamp_text_rect(vrect, card, padding=6)
        surf.blit(vtxt, vrect)
        row_y += 50

    bar = pygame.Rect(box.x + 24, box.bottom - 122, box.w - 48, 24)
    pygame.draw.rect(surf, (30, 30, 45), bar, border_radius=8)
    pygame.draw.rect(surf, WHITE, bar, width=2, border_radius=8)
    fill_w = int(bar.w * info["progress"])
    if fill_w > 0:
        fill = pygame.Rect(bar.x, bar.y, fill_w, bar.h)
        pygame.draw.rect(surf, GREEN if info["progress"] >= 1.0 else BLUE, fill, border_radius=8)
    ptxt = font_small.render(f"{info['percent']}%", True, WHITE)
    surf.blit(ptxt, ptxt.get_rect(center=bar.center))

    btn_w, btn_h, gap = 170, 46, 20
    confirm_rect = pygame.Rect(box.centerx - btn_w - gap // 2, box.bottom - 78, btn_w, btn_h)
    close_rect = pygame.Rect(box.centerx + gap // 2, box.bottom - 78, btn_w, btn_h)
    draw_button(surf, confirm_rect, "Confirm Rebirth", mouse_pos, DARK_GREEN, GREEN, enabled=info["progress"] >= 1.0)
    draw_button(surf, close_rect, "Close", mouse_pos, DARK_RED, RED)
    return confirm_rect, close_rect


# ----------------------------------------------------------------------------
# Responsive layout
# ----------------------------------------------------------------------------
hud_area = pygame.Rect(0, 0, SCREEN_W, 200)
open_btn_rect = pygame.Rect(20, 250, 190, 50)
rebirth_btn_rect = pygame.Rect(20, 312, 190, 50)
skins_btn_rect = pygame.Rect(20, 374, 190, 50)
gamble_btn_rect = pygame.Rect(20, 436, 190, 50)
settings_btn_rect = pygame.Rect(20, 498, 190, 50)
scaled_click_size = 180
skin_cell_w = 190
skin_cell_h = 230
skin_thumb = 160
settings_open = False
settings_dragging_volume = False
settings_ui = {}


def get_skins_panel_rect():
    if upgrades_open:
        left = PANEL_W + 16
    else:
        left = open_btn_rect.right + 16
    right = SCREEN_W - 16
    top = hud_area.bottom + 6
    bottom = SCREEN_H - 16
    w = max(360, right - left)
    h = max(260, bottom - top)
    return pygame.Rect(left, top, w, h)


def draw_settings_popup(surf, mouse_pos, draft):
    global settings_ui
    overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
    overlay.fill(OVERLAY)
    surf.blit(overlay, (0, 0))

    box = pygame.Rect(0, 0, min(620, SCREEN_W - 40), min(460, SCREEN_H - 40))
    box.center = (SCREEN_W // 2, SCREEN_H // 2)
    pygame.draw.rect(surf, PANEL_BG, box, border_radius=16)
    pygame.draw.rect(surf, PANEL_BORDER, box, width=3, border_radius=16)

    title = font_big.render("Settings", True, YELLOW)
    surf.blit(title, title.get_rect(centerx=box.centerx, y=box.y + 18))

    ui = {"box": box}
    row_x = box.x + 28
    label_x = row_x
    control_x = box.x + 230
    control_w = box.w - 260

    # Volume
    vy = box.y + 78
    vlabel = font_small.render("Volume", True, WHITE)
    surf.blit(vlabel, (label_x, vy + 2))
    vtrack = pygame.Rect(control_x, vy + 10, control_w - 70, 10)
    pygame.draw.rect(surf, (35, 35, 50), vtrack, border_radius=5)
    fill_w = int(vtrack.w * (draft["volume"] / 100.0))
    if fill_w > 0:
        pygame.draw.rect(surf, GREEN, (vtrack.x, vtrack.y, fill_w, vtrack.h), border_radius=5)
    knob_x = vtrack.x + fill_w
    knob = pygame.Rect(0, 0, 16, 16)
    knob.center = (knob_x, vtrack.centery)
    pygame.draw.rect(surf, WHITE, knob, border_radius=8)
    vpct = font_small.render(f"{draft['volume']}%", True, YELLOW)
    surf.blit(vpct, (vtrack.right + 12, vy))
    ui["volume_track"] = vtrack.inflate(10, 18)

    # Resolution
    ry = vy + 54
    rlabel = font_small.render("Resolution", True, WHITE)
    surf.blit(rlabel, (label_x, ry + 6))
    res_btns = []
    bw = (control_w - 16) // 3
    for i, (rw, rh) in enumerate(RESOLUTION_OPTIONS):
        b = pygame.Rect(control_x + i * (bw + 8), ry, bw, 34)
        selected = (draft["resolution_index"] == i and not draft["fullscreen"])
        bg = BLUE if selected else CARD_BG
        hov = DARK_BLUE if b.collidepoint(mouse_pos) else bg
        pygame.draw.rect(surf, hov, b, border_radius=8)
        pygame.draw.rect(surf, YELLOW if selected else WHITE, b, width=2, border_radius=8)
        t = font_tiny.render(f"{rw}x{rh}", True, WHITE)
        surf.blit(t, t.get_rect(center=b.center))
        res_btns.append((i, b))
    ui["res_btns"] = res_btns

    fy = ry + 44
    fbtn = pygame.Rect(control_x, fy, 170, 34)
    selected_f = draft["fullscreen"]
    bg = BLUE if selected_f else CARD_BG
    pygame.draw.rect(surf, DARK_BLUE if fbtn.collidepoint(mouse_pos) else bg, fbtn, border_radius=8)
    pygame.draw.rect(surf, YELLOW if selected_f else WHITE, fbtn, width=2, border_radius=8)
    ft = font_tiny.render(f"Fullscreen: {'ON' if selected_f else 'OFF'}", True, WHITE)
    surf.blit(ft, ft.get_rect(center=fbtn.center))
    ui["fullscreen_btn"] = fbtn
    note = font_tiny.render("Resolution presets apply in windowed mode.", True, (210, 210, 225))
    surf.blit(note, (control_x + 182, fy + 9))

    # FPS
    fps_y = fy + 52
    flabel = font_small.render("FPS Cap", True, WHITE)
    surf.blit(flabel, (label_x, fps_y + 6))
    fps_btns = []
    fbw = (control_w - 32) // 5
    for i, opt in enumerate(FPS_OPTIONS):
        b = pygame.Rect(control_x + i * (fbw + 8), fps_y, fbw, 34)
        selected = draft["fps_index"] == i
        bg = BLUE if selected else CARD_BG
        pygame.draw.rect(surf, DARK_BLUE if b.collidepoint(mouse_pos) else bg, b, border_radius=8)
        pygame.draw.rect(surf, YELLOW if selected else WHITE, b, width=2, border_radius=8)
        t = font_tiny.render(str(opt), True, WHITE)
        surf.blit(t, t.get_rect(center=b.center))
        fps_btns.append((i, b))
    ui["fps_btns"] = fps_btns

    info = font_tiny.render("Settings are saved to settings.json and persist after restart.", True, (220, 220, 235))
    surf.blit(info, info.get_rect(centerx=box.centerx, y=box.bottom - 110))

    btn_w, btn_h, gap = 150, 44, 20
    apply_rect = pygame.Rect(box.centerx - btn_w - gap // 2, box.bottom - 70, btn_w, btn_h)
    close_rect = pygame.Rect(box.centerx + gap // 2, box.bottom - 70, btn_w, btn_h)
    draw_button(surf, apply_rect, "Apply", mouse_pos, DARK_GREEN, GREEN, font=font_small)
    draw_button(surf, close_rect, "Close", mouse_pos, DARK_RED, RED, font=font_small)
    ui["apply_btn"] = apply_rect
    ui["close_btn"] = close_rect

    settings_ui = ui
    return ui


def handle_settings_event(event, draft):
    global settings_open, settings, settings_dragging_volume, audio_volume, _draft_settings
    ui = settings_ui
    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        pos = event.pos
        if ui.get("volume_track") and ui["volume_track"].collidepoint(pos):
            settings_dragging_volume = True
            track = ui["volume_track"].inflate(-10, -18)
            rel = (pos[0] - track.left) / max(1, track.width)
            draft["volume"] = max(0, min(100, int(rel * 100)))
            return True
        for i, b in ui.get("res_btns", []):
            if b.collidepoint(pos):
                draft["resolution_index"] = i
                draft["fullscreen"] = False
                return True
        if ui.get("fullscreen_btn") and ui["fullscreen_btn"].collidepoint(pos):
            draft["fullscreen"] = not draft["fullscreen"]
            return True
        for i, b in ui.get("fps_btns", []):
            if b.collidepoint(pos):
                draft["fps_index"] = i
                return True
        if ui.get("apply_btn") and ui["apply_btn"].collidepoint(pos):
            settings = draft.copy()
            _draft_settings = draft.copy()
            save_settings(settings)
            audio_volume = settings["volume"] / 100.0
            try:
                if pygame.mixer.get_init():
                    pygame.mixer.music.set_volume(audio_volume)
            except Exception:
                pass
            apply_display_settings(settings)
            relayout_ui(state)
            return True
        if ui.get("close_btn") and ui["close_btn"].collidepoint(pos):
            settings_open = False
            _draft_settings = settings.copy()
            return True
        # click outside modal closes? keep explicit Close; ignore outside
        return True
    if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
        settings_dragging_volume = False
        return True
    if event.type == pygame.MOUSEMOTION and settings_dragging_volume:
        track = ui.get("volume_track")
        if track:
            t = track.inflate(-10, -18)
            rel = (event.pos[0] - t.left) / max(1, t.width)
            draft["volume"] = max(0, min(100, int(rel * 100)))
        return True
    return False


def apply_skin(name):
    global clicker_img, clicker_rect, scaled_click_size
    src = skin_source_images.get(name) or click_source_img
    clicker_img = pygame.transform.smoothscale(src, (scaled_click_size, scaled_click_size))
    cx = int(SCREEN_W * 0.58)
    cy = int(SCREEN_H * 0.58)
    menu_w = open_btn_rect.right + 20 if not upgrades_open else PANEL_W + 20
    cx = max(menu_w + scaled_click_size // 2 + 10, min(cx, SCREEN_W - scaled_click_size // 2 - 20))
    cy = max(hud_area.bottom + scaled_click_size // 2 + 10, min(cy, SCREEN_H - scaled_click_size // 2 - 50))
    clicker_rect = clicker_img.get_rect(center=(cx, cy))


def relayout_ui(state):
    global SCREEN_W, SCREEN_H, PANEL_W, PANEL_Y, max_scroll, PANEL_CONTENT_H, upgrade_layout
    global hud_area, open_btn_rect, rebirth_btn_rect, skins_btn_rect, gamble_btn_rect
    global btn_close_upgrades, scaled_click_size, skin_cell_w, skin_cell_h, skin_thumb, skin_images

    SCREEN_W, SCREEN_H = screen.get_size()
    hud_area = pygame.Rect(0, 0, SCREEN_W, max(150, int(SCREEN_H * 0.26)))

    menu_x = 16
    menu_w = max(170, min(220, int(SCREEN_W * 0.2)))
    menu_h = max(44, min(54, int(SCREEN_H * 0.075)))
    menu_gap = 10
    menu_start = hud_area.bottom + 20
    open_btn_rect = pygame.Rect(menu_x, menu_start, menu_w, menu_h)
    rebirth_btn_rect = pygame.Rect(menu_x, menu_start + (menu_h + menu_gap), menu_w, menu_h)
    skins_btn_rect = pygame.Rect(menu_x, menu_start + (menu_h + menu_gap) * 2, menu_w, menu_h)
    gamble_btn_rect = pygame.Rect(menu_x, menu_start + (menu_h + menu_gap) * 3, menu_w, menu_h)
    settings_btn_rect = pygame.Rect(menu_x, menu_start + (menu_h + menu_gap) * 4, menu_w, menu_h)

    PANEL_Y = hud_area.bottom
    PANEL_W = max(320, min(420, int(SCREEN_W * 0.36)))
    btn_close_upgrades.rect = pygame.Rect(PANEL_W - 48, PANEL_Y + 10, 36, 36)

    # upgrade panel layout (category headers + cards)
    upgrade_layout = []
    pad_x = 14
    card_w = PANEL_W - pad_x * 2
    card_h = 96
    gap = 10
    y = PANEL_Y + 74
    for cat_id in CATEGORY_ORDER:
        cat = UPGRADE_CATALOG[cat_id]
        hdr_h = 30
        upgrade_layout.append(("header", cat_id, pygame.Rect(pad_x, y, card_w, hdr_h)))
        y += hdr_h + 6
        for udef in cat["upgrades"]:
            upg = next((u for u in all_upgrades if u.id == udef["id"]), None)
            if not upg:
                continue
            rect = pygame.Rect(pad_x, y, card_w, card_h)
            upg.rect = rect
            upgrade_layout.append(("upgrade", upg, rect))
            y += card_h + gap
        y += 8
    PANEL_CONTENT_H = y - PANEL_Y + 20
    view_h = SCREEN_H - (PANEL_Y + 70) - 12
    max_scroll = max(0, PANEL_CONTENT_H - view_h)

    # responsive sizes for clicker and skins
    scaled_click_size = max(140, min(220, int(min(SCREEN_W, SCREEN_H) * 0.26)))
    skin_thumb = max(110, min(170, int(min(SCREEN_W, SCREEN_H) * 0.2)))
    skin_cell_w = skin_thumb + 30
    skin_cell_h = skin_thumb + 70
    skin_images = {name: pygame.transform.smoothscale(img, (skin_thumb, skin_thumb)) for name, img in skin_source_images.items()}

    apply_skin(state.current_skin if state.current_skin in skin_source_images else "Szomszéd")


def perform_rebirth(state):
    state.score = 0
    state.click_power = 1
    state.clicks_total = 0
    state.click_speed = 0
    state.global_multiplier_bonus = 0.0
    state.crit_chance = 0.0
    state.crit_multiplier = 2.0
    state.auto_clicker_count = 0.0
    state.auto_clicker_interval = 1.0
    state.auto_clicker_timer = 0.0
    state.upgrade_levels = {uid: 0 for uid in UPGRADE_BY_ID}
    state.category_scale = {cid: 1.0 for cid in UPGRADE_CATALOG}
    state.rebirth_count += 1
    state.rebirth_multiplier *= 2.0
    state.rebirth_cost = int(state.rebirth_cost * 10)
    state.recompute_stats()

# ----------------------------------------------------------------------------
# STEP 11: INITIALIZE STATE FROM SAVE
# ----------------------------------------------------------------------------
state = load_game()
if state.current_skin not in skin_source_images:
    state.current_skin = "Szomszéd"
state.skin_multiplier = SKIN_MULTIPLIERS.get(state.current_skin, 1.0)

running = True
upgrades_open = False
skins_open = False
rebirth_open = False
settings_open = False
rebirth_confirm_rect = None
rebirth_close_rect = None
skin_rects = []
skin_scroll = 0
pop_timer = 0
pop_scale = 1.0
crit_flash = 0
last_crit = 0

apply_display_settings(settings)
relayout_ui(state)

while running:
    mouse_pos = pygame.mouse.get_pos()
    dt = clock.tick(FPS_CAP) / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            save_game(state)
            save_settings(settings)
            running = False

        elif settings_open:
            if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION):
                handle_settings_event(event, _draft_settings)
            continue

        elif event.type == pygame.VIDEORESIZE:
            if not settings.get("fullscreen", False):
                new_w = max(MIN_W, event.w)
                new_h = max(MIN_H, event.h)
                screen = pygame.display.set_mode((new_w, new_h), pygame.RESIZABLE)
                SCREEN_W, SCREEN_H = screen.get_size()
                bg_img = load_background((SCREEN_W, SCREEN_H))
                best = 0; best_d = 10**9
                for i, (rw, rh) in enumerate(RESOLUTION_OPTIONS):
                    d = abs(rw - SCREEN_W) + abs(rh - SCREEN_H)
                    if d < best_d:
                        best_d = d; best = i
                settings["resolution_index"] = best
                _draft_settings["resolution_index"] = best
                save_settings(settings)
                relayout_ui(state)
                scroll_offset = clamp_scroll(scroll_offset, max_scroll)

        elif event.type == pygame.MOUSEWHEEL:
            if rebirth_open:
                pass
            elif skins_open and get_skins_panel_rect().collidepoint(mouse_pos):
                skin_scroll -= event.y * 40
            elif upgrades_open and pygame.Rect(PANEL_X, PANEL_Y, PANEL_W, SCREEN_H - PANEL_Y).collidepoint(mouse_pos):
                scroll_offset -= event.y * 30
                scroll_offset = clamp_scroll(scroll_offset, max_scroll)

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if rebirth_open:
                if rebirth_close_rect and rebirth_close_rect.collidepoint(event.pos):
                    rebirth_open = False
                elif rebirth_confirm_rect and rebirth_confirm_rect.collidepoint(event.pos):
                    if state.score >= state.rebirth_cost:
                        perform_rebirth(state)
                        relayout_ui(state)
                        rebirth_open = False
                        upgrades_open = False
                        skins_open = False
                        scroll_offset = 0
                        save_game(state)
                continue

            if clicker_rect.collidepoint(event.pos):
                is_crit = random.random() < state.crit_chance
                base_gain = state.click_power * state.total_multiplier()
                if is_crit:
                    base_gain *= state.crit_multiplier
                    crit_flash = 20
                    last_crit = int(base_gain)
                gain = int(base_gain)
                state.score += gain
                state.clicks_total += 1
                pop_timer = 10
                pop_scale = 1.25
                save_game(state)
                continue

            if upgrades_open and btn_close_upgrades.is_clicked(event):
                upgrades_open = False
                continue

            if upgrades_open:
                panel_area = pygame.Rect(PANEL_X, PANEL_Y, PANEL_W, SCREEN_H - PANEL_Y)
                if panel_area.collidepoint(event.pos):
                    clicked_upgrade = False
                    for upg, draw_rect in get_visible_upgrades():
                        saved_rect = upg.rect
                        upg.rect = draw_rect
                        if upg.is_clicked(event):
                            clicked_upgrade = True
                            if upg.apply(state):
                                # shared category scaling happens in buy_upgrade
                                save_game(state)
                            upg.rect = saved_rect
                            break
                        upg.rect = saved_rect
                    if clicked_upgrade:
                        continue

            if skins_open:
                panel_rect = get_skins_panel_rect()
                clicked_skin = False
                if panel_rect.collidepoint(event.pos):
                    for name, r in skin_rects:
                        if r.collidepoint(event.pos):
                            clicked_skin = True
                            if name in state.owned_skins:
                                state.current_skin = name
                                state.skin_multiplier = SKIN_MULTIPLIERS.get(name, 1.0)
                                apply_skin(name)
                                save_game(state)
                            else:
                                required = list(SKIN_FILES.keys()).index(name)
                                if state.rebirth_count >= required:
                                    state.owned_skins.append(name)
                                    state.current_skin = name
                                    state.skin_multiplier = SKIN_MULTIPLIERS.get(name, 1.0)
                                    apply_skin(name)
                                    save_game(state)
                            break
                if clicked_skin:
                    continue

            if not upgrades_open:
                if open_btn_rect.collidepoint(event.pos):
                    upgrades_open = True
                    skins_open = False
                    relayout_ui(state)
                    scroll_offset = clamp_scroll(scroll_offset, max_scroll)
                    continue
                if rebirth_btn_rect.collidepoint(event.pos):
                    rebirth_open = True
                    continue
                if skins_btn_rect.collidepoint(event.pos):
                    skins_open = not skins_open
                    continue
                if gamble_btn_rect.collidepoint(event.pos):
                    if state.gamble_timer == 0 and state.score >= 100000:
                        state.score -= 100000
                        reward = random.choice(list(SKIN_FILES.keys())[4:])
                        state.gamble_timer = 120
                        state.gamble_result = reward
                        save_game(state)
                    continue
                if settings_btn_rect.collidepoint(event.pos):
                    _draft_settings = settings.copy()
                    settings_open = True
                    settings_dragging_volume = False
                    continue
    # --- UPDATE ---
    if not rebirth_open:
        btn_close_upgrades.update(mouse_pos)
        if upgrades_open:
            for upg, draw_rect in get_visible_upgrades():
                saved_rect = upg.rect
                upg.rect = draw_rect
                upg.update(mouse_pos)
                upg.rect = saved_rect

    if pop_timer > 0:
        pop_timer -= 1
        pop_scale = 1.0 + (0.25 * (pop_timer / 10))
    else:
        pop_scale = 1.0
    if crit_flash > 0:
        crit_flash -= 1

    # Passive income and auto-clicking
    total_mult = state.total_multiplier()
    state.score += state.click_speed * total_mult * dt

    if state.gamble_timer > 0:
        state.gamble_timer -= 1
        if state.gamble_timer == 0 and state.gamble_result:
            reward = state.gamble_result
            if reward in state.owned_skins:
                state.score += 10000
            else:
                state.owned_skins.append(reward)
            state.gamble_result = None
            save_game(state)

    if state.auto_clicker_count > 0:
        state.auto_clicker_timer += dt * state.auto_clicker_count
        while state.auto_clicker_timer >= 1.0:
            state.auto_clicker_timer -= 1.0
            state.score += int(state.click_power * total_mult)
            state.clicks_total += 1

    # --- DRAWING ---
    screen.blit(bg_img, (0, 0))

    # Clickable picture
    draw_w = int(scaled_click_size * pop_scale)
    draw_h = int(scaled_click_size * pop_scale)
    if draw_w != clicker_img.get_width() or draw_h != clicker_img.get_height():
        scaled = pygame.transform.smoothscale(skin_source_images.get(state.current_skin, click_source_img), (draw_w, draw_h))
        scaled_rect = scaled.get_rect(center=clicker_rect.center)
        screen.blit(scaled, scaled_rect)
    else:
        screen.blit(clicker_img, clicker_rect)

    # HUD
    pts_click = int(state.click_power * total_mult)
    stats = [
        font_big.render(f"Score: {format_num(state.score)}", True, YELLOW),
        font_med.render(f"Points/click: {format_num(pts_click)}  (+{int(state.click_speed*total_mult)}/s passive)", True, WHITE),
        font_small.render(f"Clicks: {format_num(state.clicks_total)}  |  Rebirth: #{state.rebirth_count}  |  Total Mult: x{total_mult:.2f}", True, WHITE),
    ]
    extra = []
    if state.crit_chance > 0 or state.crit_multiplier > 2.0:
        extra.append(f"Crit: {state.crit_chance*100:.1f}% x{state.crit_multiplier:.2f}")
    if state.auto_clicker_count > 0:
        extra.append(f"Auto: {format_num(state.auto_clicker_count)}/s")
    if extra:
        stats.append(font_small.render("  |  ".join(extra), True, GREEN))
    hud_y = 22
    for s in stats:
        pill = draw_text_pill(screen, s, (SCREEN_W // 2, hud_y + s.get_height() // 2))
        hud_y = pill.bottom + 6
    if crit_flash > 0 and last_crit:
        ctext = font_med.render(f"CRIT! +{format_num(last_crit)}", True, YELLOW)
        draw_text_pill(screen, ctext, (clicker_rect.centerx, clicker_rect.top - 24), bg=(120, 80, 0))

    # Upgrades panel
    if upgrades_open:
        panel_rect = pygame.Rect(PANEL_X, PANEL_Y, PANEL_W, SCREEN_H - PANEL_Y)
        pygame.draw.rect(screen, PANEL_BG, panel_rect)
        pygame.draw.rect(screen, PANEL_BORDER, panel_rect, width=3)
        panel_title = font_med.render("UPGRADES", True, YELLOW)
        screen.blit(panel_title, (PANEL_X + 16, PANEL_Y + 14))
        if max_scroll > 0:
            scroll_text = font_tiny.render(f"Scroll: {scroll_offset}/{max_scroll}", True, (200, 200, 210))
            screen.blit(scroll_text, (PANEL_X + 16, PANEL_Y + 44))

        old_clip = screen.get_clip()
        screen.set_clip(pygame.Rect(PANEL_X, PANEL_Y + 70, PANEL_W, SCREEN_H - PANEL_Y - 80))
        for kind, obj, draw_rect in get_visible_layout_items():
            if kind == "header":
                cat = UPGRADE_CATALOG[obj]
                label = font_small.render(cat["label"], True, WHITE)
                scale = state.category_scale.get(obj, 1.0)
                note = font_tiny.render(f"Shared price x{scale:.2f} (buying any raises all)", True, (230, 230, 180))
                pygame.draw.rect(screen, (45, 45, 70), draw_rect, border_radius=6)
                screen.blit(label, (draw_rect.x + 8, draw_rect.y + 2))
                screen.blit(note, (draw_rect.x + 8, draw_rect.y + 16))
            elif kind == "upgrade":
                saved_rect = obj.rect
                obj.rect = draw_rect
                obj.draw(screen, state)
                obj.rect = saved_rect
        screen.set_clip(old_clip)
        btn_close_upgrades.draw(screen)

    # Menu buttons
    if not upgrades_open and not settings_open:
        draw_button(screen, open_btn_rect, "Upgrades", mouse_pos, PINK, DARK_BLUE)
        rebirth_ready = state.score >= state.rebirth_cost
        draw_button(screen, rebirth_btn_rect, "Rebirth", mouse_pos, RED, DARK_BLUE)
        draw_button(screen, skins_btn_rect, "Skins", mouse_pos, BLUE, DARK_BLUE)
        draw_button(screen, gamble_btn_rect, "Gamble", mouse_pos, (180, 100, 0), DARK_BLUE, enabled=state.score >= 100000)
        draw_button(screen, settings_btn_rect, "Settings", mouse_pos, (90, 90, 120), DARK_BLUE)
        sub = font_tiny.render(f"Cost: {format_num(state.rebirth_cost)}", True, YELLOW if rebirth_ready else (220, 220, 220))
        screen.blit(sub, sub.get_rect(centerx=rebirth_btn_rect.centerx, y=rebirth_btn_rect.bottom - 16))
        gsub = font_tiny.render("100000", True, YELLOW if state.score >= 100000 else (220, 220, 220))
        screen.blit(gsub, gsub.get_rect(centerx=gamble_btn_rect.centerx, y=gamble_btn_rect.bottom - 16))

    skin_rects = []
    if skins_open and not rebirth_open:
        panel_rect = get_skins_panel_rect()
        pygame.draw.rect(screen, PANEL_BG, panel_rect, border_radius=10)
        pygame.draw.rect(screen, PANEL_BORDER, panel_rect, width=3, border_radius=10)
        title = font_med.render("SKINS", True, YELLOW)
        screen.blit(title, (panel_rect.x + 16, panel_rect.y + 12))
        hint = font_tiny.render("Select unlocked skins. Locked skins unlock with rebirths.", True, (220, 220, 235))
        screen.blit(hint, (panel_rect.x + 16, panel_rect.y + 40))

        grid_top = panel_rect.y + 64
        grid_bottom = panel_rect.bottom - 12
        cols = max(1, (panel_rect.w - 24) // skin_cell_w)
        rows = (len(SKIN_FILES) + cols - 1) // cols
        content_h = rows * skin_cell_h
        view_h = max(0, grid_bottom - grid_top)
        max_skin_scroll = max(0, content_h - view_h)
        skin_scroll = clamp_scroll(skin_scroll, max_skin_scroll)

        old_clip = screen.get_clip()
        screen.set_clip(pygame.Rect(panel_rect.x + 8, grid_top, panel_rect.w - 16, view_h))
        x0 = panel_rect.x + 16
        x = x0
        y = grid_top - skin_scroll
        for name in SKIN_FILES:
            r = pygame.Rect(x, y, skin_thumb, skin_thumb)
            if r.bottom >= grid_top and r.top <= grid_bottom:
                skin_rects.append((name, r))
                img = skin_images.get(name)
                if img:
                    screen.blit(img, r)
                selected = state.current_skin == name
                owned = name in state.owned_skins
                border_col = GREEN if selected else (WHITE if owned else GRAY)
                pygame.draw.rect(screen, border_col, r, width=3, border_radius=8)
                label = font_tiny.render(name, True, WHITE)
                screen.blit(label, label.get_rect(centerx=r.centerx, y=r.bottom + 4))
                mult = SKIN_MULTIPLIERS.get(name, 1.0)
                subtxt = f"x{mult:.2f}" if owned else f"Req {list(SKIN_FILES.keys()).index(name)} rebirths"
                sub = font_tiny.render(subtxt, True, YELLOW if not owned else (210, 210, 225))
                screen.blit(sub, sub.get_rect(centerx=r.centerx, y=r.bottom + 20))
            x += skin_cell_w
            if x + skin_thumb > panel_rect.right - 8:
                x = x0
                y += skin_cell_h
        screen.set_clip(old_clip)
        if max_skin_scroll > 0:
            st = font_tiny.render(f"Scroll: {skin_scroll}/{max_skin_scroll}", True, (220, 220, 235))
            screen.blit(st, (panel_rect.right - st.get_width() - 14, panel_rect.y + 14))

    # Gambling animation
    if state.gamble_timer > 60:
        names = list(SKIN_FILES.keys())[4:]
        offset = (120 - state.gamble_timer) * 12
        for i, nm in enumerate(names * 3):
            x = SCREEN_W - (i * 120) + (offset % max(1, (len(names) * 120)))
            img = skin_images.get(nm) or clicker_img
            r = pygame.Rect(x, 12, 90, 90)
            if r.right > 0 and r.left < SCREEN_W:
                screen.blit(pygame.transform.smoothscale(skin_source_images.get(nm, click_source_img), (90, 90)), r)
                pygame.draw.rect(screen, WHITE, r, width=2, border_radius=6)
        center_rect = pygame.Rect(SCREEN_W // 2 - 45, 12, 90, 90)
        pygame.draw.rect(screen, YELLOW, center_rect, width=4, border_radius=6)
    elif state.gamble_timer > 0 and state.gamble_result:
        img = skin_source_images.get(state.gamble_result, click_source_img)
        r = pygame.Rect(SCREEN_W // 2 - 80, 12, 160, 160)
        screen.blit(pygame.transform.smoothscale(img, (160, 160)), r)
        pygame.draw.rect(screen, YELLOW, r, width=4, border_radius=8)
        txt = font_med.render(f"You got: {state.gamble_result}", True, WHITE)
        draw_text_pill(screen, txt, (SCREEN_W // 2, 190), bg=(20, 20, 35))

    # Rebirth modal
    if rebirth_open:
        rebirth_confirm_rect, rebirth_close_rect = draw_rebirth_popup(screen, state, mouse_pos)
    else:
        rebirth_confirm_rect, rebirth_close_rect = None, None

    # Settings modal (on top)
    if settings_open:
        draw_settings_popup(screen, mouse_pos, _draft_settings)

    instr_text = "Click the picture to earn points. Upgrades scale by category."
    if rebirth_open:
        instr_text = "Confirm rebirth when ready, or close this window."
    elif settings_open:
        instr_text = "Adjust settings and press Apply, or Close to discard."
    instr = font_small.render(instr_text, True, WHITE)
    draw_text_pill(screen, instr, (SCREEN_W // 2, SCREEN_H - 22), padding_x=12, padding_y=6)

    pygame.display.flip()

save_game(state)
pygame.quit()
sys.exit()
