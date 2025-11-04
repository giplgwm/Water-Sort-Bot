"""
Water Sort Bot - Game Logic
Uses backtracking solver to compute all moves before executing
"""
import subprocess
from time import sleep
from adb import adb_tap, capture_screen, has_devices
from color_detection import analyze_all_tubes
from solver import state_from_tube_analysis, solve_puzzle


def get_tube_center_position(tube_info: dict) -> tuple:
    """
    Get the center tap position for a tube
    
    Args:
        tube_info: Tube information from analyze_all_tubes
    
    Returns:
        (x, y) coordinates for tapping
    """
    x = tube_info['tube_position'][0]
    y = tube_info['tube_position'][1]
    
    if len(tube_info['colors']) > 0:
        first_color = tube_info['colors'][0]
        tap_x = first_color['scan_x']
        tap_y = first_color['start_y'] + (first_color['height'] // 2)
    else:
        tap_x = x + 75
        tap_y = y + 270
    
    return (tap_x, tap_y)


def execute_move(all_tube_colors: list, from_idx: int, to_idx: int, delay: float = 0.3):
    """
    Execute a single move by tapping two tubes
    
    Args:
        all_tube_colors: Tube analysis data
        from_idx: Index of tube to pour from
        to_idx: Index of tube to pour into
        delay: Delay between taps in seconds
    """
    from_tube = all_tube_colors[from_idx]
    to_tube = all_tube_colors[to_idx]
    
    from_pos = get_tube_center_position(from_tube)
    to_pos = get_tube_center_position(to_tube)
    
    print(f"  Move: Tube {from_idx + 1} → Tube {to_idx + 1}")
    
    adb_tap(*from_pos)
    sleep(delay)
    adb_tap(*to_pos)
    sleep(delay)


def next_level():
    """Tap to proceed to next level"""
    print("Level complete! Proceeding to next level...")
    sleep(2)
    adb_tap(456, 1775)
    sleep(1)


def play_level():
    """
    Play a single level of Water Sort
    
    Returns:
        True if level was solved, False if failed
    """
    print("\n" + "=" * 60)
    print("Capturing screenshot and analyzing puzzle...")
    
    image = capture_screen()
    all_tube_colors, img = analyze_all_tubes(image, scan_offset=40)
    
    print(f"Found {len(all_tube_colors)} tubes")
    
    print("\nConverting to puzzle state...")
    puzzle_state = state_from_tube_analysis(all_tube_colors)
    
    print("\nInitial state:")
    for i, tube in enumerate(puzzle_state.tubes):
        print(f"  Tube {i + 1}: {tube if tube else '(empty)'}")
    
    if puzzle_state.is_solved():
        print("\nPuzzle is already solved!")
        next_level()
        return True
    
    print("\nSolving puzzle with backtracking...")
    solution = solve_puzzle(puzzle_state, max_capacity=4, max_moves=200)
    
    if solution is None:
        print("❌ No solution found! This puzzle may be unsolvable.")
        return False
    
    print(f"\n✓ Solution found! {len(solution)} moves required.")
    print("\nExecuting moves:")
    
    for i, (from_idx, to_idx) in enumerate(solution, 1):
        print(f"Step {i}/{len(solution)}:", end=" ")
        execute_move(all_tube_colors, from_idx, to_idx, delay=0.3)
    
    print("\n✓ All moves executed!")
    next_level()
    return True


def main():
    """Main game loop"""
    print("=" * 60)
    print("Water Sort Bot - Starting")
    print("=" * 60)
    
    if not has_devices():
        print("\n❌ No device connected!")
        print("Please connect an Android device with USB debugging enabled.")
        return
    
    print("\n✓ Device connected")
    print("\nStarting screen recording...")
    
    try:
        screenrecord_proc = subprocess.Popen(
            ["adb", "shell", "screenrecord", "/sdcard/bot_recording.mp4"]
        )
    except Exception as e:
        print(f"Warning: Could not start screen recording: {e}")
        screenrecord_proc = None
    
    print("\nStarting game loop...")
    print("Press Ctrl+C to stop\n")
    
    level_count = 0
    
    try:
        while True:
            level_count += 1
            print(f"\n{'=' * 60}")
            print(f"Level {level_count}")
            
            success = play_level()
            
            if not success:
                print("\nFailed to solve level. Stopping.")
                break
            
            sleep(1)
    
    except KeyboardInterrupt:
        print("\n\n{'=' * 60}")
        print("Stopped by user")
        print(f"Completed {level_count - 1} levels")
    
    finally:
        if screenrecord_proc:
            screenrecord_proc.terminate()
            print("Screen recording stopped")
        
        print("=" * 60)


if __name__ == "__main__":
    main()
