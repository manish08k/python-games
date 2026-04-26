import random
import os
import re

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def create_board(rows, cols, num_mines):
    board = [[' ' for _ in range(cols)] for _ in range(rows)]
    mines = set()
    while len(mines) < num_mines:
        r = random.randint(0, rows - 1)
        c = random.randint(0, cols - 1)
        mines.add((r, c))
    return board, mines

def count_adjacent_mines(r, c, mines, rows, cols):
    count = 0
    for dr in [-1, 0, 1]:
        for dc in [-1, 0, 1]:
            nr, nc = r + dr, c + dc
            if (nr, nc) in mines:
                count += 1
    return count

def reveal(board, visible, r, c, mines, rows, cols):
    if (r, c) in mines:
        return False
    if visible[r][c]:
        return True
    visible[r][c] = True
    if board[r][c] == ' ':
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols and not visible[nr][nc]:
                    reveal(board, visible, nr, nc, mines, rows, cols)
    return True

def print_board(visible, board, mines, rows, cols, show_mines=False):
    print('   ' + ' '.join(f'{i:2}' for i in range(cols)))
    print('  +' + '--' * cols + '-+')
    for r in range(rows):
        row_display = [f'{r:2}|']
        for c in range(cols):
            if show_mines and (r, c) in mines:
                row_display.append('* ')
            elif visible[r][c]:
                cell = board[r][c]
                row_display.append(f'{cell} ')
            else:
                row_display.append('. ')
        row_display.append('|')
        print(''.join(row_display))
    print('  +' + '--' * cols + '-+')

def parse_input(cmd):
    # Try "4 6" or "46" or "4,6"
    cmd = cmd.strip()
    if re.match(r'^\d+$', cmd) and len(cmd) == 2:
        # two-digit number like "46"
        return int(cmd[0]), int(cmd[1])
    parts = re.split(r'[ ,]+', cmd)
    if len(parts) == 2:
        try:
            return int(parts[0]), int(parts[1])
        except:
            pass
    return None

def minesweeper():
    rows, cols = 8, 8
    num_mines = 10
    board, mines = create_board(rows, cols, num_mines)
    
    for r in range(rows):
        for c in range(cols):
            if (r, c) not in mines:
                cnt = count_adjacent_mines(r, c, mines, rows, cols)
                board[r][c] = str(cnt) if cnt > 0 else ' '
    
    visible = [[False for _ in range(cols)] for _ in range(rows)]
    game_over = False
    
    print("💣 MINESWEEPER")
    print(f"Grid: {rows}x{cols}   Mines: {num_mines}")
    print("You can enter coordinates as:")
    print("  - Two numbers: 4 6")
    print("  - Two-digit number: 46")
    print("  - With comma: 4,6")
    print("Type 'q' to quit.\n")
    
    while not game_over:
        clear_screen()
        print_board(visible, board, mines, rows, cols)
        revealed = sum(sum(row) for row in visible)
        print(f"\nCells revealed: {revealed} / {rows*cols - num_mines}")
        
        cmd = input("> ").strip().lower()
        if cmd == 'q':
            print("\nQuitting. Mines were at:")
            print_board(visible, board, mines, rows, cols, show_mines=True)
            return
        
        coords = parse_input(cmd)
        if coords is None:
            print("Invalid input. Try '4 6', '46', or '4,6'")
            input("Press Enter...")
            continue
        
        r, c = coords
        if not (0 <= r < rows and 0 <= c < cols):
            print(f"Out of bounds! Row 0-{rows-1}, Col 0-{cols-1}")
            input("Press Enter...")
            continue
        if visible[r][c]:
            print("Already revealed!")
            input("Press Enter...")
            continue
        
        if not reveal(board, visible, r, c, mines, rows, cols):
            game_over = True
            print("\n💥 BOOM! You hit a mine!")
            print_board(visible, board, mines, rows, cols, show_mines=True)
        else:
            revealed = sum(sum(row) for row in visible)
            if revealed == rows * cols - num_mines:
                game_over = True
                print("\n🎉 CONGRATULATIONS! You cleared the board!")
                print_board(visible, board, mines, rows, cols, show_mines=True)
    
    replay = input("\nPlay again? (y/n): ").lower()
    if replay == 'y':
        minesweeper()
    else:
        print("Thanks for playing!")

if __name__ == "__main__":
    minesweeper()