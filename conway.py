import os
import time
import random

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

ALIVE = '█'
DEAD  = '░'

PRESETS = {
    '1': ('Glider', [
        (0,1),(1,2),(2,0),(2,1),(2,2)
    ]),
    '2': ('Blinker', [
        (1,0),(1,1),(1,2)
    ]),
    '3': ('Toad', [
        (1,1),(1,2),(1,3),(2,0),(2,1),(2,2)
    ]),
    '4': ('Beacon', [
        (0,0),(0,1),(1,0),(1,1),(2,2),(2,3),(3,2),(3,3)
    ]),
    '5': ('Pulsar', [
        (0,2),(0,3),(0,4),(0,8),(0,9),(0,10),
        (2,0),(2,5),(2,7),(2,12),(3,0),(3,5),(3,7),(3,12),
        (4,0),(4,5),(4,7),(4,12),(5,2),(5,3),(5,4),(5,8),(5,9),(5,10),
        (7,2),(7,3),(7,4),(7,8),(7,9),(7,10),
        (8,0),(8,5),(8,7),(8,12),(9,0),(9,5),(9,7),(9,12),
        (10,0),(10,5),(10,7),(10,12),(12,2),(12,3),(12,4),(12,8),(12,9),(12,10)
    ]),
    '6': ('Gosper Glider Gun', [
        (0,24),(1,22),(1,24),(2,12),(2,13),(2,20),(2,21),(2,34),(2,35),
        (3,11),(3,15),(3,20),(3,21),(3,34),(3,35),(4,0),(4,1),(4,10),(4,16),(4,20),(4,21),
        (5,0),(5,1),(5,10),(5,14),(5,16),(5,17),(5,22),(5,24),(6,10),(6,16),(6,24),
        (7,11),(7,15),(8,12),(8,13)
    ]),
    '7': ('R-Pentomino', [
        (0,1),(0,2),(1,0),(1,1),(2,1)
    ]),
    '8': ('Diehard', [
        (0,6),(1,0),(1,1),(2,1),(2,5),(2,6),(2,7)
    ]),
    '9': ('Acorn', [
        (0,1),(1,3),(2,0),(2,1),(2,4),(2,5),(2,6)
    ]),
}

def make_grid(rows, cols):
    return set()

def random_grid(rows, cols, density=0.3):
    cells = set()
    for r in range(rows):
        for c in range(cols):
            if random.random() < density:
                cells.add((r, c))
    return cells

def place_preset(cells, pattern, offset_r, offset_c):
    for (r, c) in pattern:
        cells.add((r + offset_r, c + offset_c))
    return cells

def count_neighbors(cells, r, c):
    count = 0
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr == 0 and dc == 0:
                continue
            if (r + dr, c + dc) in cells:
                count += 1
    return count

def next_gen(cells, rows, cols):
    neighbor_count = {}
    for (r, c) in cells:
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols:
                    neighbor_count[(nr, nc)] = neighbor_count.get((nr, nc), 0) + 1

    new_cells = set()
    for (r, c), cnt in neighbor_count.items():
        if (r, c) in cells and cnt in (2, 3):
            new_cells.add((r, c))
        elif (r, c) not in cells and cnt == 3:
            new_cells.add((r, c))
    return new_cells

def render(cells, rows, cols, gen, population, speed):
    lines = []
    lines.append("=" * (cols + 4))
    lines.append(f"  Conway's Game of Life  |  Gen: {gen:5}  |  Pop: {population:5}  |  Speed: {speed}x")
    lines.append("=" * (cols + 4))
    for r in range(rows):
        row_str = "  "
        for c in range(cols):
            row_str += ALIVE if (r, c) in cells else DEAD
        lines.append(row_str)
    lines.append("=" * (cols + 4))
    lines.append("  [P] Pause/Resume  [+] Faster  [-] Slower  [Q] Quit")
    print('\n'.join(lines))

def get_terminal_size():
    try:
        size = os.get_terminal_size()
        cols = min(size.columns - 4, 80)
        rows = min(size.lines - 10, 30)
        return max(rows, 10), max(cols, 20)
    except:
        return 24, 60

def show_menu():
    clear()
    print("=" * 50)
    print("      🧬  CONWAY'S GAME OF LIFE  🧬")
    print("=" * 50)
    print("""
  Rules:
  • A live cell with 2 or 3 neighbors survives
  • A dead cell with exactly 3 neighbors is born
  • All other live cells die, all others stay dead
""")
    print("  Presets:")
    for key, (name, _) in PRESETS.items():
        print(f"   {key}. {name}")
    print("   R. Random")
    print("   C. Custom (draw your own)")
    print()

