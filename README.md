# Mező Clicker 🎮 (v1.0)

An enhanced, data-driven incremental clicker game built in Python using Pygame! Progress through 35+ structured upgrades across four categories, unlock passive income and critical hits, utilize the Rebirth system, customize your game settings, collect skins with unique multipliers, and gamble for rare rewards—all while watching your score climb into the Decillions (`Dc`).

---

## ✨ Features

* **Expanded Upgrade Catalog & Linked Category Pricing:** 
  * Purchase upgrades across **Click Power** (17 tiers), **Auto-Income** (13 tiers), **Multipliers**, and **Critical Chance** (crit rate, crit damage, and auto-clickers).
  * Features **level counters** (`Lvl`) and **shared category scaling**: buying any upgrade slightly raises the prices of all other upgrades in that category while keeping tiered costs distinct.
* **Large Number Formatting (`format_num`):** Cleanly displays massive numbers from `k` (Thousand) all the way up to `Dc` (Decillion).
* **Responsive & Resizable Window:** Freely resize the main window or toggle Fullscreen; the HUD, clickable target, and panels dynamically adjust to fit.
* **Settings Menu (`settings.json`):** Customize **Audio Volume** (`0%–100%`), **Screen Resolution** (`1280x720`, `1600x900`, `1920x1080`, or Fullscreen), and **FPS Cap** (`30`, `60`, `120`, `144`, `Unlimited`) with persistent saving.
* **Detailed Rebirth Pop-up Modal:** View your current vs. required cash, a visual progress bar (`%`), upcoming rebirth count, and permanent multiplier rewards (`x2.0` per rebirth) before confirming.
* **Skins System:** Unlock and equip 13 custom skins by reaching rebirth milestones, each granting a unique score multiplier (`1.00x` up to `2.80x`) in a scrollable gallery.
* **Case-Opening Gambling:** Spend `100k` currency on a CS2-style animated carousel for a chance at rare skins (`mezo5`–`mezo13`), with a `10k` refund on duplicate rolls.
* **Persistent Save System (`clicker_save.json`):** Object-oriented `GameState` architecture with automatic saving on clicks, purchases, rebirths, and exit, including legacy save migration.

---

## 📋 Requirements

Make sure you have **Python 3.x** and **Pygame** installed:

```bash
pip install pygame
```

---

## 🚀 How to Play

1. Place `clicker.py` alongside the background (`bgp.webp`), default clicker (`clickPIC.jpg`), and skin image assets (`mezodeafult.jpg`, `mezo2.jpg`–`mezo13.png`) in the same folder. *(Fallback graphics are automatically generated if any image is missing.)*
2. Launch the game from your terminal:
```bash
python clicker.py
```
3. Click the picture to earn points, scroll through the **Upgrades** panel to scale your income, track your progress in the **Rebirth** pop-up, unlock **Skins**, try your luck at **Gamble**, and adjust display/audio options in **Settings**.

---

## 📜 Version History

**Mező Clicker 1.0 – Full Release: Settings, Resizable UI & Mega Upgrades**
* Added a **Settings** pop-up window with Volume slider, Resolution presets, Fullscreen toggle, and FPS Cap selector saved to `settings.json`.
* Made the main game window **fully resizable** with responsive UI layout scaling (`relayout_ui`).
* Expanded the upgrade catalog to **35+ upgrades** across four categories (*Click Power*, *Auto-Income*, *Multipliers*, *Critical Chance*) with individual level counters and linked category price scaling.
* Added a dedicated **Rebirth Pop-up Modal** featuring a progress bar, percentage tracker, and reward preview.
* Implemented large number suffix formatting up to **Decillion (`Dc`)**.

**Mező Clicker 0.6 – Gambling & Skin Multipliers**
* Added Gambling button with animated carousel and 10% duplicate refund.
* Each skin now grants a unique score multiplier.
* Skins panel is scrollable.
* Missing images use colored placeholders.

**Mező Clicker 0.5 – Skins System & Save on Click**
* Implemented Skins panel gated by rebirth count.
* Auto-save on every click.

**Mező Clicker 0.4 – Rebirth System**
* Rebirth prestige system with exponential cost scaling.

**Mező Clicker 0.3 – Tiered Upgrades & Scrollable UI**
* Data-driven upgrades with dynamic pricing.

**Mező Clicker 0.2 – Refactoring**
* Cleaned codebase and Git integration.

**Mező Clicker 0.1 – Initial Setup**
* Core Pygame app and save/load system.
