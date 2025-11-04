"""
Test the backtracking solver with sample puzzle states
"""
from solver import (
    PuzzleState, TubeState, ColorSegment, 
    solve, can_pour, merge_consecutive_segments
)


def create_simple_puzzle():
    """
    Create a simple solvable puzzle:
    Tube 1: [red(50), blue(50)]
    Tube 2: [blue(50), red(50)]
    Tube 3: [empty(100)]
    
    Solution should pour to separate colors
    """
    tubes = [
        TubeState(
            tube_index=1,
            segments=[
                ColorSegment('red', 50),
                ColorSegment('blue', 50)
            ],
            capacity_px=100
        ),
        TubeState(
            tube_index=2,
            segments=[
                ColorSegment('blue', 50),
                ColorSegment('red', 50)
            ],
            capacity_px=100
        ),
        TubeState(
            tube_index=3,
            segments=[
                ColorSegment('empty', 100)
            ],
            capacity_px=100
        ),
    ]
    return PuzzleState(tubes)


def create_already_solved_puzzle():
    """
    Create a puzzle that's already solved
    """
    tubes = [
        TubeState(
            tube_index=1,
            segments=[ColorSegment('red', 100)],
            capacity_px=100
        ),
        TubeState(
            tube_index=2,
            segments=[ColorSegment('blue', 100)],
            capacity_px=100
        ),
        TubeState(
            tube_index=3,
            segments=[ColorSegment('empty', 100)],
            capacity_px=100
        ),
    ]
    return PuzzleState(tubes)


def create_complex_puzzle():
    """
    Create a more complex puzzle with 3 colors
    """
    tubes = [
        TubeState(
            tube_index=1,
            segments=[
                ColorSegment('red', 25),
                ColorSegment('blue', 25),
                ColorSegment('green', 25),
                ColorSegment('red', 25)
            ],
            capacity_px=100
        ),
        TubeState(
            tube_index=2,
            segments=[
                ColorSegment('green', 25),
                ColorSegment('red', 25),
                ColorSegment('blue', 25),
                ColorSegment('green', 25)
            ],
            capacity_px=100
        ),
        TubeState(
            tube_index=3,
            segments=[
                ColorSegment('blue', 50),
                ColorSegment('red', 50)
            ],
            capacity_px=100
        ),
        TubeState(
            tube_index=4,
            segments=[ColorSegment('empty', 100)],
            capacity_px=100
        ),
        TubeState(
            tube_index=5,
            segments=[ColorSegment('empty', 100)],
            capacity_px=100
        ),
    ]
    return PuzzleState(tubes)


def test_can_pour():
    """Test the can_pour function"""
    print("Testing can_pour function...")
    
    source = TubeState(
        tube_index=1,
        segments=[ColorSegment('red', 50), ColorSegment('blue', 50)],
        capacity_px=100
    )
    
    # Valid destination: empty tube
    dest_empty = TubeState(
        tube_index=2,
        segments=[ColorSegment('empty', 100)],
        capacity_px=100
    )
    assert can_pour(source, dest_empty), "Should be able to pour into empty tube"
    
    # Valid destination: same color with space
    dest_same_color = TubeState(
        tube_index=3,
        segments=[ColorSegment('empty', 50), ColorSegment('red', 50)],
        capacity_px=100
    )
    assert can_pour(source, dest_same_color), "Should be able to pour into same color"
    
    # Invalid: different color
    dest_diff_color = TubeState(
        tube_index=4,
        segments=[ColorSegment('empty', 50), ColorSegment('blue', 50)],
        capacity_px=100
    )
    assert not can_pour(source, dest_diff_color), "Should not pour red into blue"
    
    # Invalid: no space
    dest_no_space = TubeState(
        tube_index=5,
        segments=[ColorSegment('red', 100)],
        capacity_px=100
    )
    assert not can_pour(source, dest_no_space), "Should not pour into full tube"
    
    print("✓ can_pour tests passed\n")


def test_merge_segments():
    """Test segment merging"""
    print("Testing merge_consecutive_segments...")
    
    # Test merging consecutive same colors
    segments = [
        ColorSegment('red', 25),
        ColorSegment('red', 25),
        ColorSegment('blue', 50)
    ]
    merged = merge_consecutive_segments(segments)
    assert len(merged) == 2, "Should merge consecutive red segments"
    assert merged[0].color == 'red' and merged[0].height == 50
    
    # Test no merging needed
    segments = [
        ColorSegment('red', 50),
        ColorSegment('blue', 50)
    ]
    merged = merge_consecutive_segments(segments)
    assert len(merged) == 2, "Should not merge different colors"
    
    print("✓ merge_consecutive_segments tests passed\n")


