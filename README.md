# Mező Clicker 🎮

An enhanced, data-driven incremental clicker game built in Python using Pygame! Progress through multiple upgrade tiers, unlock passive income, utilize the Rebirth system, change skins, and watch your score soar.

---

## ✨ New Features in this Version
* **Tiered Upgrades System:** Purchase multiple structured tiers for Click Power, Passive Income, and Auto-Clicker Speed with dynamic cumulative pricing.
* **Scrollable Upgrade Panel:** Seamlessly scroll through a rich UI menu using your mouse wheel.
* **Rebirth System:** Reset your progress to earn a massive global multiplier (`x2.0`) on all future gains.
* **Skins System:** Unlock and apply new skins for the clickable picture by reaching rebirth milestones. Default skin is free; each additional skin requires more rebirths (1, 2, 3...).
* **Robust State Management:** Clean object-oriented architecture (`GameState` class) with an auto-save on every click and load system.

---

## 📋 Requirements
Make sure you have **Python** and **Pygame** installed on your system before running the game.

If you need to install Pygame, run this in your terminal:
```bash
pip install pygame
```

---

## 🚀 How to Play

1. **Download / Clone** the repository files into the same folder (make sure `clicker.py`, `bgp.webp`, `mezodeafult.jpg`, `mezo2.jpg`, `mezo3.jpg`, `mezo4.webp` are together).
2. Open your terminal or command prompt inside that directory.
3. Launch the game:
```bash
python clicker.py
```

4. Click the target picture to gain points, open the **Upgrades** panel to boost your stats, hit **Rebirth** when ready to boost your global multiplier, and open **Skins** to change the clickable picture!

---

## 📜 Version History & Development Log

**Mező Clicker 0.5 – Skins System & Save on Click**

* Implemented the Skins panel with unlockable skins gated by rebirth count (1, 2, 3... rebirths).
* Applied new skin image set: Szomszéd, UtcaRéme, SuliFélelme, PacekMező.
* Game now auto-saves on every click for safer progress.

**Mező Clicker 0.4 – Rebirth System & Left-Menu Expansion**

* Added dedicated Rebirth and Skins buttons to the left-side interface.
* Implemented the Rebirth prestige system: costs scale exponentially ($10\times$ per level, starting at 1,000 points) for a permanent $2\times$ global score multiplier.
* Created a placeholder button for future character/object skins.

**Mező Clicker 0.3 – Tiered Upgrades & Scrollable UI**

* Refactored architecture using an encapsulated GameState class and a data-driven Upgrade class powered by TIER_CONFIG.
* Introduced 8 tiers for Click Power, 8 tiers for Passive Income, and 6 tiers for Auto-Clicker Speed.
* Added dynamic pricing ($\text{price} = \text{cumulative spent} + \text{base cost}$) and a mouse-wheel scrollable panel.

**Mező Clicker 0.2 – Code Refactoring & Git Integration**

* Refactored variable names to clean, human-friendly abbreviations.
* Integrated modular button classes.
* Configured Git tracking and pushed the initial version to GitHub.

**Mező Clicker 0.1 – Initial Setup**

* Built the core Pygame application (clicker.py) at 1000x700 resolution.
* Added clicking mechanics, background rendering, score counters, and pop animations.
* Created a local JSON save/load system (clicker_save.json).
