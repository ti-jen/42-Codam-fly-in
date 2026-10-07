from collections import deque
from cust_class import hub


def find_path(map: dict[str, hub], loc: str, goal: str) -> list[str]:
    path = []
    queue: deque[str] = deque([])
    rever = {}
    res = []
    for x in map[loc].paths:
        if (
            map[x].get_zone() != 'blocked'
            and map[loc].paths[x] > 0
            and map[x].get_zone() != 'full'
        ):
            if map[x].get_zone() == 'priority' and x not in rever:
                rever[x] = loc
                queue.append(x)
    for x in map[loc].paths:
        if (
            map[x].get_zone() != 'blocked'
            and map[loc].paths[x] > 0
            and map[x].get_zone() != 'full'
        ):
            if map[x].get_zone() != 'priority' and x not in rever:
                rever[x] = loc
                queue.append(x)

    while queue:
        if goal in queue:
            break
        current = queue.popleft()
        if map[current].get_zone() == 'restricted' and current not in res:
            queue.append(current)
            res.append(current)
        else:
            paths = map[current].paths
            for x in paths:
                if (
                    map[x].get_zone() == 'priority'
                    and x not in rever
                    and map[x].get_zone() != 'blocked'
                ):
                    rever[x] = current
                    queue.append(x)
            for x in paths:
                if (
                    map[x].get_zone() != 'priority'
                    and x not in rever
                    and map[x].get_zone() != 'blocked'
                ):
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
