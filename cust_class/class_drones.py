import pathfinding as search
from .class_hubs import hub


def set_color(input: str, color: str | None) -> str:
    if color is None:
        return input
    colors = {
        "red": "\033[31m",
        "green": "\033[32m",
        "blue": "\033[34m",
        "yellow": "\033[33m",
        "white": "\033[37m",
        "orange": "\033[38;5;208m",
        "cyan": "\033[36m",
        "purple": "\033[35m",
        "lime": "\033[38;5;118m",
        "magenta": "\033[35m",
        "gold": "\033[38;5;220m",
        "maroon": "\033[38;5;88m",
        "darkred": "\033[38;5;88m",
        "violet": "\033[38;5;129m",
        "crimson": "\033[38;5;160m",
        "rainbow": "\033[38;5;201m",
    }

    return f"{colors[color]}{input}\033[0m"


class drone:
    def __init__(self, name: str, location: str,
                 goal: str, path: list[str]) -> None:
        self.name = name
        self.location = location
        self.short_path = path
        self.goal = goal
        self.is_restricted = False

    def move(self, config: dict[str, hub]) -> None:
        if self.location == self.goal:
            return
        cur = config[self.location]
        next = config[self.short_path[0]]

        if self.is_restricted:
            cur.safe_path[self.short_path[0]] += 1
            self.location = self.short_path[0]
            next.add_drone()
            self.is_restricted = False
            return

        new_path = search.find_path(config, self.location, self.goal)
        if new_path and config[new_path[0]].get_zone() != 'blocked':
            self.short_path = new_path
        else:
            return
        if config[self.short_path[0]].get_zone() == 'restricted':
            if cur.paths[self.short_path[0]] <= 0:
                return
            cur.del_drone()
            cur.go_dir(self.short_path[0])
            cur.safe_path[self.short_path[0]] -= 1
            self.is_restricted = True
            return
        cur.go_dir(self.short_path[0])
        self.location = self.short_path[0]
        cur.del_drone()
        config[self.short_path[0]].add_drone()
        self.short_path = self.short_path[1:]

    def stats(self) -> tuple[str, str]:
        loc = self.location
        if self.is_restricted:
            loc = self.short_path[0]
        return (self.name, loc)


class swarm:
    def __init__(self, start: str, goal: str, map: dict[str, hub]):
        self.start = start
        self.goal = goal
        self.map = map
        self.drone_l: list[drone]

    def make_swarm(self, amount: int) -> None:
        drones = []
        path = search.find_path(self.map, self.start, self.goal)
        for x in range(amount):
            drones.append(drone(f"D{x + 1}", self.start, self.goal, path))
        self.drone_l = drones

    def turn(self, config: dict[str, hub]) -> None:
        for d in self.drone_l:
            d.move(config)
        for x in config:
            config[x].reset_turn()

    def get_stat(self) -> str:
        stat = ""
        for d in self.drone_l:
            info = d.stats()
            stat += f"{info[0]}-{set_color(info[1], self.map[info[1]].color)} "
        return stat
