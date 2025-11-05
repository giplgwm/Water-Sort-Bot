# Water Sort Bot

## Overview

This is an Android automation bot that plays the Water Sort puzzle game to farm coins in the Fetch app. The bot uses ADB (Android Debug Bridge) to capture screenshots, detect tubes and colors, solve the puzzle using a backtracking algorithm, and execute the solution by tapping on the device screen.

The system captures the initial state of the puzzle, computes a complete solution in memory, then executes the moves with appropriate delays to account for pour animations.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Computer Vision Pipeline

**Problem**: Need to identify tubes and their contents from Android screenshots
**Solution**: Multi-stage OpenCV-based detection pipeline
- **Tube Detection**: Uses binary thresholding to find white vertical rectangles (tubes are approximately 151x544 pixels)
- **Color Detection**: Scans vertical lines within each tube to identify color segments from top to bottom
- **Pixel-based Measurements**: Colors are tracked by pixel height rather than abstract "units" to maintain precision

**Rationale**: Pixel-based approach ensures accurate pour calculations without losing information through unit conversions.

### Puzzle Solver Architecture

**Problem**: Need to solve Water Sort puzzles optimally and compute entire solution before executing
**Solution**: In-memory backtracking DFS algorithm with immutable state transitions (see `solver.py`)

**Core Components**:
- **ColorSegment**: Represents a color block with height in pixels
- **TubeState**: Represents a single tube with segments list and capacity tracking
- **PuzzleState**: Immutable puzzle state with tubes, move generation, and state application
- **Backtracking Solver**: DFS with visited state memoization and move prioritization heuristics

**Algorithm Flow**:
1. Capture single screenshot and convert to PuzzleState
2. Generate all valid moves from current state
3. Apply heuristics to prioritize moves (empty tubes, completing tubes, same-color consolidation)
4. For each move, create new immutable state and recurse
5. Track visited states to prevent cycles
6. Return complete move sequence when solved state reached

**Pour Rules Enforced**:
- Source tube must have non-empty top color
- Destination must have 'empty' as top segment
- Destination must have sufficient capacity (empty.height >= pour_height)
- Colors must match (or destination is completely empty)

**Key Design Decisions**:
- Immutable state operations (deep copy on moves) ensure backtracking correctness
- State serialization and hashing prevent revisiting configurations
- Pixel-level precision maintains accuracy without unit conversions
- Move prioritization heuristics reduce search space significantly
- Regression tests ensure duplicate same-sized color segments handled correctly

**Critical Bug Fixes** (November 2025):
- **Empty Space Tracking**: Fixed `from_detection()` to use actual tube height from detection instead of sum of segments. Now properly tracks empty space in partially-filled tubes. Without this, solver attempted pours into "full" tubes that actually had room.

**Performance Optimizations** (November 2025):
- Fixed `is_complete` to require tubes be filled to capacity (not just one color)
- Optimized `would_complete_tube` to avoid expensive state copies (~100x faster)
- Improved move pruning to skip already-complete destination tubes
- Better heuristic ordering prioritizes completing tubes over random moves to empty
- Progress logging shows states explored per second in verbose mode
- Performance: Simple puzzles <0.1s, complex (12 tubes/9 colors) ~30-120s

### Execution System

**Problem**: Need to translate logical moves into physical device interactions
**Solution**: Execution plan with animation-aware delays
- **Tap Position Calculation**: Uses original tube detection data to compute accurate tap coordinates
- **Animation Delays**: Configurable delays (default 1.3s) between moves to wait for pour animations
- **Sequential Execution**: Moves are executed in order with appropriate pauses

**Rationale**: Animation delays prevent the bot from moving faster than the game can process, ensuring reliable execution.

### Move Optimization

**Problem**: Avoid redundant back-and-forth moves
**Solution**: Last-move tracking prevents immediate reversal
- Tracks previous move (from_idx, to_idx)
- Blocks moves that would immediately undo the last action
- Reduces search space and improves solution efficiency

## External Dependencies

### System Requirements
- **ADB (Android Debug Bridge)**: Required for device communication, screenshot capture, and tap input
  - Commands used: `adb devices`, `adb exec-out screencap`, `adb shell input tap`
  - Must have USB debugging enabled on Android device

### Python Libraries
- **Pillow (PIL)**: Image loading and manipulation from ADB screenshot data
- **OpenCV (cv2)**: Computer vision operations for tube and color detection
  - Color space conversions (RGB/BGR)
  - Binary thresholding
  - Contour detection
- **NumPy**: Array operations for image processing

### Target Platform
- **Android Device**: Must be running the Water Sort game
- **Water Sort Game**: The specific puzzle game being automated (ads removed via in-app purchase)

### Data Flow
1. ADB captures PNG screenshot from Android device
2. OpenCV processes image to detect tubes and colors
3. Solver computes complete solution using backtracking
4. ADB executes tap commands to perform moves
5. Delays account for game animations between moves