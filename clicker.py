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
    n = int(n)
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n/1_000:.1f}k"
    return str(n)
# ----------------------------------------------------------------------------
SCREEN_W, SCREEN_H = 1000, 700
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("Clicker Sim - Tiered Upgrades")
clock = pygame.time.Clock()
FPS = 60

# ----------------------------------------------------------------------------
# STEP 2: COLORS
# ----------------------------------------------------------------------------
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
BLUE = (0, 120, 255)
DARK_BLUE = (0, 90, 200)
RED = (200, 50, 50)
YELLOW = (255, 220, 0)
GREEN = (0, 200, 0)
PINK = pygame.Color("pink")
PANEL_BG = (40, 40, 60)
PANEL_BORDER = WHITE

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
BASE = os.path.dirname(os.path.abspath(__file__))

bg_path = os.path.join(BASE, "bgp.webp")
try:
    bg_img = pygame.image.load(bg_path).convert()
    bg_img = pygame.transform.scale(bg_img, (SCREEN_W, SCREEN_H))
    print("[CLICKER] Loaded background: bgp.webp")
except (pygame.error, FileNotFoundError):
    print("[CLICKER] bgp.webp not found, using solid color.")
    bg_img = pygame.Surface((SCREEN_W, SCREEN_H))
    bg_img.fill((30, 30, 50))

click_path = os.path.join(BASE, "clickPIC.jpg")
try:
    clicker_img = pygame.image.load(click_path).convert_alpha()
    clicker_img = pygame.transform.scale(clicker_img, (180, 180))
    print("[CLICKER] Loaded click picture: clickPIC.jpg")
except (pygame.error, FileNotFoundError):
    print("[CLICKER] clickPIC.jpg not found, using fallback color.")
    clicker_img = pygame.Surface((180, 180), pygame.SRCALPHA)
    clicker_img.fill(GREEN)

clicker_rect = clicker_img.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2))

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
        img = pygame.transform.scale(img, (180, 180))
        return img
    except (pygame.error, FileNotFoundError):
        print(f"[CLICKER] skin {name} not found")
        surf = pygame.Surface((180, 180))
        surf.fill((random.randint(50,200), random.randint(50,200), random.randint(50,200)))
        txt = font_small.render(name, True, WHITE)
        surf.blit(txt, txt.get_rect(center=(90,90)))
        return surf

skin_images = {name: load_skin_image(name) for name in SKIN_FILES}

# ----------------------------------------------------------------------------
# STEP 5: TIER CONFIGURATION (data-driven upgrade definitions)
# ----------------------------------------------------------------------------
# Each category defines the bonus per tier and the base cost per tier.
# Dynamic pricing: next price = cumulative spent in category + base cost of this tier.
TIER_CONFIG = {
    "click_power": {
        "label": "Click Power",
        "bonuses": [5, 10, 25, 50, 100, 250, 500, 1000],
        "base_costs": [10, 50, 200, 800, 3000, 12000, 50000, 200000],
        "suffix": " per click",
    },
    "passive_income": {
        "label": "Passive Income",
        "bonuses": [5, 10, 25, 50, 100, 250, 500, 1000],
        "base_costs": [50, 200, 800, 3000, 12000, 50000, 200000, 800000],
        "suffix": " per second",
    },
    "auto_clicker_speed": {
        "label": "Auto-Clicker Speed",
        # Interval in seconds between auto-clicks (lower = faster)
        "intervals": [1.0, 0.6, 0.4, 0.25, 0.15, 0.1],
        "base_costs": [100, 500, 2000, 8000, 30000, 100000],
        "suffix": " interval",
    },
}

MAX_TIERS = {
    "click_power": len(TIER_CONFIG["click_power"]["bonuses"]),
    "passive_income": len(TIER_CONFIG["passive_income"]["bonuses"]),
    "auto_clicker_speed": len(TIER_CONFIG["auto_clicker_speed"]["intervals"]),
}

