import random
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

def c(text, color):
    return f"{color}{BOLD}{text}{RESET}"

def clear():
    print("\033[2J\033[H", end="")

# ── Grid helpers ──────────────────────────────────────────────────────────────

def make_grid(size, val=0):
    return [[val] * size for _ in range(size)]

def toggle(grid, r, col, size):
    for dr, dc in [(0,0),(-1,0),(1,0),(0,-1),(0,1)]:
        nr, nc = r+dr, col+dc
        if 0 <= nr < size and 0 <= nc < size:
            grid[nr][nc] ^= 1

def is_solved(grid):
    return all(grid[r][c] == 0 for r in range(len(grid)) for c in range(len(grid[0])))

def generate_puzzle(size, difficulty):
    """Generate a solvable puzzle by starting from solved state and toggling."""
    grid  = make_grid(size, 0)
    moves = {"easy": size*2, "medium": size*3, "hard": size*5}[difficulty]
    solution_toggles = set()
    for _ in range(moves * 3):
        r  = random.randint(0, size-1)
        co = random.randint(0, size-1)
        toggle(grid, r, co, size)
        if (r, co) in solution_toggles:
            solution_toggles.remove((r, co))
        else:
            solution_toggles.add((r, co))
    if is_solved(grid):
        r, co = random.randint(0, size-1), random.randint(0, size-1)
        toggle(grid, r, co, size)
    return grid

# ── Hint: solve using Gaussian elimination over GF(2) ────────────────────────

