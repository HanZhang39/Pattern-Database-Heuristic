"""
Sliding puzzle
"""
import copy
import random
import pickle
from pattern_database import PDB
import numpy as np

class SlidingPuzzlePattern:
    """
    Pattern implementation of sliding puzzle.
    Could also serve as sliding puzzle node when pattern set to None
    """
    def __init__(self, L=4, pattern=None, pos=None, blank=None):
        self.L = L
        assert (pattern is None) or (pos is None)
        if (pattern is None) and (pos is None):
            pattern = list(range(1, L ** 2))
        if pos is not None:
            self.pos = pos
        else:
            self.pos = dict((i, (int(i / L), i % L)) for i in pattern)
            
        if blank is None:
            self.blank = (0, 0)
            assert self.blank not in [l[1] for l in self.pos.items()]
        else:
            self.blank = blank

    def get_children(self):
        incrs = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        children = []
        filled = dict([(k[1], k[0]) for k in self.pos.items()])

        (i, j) = self.blank
        moves = [(i + incr[0], j + incr[1])
                 for incr in incrs if
                 0 <= i + incr[0] < self.L and
                 0 <= j + incr[1] < self.L]
        for move in moves:
            new_blank = move
            new_pos = copy.deepcopy(self.pos)
            cost = 0
            
            if new_blank in filled:
                new_pos[filled[new_blank]] = self.blank
                cost = 1
            
            children.append((cost, SlidingPuzzlePattern(self.L, pos=new_pos, blank = new_blank)))
            
        return children

    def __repr__(self):
        board = [['X' for j in range(self.L)]for i in range(self.L)]
        for k in self.pos:
            val = self.pos[k]
            board[val[0]][val[1]] = str(k)
        board[self.blank[0]][self.blank[1]] = ''
        return ('\n' + '\n'.join(['\t'.join(l) for l in board]) + '\n').expandtabs(4)

    def __hash__(self):
        return hash((self.blank, tuple(self.pos.items())))

    def __eq__(self, other):
        try:
            return self.pos == other.pos and self.blank == other.blank
        except AttributeError:
            return False

    def __lt__(self, other):
        # implement less than just to make Pattern able to fit in a Heap
        return random.choice([True, False])


class SlidingPuzzlePDB(PDB):
    def __init__(self, L=4, pattern=(1, 2, 3)):
        PDB.__init__(self,start_node=SlidingPuzzlePattern(L=L, pattern=pattern),
                   table_size=(L**2) ** (len(pattern) + 1), dtype="uint8")

        self.pattern = pattern
        self.L = L
        self.name = f"{L**2 - 1}_puzzle_{'_'.join(map(str,pattern))}_addidtive_pdb"

    def __to_id__(self, pat: SlidingPuzzlePattern):
        idx = 0
        for i in self.pattern:
            idx = idx * (self.L ** 2) + pat.pos[i][0] * self.L + pat.pos[i][1]
        idx = idx * (self.L ** 2) + pat.blank[0] * self.L + pat.blank[1]
        return idx

    def __to_compressed_id__(self, pat):
        idx = 0
        for i in self.pattern:
            idx = idx * (self.L ** 2) + pat.pos[i][0] * self.L + pat.pos[i][1]
        return idx


    def __compress__(self):
        print("compressing")
        # compressing the blank
        L = self.L
        compressed_table = np.zeros((L**2) ** len(self.pattern), dtype="uint8")
        for i in range((L**2) ** len(self.pattern)):
            candidate = [l for l in self.table[(L**2) * i: (L**2) * (i + 1)] if l > 0]
            if candidate:
                compressed_table[i] = min(candidate)
            else:
                compressed_table[i] = 0
        self.table = compressed_table



def random_sliding_puzzle(l=4, run_round=100):
    """
    randomly generate sliding puzzle instance through random walk

    L - board width/height
    run_round - round of random walk.
        Larger the more difficult instance will be generated
    """
    board = SlidingPuzzlePattern(l)
    for _ in range(run_round):
        board = random.choice(board.get_children())[1]
    return board


def manhattan_dist(state: SlidingPuzzlePattern, goal = None):
    if goal is None:
        goal = SlidingPuzzlePattern(L=state.L)
    cnt = 0
    for p in state.pos:
        cnt += sum(map(abs, [i[0] - i[1] for i in zip(state.pos[p], goal.pos[p])]))
    return cnt

def symmetry_board(state:SlidingPuzzlePattern):
    pos = {}
    symetry_idx = lambda idx: (idx % state.L) * state.L +  int(idx / state.L)
    for k in state.pos:
        pos[symetry_idx(k)] = (state.pos[k][1], state.pos[k][0])
    new_blank = (state.blank[1], state.blank[0])
    return SlidingPuzzlePattern(L=state.L, pos=pos, blank=new_blank)

def __additive_heuristic__(state, heuristics, symmetry=None):
    return sum([h[state] for h in heuristics])

def additive_heuristic_symmetric_lookup(heuristics):
    return lambda state: max(__additive_heuristic__(state, heuristics),
                             __additive_heuristic__(symmetry_board(state), heuristics)
    )

