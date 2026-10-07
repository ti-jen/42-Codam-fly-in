
class hub:
    def __init__(self,
                 name: str,
                 cord_x: int,
                 cord_y: int,
                 color: str | None = None,
                 max_drones: int = 1,
                 zone: str = 'normal'):
        self.name = name
        self.cord_x = cord_x
        self.cord_y = cord_y
        self.color = color
        self.max_drones = max_drones
        self.zone = zone
        self.paths: dict[str, int] = {}
        self.safe_path: dict[str, int] = {}
        self.drones: int = 0

    def add_zone(self, zone: str) -> None:
        if zone not in ['normal', 'blocked', 'restricted', 'priority']:
            raise ValueError(f"{zone} does not exist")
        self.zone = zone

    def add_max_drones(self, max_drone: int) -> None:
        if max_drone <= 0:
            raise ValueError(f"max drones must be positve: {max_drone}")
        if max_drone > 1000:
            raise ValueError(f"max drones must be below 1000: {max_drone}")
        self.max_drones = max_drone

    def add_path(self, new_path: str, max_link_capacity: int) -> None:
        if max_link_capacity <= 0:
            raise ValueError(f"capacity must be positve: {max_link_capacity}")
        if max_link_capacity > 1000:
            raise ValueError("capacity must be below 1000:"
                             f"{max_link_capacity}")
        self.paths[new_path] = max_link_capacity
        self.safe_path[new_path] = max_link_capacity

    def get_zone(self) -> str:
        if self.drones >= self.max_drones:
            return 'full'
        else:
            return self.zone

    def add_drone(self) -> None:
        self.drones += 1

    def del_drone(self) -> None:
        self.drones -= 1

    def go_dir(self, dir: str) -> None:
        self.paths[dir] -= 1

    def reset_turn(self) -> None:
        self.paths = self.safe_path.copy()


class start_hub(hub):
    def __init__(self,
                 name: str,
                 cord_x: int,
                 cord_y: int,
                 numb_drones: int,
                 color: str | None = None,
                 zone: str = 'normal') -> None:
        super().__init__(name, cord_x, cord_y, color, numb_drones, zone)
        self.drones = numb_drones

    def add_max_drones(self, max_drone: int) -> None:
        return


class end_hub(hub):
    def __init__(self,
                 name: str,
                 cord_x: int,
                 cord_y: int,
                 numb_drones: int,
                 color: str | None = None,
                 zone: str = 'normal') -> None:
        super().__init__(name, cord_x, cord_y, color, numb_drones, zone)

    def is_deliverd(self) -> bool:
        if self.drones == self.max_drones:
            return True
        else:
            return False

    def add_max_drones(self, max_drone: int) -> None:
        return
