import sys
from parser import read_config


def main() -> None:
    if len(sys.argv) != 2:
        print('> python fly-in.py [map.txt]')
        exit()
    test = read_config(sys.argv[1])
    for x in test:
        print(test[x].paths)


if __name__ == "__main__":
    main()
