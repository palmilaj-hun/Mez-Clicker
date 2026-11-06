# ============================================================================
# CLICKER SIM - inside gyakorlas/ folder ONLY
# Uses bgp.webp (background) and clickPIC.jpg (clickable picture)
# Run:  python clicker.py    (from inside the gyakorlas folder)
# ============================================================================

import json
import os
import sys
import pygame

# --- INITIALIZE PYGAME ---
pygame.init()

# --- WINDOW SETTINGS ---
SCREEN_W, SCREEN_H = 900, 700
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("Clicker Sim - Click the Picture!")
clock = pygame.time.Clock()
FPS = 60

# --- COLORS ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
BLUE = (0, 120, 255)
DARK_BLUE = (0, 90, 200)
RED = (200, 50, 50)
YELLOW = (255, 220, 0)
GREEN = (0, 200, 0)
PINK = pygame.Color("pink")

# --- FONTS ---
font_big = pygame.font.SysFont(None, 48)
font_med = pygame.font.SysFont(None, 32)
font_small = pygame.font.SysFont(None, 24)

# --- LOAD ASSETS ---
BASE = os.path.dirname(os.path.abspath(__file__))

# Background
bg_path = os.path.join(BASE, "bgp.webp")
try:
    bg_img = pygame.image.load(bg_path).convert()
    bg_img = pygame.transform.scale(bg_img, (SCREEN_W, SCREEN_H))
except (pygame.error, FileNotFoundError):
    bg_img = pygame.Surface((SCREEN_W, SCREEN_H))
    bg_img.fill((30, 30, 50))

# Clickable Picture
click_path = os.path.join(BASE, "clickPIC.jpg")
try:
    clicker_img = pygame.image.load(click_path).convert_alpha()
    clicker_img = pygame.transform.scale(clicker_img, (180, 180))
except (pygame.error, FileNotFoundError):
    clicker_img = pygame.Surface((180, 180), pygame.SRCALPHA)
    clicker_img.fill(GREEN)

clicker_rect = clicker_img.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2))

# --- SAVE SYSTEM ---
SAVE_FILE = os.path.join(BASE, "clicker_save.json")


def save_game(
    score, clk_p, clk_total, clk_spd, auto_cnt, upg_p, clk_spd_p, auto_p
):
    data = {
        "score": score,
        "clk_p": clk_p,
        "clk_total": clk_total,
        "clk_spd": clk_spd,
        "auto_cnt": auto_cnt,
        "upg_p": upg_p,
        "clk_spd_p": clk_spd_p,
        "auto_p": auto_p,
    }
    try:
        with open(SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"[CLICKER] Save failed: {e}")


def load_game():
    default = {
        "score": 0,
        "clk_p": 1,
        "clk_total": 0,
        "clk_spd": 0,
        "auto_cnt": 0,
        "upg_p": 10,
        "clk_spd_p": 50,
        "auto_p": 100,
    }
    try:
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        for key, val in default.items():
            if key not in data:
                data[key] = val
        return data
    except (FileNotFoundError, json.JSONDecodeError, Exception):
        return default


# --- GAME STATE ---
score = 0
clk_p = 1
clk_total = 0
clk_spd = 0
auto_cnt = 0
auto_timer = 0.0

pop_timer = 0
pop_scale = 1.0

upg_p = 10
clk_spd_p = 50
auto_p = 100

# Load saved game
saved = load_game()
score = saved["score"]
clk_p = saved["clk_p"]
clk_total = saved["clk_total"]
clk_spd = saved["clk_spd"]
auto_cnt = saved["auto_cnt"]
upg_p = saved["upg_p"]
clk_spd_p = saved["clk_spd_p"]
auto_p = saved["auto_p"]

upgrades_open = False


