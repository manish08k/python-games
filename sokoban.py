import copy
import time

RESET   = "\033[0m"
BOLD    = "\033[1m"
CYAN    = "\033[96m"
YELLOW  = "\033[93m"
GREEN   = "\033[92m"
RED     = "\033[91m"
GREY    = "\033[90m"
WHITE   = "\033[97m"
MAGENTA = "\033[95m"
BLUE    = "\033[94m"
ORANGE  = "\033[38;5;214m"
BG_DARK = "\033[48;5;236m"

def c(text, color):
    return f"{color}{BOLD}{text}{RESET}"

def clear():
    print("\033[2J\033[H", end="")

# ── Tile types ────────────────────────────────────────────────────────────────
WALL    = '#'
FLOOR   = ' '
GOAL    = '.'
BOX     = '$'
BOX_ON  = '*'   # box on goal
PLAYER  = '@'
PLAYER_ON = '+'  # player on goal

# ── Levels ────────────────────────────────────────────────────────────────────
LEVELS = [
    {
        "name": "Baby Steps",
        "grid": [
            "########",
            "#   .  #",
            "#  $   #",
            "#  @   #",
            "########",
        ]
    },
    {
        "name": "Double Trouble",
        "grid": [
            "########",
            "#  ..  #",
            "# $$   #",
            "#  @   #",
            "#      #",
            "########",
        ]
    },
    {
        "name": "The Squeeze",
        "grid": [
            "##########",
            "#   .    #",
            "# #$#### #",
            "#   @    #",
            "#   .    #",
            "#  $     #",
            "##########",
        ]
    },
    {
        "name": "Zigzag",
        "grid": [
            "##########",
            "#.   #   #",
            "# $  #   #",
            "##  ###  #",
            "#   $ .  #",
            "#   @    #",
            "##########",
        ]
    },
    {
        "name": "Four Corners",
        "grid": [
            "##########",
            "#.      .#",
            "#  $  $  #",
            "#   @@   #",
            "#  $  $  #",
            "#.      .#",
            "##########",
        ]
    },
    {
        "name": "Warehouse",
        "grid": [
            "############",
            "#..  #     #",
            "#..  # $$  #",
            "#..  #  $  #",
            "#..    $   #",
            "#..  # @   #",
            "############",
        ]
    },
    {
        "name": "Labyrinth",
        "grid": [
            "############",
            "#    #     #",
            "# $  # $.  #",
            "# ## # ##  #",
            "#  .@.  $  #",
            "#    #  #  #",
            "#### # ##  #",
            "#  $   #.  #",
            "#  #   #   #",
            "############",
        ]
    },
    {
        "name": "The Gauntlet",
        "grid": [
            "##############",
            "#     #      #",
            "# $$$ # ...  #",
            "# $ $ #      #",
            "# $$$ # ...  #",
            "#     #      #",
            "#     @      #",
            "##############",
        ]
    },
]

# ── Parse level ───────────────────────────────────────────────────────────────
def parse_level(level_data):
    grid = [list(row) for row in level_data["grid"]]
    player = None
    boxes  = set()
    goals  = set()

    for r, row in enumerate(grid):
        for col, ch in enumerate(row):
            if ch in (PLAYER, PLAYER_ON):
                player = (r, col)
                grid[r][col] = GOAL if ch == PLAYER_ON else FLOOR
            if ch in (BOX, BOX_ON):
                boxes.add((r, col))
                grid[r][col] = GOAL if ch == BOX_ON else FLOOR
            if ch in (GOAL, BOX_ON, PLAYER_ON):
                goals.add((r, col))

    return grid, player, boxes, goals

# ── Render ────────────────────────────────────────────────────────────────────
TILE_DISPLAY = {
    WALL:      c("██", GREY),
    FLOOR:     "  ",
    GOAL:      c(" ·", YELLOW),
    BOX:       c("▣ ", ORANGE),
    BOX_ON:    c("▣ ", GREEN),
    PLAYER:    c("☺ ", CYAN),
    PLAYER_ON: c("☺ ", MAGENTA),
}

