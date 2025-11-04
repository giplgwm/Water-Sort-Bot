"""
Water Sort Puzzle Solver using Backtracking
Computes the entire solution in memory before executing any moves
"""
from typing import List, Tuple, Optional, Dict, Set
from dataclasses import dataclass, field
from copy import deepcopy
import time


@dataclass
class ColorSegment:
    """Represents a segment of color in a tube"""
    color: str
    height: int  # Height in pixels
    
    def __repr__(self):
        return f"{self.color}({self.height}px)"


@dataclass
class TubeState:
    """Represents the state of a single tube"""
    tube_index: int
    segments: List[ColorSegment]  # From top to bottom
    capacity_px: int  # Total capacity in pixels
    
    @property
    def current_fill_px(self) -> int:
        """Calculate current fill level in pixels"""
        return sum(seg.height for seg in self.segments if seg.color != 'empty')
    
    @property
    def available_space_px(self) -> int:
        """Calculate available space in pixels"""
        empty_seg = next((seg for seg in self.segments if seg.color == 'empty'), None)
        return empty_seg.height if empty_seg else 0
    
    @property
    def top_color(self) -> Optional[ColorSegment]:
        """Get the top non-empty color segment"""
        for seg in self.segments:
            if seg.color != 'empty':
                return seg
        return None
    
    @property
    def is_empty(self) -> bool:
        """Check if tube is completely empty"""
        return all(seg.color == 'empty' for seg in self.segments)
    
    @property
    def is_complete(self) -> bool:
        """
        Check if tube is complete (either empty OR filled to capacity with one color)
        A partially filled tube with one color is NOT complete
        """
        non_empty = [seg for seg in self.segments if seg.color != 'empty']
        if len(non_empty) == 0:
            return True  # Empty tube is complete
        
        # All non-empty segments must be the same color
        if not all(seg.color == non_empty[0].color for seg in non_empty):
            return False
        
        # Must be filled to capacity
        total_height = sum(seg.height for seg in non_empty)
        return total_height == self.capacity_px
    
    def serialize(self) -> str:
        """Serialize tube state for hashing"""
        return f"{self.tube_index}:" + ",".join(f"{s.color}:{s.height}" for s in self.segments)


class PuzzleState:
    """Represents the complete puzzle state"""
    
    def __init__(self, tubes: List[TubeState]):
        self.tubes = tubes
        self._hash = None
    
    @classmethod
    def from_detection(cls, all_tube_colors: List[Dict]) -> 'PuzzleState':
        """
        Create PuzzleState from color detection output
        
        Args:
            all_tube_colors: Output from analyze_all_tubes()
        """
        tubes = []
        
        for tube_data in all_tube_colors:
            # Extract color segments from detection
            segments = []
            
            # Calculate total capacity (we'll use the sum of all segment heights)
            capacity = sum(c['height'] for c in tube_data['colors'])
            
            # Convert detection format to ColorSegment
            for color_info in tube_data['colors']:
                segments.append(ColorSegment(
                    color=color_info['color'],
                    height=color_info['height']
                ))
            
            tubes.append(TubeState(
                tube_index=tube_data['tube_index'],
                segments=segments,
                capacity_px=capacity
            ))
        
        return cls(tubes)
    
    def is_solved(self) -> bool:
        """Check if puzzle is solved (all tubes are complete)"""
        return all(tube.is_complete for tube in self.tubes)
    
    def serialize(self) -> str:
        """Serialize state for memoization"""
        if self._hash is None:
            self._hash = "|".join(tube.serialize() for tube in self.tubes)
        return self._hash
    
    def get_valid_moves(self) -> List[Tuple[int, int]]:
        """
        Get all valid moves from current state
        Returns list of (from_tube_index, to_tube_index)
        """
        moves = []
        
        for from_idx, from_tube in enumerate(self.tubes):
            # Skip if source tube is empty or complete
            if from_tube.is_empty or from_tube.is_complete:
                continue
            
            from_color = from_tube.top_color
            if not from_color or from_color.color == 'empty':
                continue
            
            for to_idx, to_tube in enumerate(self.tubes):
                if from_idx == to_idx:
                    continue
                
                # Skip destination tubes that are complete (can't pour into them)
                if to_tube.is_complete and not to_tube.is_empty:
                    continue
                
                if can_pour(from_tube, to_tube):
                    moves.append((from_idx, to_idx))
        
        return moves
    
    def apply_move(self, from_idx: int, to_idx: int) -> 'PuzzleState':
        """
        Apply a move and return new state (immutable operation)
        
        Args:
            from_idx: Index of tube to pour from
            to_idx: Index of tube to pour into
        
        Returns:
            New PuzzleState with move applied
        """
        # Deep copy tubes
        new_tubes = deepcopy(self.tubes)
        from_tube = new_tubes[from_idx]
        to_tube = new_tubes[to_idx]
        
        # Get the top color segment to pour
        top_color = from_tube.top_color
        if not top_color:
            raise ValueError(f"Cannot pour from empty tube {from_idx}")
        
        # Remove ONLY the first (top) color segment from source
        # Find the index of the top color
        top_idx = next((i for i, seg in enumerate(from_tube.segments) if seg.color != 'empty'), None)
        if top_idx is None:
            raise ValueError(f"Cannot pour from empty tube {from_idx}")
        
        # Remove just this one segment
        from_tube.segments.pop(top_idx)
        
        # Add empty space to source
        from_tube.segments.insert(0, ColorSegment('empty', top_color.height))
        
        # Add color to destination
        # First, remove or reduce the empty segment
        empty_idx = next((i for i, seg in enumerate(to_tube.segments) if seg.color == 'empty'), None)
        if empty_idx is not None:
            empty_seg = to_tube.segments[empty_idx]
            if empty_seg.height > top_color.height:
                # Reduce empty space
                to_tube.segments[empty_idx] = ColorSegment('empty', empty_seg.height - top_color.height)
            else:
                # Remove empty segment completely
                to_tube.segments.pop(empty_idx)
        
        # Add the poured color
        # Check if we can merge with existing top color
        if to_tube.segments and to_tube.segments[0].color == top_color.color:
            # Merge with existing segment
            to_tube.segments[0] = ColorSegment(
                top_color.color,
                to_tube.segments[0].height + top_color.height
            )
        else:
            # Insert new segment
            to_tube.segments.insert(0, ColorSegment(top_color.color, top_color.height))
        
        # Merge consecutive segments of same color
        from_tube.segments = merge_consecutive_segments(from_tube.segments)
        to_tube.segments = merge_consecutive_segments(to_tube.segments)
        
        return PuzzleState(new_tubes)
    
    def __repr__(self):
        return f"PuzzleState({len(self.tubes)} tubes, solved={self.is_solved()})"


