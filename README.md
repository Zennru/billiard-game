# 🎱 8-Ball Billiard Game

A 2D Billiard Game (8-Ball Pool) application built using **Python**, featuring **Pygame** for the graphical user interface and audio, and **Pymunk** for realistic 2D physics simulation (collisions, elasticity, friction, and impulse dynamics).

Developed by **Group 7** to fulfill the coursework requirements for **Object-Oriented Programming (DPBO)**.

---

## 👥 Group 7 Members

1. **FIKRI AHMAD ARSALAN**
2. **BAHTIAR RIFAI KHUMAIDI**
3. **RAFI RUZAIN RABA**

---

## ✨ Key Features

### 🎮 Game Mechanics & Physics (Pymunk Physics)
- **Realistic 2D Physics**: Uses Pymunk physics engine to calculate velocity, linear & angular damping, cushion elasticity (wall bounces), and ball-to-ball collisions.
- **Ball Rotation & Visual Effects**: Dynamic ball rolling spin animation complete with soft shadows and specular highlights.
- **Cue Ball Placement & Ball-in-Hand**: Players can place the cue ball freely in the break area at the start of the game or anywhere on the table when a foul occurs (*Ball-in-Hand*).
- **Power Meter Shooting**: Charge cue stick power using a dynamic force meter.

### 🎯 Aim System & Trajectory Prediction
- **Aim Guide Line**: Displays the predicted path of the cue ball along with wall reflection angles.
- **Target Ball Collision Prediction**: Shows the estimated impact point and deflection angle for the target ball.

### 🏆 Complete 8-Ball Pool Rules
- **Group Assignment (Solids vs. Stripes)**: Automatic assignment of player ball groups (*Solids #1–7* vs. *Stripes #9–15*) upon potting the first legal ball after an open table.
- **Foul & Scratch System**: Detects fouls such as potting the cue ball (*scratch*), failing to hit the assigned ball group first, or failing to contact a cushion.
- **Win & Loss Conditions**: Pot the 8-ball (#8) after clearing all assigned group balls to win; automatic loss if the 8-ball is potted illegally or on a scratch.

### 🎨 Custom Skins & Customization (Settings)
- **Cue Stick Skins**: Separate skin selection for Player 1 and Player 2 (`Normal Cue`, `Japan Cue`, `Winter Cue`).
- **Table Felt Skins**: Selectable table surface skins (`Normal Table`, `Japan Table`, `Winter Table`).
- **Interactive Preview**: Live preview of table and cue skins directly inside the Settings menu.

### 🔊 Audio & Visual Effects
- **Background Music & SFX**: Menu music, cue hit sounds (`hit.wav`), ball/wall impact sounds, and victory fanfare (`menang.wav`).
- **Audio Toggle**: Mute/Unmute audio control button for music and sound effects.
- **Visual Effects**: Pocket ripple ring animations when balls are potted, and victory confetti celebration upon game completion.

---

## 🛠️ Tech Stack & Dependencies

- **Programming Language**: Python 3.x
- **GUI & Graphics Rendering**: [Pygame](https://www.pygame.org/)
- **2D Physics Engine**: [Pymunk](http://www.pymunk.org/) (Wrapper around Chipmunk Physics)
- **Standard Libraries**: `math`, `random`

---

## 📁 Project Directory Structure

```text
billiard-game/
├── assets/
│   ├── images/
│   │   ├── ball/              # Ball textures (#1-15, cue ball, shadow, highlight, bg)
│   │   ├── cue/               # Cue stick skins (normal, japan, winter)
│   │   └── table/             # Table felt/frame skins (normal, japan, winter)
│   └── sounds/                # Audio files for hit impacts & background music (.wav & .mp3)
├── game/
│   ├── __init__.py            # Python package marker
│   ├── aim_system.py          # Trajectory prediction & aim guideline raycasting
│   ├── assets_loader.py       # Asset manager (images, sounds, fonts, UI buttons, & confetti)
│   ├── collision.py           # Collision sound trigger manager (ball-wall & ball-ball)
│   ├── effects.py             # Visual effects (pocket ripple rings & victory confetti)
│   ├── game.py                # Core game loop & window state controller
│   ├── gameplay.py            # Main game loop, 8-ball rules, player turn states, & physics updates
│   ├── menu.py                # Main Menu UI state & interactions (Play, Settings, Quit)
│   ├── settings.py            # Settings UI state for skin customization (Cue P1/P2, Table)
│   └── state.py               # State constants (STATE_MENU, STATE_SETTINGS, STATE_GAME)
├── ball.py                    # Ball entity class (Pymunk body & shape, rotation, rendering)
├── cue.py                     # Cue stick entity class (aim angle & force impulse application)
├── main.py                    # Application entry point
├── pocket.py                  # Table pocket coordinates & ball-in-pocket detection
├── scoreSystem.py             # Score tracker & potted balls container per player
├── table.py                   # Static cushion wall bodies for Pymunk physics space
├── UIHandler.py               # HUD overlay renderer (scores, potted ball icons, turn status)
└── README.md                  # Project documentation
```

---

## 🚀 Installation & Setup Guide

### 1. System Requirements
Ensure you have **Python 3.8** or higher installed on your machine.

### 2. Install Dependencies
Open your terminal or Command Prompt in the project root directory and run:

```bash
pip install pygame pymunk
```

### 3. Running the Game
Execute `main.py` using Python:

```bash
python main.py
```

---

## 🕹️ Game Controls

| Action | Control |
| :--- | :--- |
| **Aim Cue Stick** | Move the **Mouse** around the Cue Ball |
| **Charge Shot Power** | **Hold Left Mouse Button / Spacebar** to fill power meter |
| **Release Shot** | **Release Left Mouse Button / Spacebar** |
| **Place Cue Ball (Placement / Ball-in-Hand)** | **Left Click** on a valid spot on the table |
| **Toggle Mute / Unmute Audio** | **Click Speaker Icon** in the bottom-right corner |