# --- BUTTON CLASSES ---
class ButtonBase:

    def __init__(
        self, x, y, w, h, name, price, color, hover_color, text_color=WHITE
    ):
        self.rect = pygame.Rect(x, y, w, h)
        self.name = name
        self.price = price
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.is_hovered = False

    def update(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def draw(self, surf):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surf, color, self.rect, border_radius=10)
        pygame.draw.rect(surf, WHITE, self.rect, width=3, border_radius=10)
        text_surf = font_med.render(self.name, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surf.blit(text_surf, text_rect)

    def is_clicked(self, event):
        return (
            event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and self.rect.collidepoint(event.pos)
        )

    def apply(self, game):
        pass


class UpgradesButton(ButtonBase):

    def __init__(self, x, y):
        super().__init__(x, y, 180, 50, "Upgrades", 0, PINK, DARK_BLUE)

    def apply(self, game):
        game["upgrades_open"] = not game["upgrades_open"]


class UpgradeClickButton(ButtonBase):

    def __init__(self, x, y, price=10):
        super().__init__(
            x, y, 260, 50, f"Upgrade Click (+1)", price, BLUE, DARK_BLUE
        )

    def apply(self, game):
        global upg_p
        if game["score"] >= self.price:
            game["score"] -= self.price
            game["clk_p"] += 1
            self.price = int(self.price * 1.5) + 5
            upg_p = self.price
            self.name = f"Upgrade Click (+1) - Cost: {self.price}"


class ClickSpeedButton(ButtonBase):

    def __init__(self, x, y, price=50):
        super().__init__(
            x, y, 260, 50, f"Click Speed (+1/s)", price, GREEN, DARK_BLUE
        )

    def apply(self, game):
        global clk_spd_p
        if game["score"] >= self.price:
            game["score"] -= self.price
            game["clk_spd"] += 1
            self.price = int(self.price * 1.5) + 25
            clk_spd_p = self.price
            self.name = f"Click Speed (+1/s) - Cost: {self.price}"


class AutoClickerButton(ButtonBase):

    def __init__(self, x, y, price=100):
        super().__init__(
            x, y, 260, 50, f"Auto Clicker", price, GREEN, DARK_BLUE
        )

    def apply(self, game):
        global auto_p
        if game["score"] >= self.price:
            game["score"] -= self.price
            game["auto_cnt"] += 1
            self.price = int(self.price * 1.5) + 50
            auto_p = self.price
            self.name = f"Auto Clicker - Cost: {self.price}"


class CloseUpgradesButton(ButtonBase):

    def __init__(self, x, y):
        super().__init__(x, y, 40, 40, "X", 0, RED, (150, 40, 40))

    def apply(self, game):
        game["upgrades_open"] = False


# --- SETUP BUTTON INSTANCES ---
btn_upgrades = UpgradesButton(20, SCREEN_H // 2 - 25)

PANEL_W = 320
BTN_W = 260
BTN_H = 50
BTN_X = (PANEL_W - BTN_W) // 2
BTN_Y_START = 220
BTN_GAP = 70

btn_upgrade_click = UpgradeClickButton(BTN_X, BTN_Y_START, upg_p)
btn_click_speed = ClickSpeedButton(BTN_X, BTN_Y_START + BTN_GAP, clk_spd_p)
btn_auto_clicker = AutoClickerButton(BTN_X, BTN_Y_START + BTN_GAP * 2, auto_p)
btn_close_upgrades = CloseUpgradesButton(PANEL_W - 60, 170)

# --- MAIN GAME LOOP ---
running = True
while running:
    mouse_pos = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            save_game(
                score, clk_p, clk_total, clk_spd, auto_cnt, upg_p, clk_spd_p, auto_p
            )
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if clicker_rect.collidepoint(event.pos):
                score += clk_p
                clk_total += 1
                pop_timer = 10
                pop_scale = 1.3

        if not upgrades_open and btn_upgrades.is_clicked(event):
            upgrades_open = True

        if upgrades_open:
            state = {
                "score": score,
                "clk_p": clk_p,
                "clk_total": clk_total,
                "clk_spd": clk_spd,
                "auto_cnt": auto_cnt,
                "upgrades_open": upgrades_open,
            }

            if btn_upgrade_click.is_clicked(event):
                btn_upgrade_click.apply(state)
                score = state["score"]
                clk_p = state["clk_p"]
                save_game(
                    score,
                    clk_p,
                    clk_total,
                    clk_spd,
                    auto_cnt,
                    upg_p,
                    clk_spd_p,
                    auto_p,
                )

            if btn_click_speed.is_clicked(event):
                btn_click_speed.apply(state)
                score = state["score"]
                clk_spd = state["clk_spd"]
                save_game(
                    score,
                    clk_p,
                    clk_total,
                    clk_spd,
                    auto_cnt,
                    upg_p,
                    clk_spd_p,
                    auto_p,
                )

            if btn_auto_clicker.is_clicked(event):
                btn_auto_clicker.apply(state)
                score = state["score"]
                auto_cnt = state["auto_cnt"]
                save_game(
                    score,
                    clk_p,
                    clk_total,
                    clk_spd,
                    auto_cnt,
                    upg_p,
                    clk_spd_p,
                    auto_p,
                )

            if btn_close_upgrades.is_clicked(event):
                btn_close_upgrades.apply(state)
                upgrades_open = state["upgrades_open"]

    # --- UPDATE ---
    btn_upgrades.update(mouse_pos)
    if upgrades_open:
        btn_upgrade_click.update(mouse_pos)
        btn_click_speed.update(mouse_pos)
        btn_auto_clicker.update(mouse_pos)
        btn_close_upgrades.update(mouse_pos)

    if pop_timer > 0:
        pop_timer -= 1
        pop_scale = 1.0 + (0.3 * (pop_timer / 10))
    else:
        pop_scale = 1.0

    dt = clock.tick(FPS) / 1000.0
    score += clk_spd * dt

    auto_timer += dt
    if auto_cnt > 0:
        interval = 1.0 / auto_cnt
        while auto_timer >= interval:
            auto_timer -= interval
            score += clk_p
            clk_total += 1
            pop_timer = 10
            pop_scale = 1.3

    # --- DRAWING ---
    screen.blit(bg_img, (0, 0))

    if pop_scale != 1.0:
        new_w = int(clicker_img.get_width() * pop_scale)
        new_h = int(clicker_img.get_height() * pop_scale)
        scaled = pygame.transform.scale(clicker_img, (new_w, new_h))
        scaled_rect = scaled.get_rect(center=clicker_rect.center)
        screen.blit(scaled, scaled_rect)
    else:
        screen.blit(clicker_img, clicker_rect)

    if upgrades_open:
        panel_rect = pygame.Rect(0, 150, PANEL_W, SCREEN_H - 150)
        pygame.draw.rect(screen, (40, 40, 60), panel_rect)
        pygame.draw.rect(screen, WHITE, panel_rect, width=3)

        panel_title = font_med.render("UPGRADES", True, YELLOW)
        screen.blit(panel_title, (panel_rect.x + 20, panel_rect.y + 20))

        btn_upgrade_click.draw(screen)
        btn_click_speed.draw(screen)
        btn_auto_clicker.draw(screen)
        btn_close_upgrades.draw(screen)
    else:
        btn_upgrades.draw(screen)

    # UI Text
    score_text = font_big.render(f"Score: {int(score)}", True, YELLOW)
    screen.blit(score_text, (SCREEN_W // 2 - score_text.get_width() // 2, 40))

    power_text = font_med.render(f"Points per click: {clk_p}", True, WHITE)
    screen.blit(power_text, (SCREEN_W // 2 - power_text.get_width() // 2, 100))

    clicks_text = font_small.render(f"Total clicks: {clk_total}", True, WHITE)
    screen.blit(clicks_text, (SCREEN_W // 2 - clicks_text.get_width() // 2, 140))

    if clk_spd > 0 or auto_cnt > 0:
        passive_text = font_small.render(
            f"+{clk_spd}/s  Auto: {auto_cnt}", True, GREEN
        )
        screen.blit(
            passive_text, (SCREEN_W // 2 - passive_text.get_width() // 2, 170)
        )

    instr = font_small.render(
        "Click the picture to gain points!", True, GRAY
    )
    screen.blit(
        instr, (SCREEN_W // 2 - instr.get_width() // 2, SCREEN_H - 160)
    )

    if score < btn_upgrade_click.price:
        hint = font_small.render("Not enough points yet!", True, RED)
        screen.blit(hint, (SCREEN_W // 2 - hint.get_width() // 2, SCREEN_H - 130))

    pygame.display.flip()

pygame.quit()
sys.exit()