def can_pour(from_tube: TubeState, to_tube: TubeState) -> bool:
    """
    Check if we can pour from from_tube into to_tube
    
    Rules:
    - Source must have a non-empty top color
    - Target must have empty space at top
    - Target must have enough capacity
    - Colors must match (or target is empty)
    """
    # Check source has something to pour
    from_color = from_tube.top_color
    if not from_color or from_color.color == 'empty':
        return False
    
    # Check destination has space
    if to_tube.available_space_px < from_color.height:
        return False
    
    # Check color compatibility
    to_color = to_tube.top_color
    if to_color is None:
        # Target is empty, always valid
        return True
    
    # Colors must match
    return to_color.color == from_color.color


def merge_consecutive_segments(segments: List[ColorSegment]) -> List[ColorSegment]:
    """Merge consecutive segments of the same color"""
    if not segments:
        return segments
    
    merged = [segments[0]]
    for seg in segments[1:]:
        if merged[-1].color == seg.color:
            # Merge with previous segment
            merged[-1] = ColorSegment(seg.color, merged[-1].height + seg.height)
        else:
            merged.append(seg)
    
    return merged


def solve(initial_state: PuzzleState, max_depth: int = 200, verbose: bool = False) -> Optional[List[Tuple[int, int]]]:
    """
    Solve the puzzle using backtracking DFS
    
    Args:
        initial_state: Initial puzzle state
        max_depth: Maximum recursion depth
        verbose: Print progress information
    
    Returns:
        List of (from_idx, to_idx) tuples representing the solution, or None if unsolvable
    """
    visited: Set[str] = set()
    states_explored = [0]  # Use list to allow modification in nested function
    
    def dfs(state: PuzzleState, depth: int, path: List[Tuple[int, int]]) -> Optional[List[Tuple[int, int]]]:
        states_explored[0] += 1
        
        # Progress logging every 1000 states
        if verbose and states_explored[0] % 1000 == 0:
            print(f"  Explored {states_explored[0]} states, depth {depth}, visited {len(visited)} unique states")
        
        # Check if solved
        if state.is_solved():
            if verbose:
                print(f"  ✓ Solution found after exploring {states_explored[0]} states!")
            return path
        
        # Check depth limit
        if depth >= max_depth:
            return None
        
        # Check if we've visited this state
        state_hash = state.serialize()
        if state_hash in visited:
            return None
        visited.add(state_hash)
        
        # Get valid moves with heuristics
        moves = state.get_valid_moves()
        
        # Apply heuristics: prioritize moves
        moves = prioritize_moves(state, moves)
        
        # Try each move
        for from_idx, to_idx in moves:
            # Prune inverse consecutive moves
            if len(path) > 0 and path[-1] == (to_idx, from_idx):
                continue
            
            # Apply move
            new_state = state.apply_move(from_idx, to_idx)
            
            # Recurse
            result = dfs(new_state, depth + 1, path + [(from_idx, to_idx)])
            if result is not None:
                return result
        
        return None
    
    if verbose:
        print(f"Starting solver (max_depth={max_depth})...")
    
    result = dfs(initial_state, 0, [])
    
    if verbose and result is None:
        print(f"  ❌ No solution found after exploring {states_explored[0]} states")
    
    return result