# ----------------------------------------------------------------------------
# STEP 6: GAME STATE (encapsulated in a class)
# ----------------------------------------------------------------------------
class GameState:
    """Holds all mutable game progress so we don't rely on scattered globals."""

    def __init__(self):
        self.score = 0
        self.click_power = 1          # base click power (starts at 1)
        self.clicks_total = 0

        # Passive income (points per second)
        self.click_speed = 0          # sum of passive tier bonuses

        # Auto-clicker
        self.auto_clicker_count = 0   # how many auto-clickers owned
        self.auto_clicker_interval = 1.0  # seconds between auto-clicks
        self.auto_clicker_timer = 0.0

        # Tier levels (how many tiers purchased in each category)
        self.tier_click_power = 0
        self.tier_passive_income = 0
        self.tier_auto_speed = 0

        # Cumulative spend per category (used for dynamic pricing)
        self.spent_click_power = 0
        self.spent_passive_income = 0
        self.spent_auto_speed = 0

        # Rebirth system
        self.rebirth_count = 0          # how many times rebirthed
        self.rebirth_cost = 1000        # cost of next rebirth (x10 each time)
        self.rebirth_multiplier = 1.0   # global multiplier on all gains

        # Skins
        self.current_skin = "Szomszéd"
        self.owned_skins = ["Szomszéd"]
        self.skin_multiplier = SKIN_MULTIPLIERS.get(self.current_skin, 1.0)
        self.gamble_timer = 0
        self.gamble_result = None

    def to_dict(self):
        return {
            "score": self.score,
            "click_power": self.click_power,
            "clicks_total": self.clicks_total,
            "click_speed": self.click_speed,
            "auto_clicker_count": self.auto_clicker_count,
            "auto_clicker_interval": self.auto_clicker_interval,
            "tier_click_power": self.tier_click_power,
            "tier_passive_income": self.tier_passive_income,
            "tier_auto_speed": self.tier_auto_speed,
            "spent_click_power": self.spent_click_power,
            "spent_passive_income": self.spent_passive_income,
            "spent_auto_speed": self.spent_auto_speed,
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
        s.click_power = d.get("click_power", 1)
        s.clicks_total = d.get("clicks_total", 0)
        s.click_speed = d.get("click_speed", 0)
        s.auto_clicker_count = d.get("auto_clicker_count", 0)
        s.auto_clicker_interval = d.get("auto_clicker_interval", 1.0)
        s.tier_click_power = d.get("tier_click_power", 0)
        s.tier_passive_income = d.get("tier_passive_income", 0)
        s.tier_auto_speed = d.get("tier_auto_speed", 0)
        s.spent_click_power = d.get("spent_click_power", 0)
        s.spent_passive_income = d.get("spent_passive_income", 0)
        s.spent_auto_speed = d.get("spent_auto_speed", 0)
        s.rebirth_count = d.get("rebirth_count", 0)
        s.rebirth_cost = d.get("rebirth_cost", 1000)
        s.rebirth_multiplier = d.get("rebirth_multiplier", 1.0)
        s.current_skin = d.get("current_skin", "default")
        s.owned_skins = d.get("owned_skins", ["Szomszéd"])
        s.skin_multiplier = d.get("skin_multiplier", SKIN_MULTIPLIERS.get(s.current_skin, 1.0))
        s.gamble_timer = d.get("gamble_timer", 0)
        s.gamble_result = d.get("gamble_result", None)
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
# STEP 8: UPGRADE CLASS (data-driven, reusable for any tier)
# ----------------------------------------------------------------------------
class Upgrade:
    """
    Represents a single purchasable tier of an upgrade category.
    self.name   : display text
    self.price  : current cost to buy this tier
    self.category: which stat it affects
    self.tier_index: which tier number this is (0-based)
    self.bonus  : the bonus value applied when purchased
    """

    def __init__(self, category, tier_index, x, y, w, h):
        self.category = category
        self.tier_index = tier_index
        self.rect = pygame.Rect(x, y, w, h)
        self.is_hovered = False

        cfg = TIER_CONFIG[category]
        if "bonuses" in cfg:
            self.bonus = cfg["bonuses"][tier_index]
        else:
            self.bonus = cfg["intervals"][tier_index]
        self.base_cost = cfg["base_costs"][tier_index]
        self.label = cfg["label"]
        self.suffix = cfg["suffix"]

        self.price = 0  # computed by manager based on state

    def update_price_from_state(self, state):
        """Recompute price based on cumulative spend in this category."""
        spent = {
            "click_power": state.spent_click_power,
            "passive_income": state.spent_passive_income,
            "auto_clicker_speed": state.spent_auto_speed,
        }[self.category]
        # Price = cumulative spent + base cost of this tier.
        # Guarantees each tier costs more than all previous combined.
        self.price = spent + self.base_cost

    def can_afford(self, state):
        return state.score >= self.price

    def apply(self, state):
        """Purchase this tier: deduct score, apply bonus, increase tier level."""
        if not self.can_afford(state):
            return False

        state.score -= self.price

        if self.category == "click_power":
            state.click_power += self.bonus
            state.tier_click_power += 1
            state.spent_click_power += self.price
        elif self.category == "passive_income":
            state.click_speed += self.bonus
            state.tier_passive_income += 1
            state.spent_passive_income += self.price
        elif self.category == "auto_clicker_speed":
            # Lower the interval (faster clicks). Never below 0.05.
            if self.bonus < state.auto_clicker_interval:
                state.auto_clicker_interval = max(0.05, self.bonus)
            state.tier_auto_speed += 1
            state.spent_auto_speed += self.price

        return True

    def update(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def draw(self, surf, state):
        self.update_price_from_state(state)
        if not self.can_afford(state):
            color = GRAY  # grayed out if too expensive
        else:
            color = DARK_BLUE if self.is_hovered else BLUE

        pygame.draw.rect(surf, color, self.rect, border_radius=8)
        pygame.draw.rect(surf, WHITE, self.rect, width=2, border_radius=8)

        name_surf = font_med.render(f"{self.label} {self.tier_index + 1}", True, WHITE)
        cost_surf = font_small.render(f"Cost: {format_num(self.price)}", True, YELLOW)
        bonus_surf = font_tiny.render(f"+{self.bonus}{self.suffix}", True, WHITE)

        total_h = name_surf.get_height() + cost_surf.get_height() + bonus_surf.get_height() + 10
        start_y = self.rect.centery - total_h // 2

        name_rect = name_surf.get_rect(centerx=self.rect.centerx, y=start_y)
        cost_rect = cost_surf.get_rect(centerx=self.rect.centerx,
                                       y=start_y + name_surf.get_height() + 4)
        bonus_rect = bonus_surf.get_rect(centerx=self.rect.centerx,
                                         y=start_y + name_surf.get_height()
                                         + cost_surf.get_height() + 8)

        surf.blit(name_surf, name_rect)
        surf.blit(cost_surf, cost_rect)
        surf.blit(bonus_surf, bonus_rect)

    def is_clicked(self, event):
        return (
            event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and self.rect.collidepoint(event.pos)
        )


# ----------------------------------------------------------------------------
# STEP 9: BUILD ALL UPGRADE INSTANCES (data-driven, no hardcoded buttons)
# ----------------------------------------------------------------------------
PANEL_W = 340
PANEL_X = 0
PANEL_Y = 150
BTN_W = 280
BTN_H = 80
BTN_X = (PANEL_W - BTN_W) // 2
BTN_GAP = 100

def build_upgrades():
    """Create one Upgrade object per tier per category."""
    upgrades = []
    BTN_Y_START = 200

    # Click Power tiers
    for i in range(MAX_TIERS["click_power"]):
        upgrades.append(Upgrade("click_power", i, BTN_X, BTN_Y_START + i * BTN_GAP,
                                BTN_W, BTN_H))

    # Passive Income tiers
    passive_start = BTN_Y_START + MAX_TIERS["click_power"] * BTN_GAP + 40
    for i in range(MAX_TIERS["passive_income"]):
        upgrades.append(Upgrade("passive_income", i, BTN_X, passive_start + i * BTN_GAP,
                                BTN_W, BTN_H))

    # Auto-Clicker Speed tiers
    auto_start = passive_start + MAX_TIERS["passive_income"] * BTN_GAP + 40
    for i in range(MAX_TIERS["auto_clicker_speed"]):
        upgrades.append(Upgrade("auto_clicker_speed", i, BTN_X, auto_start + i * BTN_GAP,
                                BTN_W, BTN_H))

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
        color = (150, 40, 40) if self.is_hovered else RED
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


btn_close_upgrades = CloseButton(PANEL_W - 60, 170, 40, 40)

# ----------------------------------------------------------------------------
# STEP 10: SCROLLABLE PANEL LOGIC
# ----------------------------------------------------------------------------
PANEL_CONTENT_H = (MAX_TIERS["click_power"] + MAX_TIERS["passive_income"] +
                   MAX_TIERS["auto_clicker_speed"]) * BTN_GAP + 200
scroll_offset = 0
max_scroll = max(0, PANEL_CONTENT_H - (SCREEN_H - PANEL_Y - 40))

def get_visible_upgrades():
    """Return (upgrade, draw_rect) pairs for upgrades that overlap the panel."""
    visible = []
    for upg in all_upgrades:
        draw_rect = upg.rect.copy()
        draw_rect.y -= scroll_offset
        if draw_rect.bottom > PANEL_Y + 60 and draw_rect.top < SCREEN_H - 20:
            visible.append((upg, draw_rect))
    return visible

# ----------------------------------------------------------------------------
# STEP 11: INITIALIZE STATE FROM SAVE
# ----------------------------------------------------------------------------
state = load_game()
if state.current_skin not in skin_images:
    state.current_skin = "Szomszéd"
if state.current_skin in skin_images:
    clicker_img = skin_images[state.current_skin]
    clicker_rect = clicker_img.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2))

