import copy
import math
import random
# from heapq import heappush, heappop
import pickle
from collections import deque

import numpy as np

class Pattern:
    def __init__(self, L=4, pattern=[1,2,3], pos=None):
        self.L = L
        if pos is not None:
            self.pos = pos
        else:
            self.pos = dict((i, (int(i / L), i % L)) for i in pattern)

    def get_children(self):
        incrs = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        children = []
        filled = {k[1] for k in self.pos.items()}

        for k in self.pos:
            (i, j) = self.pos[k]
            moves = [(i + incr[0], j + incr[1])
                     for incr in incrs if
                     0 <= i + incr[0] < self.L and
                     0 <= j + incr[1] < self.L and
                     (i + incr[0], j + incr[1]) not in filled]
            for move in moves:
                new_pos = copy.deepcopy(self.pos)
                new_pos[k] = move
                children.append(Pattern(pos=new_pos))
        return children

    def __repr__(self):
        board = [[0 for j in range(self.L)]for i in range(self.L)]
        for k in self.pos:
            val = self.pos[k]
            board[val[0]][val[1]] = k
        return '\n'.join([str(l) for l in board]) + '\n'

    def __hash__(self):
        return hash(tuple(self.pos.items()))

    def __eq__(self, other):
        return hasattr(other, 'pos') and self.pos == other.pos

    def __lt__(self, other):
        # implement less than just to make Pattern able to fit in a Heap
        return random.choice([True, False])

class SlidingBoard(Pattern):

    def __init__(self, L=4, pos: dict=None, blank=None):
        self.L = L
        if pos is None:
            self.pos = dict((i, (int(i / L), i % L)) for i in range(1, L ** 2))

        else:
            self.pos = pos

        if blank is None:
            self.blank = [(i, j) for i in range(L) for j in range(L)
                          if (i, j) not in {l[1] for l in self.pos.items()}]
            assert len(self.blank) == 1 # only one blank allowable
            self.blank = self.blank[0]
        else:
            self.blank = blank

    def get_children(self):
        incrs = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        children = []

        (i, j) = self.blank
        filled = dict((k[1], k[0]) for k in self.pos.items())
        moves = [(i + incr[0], j + incr[1])
                 for incr in incrs if
                 0 <= i + incr[0] < self.L and
                 0 <= j + incr[1] < self.L and
                 (i + incr[0], j + incr[1]) in filled]
        for move in moves:
            new_pos = copy.deepcopy(self.pos)
            blank = self.blank
            k = filled[move]
            new_pos[k], blank = blank, new_pos[k]

            children.append(SlidingBoard(L=self.L, pos=new_pos, blank=blank))
        return children

def random_board(run_round=100):
    board = SlidingBoard()
    for _ in range(run_round):
        board = random.choice(board.get_children())
    return board

class PDB:
    
    UNFILLED = 0
    
    def __init__(self, L=4, pattern=[1, 2, 3]):
        self.L = L
        self.pattern = tuple(pattern)
        self.table = np.zeros((L**2) ** len(pattern), dtype="uint8")
        self.name = f"{L**2 - 1}_puzzle_{'_'.join(map(str,pattern))}_addidtive_pdb"

    def __to_id__(self, pat: Pattern):
        idx = 0
        for i in self.pattern:
            idx = idx * (self.L ** 2) + pat.pos[i][0] * self.L + pat.pos[i][1]
        return idx

    def __getitem__(self, x):
        assert isinstance(x, Pattern)
        return self.table[self.__to_id__(x)] - 1

    def save(self, filename=None):
        if filename is None:
            filename = self.name + ".pkl"

        pickle.dump(self, open(filename, "wb"))

    def dfs(self, node, depth, lvl=0):
        cnt = 0
        if self.table[self.__to_id__(node)] == self.UNFILLED:
            cnt += 1
            self.table[self.__to_id__(node)] = lvl + 1
            
        if lvl + 1 < depth:
            for child in node.get_children():
                if self.table[self.__to_id__(child)] == self.UNFILLED or self.table[self.__to_id__(child)] == lvl + 2:
                    cnt += self.dfs(child, depth, lvl=lvl + 1)
        return cnt

    def idfs(self):
        total_cnt = int(math.factorial(self.L ** 2) / math.factorial(self.L ** 2 - len(self.pattern)))
        step = int(total_cnt / 10000) + 1
        cnt = 0
        print(f"totoal: {total_cnt}")
        dep = 1
        while(cnt != total_cnt):
            print(f"dfs with depth: {dep}")
            cnt += self.dfs(Pattern(L=self.L, pattern=self.pattern), depth = dep)
            print(f"{cnt} / {total_cnt}")
            dep += 1

    def bfs(self):
        total_cnt = math.factorial(self.L ** 2) / math.factorial(self.L ** 2 - len(self.pattern))
        step = int(total_cnt / 10000) + 1
        cnt = 1
        print(f"totoal: {total_cnt}")
        bfs_q = deque()
        start = Pattern(L=self.L, pattern=self.pattern)
        bfs_q.append(start)
        self.table[self.__to_id__(start)] = 1
        while bfs_q:
            current = bfs_q.popleft()
            for child in current.get_children():
                if self.table[self.__to_id__(child)] == self.UNFILLED:
                    cnt += 1
                    if cnt % step == 0:
                        print(f"{cnt} / {total_cnt}")
                    self.table[self.__to_id__(child)] = self.table[self.__to_id__(current)] + 1
                    bfs_q.append(child)


def load_pdb(filename):
    with open(filename, 'rb') as file_handle:
        data = pickle.load(file_handle)
        print(data)
        assert isinstance(data, PDB)
        return data

def manhattan_dist(state: Pattern, goal = None):
    if goal is None:
        goal = SlidingBoard(L=state.L)
    cnt = 0
    for p in state.pos:
        cnt += sum(map(abs, [i[0] - i[1] for i in zip(state.pos[p], goal.pos[p])]))
    return cnt

def symetry_idx(idx, L=4):
    return (idx % L) * L +  int(idx / L)

def sym_board(state):
    pos = {}
    for k in state.pos:
        pos[symetry_idx(k)] = (state.pos[k][1], state.pos[k][0])
    return SlidingBoard(pos=pos)

H_12_13_14 = load_pdb("./15_puzzle_12_13_14_addidtive_pdb.pkl")
H_1_2_4_5_8_9 = load_pdb("./15_puzzle_1_2_4_5_8_9_addidtive_pdb.pkl")
H_3_6_7_10_11_15 = load_pdb("./15_puzzle_3_6_7_10_11_15_addidtive_pdb.pkl")

def additive_heuristic_6_6_3(state: Pattern):
    sym = sym_board(state)
    return max(H_12_13_14[state] + H_1_2_4_5_8_9[state] + H_3_6_7_10_11_15[state],
               H_12_13_14[sym] + H_1_2_4_5_8_9[sym] + H_3_6_7_10_11_15[sym])
