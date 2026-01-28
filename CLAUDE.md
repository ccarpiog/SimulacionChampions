# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Monte Carlo simulation of the UEFA Champions League league phase format (introduced in 2024-25 season). It simulates 32 teams playing 8 matchdays with results influenced by team strength ratings, then runs thousands of iterations to calculate probabilities of finishing in specific positions based on final point totals.

## Running the Simulation

```bash
python champions.py
```

Dependencies: `pandas`, `tqdm`

## Architecture

Single-file simulation (`champions.py`) with these core components:

- **`simular_temporada()`**: Main simulation function that runs one complete season
  - Creates 32 teams with random strength values (50-100)
  - **`generar_calendario()`**: Nested function that creates matchday schedule using round-robin combinations
  - **`simular_jornada()`**: Nested function that simulates all matches in a matchday, updating the standings table

- **Main loop**: Runs 10,000 simulations, collecting final positions for each point total, then calculates percentages for:
  - Top 8 (direct qualification to knockout round)
  - Top 24 (playoff qualification)
  - Bottom 8 (elimination)

## Key Data Structures

- `tabla`: pandas DataFrame tracking standings (points, wins, draws, losses, goal difference)
- `fuerzas`: Dictionary mapping team names to strength ratings
- `resultados`: defaultdict collecting position outcomes grouped by final points
