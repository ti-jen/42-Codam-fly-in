import sys
from parser import read_config
from cust_class import start_hub, end_hub, swarm
from map_visuals import Render_map, set_color


def clear_lines(n: int) -> None:
    for _ in range(n):
        print("\033[F\033[K", end="")


def main() -> None:
    if len(sys.argv) != 2:
        print('> make run MAP=example.txt')
        exit()
    try:
        config = read_config(sys.argv[1])
    except Exception as e:
        exit(f'{set_color("[ERROR] ", "red")}{e}')
    for key in config:
        if isinstance(config[key], start_hub):
            start = config[key].name
        if isinstance(config[key], end_hub):
            goal = config[key]
    drones = swarm(start, goal.name, config)
    drones.make_swarm(config[start].max_drones)
    turns = []
    if isinstance(goal, end_hub):
        i = 0
        while not goal.is_deliverd():
            lines = Render_map(config)
            turns.append(f"[turn: {i} moves: {drones.turn_moves}]"
                         f"{drones.get_stat()}")
            drones.turn_moves = 0
            for x in turns:
                print(x)
            i += 1
            input()
            drones.turn(config)
            clear_lines(lines + 2 + len(turns))
    Render_map(config)
    turns.append(f"[turn: {i} moves: {drones.turn_moves}]"
                 f"{drones.get_stat()}")
    for x in turns:
        print(x)
    print(f"--finished in {i} turns--")
    drones.print_drone_turns()


if __name__ == "__main__":
    main()
