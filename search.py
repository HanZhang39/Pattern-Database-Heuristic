from heapq import heappop, heappush

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

        for neighbor in current.get_children():
            # allow reopen
            if neighbor in closed_set:
                continue

            if neighbor not in gscore or gscore[current] + 1 < gscore[neighbor]:
                gscore[neighbor] = gscore[current] + 1
                came_from[neighbor] = current
                heappush(oheap, (gscore[neighbor] + heuristic(neighbor), neighbor))

NODE_CNT = 0

def ida_star_search(start, goal, heuristic, bound=0, peri=None):
    global NODE_CNT
    NODE_CNT = 0
    bound = heuristic(start)
    path = [start]

    if peri is None:
        print("No perimeter used")

    while True:
        print(f"current bound: {bound}")
        t = search(path, goal, bound, heuristic, peri)
        if t[0]:
            print(NODE_CNT)
            return t[1]
        if t[1] is None:
            return t[1]
        bound = t[1]

def search(path, goal, bound, heuristic, peri=None):
    global NODE_CNT
    NODE_CNT += 1
    node = path[-1]

    h = heuristic(node)

    f = len(path) - 1 + h
    if f > bound:
        return (False, f)

    if peri and h <= peri.depth :
        if peri[node] is not None:
            print("using perimeter ")
            path += peri.get_path(node)
            return (True, path)

    if node == goal:
        return (True, path)
    res = None
    for succ in node.get_children():
        if succ not in path:
            path.append(succ)
            t = search(path, goal, bound, heuristic, peri)
            if t[0]:
                return (True, path)
            if t[1] is not None:
                if res is None:
                    res = t[1]
                else:
                    res = min(res, t[1])
            path.pop()
    return (False, res)
 