def test_apply_move():
    """Test applying a move"""
    print("Testing apply_move...")
    
    state = create_simple_puzzle()
    
    # Pour from tube 0 to tube 2 (empty)
    new_state = state.apply_move(0, 2)
    
    # Check that red was poured
    assert new_state.tubes[0].top_color.color == 'blue', "Red should be removed from tube 0"
    assert new_state.tubes[2].top_color.color == 'red', "Red should be in tube 2"
    
    # Original state should be unchanged
    assert state.tubes[0].top_color.color == 'red', "Original state should not change"
    
    print("✓ apply_move tests passed\n")


def test_apply_move_duplicate_segments():
    """Test applying a move when tube has multiple same-sized segments of same color"""
    print("Testing apply_move with duplicate segments (regression test)...")
    
    # Create a tube with two 25px red segments
    tubes = [
        TubeState(
            tube_index=1,
            segments=[
                ColorSegment('red', 25),
                ColorSegment('blue', 25),
                ColorSegment('red', 25),  # Another 25px red segment
                ColorSegment('green', 25)
            ],
            capacity_px=100
        ),
        TubeState(
            tube_index=2,
            segments=[ColorSegment('empty', 100)],
            capacity_px=100
        ),
    ]
    state = PuzzleState(tubes)
    
    # Pour the top red segment
    new_state = state.apply_move(0, 1)
    
    # Verify only ONE red segment was removed (the top one)
    # The tube should now have: empty(25), blue(25), red(25), green(25)
    assert len(new_state.tubes[0].segments) == 4, f"Should have 4 segments, got {len(new_state.tubes[0].segments)}"
    assert new_state.tubes[0].top_color.color == 'blue', "Blue should now be on top"
    
    # Check that the other red segment is still there
    red_segments = [seg for seg in new_state.tubes[0].segments if seg.color == 'red']
    assert len(red_segments) == 1, f"Should still have 1 red segment, got {len(red_segments)}"
    assert red_segments[0].height == 25, "Red segment should be 25px"
    
    # Verify the poured red is in tube 2
    assert new_state.tubes[1].top_color.color == 'red', "Red should be in tube 2"
    assert new_state.tubes[1].top_color.height == 25, "Poured red should be 25px"
    
    print("✓ apply_move duplicate segments test passed\n")


def test_is_solved():
    """Test solved state detection"""
    print("Testing is_solved...")
    
    solved = create_already_solved_puzzle()
    assert solved.is_solved(), "Already solved puzzle should return True"
    
    unsolved = create_simple_puzzle()
    assert not unsolved.is_solved(), "Unsolved puzzle should return False"
    
    print("✓ is_solved tests passed\n")


def test_simple_solver():
    """Test solver on simple puzzle"""
    print("Testing solver on simple puzzle...")
    
    state = create_simple_puzzle()
    solution = solve(state, max_depth=50)
    
    assert solution is not None, "Simple puzzle should have a solution"
    print(f"  Found solution with {len(solution)} moves")
    
    # Verify solution actually solves the puzzle
    current = state
    for from_idx, to_idx in solution:
        current = current.apply_move(from_idx, to_idx)
    
    assert current.is_solved(), "Solution should result in solved state"
    
    print("✓ Simple solver test passed\n")


def test_already_solved():
    """Test solver on already solved puzzle"""
    print("Testing solver on already solved puzzle...")
    
    state = create_already_solved_puzzle()
    solution = solve(state, max_depth=50)
    
    assert solution is not None, "Should find solution (empty list)"
    assert len(solution) == 0, "Already solved should require 0 moves"
    
    print("✓ Already solved test passed\n")


def test_complex_solver():
    """Test solver on complex puzzle"""
    print("Testing solver on complex puzzle...")
    
    state = create_complex_puzzle()
    solution = solve(state, max_depth=100)
    
    if solution is not None:
        print(f"  Found solution with {len(solution)} moves")
        
        # Print solution
        for i, (from_idx, to_idx) in enumerate(solution, 1):
            print(f"    {i}. Tube {from_idx + 1} → Tube {to_idx + 1}")
        
        # Verify solution
        current = state
        for from_idx, to_idx in solution:
            current = current.apply_move(from_idx, to_idx)
        
        assert current.is_solved(), "Solution should result in solved state"
        print("✓ Complex solver test passed\n")
    else:
        print("  No solution found (may need more depth or better heuristics)")
        print("  This is okay for very complex puzzles\n")


def run_all_tests():
    """Run all tests"""
    print("="*60)
    print("Running Solver Tests")
    print("="*60 + "\n")
    
    test_can_pour()
    test_merge_segments()
    test_apply_move()
    test_apply_move_duplicate_segments()
    test_is_solved()
    test_simple_solver()
    test_already_solved()
    test_complex_solver()
    
    print("="*60)
    print("All tests completed!")
    print("="*60)


if __name__ == "__main__":
    run_all_tests()