def prioritize_moves(state: PuzzleState, moves: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
    """
    Prioritize moves using heuristics:
    1. Moves that complete a tube (best outcome)
    2. Moves to same color (consolidation progress)
    3. Moves from complete tubes to empty (free up space)
    4. Other moves to empty tubes
    5. Other moves
    """
    priority_1 = []  # Completes a tube
    priority_2 = []  # Same color consolidation
    priority_3 = []  # From complete to empty (frees working tube)
    priority_4 = []  # To empty tubes
    priority_5 = []  # Other moves
    
    for from_idx, to_idx in moves:
        to_tube = state.tubes[to_idx]
        from_tube = state.tubes[from_idx]
        
        if would_complete_tube(state, from_idx, to_idx):
            priority_1.append((from_idx, to_idx))
        elif to_tube.top_color and to_tube.top_color.color == from_tube.top_color.color:
            priority_2.append((from_idx, to_idx))
        elif to_tube.is_empty and from_tube.is_complete:
            # Moving complete tube to empty is wasteful unless necessary
            # But keep it as lower priority option
            priority_3.append((from_idx, to_idx))
        elif to_tube.is_empty:
            priority_4.append((from_idx, to_idx))
        else:
            priority_5.append((from_idx, to_idx))
    
    return priority_1 + priority_2 + priority_3 + priority_4 + priority_5


def would_complete_tube(state: PuzzleState, from_idx: int, to_idx: int) -> bool:
    """
    Check if a move would complete the destination tube
    Optimized to avoid expensive state copying
    """
    from_tube = state.tubes[from_idx]
    to_tube = state.tubes[to_idx]
    
    from_color = from_tube.top_color
    if not from_color:
        return False
    
    # If destination is empty, pouring won't complete it (unless it fills it completely)
    if to_tube.is_empty:
        # Would only complete if the pour fills the entire tube with one color
        return from_color.height == to_tube.capacity_px
    
    # If destination already has content, check if adding would complete it
    to_color = to_tube.top_color
    if not to_color or to_color.color != from_color.color:
        return False  # Different colors, won't complete
    
    # Check if destination would contain only one color after the pour
    # This means all non-empty segments in destination must be the same color as what we're pouring
    non_empty = [seg for seg in to_tube.segments if seg.color != 'empty']
    if not all(seg.color == from_color.color for seg in non_empty):
        return False
    
    # Check if the combined amount would fill the tube completely
    total_height = sum(seg.height for seg in non_empty) + from_color.height
    return total_height == to_tube.capacity_px


def compute_execution_plan(moves: List[Tuple[int, int]], animation_delay: float = 1.3) -> List[Tuple[int, int, float]]:
    """
    Compute execution plan with delays to respect animation times
    
    Args:
        moves: List of (from_idx, to_idx) tuples
        animation_delay: Time in seconds for pour animation
    
    Returns:
        List of (from_idx, to_idx, delay_before) tuples
    """
    execution_plan = []
    tube_last_used: Dict[int, float] = {}  # tube_idx -> timestamp when available
    current_time = 0.0
    
    for from_idx, to_idx in moves:
        # Calculate when we can execute this move
        # We need to wait for both tubes to be available
        earliest_time = max(
            tube_last_used.get(from_idx, 0.0),
            tube_last_used.get(to_idx, 0.0)
        )
        
        # Calculate delay needed
        delay = max(0, earliest_time - current_time)
        
        execution_plan.append((from_idx, to_idx, delay))
        
        # Update timing
        current_time = earliest_time + animation_delay
        tube_last_used[from_idx] = current_time
        tube_last_used[to_idx] = current_time
    
    return execution_plan
