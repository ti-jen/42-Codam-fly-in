import re
from cust_class import hub, end_hub, start_hub
from map_visuals import set_color


def check_input(input: list[str]) -> list[str]:
    if len(input) < 4:
        raise ValueError(
            "zone definition error:",
            "(expected 'type: name x y [metadata]'): {input}"
        )
    if "-" in input[1]:
        raise ValueError(f"Invalid dash in: {input[1]}")
    if (not input[2].lstrip('-+').isdigit() or
       not input[3].lstrip('-+').isdigit()):
        print(input)
        raise ValueError(f"Invalid input in {input[0]}")
    return input


def read_config(filename: str) -> dict[str, hub]:
    hubs: dict[str, hub] = {}
    reg_names = []
    reg_paths = []
    reg_cords = []
    valid_start = False
    valid_end = False
    with open(filename, 'r') as file:
        for line in file:
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            if line.startswith('nb_drones:'):
                if len(line.split(":")) != 2:
                    raise ValueError("wrong nb_drones"
                                     "(excpected: nb_drones: 1)")
                try:
                    nb_drones = int(line.split(":")[1])
                except ValueError:
                    raise ValueError(f"nb_drones is not 'int': {line}")
                if nb_drones <= 0:
                    raise ValueError("drones can't be less than 1")
                break
            else:
                raise ValueError("missing nb_drones first line")
        for line in file:
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            if line.startswith(('hub:', 'start_hub:', 'end_hub:')):
                metadata = re.search(r"\[(.*?)\]", line)
                item = check_input(line.split())
                if item[1] in reg_names:
                    raise ValueError(f"dubbel hub name: {item[1]}")
                else:
                    reg_names.append(item[1])
                if (item[2], item[3]) in reg_cords:
                    raise ValueError(f"dubbel cords: x,{item[2]} y,{item[3]}")
                else:
                    reg_cords.append((item[2], item[3]))
                if item[0] == 'start_hub:':
                    if valid_start:
                        raise ValueError("dubbel start_hub")
                    hubs[item[1]] = start_hub(item[1],
                                              int(item[2]),
                                              int(item[3]),
                                              nb_drones)
                    valid_start = True
                elif item[0] == 'end_hub:':
                    if valid_end:
                        raise ValueError("dubbel end_hub")
                    hubs[item[1]] = end_hub(item[1],
                                            int(item[2]),
                                            int(item[3]),
                                            nb_drones)
                    valid_end = True
                else:
                    hubs[item[1]] = hub(item[1], int(item[2]), int(item[3]))
                if metadata:
                    for x in metadata.group(1).split():
                        value = x.split("=")
                        if len(value) != 2:
                            raise ValueError("Invalid metadata"
                                             f"'{x}' in: {line}")
                        if value[0] == 'zone':
                            hubs[item[1]].add_zone(value[1])
                        elif value[0] == 'color':
                            try:
                                set_color("", value[1])
                            except KeyError as e:
                                raise KeyError(f"{e} is not a color: {line}")
                            hubs[item[1]].color = value[1]
                        elif value[0] == 'max_drones':
                            try:
                                hubs[item[1]].add_max_drones(int(value[1]))
                            except ValueError:
                                raise ValueError("add_max_drones is not"
                                                 f"'int':{line}")
                        else:
                            raise ValueError(f"{value[0]} does not exist")
            elif line.startswith('connection:'):
                link_cap = 1
                path = line.split()
                if len(path) < 2:
                    raise ValueError(f"wrong connection (expected 'connection:"
                                     f"name1-name2'): {line}")
                path = path[1].split("-")
                if len(path) != 2:
                    raise ValueError(f"wrong connection (expected 'connection:"
                                     f"name1-name2'): {line}")
                if path[0] not in reg_names or path[1] not in reg_names:
                    raise ValueError(f"name does not exist: {line}")
                if path in reg_paths or path[::-1] in reg_paths:
                    raise ValueError(f"path already exists: {line}")
                else:
                    reg_paths.append(path)
                metadata = re.search(r"\[(.*?)\]", line)
                if metadata:
                    cap_value = metadata.group(1).split("=")
                    if len(cap_value) != 2:
                        raise ValueError("Invalid metadata"
                                         f"'{metadata.group(1)}' in: {line}")
                    if cap_value[0] == 'max_link_capacity':
                        if len(cap_value) != 2:
                            raise ValueError("Invalid metadata "
                                             f"{metadata.group(1)} in: {line}")
                    else:
                        raise ValueError(f"{cap_value[0]} does not exist")
                    try:
                        link_cap = int(cap_value[1])
                    except ValueError:
                        raise ValueError("max_link_capacity is not"
                                         f"'int':{line}")
                hubs[path[0]].add_path(path[1], link_cap)
        if not valid_end or not valid_start:
            raise ValueError("No valid start/end")
    return hubs