def get_hint(grid, size):
    """Return a list of (r,c) cells to toggle to solve. Uses GF(2) Gaussian elimination."""
    n = size * size
    # Build the toggle matrix
    A = []
    for r in range(size):
        for co in range(size):
            row_eq = [0] * n
            for dr, dc in [(0,0),(-1,0),(1,0),(0,-1),(0,1)]:
                nr, nc = r+dr, co+dc
                if 0 <= nr < size and 0 <= nc < size:
                    row_eq[nr*size + nc] = 1
            A.append(row_eq)
    b = [grid[r][co] for r in range(size) for co in range(size)]

    # Augmented matrix
    mat = [A[i][:] + [b[i]] for i in range(n)]

    pivot_cols = []
    row_idx = 0
    for col in range(n):
        found = -1
        for r in range(row_idx, n):
            if mat[r][col] == 1:
                found = r
                break
        if found == -1:
            continue
        mat[row_idx], mat[found] = mat[found], mat[row_idx]
        pivot_cols.append((row_idx, col))
        for r in range(n):
            if r != row_idx and mat[r][col] == 1:
                mat[r] = [(mat[r][i] ^ mat[row_idx][i]) for i in range(n+1)]
        row_idx += 1

    solution = [0] * n
    for r, col in pivot_cols:
        solution[col] = mat[r][n]

    hints = []
    for i, v in enumerate(solution):
        if v == 1:
            hints.append((i // size, i % size))
    return hints

# ── Render ────────────────────────────────────────────────────────────────────

def render(grid, size, cursor, moves, hints_used, hint_cells, difficulty, level_name, start_time):
    clear()
    elapsed = int(time.time() - start_time)
    mins, secs = divmod(elapsed, 60)

    print(c("\n  ╔══════════════════════════════════════╗", CYAN))
    print(c("  ║        💡  L I G H T S  O U T        ║", CYAN))
    print(c("  ╚══════════════════════════════════════╝\n", CYAN))

    diff_col = {
        "easy":   GREEN,
        "medium": YELLOW,
        "hard":   RED,
    }.get(difficulty, WHITE)

    lights_on  = sum(grid[r][co] for r in range(size) for co in range(size))
    total      = size * size
    lights_off = total - lights_on

    print(f"  Level : {c(level_name, MAGENTA)}   Difficulty: {c(difficulty.capitalize(), diff_col)}")
    print(f"  Moves : {c(str(moves), YELLOW)}   Hints used: {c(str(hints_used), CYAN)}   Time: {c(f'{mins:02d}:{secs:02d}', WHITE)}")

    # Progress bar
    bar = c("●" * lights_off, GREEN) + c("●" * lights_on, RED)
    print(f"  Lights: {bar}  {lights_off}/{total} off\n")

    cr, cc = cursor

    # Column headers
    header = "      " + "  ".join(c(str(co+1).center(3), GREY) for co in range(size))
    print(header)
    print()

    for r in range(size):
        row_label = c(str(r+1).rjust(2), GREY)
        row_str   = f"  {row_label}  "
        for co in range(size):
            cell      = grid[r][co]
            is_cursor = (r == cr and co == cc)
            is_hint   = (r, co) in hint_cells

            if cell == 1:
                # ON — bright yellow square
                inner = c("▓▓▓", YELLOW)
            else:
                # OFF — dark square
                inner = c("░░░", GREY)

            if is_cursor and is_hint:
                border_l = c("[", MAGENTA)
                border_r = c("]", MAGENTA)
            elif is_cursor:
                border_l = c("[", CYAN)
                border_r = c("]", CYAN)
            elif is_hint:
                border_l = c("⟨", RED)
                border_r = c("⟩", RED)
            else:
                border_l = " "
                border_r = " "

            row_str += border_l + inner + border_r
        print(row_str)
    print()

    if hint_cells:
        positions = ", ".join(f"({r+1},{co+1})" for r, co in sorted(hint_cells))
        print(c(f"  💡 Hint cells: {positions}", RED))
        print()

    print(c("  Controls:", CYAN))
    print("   W/A/S/D or ↑↓←→  move cursor")
    print("   SPACE or ENTER    toggle cell")
    print("   H                 get a hint  (shows cells to press)")
    print("   C                 clear hints")
    print("   R                 restart level")
    print("   Q                 quit to menu")
    print()

# ── Get keypress ──────────────────────────────────────────────────────────────

def get_key():
    import sys, tty, termios
    fd  = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
        if ch == '\x1b':
            ch2 = sys.stdin.read(1)
            if ch2 == '[':
                ch3 = sys.stdin.read(1)
                return '\x1b[' + ch3
            return ch + ch2
        return ch
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)

# ── Play ──────────────────────────────────────────────────────────────────────

def play(size, difficulty, level_name):
    grid        = generate_puzzle(size, difficulty)
    orig_grid   = copy.deepcopy(grid)
    cursor      = (0, 0)
    moves       = 0
    hints_used  = 0
    hint_cells  = set()
    start_time  = time.time()

    while True:
        render(grid, size, cursor, moves, hints_used, hint_cells, difficulty, level_name, start_time)
        key = get_key().lower()
        cr, cc = cursor

        if key == 'q':
            return "quit"
        elif key == 'r':
            grid       = copy.deepcopy(orig_grid)
            cursor     = (0, 0)
            moves      = 0
            hints_used = 0
            hint_cells = set()
            start_time = time.time()
        elif key == 'h':
            hint_cells  = set(get_hint(grid, size))
            hints_used += 1
        elif key == 'c':
            hint_cells = set()
        elif key in ('w', '\x1b[a'):
            cursor = (max(0, cr-1), cc)
        elif key in ('s', '\x1b[b'):
            cursor = (min(size-1, cr+1), cc)
        elif key in ('d', '\x1b[c'):
            cursor = (cr, min(size-1, cc+1))
        elif key in ('a', '\x1b[d'):
            cursor = (cr, max(0, cc-1))
        elif key in (' ', '\r', '\n'):
            toggle(grid, cr, cc, size)
            moves += 1
            if (cr, cc) in hint_cells:
                hint_cells.discard((cr, cc))
            if is_solved(grid):
                elapsed = int(time.time() - start_time)
                render(grid, size, cursor, moves, hints_used, hint_cells, difficulty, level_name, start_time)
                mins, secs = divmod(elapsed, 60)
                print(c("  ╔══════════════════════════════╗", GREEN))
                print(c("  ║   🎉  ALL LIGHTS OUT! WIN!    ║", GREEN))
                print(c("  ╚══════════════════════════════╝\n", GREEN))
                print(f"  Moves : {c(str(moves), YELLOW)}   Hints: {c(str(hints_used), CYAN)}   Time: {c(f'{mins:02d}:{secs:02d}', WHITE)}")
                print()
                penalty = hints_used * 5
                raw     = max(0, 100 - moves - penalty)
                if hints_used == 0 and moves <= size * size:
                    rating = c("🏆 Flawless!", YELLOW)
                elif hints_used == 0:
                    rating = c("🥇 Excellent", GREEN)
                elif raw >= 60:
                    rating = c("🥈 Good",      CYAN)
                else:
                    rating = c("🥉 Solved!",   WHITE)
                print(f"  Rating: {rating}")
                print()
                input(c("  Press ENTER to continue...", GREY))
                return "solved"

# ── Menu ──────────────────────────────────────────────────────────────────────

def main_menu():
    while True:
        clear()
        print(c("\n  ╔══════════════════════════════════════╗", CYAN))
        print(c("  ║        💡  L I G H T S  O U T        ║", CYAN))
        print(c("  ╚══════════════════════════════════════╝\n", CYAN))
        print("  Toggle a cell to flip it and all its neighbours.")
        print("  Goal: turn ALL lights OFF.\n")

        print(c("  Grid Size:\n", WHITE))
        print(f"   {c('1', YELLOW)}. 3×3  (Quick)")
        print(f"   {c('2', YELLOW)}. 4×4  (Standard)")
        print(f"   {c('3', YELLOW)}. 5×5  (Classic)")
        print(f"   {c('4', YELLOW)}. 6×6  (Large)")
        print(f"   {c('5', YELLOW)}. 7×7  (XL)")
        print(f"   {c('Q', RED)}.  Quit\n")

        size_map = {'1':3,'2':4,'3':5,'4':6,'5':7}
        ch = input("  Choose grid size: ").strip().lower()
        if ch == 'q':
            print(c("\n  Thanks for playing Lights Out! 💡\n", CYAN))
            return
        if ch not in size_map:
            continue
        size = size_map[ch]

        print(c("\n  Difficulty:\n", WHITE))
        print(f"   {c('1', GREEN)}.   Easy   — few lights on")
        print(f"   {c('2', YELLOW)}.   Medium — moderate puzzle")
        print(f"   {c('3', RED)}.   Hard   — many lights on\n")

        diff_map = {'1':'easy','2':'medium','3':'hard'}
        dch = input("  Choose difficulty: ").strip()
        if dch not in diff_map:
            continue
        difficulty = diff_map[dch]
        level_name = f"{size}×{size} {difficulty.capitalize()}"

        result = play(size, difficulty, level_name)
        if result == "quit":
            continue

def main():
    main_menu()

if __name__ == "__main__":
    main()
