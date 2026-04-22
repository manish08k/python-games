import copy
import math
import random

class Connect4:
    def __init__(self, rows=6, cols=7):
        self.rows = rows
        self.cols = cols
        self.board = [[' ' for _ in range(cols)] for _ in range(rows)]
        self.current_player = 'X'   # X always starts (human by default)
        self.ai_player = 'O'

    def print_board(self):
        print("\n  " + " ".join(str(i) for i in range(self.cols)))
        for r in range(self.rows):
            print("| " + " ".join(self.board[r]) + " |")
        print("+" + "---+" * self.cols)

    def drop_piece(self, col, piece):
        for r in range(self.rows-1, -1, -1):
            if self.board[r][col] == ' ':
                self.board[r][col] = piece
                return r
        return -1

    def is_valid_move(self, col):
        return 0 <= col < self.cols and self.board[0][col] == ' '

    def get_valid_moves(self):
        return [c for c in range(self.cols) if self.is_valid_move(c)]

    def check_win(self, piece):
        # Horizontal
        for r in range(self.rows):
            for c in range(self.cols - 3):
                if all(self.board[r][c+i] == piece for i in range(4)):
                    return True
        # Vertical
        for r in range(self.rows - 3):
            for c in range(self.cols):
                if all(self.board[r+i][c] == piece for i in range(4)):
                    return True
        # Diagonal (down-right)
        for r in range(self.rows - 3):
            for c in range(self.cols - 3):
                if all(self.board[r+i][c+i] == piece for i in range(4)):
                    return True
        # Diagonal (down-left)
        for r in range(self.rows - 3):
            for c in range(3, self.cols):
                if all(self.board[r+i][c-i] == piece for i in range(4)):
                    return True
        return False

    def is_draw(self):
        return all(self.board[0][c] != ' ' for c in range(self.cols))

    def game_over(self):
        return self.check_win('X') or self.check_win('O') or self.is_draw()

    def evaluate_window(self, window, piece):
        opponent = 'O' if piece == 'X' else 'X'
        score = 0
        count_piece = window.count(piece)
        count_opp = window.count(opponent)
        empty = window.count(' ')

        if count_piece == 4:
            score += 100
        elif count_piece == 3 and empty == 1:
            score += 10
        elif count_piece == 2 and empty == 2:
            score += 2
        if count_opp == 3 and empty == 1:
            score -= 8
        return score

    def evaluate_board(self, piece):
        score = 0
        opponent = 'O' if piece == 'X' else 'X'

        # Horizontal
        for r in range(self.rows):
            for c in range(self.cols - 3):
                window = [self.board[r][c+i] for i in range(4)]
                score += self.evaluate_window(window, piece)
                score -= self.evaluate_window(window, opponent)

        # Vertical
        for r in range(self.rows - 3):
            for c in range(self.cols):
                window = [self.board[r+i][c] for i in range(4)]
                score += self.evaluate_window(window, piece)
                score -= self.evaluate_window(window, opponent)

        # Diagonal down-right
        for r in range(self.rows - 3):
            for c in range(self.cols - 3):
                window = [self.board[r+i][c+i] for i in range(4)]
                score += self.evaluate_window(window, piece)
                score -= self.evaluate_window(window, opponent)

        # Diagonal down-left
        for r in range(self.rows - 3):
            for c in range(3, self.cols):
                window = [self.board[r+i][c-i] for i in range(4)]
                score += self.evaluate_window(window, piece)
                score -= self.evaluate_window(window, opponent)

        # Center column bonus
        center_col = self.cols // 2
        center_array = [self.board[r][center_col] for r in range(self.rows)]
        score += center_array.count(piece) * 3
        return score

    def minimax(self, depth, alpha, beta, maximizing):
        if depth == 0 or self.game_over():
            if self.check_win(self.ai_player):
                return (None, 1000000)
            elif self.check_win('X'):
                return (None, -1000000)
            elif self.is_draw():
                return (None, 0)
            else:
                return (None, self.evaluate_board(self.ai_player))

        valid_moves = self.get_valid_moves()
        if maximizing:
            value = -math.inf
            best_col = random.choice(valid_moves) if valid_moves else None
            for col in valid_moves:
                temp_board = copy.deepcopy(self.board)
                self.drop_piece(col, self.ai_player)
                new_score = self.minimax(depth-1, alpha, beta, False)[1]
                self.board = temp_board
                if new_score > value:
                    value = new_score
                    best_col = col
                alpha = max(alpha, value)
                if alpha >= beta:
                    break
            return best_col, value
        else:
            value = math.inf
            best_col = random.choice(valid_moves) if valid_moves else None
            for col in valid_moves:
                temp_board = copy.deepcopy(self.board)
                self.drop_piece(col, 'X')
                new_score = self.minimax(depth-1, alpha, beta, True)[1]
                self.board = temp_board
                if new_score < value:
                    value = new_score
                    best_col = col
                beta = min(beta, value)
                if alpha >= beta:
                    break
            return best_col, value

    def ai_move(self, depth):
        col, _ = self.minimax(depth, -math.inf, math.inf, True)
        if col is not None:
            self.drop_piece(col, self.ai_player)

    def play(self):
        print("="*50)
        print("         CONNECT 4 - Minimax AI with Alpha-Beta")
        print("="*50)

        while True:
            # Reset board
            self.board = [[' ' for _ in range(self.cols)] for _ in range(self.rows)]

            # Choose who starts
            first = input("\nDo you want to go first? (y/n): ").strip().lower()
            human_first = first == 'y'
            self.current_player = 'X' if human_first else 'O'

            # Difficulty
            print("\nChoose AI difficulty:")
            print("  1 - Easy (depth 2)")
            print("  2 - Medium (depth 4)")
            print("  3 - Hard (depth 6)")
            choice = input("Enter 1/2/3: ")
            depth_map = {'1': 2, '2': 4, '3': 6}
            depth = depth_map.get(choice, 4)
            print(f"\nAI depth set to {depth}.\n")

            self.print_board()

            while not self.game_over():
                if self.current_player == 'X':   # Human
                    while True:
                        try:
                            col = int(input(f"Your move (0-{self.cols-1}): "))
                            if self.is_valid_move(col):
                                self.drop_piece(col, 'X')
                                break
                            else:
                                print("Column full or invalid. Try again.")
                        except:
                            print(f"Enter a number between 0 and {self.cols-1}.")
                    self.print_board()
                    if self.check_win('X'):
                        print("🎉 You win! Congratulations!")
                        break
                    if self.is_draw():
                        print("It's a draw!")
                        break
                    self.current_player = 'O'
                else:   # AI
                    print("AI is thinking...")
                    self.ai_move(depth)
                    self.print_board()
                    if self.check_win('O'):
                        print("🤖 AI wins! Better luck next time.")
                        break
                    if self.is_draw():
                        print("It's a draw!")
                        break
                    self.current_player = 'X'

            # Ask for rematch
            again = input("\nPlay another game? (y/n): ").strip().lower()
            if again != 'y':
                print("Thanks for playing Connect 4!")
                break

if __name__ == "__main__":
    game = Connect4()
    game.play()