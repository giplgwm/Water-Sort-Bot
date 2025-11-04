# Water Sort Bot

## Overview
An automated bot that plays Water Sort puzzle games on Android devices using ADB (Android Debug Bridge). The bot uses computer vision to detect puzzle states and a backtracking solver to compute optimal solutions.

## Recent Changes (November 4, 2025)

### Major Refactoring: Robust Backtracking Solver
Completely rewrote the solving logic from a greedy screenshot-based approach to a robust state-based solver:

**Previous Approach:**
- Took screenshot, made one "obvious" move, took another screenshot, repeated
- Greedy algorithm without planning ahead
- Many delays between moves
- No backtracking for complex puzzles

**New Approach:**
1. Capture initial state once from screenshot
2. Convert to in-memory puzzle representation (PuzzleState class)
3. Use DFS with backtracking to compute complete solution
4. Return list of (from_tube, to_tube) move tuples
5. Execute all moves with minimal delays (0.3s between taps)

**Files Added:**
- `solver.py` - Core solver with backtracking algorithm
- `test_solver.py` - Comprehensive test suite with 4 test cases
- `main.py` - User-friendly entry point

**Files Modified:**
- `game-logic.py` - Complete refactor to use new solver

### Bug Fixes
- Fixed critical bug where solver prevented pouring uniform tubes into empty tubes, making some solvable puzzles appear unsolvable
- Added regression test to prevent reintroduction of this bug

## Project Architecture

### Core Components

#### 1. Computer Vision (color_detection.py, tube_detection.py)
- Detects tubes from screenshots using OpenCV
- Identifies liquid colors using precise RGB matching
- Scans vertical lines to determine color order in each tube

#### 2. Solver (solver.py)
- `PuzzleState` class: Represents game state in memory
- `solve_puzzle()`: DFS with backtracking to find optimal solution
- Heuristic move ordering: prioritizes moves that complete tubes
- State deduplication to avoid revisiting positions

#### 3. Game Logic (game-logic.py)
- Orchestrates the solving process
- Converts tube analysis to puzzle state
- Executes computed moves via ADB
- Handles level progression

#### 4. ADB Interface (adb.py)
- Captures screenshots from Android device
- Simulates screen taps at specific coordinates
- Checks for connected devices

## Requirements

### System Dependencies
- **ADB (Android Debug Bridge)** - Installed via `android-tools`
- Python 3.11+

### Python Dependencies
- `numpy` >= 2.3.4
- `opencv-python` >= 4.11.0.86
- `pillow` >= 12.0.0
- `scikit-learn` >= 1.7.2

### Hardware Requirements
- Android device with USB debugging enabled
- USB cable connection to host machine
- Water Sort game installed and running on device

## Usage

### Quick Start
```bash
# Run the main entry point to check device connection
uv run python main.py

# Run the bot to play the game
uv run python game-logic.py
```

### Running Tests
```bash
# Run solver test suite (4 test cases)
uv run python test_solver.py
```

### Testing Individual Components
```bash
# Test tube detection
uv run python tube_detection.py

# Test color detection
uv run python color_detection.py

# Test ADB connection
uv run python adb.py
```

## How It Works

1. **Initial Capture**: Bot takes a screenshot of the current puzzle
2. **Vision Processing**: 
   - Detects tube positions using contour detection
   - Scans each tube vertically to identify color layers
   - Builds a list of tube states with color information
3. **State Conversion**: Converts vision data to internal PuzzleState representation
4. **Solving**: Backtracking DFS finds complete solution path
5. **Execution**: Executes all moves by tapping tubes in sequence
6. **Level Progression**: Automatically proceeds to next level

## Solver Algorithm

The backtracking solver uses depth-first search with several optimizations:

### Move Validation
- Can't pour from/to same tube
- Can't pour from empty tube
- Can't pour into full tube
- Can only pour matching colors (unless destination is empty)
- Allows pouring uniform tubes to empty slots (for buffer space)

### Heuristic Ordering
Moves are prioritized by:
1. Moves that complete a tube (fill to capacity with single color)
2. Pouring into matching non-empty tube
3. Pouring into empty tube
4. Other valid moves

### State Management
- Hash-based visited set prevents revisiting states
- Deep copy for state exploration
- Maximum move limit (default: 200) prevents infinite search

## Testing

The test suite includes:
1. Simple 2-color puzzle (8 moves)
2. Complex 3-color puzzle (17 moves)
3. Already-solved puzzle detection
4. Regression test for uniform-tube-to-empty bug

All tests verify:
- Solution is found
- Solution length is reasonable
- Final state is actually solved

## User Preferences
None documented yet.

## Known Limitations
- Requires physical Android device (no emulator support)
- Color detection is tuned for specific game version
- Assumes standard tube capacity of 4 units
- Screen recording requires manual stop

## Future Improvements
1. Broader puzzle corpus testing (architect recommendation)
2. CI regression coverage for move validation rules
3. Performance profiling for larger puzzles
4. Dynamic color learning instead of hardcoded RGB values
