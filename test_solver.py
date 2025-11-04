"""
Test the water sort solver with simple examples
"""
from solver import PuzzleState, solve_puzzle


def test_simple_puzzle():
    """Test with a simple 2-tube puzzle"""
    print("=" * 60)
    print("Test 1: Simple 2-color, 4-tube puzzle")
    print("=" * 60)
    
    tubes = [
        ['red', 'blue', 'red', 'blue'],
        ['blue', 'red', 'blue', 'red'],
        [],
        []
    ]
    
    state = PuzzleState(tubes)
    print("\nInitial state:")
    print(state)
    
    print("\nSolving...")
    solution = solve_puzzle(state, max_capacity=4, max_moves=50)
    
    if solution:
        print(f"\n✓ Solution found in {len(solution)} moves:")
        for i, (from_idx, to_idx) in enumerate(solution, 1):
            print(f"  {i}. Pour tube {from_idx} → tube {to_idx}")
        
        print("\nVerifying solution...")
        test_state = PuzzleState(tubes)
        for from_idx, to_idx in solution:
            test_state.pour(from_idx, to_idx, max_capacity=4)
        
        if test_state.is_solved():
            print("✓ Solution is correct!")
        else:
            print("❌ Solution is incorrect!")
            print(test_state)
    else:
        print("❌ No solution found")
    
    return solution is not None


def test_three_color_puzzle():
    """Test with a 3-color puzzle"""
    print("\n" + "=" * 60)
    print("Test 2: 3-color, 5-tube puzzle")
    print("=" * 60)
    
    tubes = [
        ['red', 'blue', 'green', 'red'],
        ['green', 'blue', 'red', 'blue'],
        ['blue', 'green', 'red', 'green'],
        [],
        []
    ]
    
    state = PuzzleState(tubes)
    print("\nInitial state:")
    print(state)
    
    print("\nSolving...")
    solution = solve_puzzle(state, max_capacity=4, max_moves=100)
    
    if solution:
        print(f"\n✓ Solution found in {len(solution)} moves:")
        for i, (from_idx, to_idx) in enumerate(solution, 1):
            print(f"  {i}. Pour tube {from_idx} → tube {to_idx}")
        
        print("\nVerifying solution...")
        test_state = PuzzleState(tubes)
        for from_idx, to_idx in solution:
            test_state.pour(from_idx, to_idx, max_capacity=4)
        
        if test_state.is_solved():
            print("✓ Solution is correct!")
        else:
            print("❌ Solution is incorrect!")
            print(test_state)
    else:
        print("❌ No solution found")
    
    return solution is not None


def test_already_solved():
    """Test with already solved puzzle"""
    print("\n" + "=" * 60)
    print("Test 3: Already solved puzzle")
    print("=" * 60)
    
    tubes = [
        ['red', 'red', 'red', 'red'],
        ['blue', 'blue', 'blue', 'blue'],
        []
    ]
    
    state = PuzzleState(tubes)
    print("\nInitial state:")
    print(state)
    
    if state.is_solved():
        print("\n✓ Correctly identified as already solved")
        return True
    else:
        print("\n❌ Failed to identify as solved")
        return False


def test_uniform_tube_to_empty():
    """Test that requires moving a uniform tube to empty slot (regression test)"""
    print("\n" + "=" * 60)
    print("Test 4: Puzzle requiring uniform tube → empty (regression)")
    print("=" * 60)
    
    # Simpler test: one uniform tube with reds, mixed tube, and empty
    # This tests that we CAN pour a uniform tube when needed
    tubes = [
        ['blue', 'red'],
        ['red', 'red'],  # Uniform but not full
        ['blue'],
        []
    ]
    
    state = PuzzleState(tubes)
    print("\nInitial state:")
    print(state)
    
    print("\nSolving...")
    solution = solve_puzzle(state, max_capacity=2, max_moves=50)
    
    if solution:
        print(f"\n✓ Solution found in {len(solution)} moves:")
        for i, (from_idx, to_idx) in enumerate(solution, 1):
            print(f"  {i}. Pour tube {from_idx} → tube {to_idx}")
        
        print("\nVerifying solution...")
        test_state = PuzzleState(tubes)
        for from_idx, to_idx in solution:
            test_state.pour(from_idx, to_idx, max_capacity=2)
        
        if test_state.is_solved():
            print("✓ Solution is correct!")
        else:
            print("❌ Solution is incorrect!")
            print(test_state)
        return True
    else:
        print("❌ No solution found - this is the bug we're testing for!")
        return False


def test_is_solved_check():
    """Test that is_solved() correctly requires all instances of a color in one tube"""
    print("\n" + "=" * 60)
    print("Test 5: Verify is_solved() requires colors in single tubes")
    print("=" * 60)
    
    # This should NOT be considered solved - red is in two different tubes
    tubes_not_solved = [
        ['red', 'red'],
        ['blue', 'blue'],
        ['red', 'red'],  # Red in another tube - NOT SOLVED!
        []
    ]
    
    state = PuzzleState(tubes_not_solved)
    print("\nTest case 1: Red in tubes 0 and 2 (should be NOT solved)")
    print(state)
    
    if not state.is_solved():
        print("✓ Correctly identified as NOT solved")
        test1_pass = True
    else:
        print("❌ Incorrectly marked as solved!")
        test1_pass = False
    
    # This SHOULD be considered solved - each color in exactly one tube
    tubes_solved = [
        ['red', 'red', 'red', 'red'],
        ['blue', 'blue', 'blue', 'blue'],
        [],
        []
    ]
    
    state2 = PuzzleState(tubes_solved)
    print("\nTest case 2: Each color in one tube (should be solved)")
    print(state2)
    
    if state2.is_solved():
        print("✓ Correctly identified as solved")
        test2_pass = True
    else:
        print("❌ Incorrectly marked as NOT solved!")
        test2_pass = False
    
    return test1_pass and test2_pass


if __name__ == "__main__":
    print("\nRunning Water Sort Solver Tests\n")
    
    results = []
    results.append(("Simple 2-color puzzle", test_simple_puzzle()))
    results.append(("3-color puzzle", test_three_color_puzzle()))
    results.append(("Already solved", test_already_solved()))
    results.append(("Uniform tube to empty (regression)", test_uniform_tube_to_empty()))
    results.append(("is_solved() color uniqueness check", test_is_solved_check()))
    
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✓ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    all_passed = all(result[1] for result in results)
    
    if all_passed:
        print("\n✓ All tests passed!")
    else:
        print("\n❌ Some tests failed")
    
    print("=" * 60)
