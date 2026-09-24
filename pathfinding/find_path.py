from collections import deque
from cust_class import hub


def find_path(map: dict[str, hub], loc: str, goal: str) -> list[str]:
    path = []
    queue: deque[str] = deque([])
    rever = {}

    for x in map[loc].paths:
        if map[x].get_zone() != 'blocked' and map[loc].paths[x] > 0:
            rever[x] = loc
            queue.append(x)

    while queue:
        current = queue.popleft()
        if current == goal:
            break
        paths = map[current].paths
        for x in paths:
            if map[x].get_zone() != 'blocked':
                rever[x] = current
                queue.append(x)

    if goal not in rever:
        return []
    path_current = goal
    while path_current != loc:
        path.append(path_current)
        path_current = rever[path_current]
    path.reverse()
    return path
