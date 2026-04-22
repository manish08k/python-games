import random
import copy
import os
import sys
import termios
import tty
import json
from pathlib import Path

# ANSI color codes for pretty display
COLORS = {
    0:      '\033[90m',      # dark gray (empty)
    2:      '\033[37m',      # white
    4:      '\033[36m',      # cyan
    8:      '\033[34m',      # blue
    16:     '\033[32m',      # green
    32:     '\033[33m',      # yellow
    64:     '\033[35m',      # magenta
    128:    '\033[31m',      # red
    256:    '\033[91m',      # bright red
    512:    '\033[93m',      # bright yellow
    1024:   '\033[95m',      # bright magenta
    2048:   '\033[92m',      # bright green
}
DEFAULT_COLOR = '\033[0m'    # reset
BG_COLOR = '\033[48;5;236m'  # dark background for tiles

class Game2048:
    def __init__(self, size=4, highscore_file="2048_highscore.json"):
        self.size = size
        self.board = [[0]*size for _ in range(size)]
        self.score = 0
        self.history = []
        self.highscore_file = highscore_file
        self.highscore = self.load_highscore()
        self.add_new_tile()
        self.add_new_tile()

    def load_highscore(self):
        """Load high score from file, return 0 if file doesn't exist."""
        path = Path(self.highscore_file)
        if path.exists():
            try:
                with open(path, 'r') as f:
                    data = json.load(f)
                    return data.get('highscore', 0)
            except:
                return 0
        return 0

    def save_highscore(self):
        """Save current high score to file."""
        with open(self.highscore_file, 'w') as f:
            json.dump({'highscore': self.highscore}, f)

    def update_highscore(self):
        """Update high score if current score exceeds it."""
        if self.score > self.highscore:
            self.highscore = self.score
            self.save_highscore()
            return True
        return False

    def add_new_tile(self):
        """Add a random tile (2 with 90% chance, 4 with 10%) to an empty cell."""
        empty = [(i, j) for i in range(self.size) for j in range(self.size) if self.board[i][j] == 0]
        if empty:
            i, j = random.choice(empty)
            self.board[i][j] = 2 if random.random() < 0.9 else 4

    def compress(self, row):
        """Shift non-zero numbers to the left."""
        new_row = [v for v in row if v != 0]
        new_row += [0] * (self.size - len(new_row))
        return new_row

    def merge(self, row):
        """Merge adjacent equal numbers, return (new_row, score_gain)."""
        score_gain = 0
        for i in range(self.size - 1):
            if row[i] != 0 and row[i] == row[i+1]:
                row[i] *= 2
                score_gain += row[i]
                row[i+1] = 0
        return row, score_gain

    # Core move logic (reused for all directions)
    def move_left_on_board(self, board):
        new_board = []
        total_gain = 0
        for row in board:
            compressed = self.compress(row)
            merged, gain = self.merge(compressed)
            total_gain += gain
            final = self.compress(merged)
            new_board.append(final)
        return new_board, total_gain

    def move_right_on_board(self, board):
        reversed_board = [row[::-1] for row in board]
        moved, gain = self.move_left_on_board(reversed_board)
        final_board = [row[::-1] for row in moved]
        return final_board, gain

    def move_left(self):
        return self.move_left_on_board(self.board)

    def move_right(self):
        return self.move_right_on_board(self.board)

    def move_up(self):
        transposed = [list(col) for col in zip(*self.board)]
        moved, gain = self.move_left_on_board(transposed)
        final_board = [list(row) for row in zip(*moved)]
        return final_board, gain

    def move_down(self):
        transposed = [list(col) for col in zip(*self.board)]
        moved, gain = self.move_right_on_board(transposed)
        final_board = [list(row) for row in zip(*moved)]
        return final_board, gain

    def is_valid_move(self):
        """Check if any move is possible (empty cell or adjacent equal)."""
        for i in range(self.size):
            for j in range(self.size):
                if self.board[i][j] == 0:
                    return True
                if j+1 < self.size and self.board[i][j] == self.board[i][j+1]:
                    return True
                if i+1 < self.size and self.board[i][j] == self.board[i+1][j]:
                    return True
        return False

    def is_board_full(self):
        """Return True if no empty cells."""
        return all(cell != 0 for row in self.board for cell in row)

    def is_game_over(self):
        """Game over if no moves possible (board full and no merges)."""
        return not self.is_valid_move()

    def make_move(self, direction):
        """Apply a move, save state, add new tile, return True if board changed."""
        self.save_state()
        move_func = {
            'left': self.move_left,
            'right': self.move_right,
            'up': self.move_up,
            'down': self.move_down
        }
        if direction not in move_func:
            return False
        new_board, gain = move_func[direction]()
        if new_board != self.board:
            self.board = new_board
            self.score += gain
            self.update_highscore()
            self.add_new_tile()
            return True
        else:
            # No change: discard saved state
            self.history.pop()
            return False

    def save_state(self):
        """Save current board and score for undo."""
        self.history.append((copy.deepcopy(self.board), self.score))

    def undo(self):
        """Revert to previous state if available."""
        if self.history:
            self.board, self.score = self.history.pop()
            return True
        return False

    def restart(self):
        """Reset the game with a clean board."""
        self.board = [[0]*self.size for _ in range(self.size)]
        self.score = 0
        self.history = []
        self.add_new_tile()
        self.add_new_tile()

    def get_colored_tile(self, value):
        """Return a colored string representation of a tile."""
        if value == 0:
            return f"{COLORS[0]}  .  {DEFAULT_COLOR}"
        color = COLORS.get(value, COLORS[2048])  # fallback for >2048
        return f"{color}{value:>5}{DEFAULT_COLOR}"

    def display(self):
        """Clear screen and draw the game board with colors."""
        os.system('cls' if os.name == 'nt' else 'clear')
        # Header
        print("\n" + "=" * (self.size * 6 + 10))
        print(f" 2048 Game  |  Score: {self.score}  |  High Score: {self.highscore}  |  Size: {self.size}x{self.size}")
        print("=" * (self.size * 6 + 10))
        # Column numbers
        print("     ", end="")
        for c in range(self.size):
            print(f"  {c}   ", end="")
        print()
        # Board
        print("   " + "+-----" * self.size + "+")
        for r, row in enumerate(self.board):
            print(f" {r} ", end="")
            for val in row:
                print(f"|{self.get_colored_tile(val)}", end="")
            print("|")
            print("   " + "+-----" * self.size + "+")
        # Controls
        print("\n Controls: ← ↑ → ↓  (or W A S D)   |   u=undo   r=restart   q=quit")
        print(" Tip: Game auto-restarts when board is completely filled!\n")