def render(grid, player, boxes, goals, level_name, moves, pushes, undos_left):
    pr, pc = player
    board  = [row[:] for row in grid]

    for (r, col) in boxes:
        if (r, col) in goals:
            board[r][col] = BOX_ON
        else:
            board[r][col] = BOX

    if player in goals:
        board[pr][pc] = PLAYER_ON
    else:
        board[pr][pc] = PLAYER

    clear()
    print(c(f"\n  ╔══ SOKOBAN ══ {level_name} ══╗", CYAN))
    print()
    for row in board:
        line = "  "
        for ch in row:
            line += TILE_DISPLAY.get(ch, "  ")
        print(line)
    print()
    boxes_done = len(boxes & goals)
    total_boxes = len(boxes)
    bar = c("█" * boxes_done, GREEN) + c("█" * (total_boxes - boxes_done), GREY)
    print(f"  Progress : {bar}  {boxes_done}/{total_boxes}")
    print(f"  Moves    : {c(str(moves), YELLOW)}   Pushes: {c(str(pushes), CYAN)}   Undos left: {c(str(undos_left), MAGENTA)}")
    print()
    print(c("  Controls: W/A/S/D or arrows  |  U = Undo  |  R = Restart  |  Q = Quit", GREY))
    print()

# ── Move logic ────────────────────────────────────────────────────────────────
DIRS = {
    'w': (-1, 0), 'a': (0, -1), 's': (1, 0), 'd': (0, 1),
    '\x1b[A': (-1, 0), '\x1b[B': (1, 0), '\x1b[C': (0, 1), '\x1b[D': (0, -1),
}

def try_move(grid, player, boxes, direction):
    dr, dc  = direction
    pr, pc  = player
    nr, nc  = pr + dr, pc + dc

    if grid[nr][nc] == WALL:
        return player, boxes, False, False

    pushed = False
    new_boxes = set(boxes)

    if (nr, nc) in boxes:
        br, bc = nr + dr, nc + dc
        if grid[br][bc] == WALL or (br, bc) in boxes:
            return player, boxes, False, False
        new_boxes.remove((nr, nc))
        new_boxes.add((br, bc))
        pushed = True

    return (nr, nc), new_boxes, True, pushed

# ── Get single keypress ───────────────────────────────────────────────────────
def get_key():
    import sys, tty, termios
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
        if ch == '\x1b':
            ch2 = sys.stdin.read(1)
            ch3 = sys.stdin.read(1)
            return ch + ch2 + ch3
        return ch
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)

# ── Play one level ────────────────────────────────────────────────────────────
def play_level(level_index):
    level_data         = LEVELS[level_index]
    grid, player, boxes, goals = parse_level(level_data)

    history    = []
    max_undos  = 15
    moves      = 0
    pushes     = 0
    start_time = time.time()

    while True:
        undos_left = max_undos - len([_ for _ in history])
        render(grid, player, boxes, goals, level_data["name"], moves, pushes, max(0, max_undos - moves + len(history) + moves - len(history)))

        # Better undo count display
        render(grid, player, boxes, goals, level_data["name"], moves, pushes, max_undos)

        key = get_key().lower()

        if key in ('q',):
            return "quit"

        if key in ('r',):
            grid, player, boxes, goals = parse_level(level_data)
            history = []
            moves   = 0
            pushes  = 0
            continue

        if key == 'u':
            if history:
                player, boxes = history.pop()
                moves  = max(0, moves - 1)
                pushes = max(0, pushes)
            else:
                pass
            continue

        direction = None
        for k, d in DIRS.items():
            if key == k or key == k.lower():
                direction = d
                break

        if direction is None:
            # handle raw arrow key sequences
            for k, d in DIRS.items():
                if len(k) > 1 and key in k:
                    direction = d
                    break

        if direction is None:
            continue

        history.append((player, frozenset(boxes)))
        if len(history) > max_undos:
            history.pop(0)

        new_player, new_boxes, moved, pushed = try_move(grid, player, boxes, direction)

        if moved:
            player  = new_player
            boxes   = new_boxes
            moves  += 1
            if pushed:
                pushes += 1

        # Win check
        if boxes == goals:
            elapsed = int(time.time() - start_time)
            render(grid, player, boxes, goals, level_data["name"], moves, pushes, max_undos)
            print(c("  ╔══════════════════════════════╗", GREEN))
            print(c("  ║   🎉  LEVEL COMPLETE!         ║", GREEN))
            print(c("  ╚══════════════════════════════╝", GREEN))
            print()
            print(f"  Moves : {c(str(moves), YELLOW)}   Pushes: {c(str(pushes), CYAN)}   Time: {c(str(elapsed)+'s', MAGENTA)}")
            print()

            if moves < 20:
                rating = c("🏆 Perfect!", YELLOW)
            elif moves < 40:
                rating = c("🥇 Excellent", GREEN)
            elif moves < 70:
                rating = c("🥈 Good",     CYAN)
            else:
                rating = c("🥉 Solved!",  WHITE)
            print(f"  Rating: {rating}")
            print()
            input(c("  Press ENTER to continue...", GREY))
            return "next"

