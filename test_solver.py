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
    
    # This puzzle requires temporarily moving a uniform tube to create buffer space
    tubes = [
        ['red', 'blue'],
        ['blue', 'red'],
        ['red', 'red'],
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


if __name__ == "__main__":
    print("\nRunning Water Sort Solver Tests\n")
    
    results = []
    results.append(("Simple 2-color puzzle", test_simple_puzzle()))
    results.append(("3-color puzzle", test_three_color_puzzle()))
    results.append(("Already solved", test_already_solved()))
    results.append(("Uniform tube to empty (regression)", test_uniform_tube_to_empty()))
    
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
