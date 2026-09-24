import sys
from parser import read_config
from cust_class import start_hub, end_hub, swarm


def main() -> None:
    if len(sys.argv) != 2:
        print('> python fly-in.py [map.txt]')
        exit()
    config = read_config(sys.argv[1])
    for key in config:
        if isinstance(config[key], start_hub):
            start = config[key].name
        if isinstance(config[key], end_hub):
            goal = config[key]
    drones = swarm(start, goal.name, config)
    drones.make_swarm(config[start].max_drones)
    if isinstance(goal, end_hub):
        i = 1
        while not goal.is_deliverd():
            drones.turn(config)
            print(drones.get_stat())
            print(f"turn: {i}")
            i += 1
            input()


if __name__ == "__main__":
    main()