# ── Level select ──────────────────────────────────────────────────────────────
def level_select(completed):
    clear()
    print(c("\n  ╔══════════════════════════════╗", CYAN))
    print(c("  ║   📦  SOKOBAN  LEVEL SELECT   ║", CYAN))
    print(c("  ╚══════════════════════════════╝\n", CYAN))
    for i, lv in enumerate(LEVELS):
        done = c(" ✓", GREEN) if i in completed else "  "
        lock = "" if i == 0 or (i-1) in completed or i in completed else c(" 🔒", GREY)
        print(f"  {c(str(i+1)+'.', YELLOW)} {lv['name']}{done}{lock}")
    print()
    print(f"  {c('Q', RED)}. Quit")
    print()
    while True:
        ch = input("  Choose level: ").strip().lower()
        if ch == 'q':
            return None
        if ch.isdigit():
            idx = int(ch) - 1
            if 0 <= idx < len(LEVELS):
                if idx == 0 or (idx-1) in completed or idx in completed:
                    return idx
                else:
                    print(c("  Complete the previous level first!", RED))
            else:
                print(c("  Invalid level number.", RED))

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    clear()
    print(c("\n  ╔══════════════════════════════════════╗", CYAN))
    print(c("  ║      📦  S O K O B A N               ║", CYAN))
    print(c("  ║   Push all boxes onto the goals (·)  ║", CYAN))
    print(c("  ╚══════════════════════════════════════╝\n", CYAN))
    print(f"  {c('Tiles:', WHITE)}")
    print(f"  {c('☺', CYAN)}  = You          {c('▣', ORANGE)} = Box         {c('·', YELLOW)} = Goal")
    print(f"  {c('▣', GREEN)} = Box on goal   {c('██', GREY)} = Wall")
    print()
    print(f"  {c('Controls:', WHITE)}  W/A/S/D to move  |  U = Undo  |  R = Restart  |  Q = Quit")
    print()
    input(c("  Press ENTER to start...", GREY))

    completed   = set()
    current     = 0

    while True:
        idx = level_select(completed)
        if idx is None:
            print(c("\n  Thanks for playing Sokoban! 📦\n", CYAN))
            break

        result = play_level(idx)

        if result == "next":
            completed.add(idx)
            if len(completed) == len(LEVELS):
                clear()
                print(c("\n  🏆  YOU COMPLETED ALL LEVELS!  🏆\n", YELLOW))
                print(c("  Amazing work! You are a Sokoban master!\n", GREEN))
                input(c("  Press ENTER to exit...", GREY))
                break
        elif result == "quit":
            print(c("\n  Thanks for playing Sokoban! 📦\n", CYAN))
            break

if __name__ == "__main__":
    main()
