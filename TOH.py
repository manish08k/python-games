import os
import time

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_towers(towers, n, moves, move_log):
    clear()
    print("=" * 60)
    print("           🗼  TOWER OF HANOI  🗼")
    print("=" * 60)
    print(f"  Disks: {n}   |   Moves: {moves}   |   Min Moves: {2**n - 1}")
    print("=" * 60)

    height = n + 1
    width = n * 2 + 3
    total_width = width * 3 + 6

    for level in range(height, 0, -1):
        row = ""
        for peg in range(3):
            stack = towers[peg]
            if len(stack) >= level:
                disk = stack[level - 1]
                disk_w = disk * 2 - 1
                pad = (width - disk_w) // 2
                row += " " * (pad + 2) + "█" * disk_w + " " * (pad + 2)
            else:
                pole_pos = width // 2
                row += " " * (pole_pos + 2) + "│" + " " * (pole_pos + 2)
        print(row)

    base = ""
    for _ in range(3):
        base += "  " + "▀" * width + "  "
    print(base)

    labels = ""
    for i, label in enumerate(["  A (Source)  ", "  B (Helper)  ", "  C (Target)  "]):
        labels += f"  {label:^{width}}  "
    print(labels)

    print("=" * 60)

    if move_log:
        print("  Last moves:")
        for log in move_log[-4:]:
            print(f"    {log}")
    print("=" * 60)

def get_disk_sizes(n):
    sizes = {}
    for i in range(1, n + 1):
        sizes[i] = i
    return sizes

def auto_solve(n, towers, source, target, helper, moves, move_log, speed):
    if n == 0:
        return moves

    moves = auto_solve(n-1, towers, source, helper, target, moves, move_log, speed)

    disk = towers[source].pop()
    towers[target].append(disk)
    moves += 1
    peg_names = {0: 'A', 1: 'B', 2: 'C'}
    move_log.append(f"Move {moves}: Disk {disk} → {peg_names[source]} to {peg_names[target]}")

    print_towers(towers, max(towers[0] + towers[1] + towers[2], default=n), moves, move_log)
    time.sleep(speed)

    moves = auto_solve(n-1, towers, helper, target, source, moves, move_log, speed)
    return moves

def manual_play(n, towers):
    moves = 0
    move_log = []
    peg_map = {'A': 0, 'B': 1, 'C': 2}
    peg_names = {0: 'A', 1: 'B', 2: 'C'}
    min_moves = 2 ** n - 1

    while True:
        print_towers(towers, n, moves, move_log)

        if towers[2] == list(range(1, n + 1)):
            print(f"\n  🏆 Congratulations! Solved in {moves} moves!")
            if moves == min_moves:
                print("  ⭐ PERFECT! Minimum moves achieved!")
            else:
                print(f"  (Minimum possible: {min_moves} moves)")
            input("\n  Press Enter to exit...")
            return

        print(f"\n  Move a disk: enter source and target peg")
        print("  Example: A C  (moves top disk from A to C)")
        print("  Type HINT for a hint | QUIT to exit")

        cmd = input("\n  Your move: ").strip().upper()

        if cmd == 'QUIT':
            print(f"\n  Game ended. Moves used: {moves}")
            break

        if cmd == 'HINT':
            hint = get_hint(towers, n)
            if hint:
                src, tgt = hint
                print(f"\n  💡 Hint: Move from {peg_names[src]} to {peg_names[tgt]}")
                input("  Press Enter to continue...")
            continue

        parts = cmd.split()
        if len(parts) != 2 or parts[0] not in peg_map or parts[1] not in peg_map:
            print("  ❌ Invalid input! Use letters A, B, or C.")
            time.sleep(1)
            continue

        src = peg_map[parts[0]]
        tgt = peg_map[parts[1]]

        if src == tgt:
            print("  ❌ Source and target must be different!")
            time.sleep(1)
            continue

        if not towers[src]:
            print(f"  ❌ Peg {parts[0]} is empty!")
            time.sleep(1)
            continue

        if towers[tgt] and towers[tgt][-1] < towers[src][-1]:
            print(f"  ❌ Cannot place larger disk on smaller disk!")
            time.sleep(1)
            continue

        disk = towers[src].pop()
        towers[tgt].append(disk)
        moves += 1
        move_log.append(f"Move {moves}: Disk {disk} → {parts[0]} to {parts[1]}")

def get_hint(towers, n):
    def hanoi_moves(n, src, tgt, hlp, result):
        if n == 0:
            return
        hanoi_moves(n-1, src, hlp, tgt, result)
        result.append((src, tgt))
        hanoi_moves(n-1, hlp, tgt, src, result)

    all_disks = sorted(towers[0] + towers[1] + towers[2])
    if not all_disks:
        return None

    for top_n in range(1, len(all_disks) + 1):
        moves = []
        hanoi_moves(top_n, 0, 2, 1, moves)
        test = [list(range(1, top_n + 1)), [], []]
        for src, tgt in moves:
            if test[src] and (not test[tgt] or test[tgt][-1] > test[src][-1]):
                if towers[src] and towers[src][-1] == test[src][-1]:
                    if not towers[tgt] or towers[tgt][-1] > towers[src][-1]:
                        return (src, tgt)
                test[tgt].append(test[src].pop())
    return None

def main():
    clear()
    print("=" * 60)
    print("           🗼  TOWER OF HANOI  🗼")
    print("=" * 60)
    print("""
  Rules:
  • Move all disks from peg A to peg C
  • Only one disk can be moved at a time
  • A larger disk cannot be placed on a smaller disk
  • FREE space = peg B (helper)
""")

    try:
        n = int(input("  Number of disks (1-10): "))
        n = max(1, min(10, n))
    except ValueError:
        n = 3

    print(f"\n  Mode:")
    print("   1. Manual Play")
    print("   2. Watch Auto Solve (Fast)")
    print("   3. Watch Auto Solve (Slow)")

    mode = input("\n  Choose (1/2/3): ").strip()

    towers = [list(range(1, n + 1)), [], []]

    if mode == '1':
        manual_play(n, towers)
    elif mode in ('2', '3'):
        speed = 0.1 if mode == '2' else 0.5
        move_log = []
        print_towers(towers, n, 0, move_log)
        print("\n  🤖 Auto solving...")
        time.sleep(1)
        total = auto_solve(n, towers, 0, 2, 1, 0, move_log, speed)
        print(f"\n  ✅ Solved in {total} moves! (Minimum: {2**n - 1})")
        input("\n  Press Enter to exit...")
    else:
        manual_play(n, towers)

if __name__ == "__main__":
    main()