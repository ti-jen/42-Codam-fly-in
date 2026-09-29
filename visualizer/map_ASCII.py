from cust_class import hub


class GridMapper:
    def __init__(self,
                 xl: list[int],
                 yl: list[int],
                 config: dict[str, hub]) -> None:
        self.config = config
        self.min_x, self.max_x = min(xl), max(xl)
        self.min_y, self.max_y = min(yl), max(yl)

    def get_cords(self, x: str) -> tuple[int, int]:
        return (self.config[x].cord_x - self.min_x,
                self.max_y - self.config[x].cord_y)

    def range_x(self) -> int:
        return self.max_x - self.min_x + 1

    def range_y(self) -> int:
        return self.max_y - self.min_y + 1


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
        "black": "\033[30m",
        "brown": "\033[38;5;130m",

    }
    return f"{colors[color]}{input}\033[0m"


def make_hub_card(zone: hub) -> list[str]:
    fields = [
        f"│name: {zone.name}",
        f"│zone: {zone.zone}",
        f"│drones: {zone.drones}/{zone.max_drones}",
    ]

    def trim_line(line: str) -> str:
        if len(line) >= 25:
            line = line[:22] + "..."
        else:
            while len(line) <= 24:
                line += " "
        line += "│"
        return line

    result = [set_color("██████████████████████████", zone.color)]
    for x in fields:
        result.append(trim_line(x))
    result.append("└────────────────────────┘")
    return result


def make_line(cacl: GridMapper,
              config: dict[str, hub],
              source: str,
              line_grid: dict[int, list[list[str]]],
              cord: int,
              card: dict[int, list[str]]
              ) -> tuple[dict[int, list[str]], dict[int, list[list[str]]]]:
    def draw_line(line: list[str]) -> list[str]:
        return list(map(lambda x: "─" if x == " " else x, line))
    paths = config[source].paths
    s_cord = cacl.get_cords(source)
    s_row = (s_cord[1] * 5) + 2
    line = line_grid[cord]
    for p in paths:
        p_cord = cacl.get_cords(p)
        p_row = (p_cord[1] * 5) + 2

        if s_cord[0] <= p_cord[0]:
            line = line_grid[cord]
        else:
            line = line_grid[cord - 1]

        if s_cord[1] == p_cord[1]:
            line[s_row] = draw_line(line[s_row])
        elif s_cord[1] > p_cord[1]:
            line[s_row][:2] = draw_line(line[s_row][:2])
            line[s_row][2] = "┘"
            if s_cord[0] < p_cord[0]:
                line[p_row][2:] = draw_line(line[p_row][2:])
                line[(p_cord[1] * 5) + 2][2] = "┌"
            else:
                line[p_row][:2] = draw_line(line[p_row][:2])
                line[(p_cord[1] * 5) + 2][2] = "┐"
            i = 1
            while s_row - i != p_row:
                line[s_row - i][2] = "│"
                i += 1
        elif s_cord[1] < p_cord[1]:

            line[s_row][:1] = draw_line(line[s_row][:1])
            line[s_row][1] = "┐"
            if s_cord[0] < p_cord[0]:
                line[p_row][2:] = draw_line(line[p_row][2:])
                line[(p_cord[1] * 5) + 2][1] = "└"
            else:
                line[p_row][:2] = draw_line(line[p_row][:2])
                line[p_row][1] = "┘"
            i = 1
            while s_row + i != p_row:
                line[s_row + i][1] = "│"
                i += 1
        if s_cord[0] - 1 > p_cord[0]:
            span = s_cord[0] - p_cord[0]
            for step in range(1, span):
                card[cord - step][p_row] = "──────────────────────────"
            for step in range(1, span + 1):
                line_grid[cord - step][p_row] = draw_line(
                    line_grid[cord - step][p_row])
        if s_cord[0] + 1 < p_cord[0]:
            span = p_cord[0] - s_cord[0]
            for step in range(1, span):
                card[cord + step][p_row] = "──────────────────────────"
                line_grid[cord + step][p_row] = draw_line(
                    line_grid[cord + step][p_row])

        if s_cord[0] <= p_cord[0]:
            line_grid[cord] = line
        else:
            line_grid[cord - 1] = line

    return card, line_grid


def set_hub_card(card: list[str], grid: list[str], cord_y: int) -> list[str]:
    y = 0
    card_y = 0 - (cord_y * 5)
    for _ in grid:
        if card_y >= 0 and card_y < 5:
            grid[y] = card[card_y]
        card_y += 1
        y += 1
    return grid


def print_canvas(can: dict[int, list[str]],
                 line: dict[int, list[str]],
                 size: int) -> None:
    result = ["" for _ in range(size)]
    for key in can:
        i = 0
        for card, dir in zip(can[key], line[key]):
            result[i] += card + dir
            i += 1
    for x in result:
        print(x)


def Render_map(config: dict[str, hub]) -> int:
    xl = [config[cord].cord_x for cord in config]
    yl = [config[cord].cord_y for cord in config]
    grid = GridMapper(xl, yl, config)
    cards = {x: ["                          " for _ in range(
        (grid.range_y() * 5))] for x in range(grid.range_x())}
    line = {x: [[" " for _ in range(4)] for _ in range(
        (grid.range_y()) * 5)] for x in range(grid.range_x())}
    for x in config:
        cord = grid.get_cords(x)
        new = make_line(grid, config, x, line, cord[0], cards)
        cards = new[0]
        line = new[1]
    str_line = {
        key: ["".join(inner) for inner in value]
        for key, value in line.items()
        }

    for x in config:
        card = (make_hub_card(config[x]))
        cord = grid.get_cords(x)
        cards[cord[0]] = set_hub_card(card, cards[cord[0]],  cord[1])
    print_canvas(cards, str_line, grid.range_y() * 5)
    return grid.range_y() * 5
