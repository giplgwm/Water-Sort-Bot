"""
Water Sort Puzzle Solver using backtracking
Computes complete solution from initial state before executing any moves
"""
from typing import List, Tuple, Optional
from copy import deepcopy


class PuzzleState:
    """Represents the state of the water sort puzzle"""
    
    def __init__(self, tubes: List[List[str]]):
        """
        Initialize puzzle state
        
        Args:
            tubes: List of tubes, where each tube is a list of colors from bottom to top
                   Example: [['red', 'blue'], ['blue', 'red'], []]
        """
        self.tubes = tubes
        self.num_tubes = len(tubes)
    
    def copy(self) -> 'PuzzleState':
        """Create a deep copy of this state"""
        return PuzzleState(deepcopy(self.tubes))
    
    def is_solved(self) -> bool:
        """
        Check if puzzle is solved.
        A puzzle is solved when each color appears in at most one tube,
        and all tubes are either empty or contain only one color.
        """
        color_locations = {}
        
        for tube_idx, tube in enumerate(self.tubes):
            if len(tube) == 0:
                continue
            
            # Check if tube has mixed colors
            if len(set(tube)) > 1:
                return False
            
            # Check if this color appears in multiple tubes
            color = tube[0]
            if color in color_locations:
                return False  # Same color in multiple tubes = not solved
            color_locations[color] = tube_idx
        
        return True
    
    def can_pour(self, from_idx: int, to_idx: int, max_capacity: int = 4) -> bool:
        """
        Check if we can pour from one tube to another
        
        Args:
            from_idx: Index of source tube
            to_idx: Index of destination tube
            max_capacity: Maximum capacity of each tube (default 4)
        """
        if from_idx == to_idx:
            return False
        
        from_tube = self.tubes[from_idx]
        to_tube = self.tubes[to_idx]
        
        # Can't pour from empty tube
        if len(from_tube) == 0:
            return False
        
        # Can't pour into full tube
        if len(to_tube) >= max_capacity:
            return False
        
        # If destination is empty, allow pour
        # (May need to move uniform tubes to create buffer space)
        if len(to_tube) == 0:
            return True
        
        # Can only pour if top colors match
        from_color = from_tube[-1]
        to_color = to_tube[-1]
        
        if from_color != to_color:
            return False
        
        # Count how many of the same color at top of source
        from_count = 0
        for i in range(len(from_tube) - 1, -1, -1):
            if from_tube[i] == from_color:
                from_count += 1
            else:
                break
        
        # Don't make useless moves (pouring when it doesn't help)
        # If both tubes have same color on top and would still be mixed after pour, avoid
        space_in_dest = max_capacity - len(to_tube)
        
        return True
    
    def pour(self, from_idx: int, to_idx: int, max_capacity: int = 4) -> bool:
        """
        Pour from one tube to another (modifies state in place)
        
        Returns:
            True if pour was successful, False otherwise
        """
        if not self.can_pour(from_idx, to_idx, max_capacity):
            return False
        
        from_tube = self.tubes[from_idx]
        to_tube = self.tubes[to_idx]
        
        # Get the color being poured
        pour_color = from_tube[-1]
        
        # Pour as many of the same color as possible
        poured = 0
        while (len(from_tube) > 0 and 
               len(to_tube) < max_capacity and 
               from_tube[-1] == pour_color):
            to_tube.append(from_tube.pop())
            poured += 1
        
        return poured > 0
    
    def get_possible_moves(self, max_capacity: int = 4) -> List[Tuple[int, int]]:
        """
        Get all possible moves from current state
        
        Returns:
            List of (from_idx, to_idx) tuples
        """
        moves = []
        for from_idx in range(self.num_tubes):
            for to_idx in range(self.num_tubes):
                if self.can_pour(from_idx, to_idx, max_capacity):
                    moves.append((from_idx, to_idx))
        return moves
    
    def __hash__(self):
        """Hash state for visited set in search"""
        return hash(tuple(tuple(tube) for tube in self.tubes))
    
    def __eq__(self, other):
        """Check equality for visited set"""
        return self.tubes == other.tubes
    
    def __str__(self):
        """String representation for debugging"""
        result = []
        for i, tube in enumerate(self.tubes):
            result.append(f"Tube {i}: {tube}")
        return "\n".join(result)


