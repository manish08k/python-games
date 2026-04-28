import os
import time
import random

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def create_board(size):
    nums = list(range(1, size * size)) + [0]
    return [nums[i*size:(i+1)*size] for i in range(size)]

def find_blank(board):
    for r, row in enumerate(board):
        for c, val in enumerate(row):
            if val == 0:
                return r, c

def is_solved(board, size):
    flat = [board[r][c] for r in range(size) for c in range(size)]
    goal = list(range(1, size * size)) + [0]
    return flat == goal

def shuffle_board(board, size, moves=200):
    dirs = [(-1,0),(1,0),(0,-1),(0,1)]
    last = None
    for _ in range(moves):
        br, bc = find_blank(board)
        valid = []
        for dr, dc in dirs:
            nr, nc = br+dr, bc+dc
            if 0 <= nr < size and 0 <= nc < size:
                if (dr, dc) != last:
                    valid.append((dr, dc))
        dr, dc = random.choice(valid)
        nr, nc = br+dr, bc+dc
        board[br][bc], board[nr][nc] = board[nr][nc], board[br][bc]
        last = (-dr, -dc)
    return board

def print_board(board, size, moves, time_elapsed, best):
    print("=" * (size * 6 + 2))
    print(f"  🧩  SLIDING PUZZLE  {size}x{size}")
    print("=" * (size * 6 + 2))
    print(f"  Moves: {moves:<6} Time: {int(time_elapsed)}s   Best: {best if best else '-'}")
    print()

    cell_w = 5
    border = "  +" + ("-----+" * size)

    print(border)
    for r in range(size):
        row_str = "  |"
        for c in range(size):
            val = board[r][c]
            if val == 0:
                row_str += "     |"
            else:
                row_str += f" {val:2}  |" if val < 10 else f"  {val} |"
        print(row_str)
        print(border)
    print()

def print_board_fancy(board, size, moves, time_elapsed, best):
    clear()
    print("=" * (size * 6 + 4))
    title = f"  🧩  SLIDING PUZZLE  ({size}x{size})"
    print(title)
    print("=" * (size * 6 + 4))
    print(f"  Moves : {moves:<8} Time : {int(time_elapsed)}s")
    print(f"  Best  : {best if best else 'N/A':<8} Goal : {size*size-1} tiles in order")
    print()

    border = "  +" + ("─────+" * size)
    print(border)
    for r in range(size):
        row_str = "  │"
        for c in range(size):
            val = board[r][c]
            if val == 0:
                row_str += "     │"
            else:
                goal_r, goal_c = (val-1)//size, (val-1)%size
                correct = (r == goal_r and c == goal_c)
                marker = "✓" if correct else " "
                if val < 10:
                    row_str += f"  {val}{marker} │"
                else:
                    row_str += f" {val}{marker} │"
        print(row_str)
        print(border)
    print()

def move_tile(board, size, direction):
    br, bc = find_blank(board)
    dir_map = {
        'W': (1, 0),  'S': (-1, 0),
        'A': (0, 1),  'D': (0, -1),
        'UP': (1,0),  'DOWN': (-1,0),
        'LEFT': (0,1),'RIGHT': (0,-1),
    }
    if direction not in dir_map:
        return False
    dr, dc = dir_map[direction]
    nr, nc = br+dr, bc+dc
    if 0 <= nr < size and 0 <= nc < size:
        board[br][bc], board[nr][nc] = board[nr][nc], board[br][bc]
        return True
    return False

def count_inversions(flat, size):
    tiles = [x for x in flat if x != 0]
    inv = 0
    for i in range(len(tiles)):
        for j in range(i+1, len(tiles)):
            if tiles[i] > tiles[j]:
                inv += 1
    return inv

def is_solvable(board, size):
    flat = [board[r][c] for r in range(size) for c in range(size)]
    inv = count_inversions(flat, size)
    if size % 2 == 1:
        return inv % 2 == 0
    else:
        br, _ = find_blank(board)
        blank_row_from_bottom = size - br
        return (blank_row_from_bottom % 2 == 0) == (inv % 2 == 1)