def draw_custom(rows, cols):
    cells = set()
    print(f"\n  Draw mode: enter row,col to toggle cells (0-{rows-1}, 0-{cols-1})")
    print("  Type DONE when finished, CLEAR to reset, PREVIEW to see grid")

    while True:
        cmd = input("  > ").strip().upper()
        if cmd == 'DONE':
            break
        elif cmd == 'CLEAR':
            cells = set()
            print("  Grid cleared.")
        elif cmd == 'PREVIEW':
            clear()
            render(cells, rows, cols, 0, len(cells), 1)
        else:
            try:
                parts = cmd.replace(' ', ',').split(',')
                r, c = int(parts[0]), int(parts[1])
                if 0 <= r < rows and 0 <= c < cols:
                    if (r, c) in cells:
                        cells.discard((r, c))
                        print(f"  Removed ({r},{c})")
                    else:
                        cells.add((r, c))
                        print(f"  Added ({r},{c})")
                else:
                    print(f"  Out of bounds! Max row={rows-1}, col={cols-1}")
            except:
                print("  Invalid input. Use: row,col")
    return cells

def run_simulation(cells, rows, cols):
    import sys
    import select

    gen = 0
    speed = 2
    paused = False
    speed_delays = {1: 0.5, 2: 0.2, 3: 0.1, 4: 0.05, 5: 0.01}
    history = set()
    history.add(frozenset(cells))

    def check_input():
        if os.name == 'nt':
            import msvcrt
            if msvcrt.kbhit():
                return msvcrt.getch().decode('utf-8', errors='ignore').upper()
        else:
            rlist, _, _ = select.select([sys.stdin], [], [], 0)
            if rlist:
                return sys.stdin.read(1).upper()
        return None

    import tty
    import termios

    if os.name != 'nt':
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        tty.setcbreak(sys.stdin.fileno())

    try:
        while True:
            clear()
            render(cells, rows, cols, gen, len(cells), speed)

            if paused:
                print("  *** PAUSED ***")

            ch = check_input()
            if ch:
                if ch in ('Q', 'q', '\x03'):
                    break
                elif ch in ('P', 'p', ' '):
                    paused = not paused
                elif ch in ('+', '=') and speed < 5:
                    speed += 1
                elif ch == '-' and speed > 1:
                    speed -= 1

            if not paused:
                if not cells:
                    print("  💀 Population extinct!")
                    time.sleep(2)
                    break

                new_cells = next_gen(cells, rows, cols)
                frozen = frozenset(new_cells)

                if frozen in history:
                    clear()
                    render(new_cells, rows, cols, gen, len(new_cells), speed)
                    print("  🔄 Stable state detected! (period or still life)")
                    time.sleep(3)
                    break

                if len(history) > 20:
                    history.pop()
                history.add(frozen)

                cells = new_cells
                gen += 1

            time.sleep(speed_delays.get(speed, 0.2))

    finally:
        if os.name != 'nt':
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    print(f"\n  Simulation ended at generation {gen}.")
    input("  Press Enter to exit...")

def run_simulation_simple(cells, rows, cols):
    gen = 0
    speed = 2
    speed_delays = {1: 0.5, 2: 0.3, 3: 0.15, 4: 0.07, 5: 0.02}
    history = []

    print("  Running... Press Ctrl+C to stop.\n")
    time.sleep(1)

    try:
        while True:
            clear()
            render(cells, rows, cols, gen, len(cells), speed)

            if not cells:
                print("  💀 Population extinct!")
                time.sleep(2)
                break

            frozen = frozenset(cells)
            if frozen in history[-10:]:
                print("  🔄 Stable/periodic state detected!")
                time.sleep(2)
                break

            history.append(frozen)
            if len(history) > 20:
                history.pop(0)

            cells = next_gen(cells, rows, cols)
            gen += 1
            time.sleep(speed_delays.get(speed, 0.2))

    except KeyboardInterrupt:
        print(f"\n\n  Stopped at generation {gen}. Population: {len(cells)}")
        input("  Press Enter to exit...")

def main():
    show_menu()
    rows, cols = get_terminal_size()

    choice = input("  Choose preset (1-9 / R / C): ").strip().upper()
    cells = set()

    if choice == 'R':
        try:
            d = float(input("  Density (0.1 - 0.5, default 0.3): ") or "0.3")
            d = max(0.1, min(0.5, d))
        except ValueError:
            d = 0.3
        cells = random_grid(rows, cols, d)

    elif choice == 'C':
        cells = draw_custom(rows, cols)

    elif choice in PRESETS:
        name, pattern = PRESETS[choice]
        offset_r = (rows - max(r for r, c in pattern) - 1) // 2
        offset_c = (cols - max(c for r, c in pattern) - 1) // 2
        cells = place_preset(cells, pattern, max(0, offset_r), max(0, offset_c))
        print(f"  Loaded: {name}")
        time.sleep(0.5)
    else:
        cells = random_grid(rows, cols, 0.3)

    try:
        import select
        if os.name != 'nt':
            run_simulation(cells, rows, cols)
        else:
            run_simulation_simple(cells, rows, cols)
    except Exception:
        run_simulation_simple(cells, rows, cols)

if __name__ == "__main__":
    main()