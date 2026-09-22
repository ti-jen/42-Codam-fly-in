import re


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

    def add_path(self, new_path: str, max_link_capacity: int) -> None:
        self.paths[new_path] = max_link_capacity


def read_config(filename: str) -> dict[str, hub]:
    hubs = {}
    with open(filename, 'r') as file:
        for line in file:
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            if line.startswith('nb_drones:'):
                nb_drones = int(line.split(":")[1])
            elif line.startswith(('hub:', 'start_hub:', 'end_hub:')):
                metadata = re.search(r"\[(.*?)\]", line)
                item = line.split()
                hubs[item[1]] = hub(item[1], int(item[2]), int(item[3]))
                if metadata:
                    for x in metadata.group(1).split():
                        value = x.split("=")
                        if value[0] == 'zone':
                            hubs[item[1]].zone = value[1]
                        elif value[0] == 'color':
                            hubs[item[1]].color = value[1]
                        elif value[0] == 'max_drones':
                            hubs[item[1]].max_drones = int(value[1])
                if item[0] == 'start_hub:' or item[0] == 'end_hub:':
                    hubs[item[1]].max_drones = nb_drones
            elif line.startswith('connection:'):
                link_cap = 1
                path = line.split()[1].split("-")
                metadata = re.search(r"\[(.*?)\]", line)
                if metadata:
                    link_cap = int(metadata.group(1).split("=")[1])
                hubs[path[0]].add_path(path[1], link_cap)
                hubs[path[1]].add_path(path[0], link_cap)
    return hubs
