"""
Water Sort Bot - Game Logic with Backtracking Solver
Captures initial state, computes complete solution, then executes moves
"""
import sys
from color_detection import analyze_all_tubes
from adb import adb_tap, capture_screen, has_devices
from solver import PuzzleState, solve, compute_execution_plan
from time import sleep
import subprocess


def get_tap_position(tube_data):
    """
    Get the tap position for a tube based on original detection data
    
    Args:
        tube_data: Original tube data from analyze_all_tubes
    
    Returns:
        (x, y) tuple for tap position
    """
    tap_x = tube_data['top_color']['scan_x']
    tap_y = tube_data['top_color']['start_y'] + (tube_data['top_color']['height'] / 2)
    return (tap_x, tap_y)


def execute_solution(moves, all_tube_colors, animation_delay=1.3):
    """
    Execute the solution moves on the device
    
    Args:
        moves: List of (from_idx, to_idx) tuples (0-indexed)
        all_tube_colors: Original detection data for tap positions
        animation_delay: Delay for pour animations
    """
    # Compute execution plan with delays
    execution_plan = compute_execution_plan(moves, animation_delay)
    
    print(f"\n{'='*60}")
    print(f"Executing {len(moves)} moves...")
    print(f"{'='*60}\n")
    
    # Create lookup for tube data by index (detection uses 1-indexed)
    tube_lookup = {tube['tube_index']: tube for tube in all_tube_colors}
    
    for move_num, (from_idx, to_idx, delay) in enumerate(execution_plan, 1):
        # Wait for animation delay if needed
        if delay > 0:
            print(f"  Waiting {delay:.1f}s for animations...")
            sleep(delay)
        
        # Convert 0-indexed to 1-indexed for lookup
        from_tube = tube_lookup[from_idx + 1]
        to_tube = tube_lookup[to_idx + 1]
        
        print(f"Move {move_num}/{len(moves)}: Tube {from_idx + 1} → Tube {to_idx + 1}")
        
        # Get tap positions
        from_pos = get_tap_position(from_tube)
        to_pos = get_tap_position(to_tube)
        
        # Execute taps
        adb_tap(*from_pos)
        sleep(0.1)  # Small delay between taps
        adb_tap(*to_pos)
        
        # Wait for animation
        sleep(animation_delay)
    
    print(f"\n{'='*60}")
    print("Solution executed successfully!")
    print(f"{'='*60}\n")


def next_level():
    """Progress to next level after solving"""
    sleep(2)
    adb_tap(456, 1775)
    print("Tapping to advance to next level...")
    sleep(1)


def solve_puzzle():
    """Main puzzle solving logic"""
    print("\n" + "="*60)
    print("Water Sort Bot - Backtracking Solver")
    print("="*60 + "\n")
    
    # Capture initial screenshot
    print("Capturing screenshot...")
    image = capture_screen()
    
    # Analyze all tubes
    print("Analyzing tubes and colors...")
    all_tube_colors, img = analyze_all_tubes(image, scan_offset=40)
    
    print(f"Found {len(all_tube_colors)} tubes\n")
    
    # Print initial state
    print("Initial State:")
    for tube in all_tube_colors:
        colors = [seg['color'] for seg in tube['colors'] if seg['color'] != 'empty']
        print(f"  Tube {tube['tube_index']}: {colors}")
    
    # Convert to PuzzleState
    print("\nConverting to puzzle state...")
    state = PuzzleState.from_detection(all_tube_colors)
    
    # Check if already solved
    if state.is_solved():
        print("\n✓ Puzzle is already solved!")
        return True
    
    # Solve using backtracking
    print("Computing solution using backtracking...")
    solution = solve(state, max_depth=200)
    
    if solution is None:
        print("\n❌ No solution found! Puzzle may be unsolvable.")
        return False
    
    print(f"\n✓ Solution found! {len(solution)} moves required.\n")
    
    # Print solution
    print("Solution sequence:")
    for i, (from_idx, to_idx) in enumerate(solution, 1):
        print(f"  {i}. Tube {from_idx + 1} → Tube {to_idx + 1}")
    
    # Execute solution
    execute_solution(solution, all_tube_colors)
    
    return True


def main():
    """Main entry point for the bot"""
    # Check for devices
    print("Checking for connected devices...\n")
    if not has_devices():
        print("❌ No device found! Please connect an Android device via ADB.")
        return
    
    print("✓ Device connected!\n")
    
    # Start screen recording
    print("Starting screen recording...")
    screenrecord_proc = subprocess.Popen(
        ["adb", "shell", "screenrecord", "/sdcard/bot_recording.mp4"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    
    try:
        # Solve the puzzle
        success = solve_puzzle()
        
        if success:
            # Wait a bit before advancing
            next_level()
            print("\n✓ Level complete! Ready for next puzzle.")
        
    except KeyboardInterrupt:
        print("\n\nStopped by user.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Stop screen recording
        print("\nStopping screen recording...")
        screenrecord_proc.terminate()
        try:
            screenrecord_proc.wait(timeout=2)
        except subprocess.TimeoutExpired:
            screenrecord_proc.kill()


if __name__ == "__main__":
    main()
