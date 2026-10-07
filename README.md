*This project has been created as part of the 42 curriculum by tkroon*

# Fly-In

## Description

Fly-In is a turn-based simulation of a swarm of drones navigating a network
of delivery hubs from a single **start hub** to a single **end hub**. The
network is described in a plain-text level file as a graph of hubs
(nodes) and connections (edges), each with its own constraints — capacity
limits, movement cost, and accessibility — that a routing algorithm has to
respect and route around.

Each hub can be one of four zone types, which is the main lever the maps
use to create interesting routing problems:

| Zone | Movement cost | Notes |
|---|---|---|
| `normal` | 1 turn | Default |
| `priority` | 1 turn | Preferred when a route has a choice |
| `restricted` | 2 turns | Slower, sometimes the only way through |
| `blocked` | — | Impassable |

A hub also becomes **dynamically blocked** once it's holding as many
drones as its `max_drones` allows, regardless of its declared zone type —
so even a `normal` or `priority` hub can turn into a temporary obstacle
under congestion.

## Instructions

### Project layout
```
fly-in.py          entry point: loads a map, runs the turn-by-turn simulation
cust_class/         hub / start_hub / end_hub, drone, and swarm classes
parser/              read_config.py — loads and validates a level file
pathfinding/          find_path.py — the routing algorithm
map_visuals/           ASCII rendering + terminal colors
```

### Running the simulation
```
make run MAP=example.txt
```
Each turn, every drone's position is printed to the terminal (colored to
match its current hub), followed by the turn counter; press Enter to
advance to the next turn. The simulation ends once every drone has
reached the end hub.
```
make debug MAP=example.txt
```
this wil run the programm in debug mode using pdb

```
make clean
```
Remove temporary files or caches (e.g., __pycache__, .mypy_cache) to
keep the project environment clean.

```
make lint
make lint-strict
```
checks the programm with the giving flags.

```
make venv
```
creates a virtual environemnt

### Level file format
```
nb_drones: <positive integer>

start_hub: <name> <x> <y> [metadata]
hub: <name> <x> <y> [metadata]
end_hub: <name> <x> <y> [metadata]

connection: <name>-<name> [max_link_capacity=<n>]
```
- Exactly one `start_hub` and one `end_hub` are required.
- Hub names may use any characters except `-` (reserved for connections)
  or whitespace, and must be unique, as must each hub's coordinates.
- Metadata is a space-separated `key=value` list in square brackets:
  `zone=` (`normal`/`priority`/`restricted`/`blocked`), `color=` (for the
  ASCII renderer), `max_drones=` (ignored on the start/end hub, which have
  no capacity limit).
- `#` starts a comment; blank lines are ignored.

## Algorithm Choices and Implementation Strategy

### Parsing (`parser/read_config.py`)
The level file is parsed in a single top-to-bottom pass. Hub names and
coordinates are registered as they're read, so a `connection:` line can
only reference hubs that have *already* been declared earlier in the file
— this catches typos and forward references for free, without a second
pass. Every malformed line (wrong token count, unknown metadata key,
non-numeric capacity, a connection naming an unregistered hub, a
duplicate hub name or duplicate connection in either direction, and so
on) raises a specific `ValueError` naming the offending line, rather than
failing with a generic parser crash.

### Capacity model (`cust_class/class_hubs.py`)
A hub tracks two things: how many drones currently occupy it (`drones`),
and the largest number it's allowed to hold (`max_drones`). Rather than
treating capacity as a separate check layered on top of zone type, the
two are unified in one place — `get_zone()` — which returns `'blocked'`
whenever a hub is at capacity, *regardless of its declared zone type*,
and falls back to the hub's real zone otherwise. Every other part of the
codebase (pathfinding, movement, rendering) reads a hub's zone exclusively
through this method, so congestion-driven blocking and declared
`zone=blocked` zones are indistinguishable to the rest of the system —
one fewer special case to get wrong.

Connections carry a similar two-tier capacity system:
- `paths` is the connection's *remaining capacity for this turn* — how
  many more drones can start crossing it right now. It resets to the
  declared maximum (`safe_path`) at the start of every turn.
- `safe_path` is the connection's *declared* maximum, and doubles as the
  reservation table for drones that are mid-crossing on a 2-turn
  `restricted` connection: capacity is held for the full two turns, not
  released after the first, so a restricted link can't be oversubscribed
  by drones starting their crossing on consecutive turns.

### Pathfinding (`pathfinding/find_path.py`)
Routing is re-computed **every turn, for every drone**, rather than
planned once at the start — this is what lets a drone react to a hub that
has since filled up or a link that's since been exhausted by another
drone, instead of committing to a route that might deadlock partway
through.

The search itself is a modified breadth-first search with two
adjustments on top of plain BFS:

1. **Priority-zone preference.** At every expansion step, a node's
   `priority`-zone neighbors are enqueued *before* its other neighbors.
   Since BFS explores in queue order, this biases the search toward
   routes through priority zones without needing explicit edge weights —
   a priority zone is still reached in the same number of turns as a
   normal one, but the algorithm will reach for it first when a route has
   a choice.
2. **Restricted-zone cost.** When a `restricted` zone is dequeued, it's
   re-queued once and marked, so its own neighbors aren't expanded until
   its *second* dequeue — effectively giving it one extra turn in the
   search before the path can continue past it, which is what encodes
   "restricted costs 2 turns" inside a BFS rather than switching to a
   full weighted-shortest-path algorithm.

Blocked hubs (by zone or by capacity, via `get_zone()`) are never
enqueued, so the search naturally routes around congestion as it builds
up over the course of the simulation.

### Movement (`cust_class/class_drones.py`)
Each turn, a drone re-plans with `find_path`; if its next hop is
currently blocked, it simply waits (no move, no capacity consumed) rather
than committing to a stale path. A move onto a `restricted` hub is split
across two turns: on the first turn the drone reserves its spot (holding
the link's `safe_path` capacity and leaving the source hub), and the
second turn is treated as free transit time before it formally arrives
and the destination hub's drone count increments — mirroring the 2-turn
cost the pathfinder already accounts for.

## Visual Representation

The project has two layers of visualization, for two different purposes.

### In-simulation ASCII map (`map_visuals/`)
While `fly-in.py` is running, each hub is rendered as a small bordered
"card" showing its name, zone, and current occupancy (`drones/max_drones`),
color-coded by its declared `color` metadata. Connections between hubs are
drawn with Unicode box-drawing characters (`─│┌┐└┘`), computed from each
hub's relative grid position so that straight runs, corners, and
multi-column spans all render correctly regardless of the map's layout.
Each turn's frame is redrawn in place — using ANSI cursor-control codes
to move up and clear the previous frame rather than scrolling the
terminal — so the map reads as a live, updating view of the simulation
rather than a growing log. This is the primary way to actually watch a
simulation unfold: at a glance, you can see which hubs are congested
(occupancy close to their cap), which zones a given drone is routing
through, and where bottlenecks are forming turn to turn.

Together, these give three views of the same underlying model: a live,
turn-by-turn terminal view for watching a simulation run, an animated
desktop view for checking a computed route.

## Resources
https://www.w3schools.com/python/default.asp
https://www.geeksforgeeks.org/
https://claude.ai
https://chatgpt.com/
https://www.geeksforgeeks.org/python/python-program-for-breadth-first-search-or-bfs-for-a-graph/

## AI use
AI was used to find the leaks in my code with the parser it was also used to write out all the color hex codes or suggesting diffrent ways to approach somthing. AI was also used to help write out this ReadMe