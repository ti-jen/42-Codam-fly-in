import pathfinding as search
from .class_hubs import hub
from map_visuals import set_color


class drone:
    def __init__(self, name: str, location: str,
                 goal: str, path: list[str]) -> None:
        self.name = name
        self.location = location
        self.safe_location = location
        self.short_path = path
        self.goal = goal
        self.turns = 0
        self.is_restricted = False

    def move(self, config: dict[str, hub]) -> int:
        if self.location == self.goal:
            return 0
        self.turns += 1
        cur = config[self.location]

        if self.is_restricted:
            cur.safe_path[self.short_path[0]] += 1
            self.location = self.short_path[0]
            self.is_restricted = False
            return 1

        new_path = search.find_path(config, self.location, self.goal)
        if new_path and config[new_path[0]].get_zone() != 'full':
            self.short_path = new_path
        else:
            return 0
        if config[self.short_path[0]].get_zone() == 'restricted':
            if cur.paths[self.short_path[0]] <= 0:
                return 0
            cur.del_drone()
            config[self.short_path[0]].add_drone()
            cur.go_dir(self.short_path[0])
            cur.safe_path[self.short_path[0]] -= 1

            self.is_restricted = True
            return 1
        cur.go_dir(self.short_path[0])
        self.location = self.short_path[0]
        cur.del_drone()
        config[self.short_path[0]].add_drone()
        self.short_path = self.short_path[1:]
        return 1

    def stats(self) -> tuple[str, str] | None:
        loc = self.location
        if self.is_restricted:
            loc = self.short_path[0]
        if loc == self.safe_location:
            return None
        self.safe_location = loc
        return (self.name, loc)


class swarm:
    def __init__(self, start: str, goal: str, map: dict[str, hub]):
        self.start = start
        self.goal = goal
        self.map = map
        self.drone_l: list[drone]
        self.turn_moves = 0

    def make_swarm(self, amount: int) -> None:
        drones = []
        path = search.find_path(self.map, self.start, self.goal)
        for x in range(amount):
            drones.append(drone(f"D{x + 1}", self.start, self.goal, path))
        self.drone_l = drones

    def turn(self, config: dict[str, hub]) -> None:
        for d in self.drone_l:
            self.turn_moves += d.move(config)
        for x in config:
            config[x].reset_turn()

    def get_stat(self) -> str:
        stat = ""
        for d in self.drone_l:
            info = d.stats()
            if info is not None:
                stat += (f"{info[0]}-"
                         f"{set_color(info[1], self.map[info[1]].color)} ")
        return stat

    def print_drone_turns(self) -> None:
        for d in self.drone_l:
            print(f"[{d.name}] turns:{d.turns}")
