from sliding_puzzle import SlidingPuzzlePDB

P1 = SlidingPuzzlePDB(pattern=[3, 6, 7, 10, 11, 15])
P1.expand()
P1.save()

P2 = SlidingPuzzlePDB(pattern=[12,13,14])
P2.expand()
P2.save()

P3 = SlidingPuzzlePDB(pattern=[1, 2, 4, 5, 8, 9])
P3.expand()
P3.save()
