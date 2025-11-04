"""Test solver performance on level 52"""
from solver import PuzzleState, TubeState, ColorSegment, solve
import time

def createLevel52():
    """Recreates the level 52 state of the game"""
    tubes = [
        TubeState(tube_index=1,
                  segments=[
                      ColorSegment('red', 25),
                      ColorSegment('blue', 25),
                      ColorSegment('red', 25),
                      ColorSegment('light_blue', 25)
                  ],
                  capacity_px=100),
        TubeState(tube_index=2,
                  segments=[
                      ColorSegment('pink', 25),
                      ColorSegment('green', 25),
                      ColorSegment('purple', 25),
                      ColorSegment('green', 25)
                  ],
                  capacity_px=100),
        TubeState(tube_index=3,
                  segments=[
                      ColorSegment('poop', 25),
                      ColorSegment('green', 50),
                      ColorSegment('grey', 25),
                  ],
                  capacity_px=100),
        TubeState(tube_index=4,
                  segments=[
                      ColorSegment('blue', 25),
                      ColorSegment('pink', 25),
                      ColorSegment('light_blue', 25),
                      ColorSegment('grey', 25)
                  ],
                  capacity_px=100),
        TubeState(tube_index=5,
                  segments=[
                      ColorSegment('purple', 50),
                      ColorSegment('orange', 25),
                      ColorSegment('pink', 25),
                  ],
                  capacity_px=100),
        TubeState(tube_index=6,
                  segments=[
                      ColorSegment('light_blue', 25),
                      ColorSegment('purple', 25),
                      ColorSegment('blue', 25),
                  ],
                  capacity_px=100),
        TubeState(tube_index=7,
                  segments=[
                      ColorSegment('orange', 50),
                      ColorSegment('red', 25),
                      ColorSegment('grey', 25),
                  ],
                  capacity_px=100),
        TubeState(tube_index=8,
                  segments=[
                      ColorSegment('poop', 25),
                      ColorSegment('pink', 25),
                      ColorSegment('orange', 25),
                      ColorSegment('poop', 25)
                  ],
                  capacity_px=100),
        TubeState(tube_index=9,
                  segments=[
                      ColorSegment('poop', 25),
                      ColorSegment('red', 25),
                      ColorSegment('grey', 25),
                      ColorSegment('light_blue', 25)
                  ],
                  capacity_px=100),
        TubeState(tube_index=10,
                  segments=[
                      ColorSegment('empty', 100),
                  ],
                  capacity_px=100),
        TubeState(tube_index=11,
                  segments=[
                      ColorSegment('empty', 100),
                  ],
                  capacity_px=100),
        TubeState(tube_index=12,
                  segments=[
                      ColorSegment('empty', 100),
                  ],
                  capacity_px=100)
    ]
    return PuzzleState(tubes)

if __name__ == "__main__":
    print("Testing solver on Level 52...")
    print("This is a complex puzzle with 9 colors and 12 tubes")
    print("Starting solve...\n")
    
    state = createLevel52()
    start_time = time.time()
    
    # Use verbose mode to see progress
    solution = solve(state, max_depth=150, verbose=True)
    
    elapsed = time.time() - start_time
    
    if solution:
        print(f"\n✓ Solution found in {elapsed:.2f} seconds!")
        print(f"Number of moves: {len(solution)}\n")
        print("Solution:")
        for i, (from_idx, to_idx) in enumerate(solution, 1):
            print(f"  {i}. Tube {from_idx + 1} → Tube {to_idx + 1}")
    else:
        print(f"\n❌ No solution found after {elapsed:.2f} seconds")
