# Tug of War Repair Lab

This project is a competitive tug-of-war game using **Pygame**. It introduces students to alternating keyboard input synchronization, debounce and lock state patterns, physics-based tension balancing, and autonomous AI pulling mechanics within an object-oriented codebase.
---

## What's Provided

A working Tug of War game with:

- A horizontal rope setup with goal markers, center boundary indicators, and a center position flag
- Two anchor pullers (`PLAYER` and `COMPUTER`) rendered with visual team colorings
- An alternating key input model requiring players to alternate `A` and `D` to pull left
- An autonomous computer opponent that pulls the rope rightward at recurring intervals
- Win-state boundary detection and a Game Over overlay with rematch support

It has **one deliberate bug** and **three optional features** left as tasks to implement. You are expected to **analyze**, **interact with an AI assistant**, and **complete/fix** the game to make it fully functional and more interesting.

### **Use an LLM (e.g. ChatGPT or Claude) as your debugging and pair-programming partner for this lab.**
---

## Getting Started

### Setup

1. Make sure you have Python 3.10+ installed.
2. Install dependencies:

```bash
pip install pygame
```

> On Python 3.14+, `pygame` may fail to build. Use the drop-in replacement instead: `pip install pygame-ce`.

3. Run the game:

```bash
python main.py
```

**Controls:**

| Key | Action |
|---|---|
| `A` / `D` (alternate) | Pull the rope left toward your goal |
| `R` | Play again from the Game Over screen |

---

## Changes Implemented

| Task | Status | Commit | Files |
|---|---|---|---|
| 1. Fix alternating input deadlock | ✅ Done | `1aa6a5f` | `game/game_engine.py` |
| 2. Dynamic AI panic surges | ✅ Done | `cb29cba` | `game/game_engine.py` |
| 3. Rope tension & leaning animations | ✅ Done | `d4dd86d` | `game/game_engine.py`, `game/rope.py`, `game/player.py` |
| 4. Match timer & sudden death | ✅ Done | `d434cf0` | `game/game_engine.py` |

### Task 1: Input deadlock fix
**Root cause:** each pull set `is_pull_locked = True`, and only the `KEYUP` of that *same* key cleared it. During fast mashing your fingers overlap (D goes down before A comes up), so the overlapping press was dropped, and the next press of the original key was then rejected as "not alternating". About half the presses were lost. If a `KEYUP` was missed entirely (e.g. focus loss), input stayed locked forever.

**Fix:** removed the lock. A pull now registers on every `A`/`D` `KEYDOWN` that differs from the previous pull key. Alternation is still enforced (holding or repeating one key does nothing), but overlapping presses always count and input can never freeze.

### Task 2: AI panic surges
- `GameEngine.compute_panic_level()` returns `0.0` until the player has dragged the flag **50%** of the way to their goal, then ramps linearly to `1.0` at the goal line.
- The computer's pull interval shrinks from **180 ms to 130 ms**, and its pull strength grows up to **1.35×**, in proportion to the panic level.
- A flashing orange **COMPUTER PANIC SURGE!** banner appears at the bottom, blinking faster as panic rises.
- Tuned so that a fast-mashing player can still win.

### Task 3: Rope tension & leaning animations
- The engine tracks two decaying values: **momentum** (which side has been pulling more recently) and **struggle** (total recent pulling activity).
- **Rope** (`Rope.rope_y`): drawn as a polyline. When slack it **sags** in the middle; as struggle rises it pulls taut and **hums** with a travelling vibration. The ends stay pinned and the colour brightens when taut. The flag rides on the rope.
- **Pullers** (`Puller.lean_toward`): each body tilts back up to 28°. The side holding momentum leans back hardest, and lean is smoothed so motion stays fluid. Arms now reach forward and grip the rope.

### Task 4: Match timer & sudden death
- A live `TIME MM:SS` timer at the top of the screen. It turns yellow in the final 10 seconds before sudden death and freezes on Game Over.
- After **45 seconds** with no winner, **Sudden Death** begins: a red **SUDDEN DEATH x2 POWER** banner appears and all pulls (player and computer) are doubled.
- Pressing `R` resets the timer, sudden death, panic level, and animation state along with the rope.


## Tasks to Complete

Each task must be completed using an iterative process involving LLM suggestions and your critical code review.

### Task 1: Fix the Alternating Input Deadlock Bug

Rapidly mashing back and forth between A and D suddenly freezes input handling completely, leaving the rope unresponsive while the computer effortlessly pulls away with the win. Redesign the input synchronization so that overlapping or rapid alternating keystrokes consistently register pulls without locking the player out.

### Task 2: Implement Dynamic AI Panic Surges

The computer currently pulls at a fixed cadence with minimal variation. Introduce dynamic difficulty: as the center marker gets pulled closer to the player's winning threshold, have the computer enter a high-intensity panic surge with faster reaction intervals and aggressive pulling strength to stage a comeback.

### Task 3: Implement Rope Tension & Puller Leaning Animations

The rope and pullers are currently visually static. Add dynamic visual feedback: give the rope a vibrating high-tension hum or sag depending on struggle intensity, and animate both characters with backward leaning postures based on which side holds pulling momentum.

### Task 4: Implement a match timer and sudden death mode

Matches between evenly matched opponents can drag on indefinitely. Add a live match timer at the top of the screen. If no side has won within 45 seconds, trigger a "Sudden Death" state that doubles pulling power across all actions to force a swift finish.

---

## Expected Behavior

- Rapidly alternating between A and D reliably moves the red center flag to the left without freezing or dropping inputs during fast mashing.
- The computer pulls the marker to the right at recurring intervals.
- The match ends when the flag crosses the left boundary (Player wins) or right boundary (Computer wins).
- Pressing R on the Game Over screen resets the rope marker, keys, timers, and game states.
---

## Folder Structure

```
tug_of_war/
├── game/
│   ├── game_engine.py
│   ├── player.py
│   └── rope.py
├── main.py
└── README.md
```

---

## Submission Checklist

Submission is only the following three things:

- [] A 10-second video of gameplay **before** your changes, showing the bug/broken behavior
- [] A 10-second video of gameplay **after** your changes, showing the bug fixed and the new features working
- [] The Chat/LLM used page link, with the complete chat history
