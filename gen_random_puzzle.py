from sliding_puzzle import random_board
import pickle

l = [random_board(1000) for i in range(1000)]

pickle.dump(l, open("random_puzzle_1000.pkl", "wb"))
