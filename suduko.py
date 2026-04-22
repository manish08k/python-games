import random
import copy

class Sudoku:
    def __init__(self):
        self.board = [[0]*9 for _ in range(9)]

    # ---------- PRINT ----------
    def print_board(self):
        print("\n   0 1 2   3 4 5   6 7 8")
        for i in range(9):
            if i % 3 == 0:
                print("  +-------+-------+-------+")
            print(i, end=" | ")
            for j in range(9):
                val = self.board[i][j] if self.board[i][j] != 0 else "."
                print(val, end=" ")
                if (j+1) % 3 == 0:
                    print("| ", end="")
            print()
        print("  +-------+-------+-------+\n")

    # ---------- VALID CHECK ----------
    def is_valid(self, num, pos):
        r, c = pos

        if num in self.board[r]:
            return False

        for i in range(9):
            if self.board[i][c] == num:
                return False

        br, bc = r//3, c//3
        for i in range(br*3, br*3+3):
            for j in range(bc*3, bc*3+3):
                if self.board[i][j] == num:
                    return False
        return True

    # ---------- SOLVER ----------
    def find_empty(self):
        for i in range(9):
            for j in range(9):
                if self.board[i][j] == 0:
                    return i, j
        return None

    def solve(self):
        empty = self.find_empty()
        if not empty:
            return True

        r, c = empty
        nums = list(range(1,10))
        random.shuffle(nums)

        for num in nums:
            if self.is_valid(num, (r,c)):
                self.board[r][c] = num
                if self.solve():
                    return True
                self.board[r][c] = 0
        return False

    # ---------- COUNT SOLUTIONS (FIXED) ----------
    def count_solutions(self, board):
        board_copy = copy.deepcopy(board)

        def find_empty(b):
            for i in range(9):
                for j in range(9):
                    if b[i][j] == 0:
                        return i, j
            return None

        def is_valid(b, num, pos):
            r, c = pos
            if num in b[r]:
                return False
            for i in range(9):
                if b[i][c] == num:
                    return False
            br, bc = r//3, c//3
            for i in range(br*3, br*3+3):
                for j in range(bc*3, bc*3+3):
                    if b[i][j] == num:
                        return False
            return True

        def solve_count(b):
            empty = find_empty(b)
            if not empty:
                return 1
            r, c = empty
            count = 0
            for num in range(1, 10):
                if is_valid(b, num, (r, c)):
                    b[r][c] = num
                    count += solve_count(b)
                    b[r][c] = 0
                    if count > 1:
                        break
            return count

        return solve_count(board_copy)

    # ---------- GENERATE ----------
    def generate_full(self):
        self.solve()

    def generate_puzzle(self, difficulty=40):
        self.generate_full()

        attempts = difficulty
        while attempts > 0:
            r = random.randint(0, 8)
            c = random.randint(0, 8)

            if self.board[r][c] == 0:
                continue

            backup = self.board[r][c]
            self.board[r][c] = 0

            board_copy = copy.deepcopy(self.board)
            if self.count_solutions(board_copy) != 1:
                self.board[r][c] = backup
            else:
                attempts -= 1


# ---------- GAME LOOP (MULTIPLE PUZZLES) ----------
def play_game():
    while True:
        game = Sudoku()
        game.generate_puzzle(difficulty=40)
        original = copy.deepcopy(game.board)

        print("\n" + "="*50)
        print("🎲 NEW SUDOKU PUZZLE (type -1 at row to give up)")
        print("="*50)

        while True:
            game.print_board()

            try:
                row = input("Row (0-8) or -1 to give up: ")
                if row == "-1":
                    print("\n💡 Solution:")
                    game.solve()
                    game.print_board()
                    break

                row = int(row)
                col = int(input("Col (0-8): "))
                val = int(input("Value (1-9): "))
            except:
                print("❌ Invalid input – use numbers only")
                continue

            # Check bounds
            if not (0 <= row <= 8 and 0 <= col <= 8 and 1 <= val <= 9):
                print("❌ Row/Col must be 0-8, Value 1-9")
                continue

            if original[row][col] != 0:
                print("❌ Cannot change original cells")
                continue

            if game.is_valid(val, (row, col)):
                game.board[row][col] = val
            else:
                print("❌ Invalid move – row, column, or box conflict")

            if game.find_empty() is None:
                game.print_board()
                print("🏆 YOU SOLVED IT!")
                break

        # Ask to play again
        again = input("\nPlay another puzzle? (y/n): ").strip().lower()
        if again != 'y':
            print("Thanks for playing!")
            break


if __name__ == "__main__":
    play_game()