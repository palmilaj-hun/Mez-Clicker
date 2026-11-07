# Mező Clicker 🎮

An enhanced, data-driven incremental clicker game built in Python using Pygame! Progress through multiple upgrade tiers, unlock passive income, utilize the Rebirth system, change skins with unique multipliers, gamble for rare skins, and watch your score soar.

---

## ✨ Features
* **Tiered Upgrades System:** Purchase multiple structured tiers for Click Power, Passive Income, and Auto-Clicker Speed with dynamic cumulative pricing.
* **Scrollable Upgrade Panel:** Seamlessly scroll through a rich UI menu using your mouse wheel.
* **Rebirth System:** Reset your progress to earn a massive global multiplier (`x2.0`) on all future gains.
* **Skins System:** Unlock and apply new skins by reaching rebirth milestones. Each skin has a unique score multiplier. Skins panel is scrollable.
* **Gambling:** Spend 100,000 currency on a CS2-style case opening carousel for a chance at rare skins (mezo5–mezo13). Duplicate rolls refund 10%.
* **Robust State Management:** Clean object-oriented architecture (`GameState` class) with auto-save on every click.

---

## 📋 Requirements
Make sure you have **Python** and **Pygame** installed.

```bash
pip install pygame
```

---

## 🚀 How to Play

1. Place `clicker.py` and all image files in the same folder.
2. Launch:
```bash
python clicker.py
```
3. Click the target picture, buy upgrades, rebirth, change skins, or gamble.

---

## 📜 Version History

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