def solve_puzzle(initial_state: PuzzleState, max_capacity: int = 4, max_moves: int = 200) -> Optional[List[Tuple[int, int]]]:
    """
    Solve the water sort puzzle using backtracking
    
    Args:
        initial_state: Initial puzzle state
        max_capacity: Maximum capacity of each tube
        max_moves: Maximum number of moves to try before giving up
    
    Returns:
        List of (from_idx, to_idx) moves to solve puzzle, or None if no solution
    """
    
    def dfs(state: PuzzleState, moves: List[Tuple[int, int]], visited: set) -> Optional[List[Tuple[int, int]]]:
        """Depth-first search with backtracking"""
        
        # Check if we've exceeded move limit
        if len(moves) > max_moves:
            return None
        
        # Check if solved
        if state.is_solved():
            return moves
        
        # Check if we've seen this state before
        state_hash = hash(state)
        if state_hash in visited:
            return None
        visited.add(state_hash)
        
        # Try all possible moves
        possible_moves = state.get_possible_moves(max_capacity)
        
        # Optimize: prioritize moves that complete a tube
        def move_priority(move):
            from_idx, to_idx = move
            from_tube = state.tubes[from_idx]
            to_tube = state.tubes[to_idx]
            
            # Get color being poured
            if len(from_tube) == 0:
                return 99
            
            pour_color = from_tube[-1]
            
            # Deprioritize moving already-complete tubes (full + single color + only tube with that color)
            if len(from_tube) == max_capacity and len(set(from_tube)) == 1:
                # Check if this color exists in any other tube
                color_exists_elsewhere = any(
                    pour_color in tube for idx, tube in enumerate(state.tubes) if idx != from_idx
                )
                if not color_exists_elsewhere:
                    return 98  # Very low priority, but not impossible
            
            # Count how many we'll pour
            pour_count = 0
            for i in range(len(from_tube) - 1, -1, -1):
                if from_tube[i] == pour_color:
                    pour_count += 1
                else:
                    break
            
            # Priority 0: Moves that complete a tube
            after_pour_count = len(to_tube) + pour_count
            if after_pour_count == max_capacity and (len(to_tube) == 0 or to_tube[-1] == pour_color):
                return 0
            
            # Priority 1: Pour into non-empty matching color
            if len(to_tube) > 0 and to_tube[-1] == pour_color:
                return 1
            
            # Priority 2: Pour into empty tube
            if len(to_tube) == 0:
                return 2
            
            return 3
        
        possible_moves.sort(key=move_priority)
        
        for from_idx, to_idx in possible_moves:
            # Make the move
            new_state = state.copy()
            if new_state.pour(from_idx, to_idx, max_capacity):
                new_moves = moves + [(from_idx, to_idx)]
                
                # Recurse
                result = dfs(new_state, new_moves, visited)
                if result is not None:
                    return result
        
        return None
    
    visited = set()
    return dfs(initial_state, [], visited)


def state_from_tube_analysis(all_tube_colors: List[dict]) -> PuzzleState:
    """
    Convert tube analysis results to PuzzleState
    
    Args:
        all_tube_colors: Output from color_detection.analyze_all_tubes
    
    Returns:
        PuzzleState ready for solving
    """
    tubes = []
    
    for tube_info in all_tube_colors:
        tube = []
        # Colors are listed top to bottom, but we want bottom to top for state
        colors = tube_info['colors']
        
        # Skip empty space at top, collect actual colors from bottom to top
        for color_segment in reversed(colors):
            color = color_segment['color']
            if color not in ['empty', 'background', 'white']:
                # Add one entry per segment (each segment is one liquid level)
                tube.append(color)
        
        tubes.append(tube)
    
    return PuzzleState(tubes)