def get_key():
    """Raw key input for Unix/Linux/Mac and Windows. Returns command string."""
    if os.name == 'nt':
        import msvcrt
        key = msvcrt.getch()
        if key == b'\xe0':  # arrow key prefix
            key = msvcrt.getch()
            return {
                b'H': 'up', b'P': 'down', b'K': 'left', b'M': 'right'
            }.get(key, None)
        else:
            try:
                ch = key.decode().lower()
                if ch in 'uq r':  # 'u', 'q', 'r'
                    return ch
                if ch in 'wasd':
                    return {'w':'up','a':'left','s':'down','d':'right'}[ch]
            except:
                pass
        return None
    else:
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
            if ch == '\x1b':  # escape sequence
                ch2 = sys.stdin.read(1)
                if ch2 == '[':
                    ch3 = sys.stdin.read(1)
                    if ch3 == 'A': return 'up'
                    if ch3 == 'B': return 'down'
                    if ch3 == 'C': return 'right'
                    if ch3 == 'D': return 'left'
            else:
                ch = ch.lower()
                if ch in 'uqr':
                    return ch
                if ch in 'wasd':
                    return {'w':'up','a':'left','s':'down','d':'right'}[ch]
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return None


def main():
    print("Welcome to Advanced 2048!")
    print("Choose board size:")
    print("  1 - 4x4 (classic)")
    print("  2 - 5x5 (bigger)")
    print("  3 - 6x6 (expert)")
    size_choice = input("Enter 1/2/3: ").strip()
    size_map = {'1':4, '2':5, '3':6}
    size = size_map.get(size_choice, 4)

    game = Game2048(size)
    message = ""

    while True:
        game.display()
        if message:
            print(message)
            message = ""

        # Condition 1: board completely filled -> auto restart (no prompt)
        if game.is_board_full():
            print("\n🏁 The board is completely filled! Starting a new game...")
            game.restart()
            continue

        # Condition 2: no moves possible (classic game over) -> ask to restart
        if game.is_game_over():
            print(f"\n💀 GAME OVER! Your score: {game.score}")
            if game.score == game.highscore:
                print("🎉 New high score! 🎉")
            again = input("Play again with same size? (y/n): ").strip().lower()
            if again == 'y':
                game.restart()
                continue
            else:
                break

        key = get_key()
        if key == 'q':
            confirm = input("Quit game? (y/n): ").strip().lower()
            if confirm == 'y':
                break
            else:
                continue
        elif key == 'u':
            if game.undo():
                message = "↩️ Undo successful."
            else:
                message = "Nothing to undo."
        elif key == 'r':
            game.restart()
            message = "🔄 Game restarted."
        elif key in ('up', 'down', 'left', 'right'):
            if not game.make_move(key):
                message = "⚠️ No movement possible in that direction."
        # else ignore other keys


if __name__ == "__main__":
    main()