# ----------------------------------------------------------------------------
# STEP 12: MAIN GAME LOOP
# ----------------------------------------------------------------------------
running = True
upgrades_open = False
skins_open = False
skin_rects = []
skin_scroll = 0
pop_timer = 0
pop_scale = 1.0

# "Open Upgrades" button rect (left middle, only when panel closed)
open_btn_rect = pygame.Rect(20, SCREEN_H // 2 - 25, 180, 50)

# Rebirth button (under Upgrades)
rebirth_btn_rect = pygame.Rect(20, SCREEN_H // 2 + 35, 180, 50)

# Skins button (under Rebirth)
skins_btn_rect = pygame.Rect(20, SCREEN_H // 2 + 95, 180, 50)

# Gambling button (under Skins)
gamble_btn_rect = pygame.Rect(20, SCREEN_H // 2 + 155, 180, 50)

while running:
    mouse_pos = pygame.mouse.get_pos()

    # --- EVENT HANDLING ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            save_game(state)
            running = False

        # Mouse wheel: scroll the upgrades panel
        if event.type == pygame.MOUSEWHEEL and upgrades_open:
            scroll_offset -= event.y * 30
            scroll_offset = max(0, min(scroll_offset, max_scroll))
        if event.type == pygame.MOUSEWHEEL and skins_open:
            skin_scroll -= event.y * 30
            skin_scroll = max(0, skin_scroll)

        # --- Click on the big clickable picture ---
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if clicker_rect.collidepoint(event.pos):
                gain = int(state.click_power * state.rebirth_multiplier * state.skin_multiplier)
                state.score += gain
                state.clicks_total += 1
                pop_timer = 10
                pop_scale = 1.3
                save_game(state)

            # --- Open Upgrades button (only when panel closed) ---
            if not upgrades_open and open_btn_rect.collidepoint(event.pos):
                upgrades_open = True

            # --- Rebirth button (only when panel closed) ---
            if not upgrades_open and rebirth_btn_rect.collidepoint(event.pos):
                if state.score >= state.rebirth_cost:
                    state.score = 0
                    state.click_power = 1
                    state.clicks_total = 0
                    state.click_speed = 0
                    state.auto_clicker_count = 0
                    state.auto_clicker_interval = 1.0
                    state.auto_clicker_timer = 0.0
                    state.tier_click_power = 0
                    state.tier_passive_income = 0
                    state.tier_auto_speed = 0
                    state.spent_click_power = 0
                    state.spent_passive_income = 0
                    state.spent_auto_speed = 0
                    state.rebirth_count += 1
                    state.rebirth_multiplier *= 2.0
                    state.rebirth_cost = int(state.rebirth_cost * 10)
                    save_game(state)

            # --- Skins button ---
            if not upgrades_open and skins_btn_rect.collidepoint(event.pos):
                skins_open = not skins_open

            # --- Gambling button ---
            if not upgrades_open and gamble_btn_rect.collidepoint(event.pos):
                if state.gamble_timer == 0 and state.score >= 100000:
                    state.score -= 100000
                    reward = random.choice(list(SKIN_FILES.keys())[4:])
                    state.gamble_timer = 120
                    state.gamble_result = reward
                    save_game(state)

            # --- Clicks inside the upgrades panel ---
            if upgrades_open:
                if btn_close_upgrades.is_clicked(event):
                    upgrades_open = False

                for upg, draw_rect in get_visible_upgrades():
                    # Temporarily swap rect for click detection
                    saved_rect = upg.rect
                    upg.rect = draw_rect
                    if upg.is_clicked(event):
                        if upg.apply(state):
                            save_game(state)
                    upg.rect = saved_rect

            # --- Clicks inside skins panel ---
            if skins_open:
                for name, r in skin_rects:
                    if r.collidepoint(event.pos):
                        if name == "default" or name in state.owned_skins:
                            state.current_skin = name
                            state.skin_multiplier = SKIN_MULTIPLIERS.get(name, 1.0)
                            clicker_img = skin_images[name]
                            clicker_rect = clicker_img.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2))
                            save_game(state)
                        else:
                            required = list(SKIN_FILES.keys()).index(name)
                            if state.rebirth_count >= required:
                                state.owned_skins.append(name)
                                state.current_skin = name
                                clicker_img = skin_images[name]
                                clicker_rect = clicker_img.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2))
                                save_game(state)

    # --- UPDATE ---
    btn_close_upgrades.update(mouse_pos)
    if upgrades_open:
        for upg, draw_rect in get_visible_upgrades():
            saved_rect = upg.rect
            upg.rect = draw_rect
            upg.update(mouse_pos)
            upg.rect = saved_rect

    # --- Pop animation ---
    if pop_timer > 0:
        pop_timer -= 1
        pop_scale = 1.0 + (0.3 * (pop_timer / 10))
    else:
        pop_scale = 1.0

    # --- Passive income (points per second) ---
    dt = clock.tick(FPS) / 1000.0
    state.score += state.click_speed * state.rebirth_multiplier * dt

    # --- Gambling animation timer ---
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
    state.auto_clicker_timer += dt
    if state.auto_clicker_count > 0:
        interval = state.auto_clicker_interval / max(1, state.auto_clicker_count)
        while state.auto_clicker_timer >= interval:
            state.auto_clicker_timer -= interval
            state.score += int(state.click_power * state.rebirth_multiplier)
            state.clicks_total += 1
            pop_timer = 10
            pop_scale = 1.3

    # --- DRAWING ---
    screen.blit(bg_img, (0, 0))

    # Draw clickable picture
    if pop_scale != 1.0:
        new_w = int(clicker_img.get_width() * pop_scale)
        new_h = int(clicker_img.get_height() * pop_scale)
        scaled = pygame.transform.scale(clicker_img, (new_w, new_h))
        scaled_rect = scaled.get_rect(center=clicker_rect.center)
        screen.blit(scaled, scaled_rect)
    else:
        screen.blit(clicker_img, clicker_rect)

    # --- Draw upgrades panel ---
    if upgrades_open:
        panel_rect = pygame.Rect(PANEL_X, PANEL_Y, PANEL_W, SCREEN_H - PANEL_Y)
        pygame.draw.rect(screen, PANEL_BG, panel_rect)
        pygame.draw.rect(screen, PANEL_BORDER, panel_rect, width=3)

        # Panel title
        panel_title = font_med.render("UPGRADES", True, YELLOW)
        screen.blit(panel_title, (PANEL_X + 20, PANEL_Y + 20))

        # Scroll indicator
        if max_scroll > 0:
            scroll_text = font_tiny.render(f"Scroll {scroll_offset}/{max_scroll}",
                                           True, GRAY)
            screen.blit(scroll_text, (PANEL_X + 20, PANEL_Y + 55))

        # Draw upgrades (with scroll applied to their rects)
        for upg, draw_rect in get_visible_upgrades():
            saved_rect = upg.rect
            upg.rect = draw_rect
            upg.draw(screen, state)
            upg.rect = saved_rect

        # X close button (fixed at top-right of panel, not scrolled)
        btn_close_upgrades.draw(screen)

    # --- Draw the "Open Upgrades" button (only when panel closed) ---
    if not upgrades_open:
        # Upgrades button
        open_color = DARK_BLUE if open_btn_rect.collidepoint(mouse_pos) else PINK
        pygame.draw.rect(screen, open_color, open_btn_rect, border_radius=10)
        pygame.draw.rect(screen, WHITE, open_btn_rect, width=3, border_radius=10)
        open_text = font_med.render("Upgrades", True, WHITE)
        screen.blit(open_text, open_text.get_rect(center=open_btn_rect.center))

        # Rebirth button
        rebirth_color = DARK_BLUE if rebirth_btn_rect.collidepoint(mouse_pos) else RED
        if state.score < state.rebirth_cost:
            rebirth_color = GRAY
        pygame.draw.rect(screen, rebirth_color, rebirth_btn_rect, border_radius=10)
        pygame.draw.rect(screen, WHITE, rebirth_btn_rect, width=3, border_radius=10)
        rebirth_text = font_med.render("Rebirth", True, WHITE)
        screen.blit(rebirth_text, rebirth_text.get_rect(center=rebirth_btn_rect.center))
        rebirth_cost_text = font_small.render(f"Cost: {format_num(state.rebirth_cost)}", True, YELLOW)
        screen.blit(rebirth_cost_text, rebirth_cost_text.get_rect(
            centerx=rebirth_btn_rect.centerx, y=rebirth_btn_rect.bottom - 20))

        # Skins button
        skins_color = DARK_BLUE if skins_btn_rect.collidepoint(mouse_pos) else BLUE
        pygame.draw.rect(screen, skins_color, skins_btn_rect, border_radius=10)
        pygame.draw.rect(screen, WHITE, skins_btn_rect, width=3, border_radius=10)
        skins_text = font_med.render("Skins", True, WHITE)
        screen.blit(skins_text, skins_text.get_rect(center=skins_btn_rect.center))

    # --- Gambling button ---
    if not upgrades_open:
        gamble_color = DARK_BLUE if gamble_btn_rect.collidepoint(mouse_pos) else (180, 100, 0)
        pygame.draw.rect(screen, gamble_color, gamble_btn_rect, border_radius=10)
        pygame.draw.rect(screen, WHITE, gamble_btn_rect, width=3, border_radius=10)
        gamble_text = font_med.render("Gamble", True, WHITE)
        screen.blit(gamble_text, gamble_text.get_rect(center=gamble_btn_rect.center))
        gamble_sub = font_tiny.render("100000", True, YELLOW)
        screen.blit(gamble_sub, gamble_sub.get_rect(centerx=gamble_btn_rect.centerx, y=gamble_btn_rect.bottom - 20))

    # --- Gambling animation ---
    if state.gamble_timer > 60:
        names = list(SKIN_FILES.keys())[4:]
        offset = (120 - state.gamble_timer) * 12
        for i, nm in enumerate(names * 3):
            x = SCREEN_W - (i * 120) + (offset % (len(names) * 120))
            img = skin_images.get(nm, clicker_img)
            r = pygame.Rect(x, 20, 100, 100)
            screen.blit(pygame.transform.scale(img, (100, 100)), r)
            pygame.draw.rect(screen, WHITE, r, width=2, border_radius=6)
        center_rect = pygame.Rect(SCREEN_W // 2 - 50, 20, 100, 100)
        pygame.draw.rect(screen, YELLOW, center_rect, width=4, border_radius=6)
    elif state.gamble_timer > 0 and state.gamble_result:
        img = skin_images.get(state.gamble_result, clicker_img)
        r = pygame.Rect(SCREEN_W // 2 - 90, 20, 180, 180)
        screen.blit(pygame.transform.scale(img, (180, 180)), r)
        pygame.draw.rect(screen, YELLOW, r, width=4, border_radius=8)
        txt = font_med.render(f"You got: {state.gamble_result}", True, WHITE)
        screen.blit(txt, txt.get_rect(centerx=SCREEN_W // 2, y=210))

    # --- Skins panel ---
    skin_rects = []
    if skins_open:
        panel_rect = pygame.Rect(200, 150, SCREEN_W - 240, SCREEN_H - 200)
        pygame.draw.rect(screen, PANEL_BG, panel_rect, border_radius=10)
        pygame.draw.rect(screen, PANEL_BORDER, panel_rect, width=3, border_radius=10)
        title = font_med.render("SKINS", True, YELLOW)
        screen.blit(title, (panel_rect.x + 20, panel_rect.y + 20))
        x = panel_rect.x + 30
        y = panel_rect.y + 70 - skin_scroll
        for name in SKIN_FILES:
            r = pygame.Rect(x, y, 180, 180)
            skin_rects.append((name, r))
            img = skin_images[name]
            screen.blit(img, r)
            pygame.draw.rect(screen, WHITE if state.current_skin == name else GRAY, r, width=3, border_radius=8)
            label = font_small.render(name, True, WHITE)
            screen.blit(label, label.get_rect(centerx=r.centerx, y=r.bottom + 5))
            if name != "default" and name not in state.owned_skins:
                required = list(SKIN_FILES.keys()).index(name)
                price_surf = font_small.render(f"Requires {required} rebirths", True, YELLOW)
                screen.blit(price_surf, price_surf.get_rect(centerx=r.centerx, y=r.bottom + 25))
            x += 210
            if x + 180 > panel_rect.right:
                x = panel_rect.x + 30
                y += 220

    # --- UI TEXT ---
    score_text = font_big.render(f"Score: {format_num(state.score)}", True, YELLOW)
    screen.blit(score_text, (SCREEN_W // 2 - score_text.get_width() // 2, 40))

    power_text = font_med.render(f"Points per click: {state.click_power}",
                                 True, WHITE)
    screen.blit(power_text, (SCREEN_W // 2 - power_text.get_width() // 2, 100))

    clicks_text = font_small.render(f"Total clicks: {state.clicks_total}",
                                    True, WHITE)
    screen.blit(clicks_text, (SCREEN_W // 2 - clicks_text.get_width() // 2, 140))

    # Passive income display
    if state.click_speed > 0 or state.auto_clicker_count > 0:
        passive_text = font_small.render(
            f"+{int(state.click_speed)}/s  Auto: {state.auto_clicker_count}"
            f" (every {state.auto_clicker_interval:.2f}s)", True, GREEN)
        screen.blit(passive_text, (SCREEN_W // 2 - passive_text.get_width() // 2, 170))

    # Instructions
    instr = font_small.render("Click the picture to gain points!", True, GRAY)
    screen.blit(instr, (SCREEN_W // 2 - instr.get_width() // 2, SCREEN_H - 160))

    pygame.display.flip()

# ----------------------------------------------------------------------------
# STEP 13: CLEANUP AND EXIT
# ----------------------------------------------------------------------------
save_game(state)
pygame.quit()
sys.exit()
