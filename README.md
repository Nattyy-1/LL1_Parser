# LL(1) Parser Visualizer

A Python-based LL(1) predictive parser with a full graphical interface for computing FIRST/FOLLOW sets, generating parse tables, building parse trees, and stepping through the parsing process visually.

## Overview

LL(1) parsing is a top-down parsing technique that reads input **L**eft-to-right, produces a **L**eftmost derivation, and uses **1** token of lookahead. This project implements the complete LL(1) parsing pipeline and provides an interactive GUI to visualize every step.

## Features

- **FIRST & FOLLOW Set Computation** — Iteratively computes FIRST and FOLLOW sets for any context-free grammar, including epsilon productions
- **LL(1) Parse Table Generation** — Constructs a predictive parsing table from grammar rules, FIRST, and FOLLOW sets
- **Input Parsing** — Parses a tokenized input string against the grammar using the parse table, producing a parse tree and step-by-step trace
- **Parse Tree Visualization** — Renders the parse tree as both an ASCII representation and a Graphviz-generated image
- **Interactive GUI (CustomTkinter)** — Full dark-themed desktop application with:
  - Information page explaining LL(1) parsing
  - Grammar input with pre-loaded example
  - Tabbed results view (FIRST/FOLLOW, Parse Table, Parse Tree, Simulation)
  - **Step-by-step simulation player** with canvas-based stack and input buffer visualization, play/pause controls, speed slider, and trace table
- **Left Recursion Support Detection** — Gracefully handles grammars that are not LL(1) compatible

## Project Structure

```
root/
├── receive_grammar.py      # Console grammar input handler
├── first.py                # FIRST set computation
├── follow.py               # FOLLOW set computation (depends on FIRST)
├── create_parse_table.py   # LL(1) predictive parse table construction
├── parse_input.py          # Input string parsing with trace & tree building
└── gui.py                  # CustomTkinter desktop GUI application
    ├── LL1ParserGUI        # Main application window (info page + parser workspace)
    └── ParserSimulationPlayer  # Step-by-step canvas-based simulation player
```

## How It Works

```
Grammar Input
     │
     ▼
┌──────────────┐
│  first.py    │  → Compute FIRST sets for all non-terminals
└──────┬───────┘
       │
┌──────▼───────┐
│  follow.py   │  → Compute FOLLOW sets (uses FIRST)
└──────┬───────┘
       │
┌──────▼───────────────┐
│ create_parse_table.py│  → Build LL(1) parse table
└──────┬───────────────┘
       │
┌──────▼─────────┐
│  parse_input.py│  → Parse input string, build tree & trace steps
└──────┬─────────┘
       │
┌──────▼─────┐
│   gui.py   │  → Visualize everything interactively
└────────────┘
```

## Grammar Format

Each production is written on its own line using `->` as the arrow, with space-separated symbols:

```
E -> T E'
E' -> + T E'
E' -> e
T -> F T'
T' -> * F T'
T' -> e
F -> ( E )
F -> id
```

**Rules:**
- `->` separates left-hand side (non-terminal) from right-hand side
- Symbols are space-separated
- `e` represents epsilon (ε, the empty string)
- Non-terminals are uppercase letters; terminals are lowercase or symbols
- One production per line

## Requirements

- **Python 3.8+**
- **CustomTkinter** — Modern themed Tkinter widgets
- **tabulate** — Formatted table output
- **anytree** — Parse tree data structure and ASCII rendering
- **graphviz** (optional) — Graphical parse tree image generation
- **Pillow** — Image handling for Graphviz output

## Installation

```bash
pip install customtkinter tabulate anytree pillow
```

For Graphviz tree rendering:

```bash
# System-level Graphviz installation
sudo apt install graphviz    # Ubuntu/Debian
brew install graphviz        # macOS

# Python bindings
pip install graphviz
```

## Usage

### GUI Mode (Recommended)

```bash
cd root
python gui.py
```

1. Enter your grammar in the left panel (pre-loaded example provided)
2. Enter the input string (e.g., `id + id * id`)
3. Click **Calculate FIRST/FOLLOW** to view computed sets
4. Click **Show Parse Table** to generate the LL(1) table
5. Click **Parse Input** to build the parse tree
6. Click **Step-by-Step Simulation** for a full-screen animated walkthrough

### Programmatic API

```python
from first import first
from follow import follow
from create_parse_table import create_parse_table
from parse_input import parse_input

grammar = [
    "E -> T E'",
    "E' -> + T E'",
    "E' -> e",
    "T -> F T'",
    "T' -> * F T'",
    "T' -> e",
    "F -> ( E )",
    "F -> id"
]

first_sets = first(grammar)
follow_sets = follow(grammar)
parse_table = create_parse_table(grammar)
tree, steps = parse_input(grammar, "id + id * id")
```

## Parse Table Example

For the expression grammar above, the generated LL(1) table maps each (non-terminal, terminal) pair to the correct production, enabling predictive parsing with no backtracking.

## Simulation

The step-by-step simulation player visualizes the parsing process with:

- **Stack visualization** — Color-coded boxes showing the parser's stack (top highlighted)
- **Input buffer visualization** — Shows remaining input with a lookahead pointer
- **Trace table** — Step-by-step log of stack state, remaining input, and action (match/expand)
- **Parse table reference** — Side-by-side view of the current parse table
- **Playback controls** — First, Prev, Play/Pause, Next, Last buttons with adjustable speed

## Author

**Natnael Samson** — [Nattyy-1](https://github.com/Nattyy-1)