def manhattan_distance(board, size):
    dist = 0
    for r in range(size):
        for c in range(size):
            val = board[r][c]
            if val != 0:
                gr, gc = (val-1)//size, (val-1)%size
                dist += abs(r-gr) + abs(c-gc)
    return dist

def hint(board, size):
    br, bc = find_blank(board)
    best_dir = None
    best_dist = manhattan_distance(board, size)
    dir_map = {'W':(1,0),'S':(-1,0),'A':(0,1),'D':(0,-1)}
    dir_names = {'W':'W (slide tile down)','S':'S (slide tile up)','A':'A (slide tile right)','D':'D (slide tile left)'}
    for d, (dr,dc) in dir_map.items():
        nr, nc = br+dr, bc+dc
        if 0 <= nr < size and 0 <= nc < size:
            board[br][bc], board[nr][nc] = board[nr][nc], board[br][bc]
            dist = manhattan_distance(board, size)
            board[br][bc], board[nr][nc] = board[nr][nc], board[br][bc]
            if dist < best_dist:
                best_dist = dist
                best_dir = dir_names[d]
    return best_dir

def show_controls():
    print("  Controls:")
    print("   W / ↑  : Slide tile DOWN  into blank")
    print("   S / ↓  : Slide tile UP    into blank")
    print("   A / ←  : Slide tile RIGHT into blank")
    print("   D / →  : Slide tile LEFT  into blank")
    print("   H      : Hint")
    print("   R      : Restart")
    print("   Q      : Quit")
    print()

def play(size, best_scores):
    board = create_board(size)
    board = shuffle_board(board, size, moves=300)

    while not is_solvable(board, size):
        board = shuffle_board(board, size, moves=300)

    moves = 0
    start = time.time()
    best = best_scores.get(size)

    while True:
        elapsed = time.time() - start
        print_board_fancy(board, size, moves, elapsed, best)
        show_controls()

        if is_solved(board, size):
            elapsed = time.time() - start
            print(f"  🎉 CONGRATULATIONS! Solved in {moves} moves & {int(elapsed)}s!")
            if best is None or moves < best:
                best_scores[size] = moves
                print(f"  🏆 New Best: {moves} moves!")
            input("\n  Press Enter to continue...")
            return

        print(f"  Hint score (Manhattan distance): {manhattan_distance(board, size)}")
        cmd = input("\n  Move: ").strip().upper()

        if cmd == 'Q':
            print("  Goodbye!")
            time.sleep(0.5)
            return
        elif cmd == 'R':
            play(size, best_scores)
            return
        elif cmd == 'H':
            h = hint(board, size)
            if h:
                print(f"\n  💡 Hint: Press {h}")
            else:
                print("  💡 Try any move!")
            input("  Press Enter to continue...")
        elif cmd in ('W','A','S','D'):
            if not move_tile(board, size, cmd):
                print("  ❌ Can't move that way!")
                time.sleep(0.4)
            else:
                moves += 1
        else:
            print("  ❌ Invalid key! Use W/A/S/D, H, R, Q")
            time.sleep(0.4)

def main():
    best_scores = {}
    while True:
        clear()
        print("=" * 40)
        print("       🧩  SLIDING PUZZLE  🧩")
        print("=" * 40)
        print("""
  Choose board size:
   1.  3x3  (8-puzzle)   - Easy
   2.  4x4  (15-puzzle)  - Medium
   3.  5x5  (24-puzzle)  - Hard

  Best Scores:""")
        for s in (3, 4, 5):
            b = best_scores.get(s, 'N/A')
            print(f"   {s}x{s}: {b} moves")
        print()
        print("   Q. Quit")
        print()

        choice = input("  Your choice: ").strip().upper()
        if choice == '1':
            play(3, best_scores)
        elif choice == '2':
            play(4, best_scores)
        elif choice == '3':
            play(5, best_scores)
        elif choice == 'Q':
            print("\n  Thanks for playing! Goodbye! 👋")
            break
        else:
            print("  Invalid choice.")
            time.sleep(0.5)

if __name__ == "__main__":
    main()