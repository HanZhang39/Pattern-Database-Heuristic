from heapq import heappop, heappush
from collections import deque
import pickle

def a_star_search(start, goal, heuristic):
    closed_set = set()
    gscore = {start:0}
    came_from = {}
    oheap = []

    print(start)
    heappush(oheap, (gscore[start] + heuristic(start), start))

    while oheap:
        current = heappop(oheap)[1]
        if current in closed_set:
            continue
        if current == goal:
            print(len(closed_set))
            path = []
            # print(f"path_length: {gscore[current]}")
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start)
            path.reverse()
            return path

        closed_set.add(current)

        for dist, neighbor in current.get_children():
            # allow reopen
            if neighbor in closed_set:
                continue

            if neighbor not in gscore or gscore[current] + dist < gscore[neighbor]:
                gscore[neighbor] = gscore[current] + dist
                came_from[neighbor] = current
                heappush(oheap, (gscore[neighbor] + heuristic(neighbor), neighbor))


def ida_star_search(start, goal, heuristic, bound=0):
    node_cnt = 0
    bound = heuristic(start)
    path = [start]

    while True:
        print(f"current bound: {bound}")
        finished, bound, cnt = search(path, goal, bound, heuristic)
        node_cnt += cnt
        if finished:
            print(f"totalcnt: {node_cnt}")
            return path
        if bound is None:
            print(f"totalcnt: {node_cnt}")
            print("Not found")
            return None

def search(path, goal, bound, heuristic):
    node_cnt = 1
    node = path[-1]

    h = heuristic(node)

    f = len(path) - 1 + h
    if f > bound:
        return (False, f, node_cnt)

    if node == goal:
        return (True, None, node_cnt)
    res = None
    for _, succ in node.get_children():
        if succ not in path:
            path.append(succ)
            finished, new_bound, cnt = search(path, goal, bound, heuristic)
            node_cnt += cnt
            if finished:
                return (True, None, node_cnt)
            if new_bound is not None:
                if res is None:
                    res = new_bound
                else:
                    res = min(res, new_bound)
            path.pop()
    return (False, res, node_cnt)
 
