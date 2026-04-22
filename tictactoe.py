class TicTacToe:
    def __init__(self):
        self.board = [[' ' for _ in range(3)] for _ in range(3)]
        self.current_player = 1

    def print_board(self):
        print("\n   0   1   2")
        print("  -------------")
        for i in range(3):
            print(f"{i} | {self.board[i][0]} | {self.board[i][1]} | {self.board[i][2]} |")
            print("  -------------")
        print("\n")

    def make_move(self, row, col):
        if self.board[row][col] != ' ':
            return False

        self.board[row][col] = 'X' if self.current_player == 1 else 'O'
        self.current_player = 3 - self.current_player
        return True

    def check_winner(self):
        for i in range(3):
            if self.board[i][0] != ' ' and self.board[i][0] == self.board[i][1] == self.board[i][2]:
                return self.board[i][0]
            if self.board[0][i] != ' ' and self.board[0][i] == self.board[1][i] == self.board[2][i]:
                return self.board[0][i]

        if self.board[0][0] != ' ' and self.board[0][0] == self.board[1][1] == self.board[2][2]:
            return self.board[0][0]

        if self.board[0][2] != ' ' and self.board[0][2] == self.board[1][1] == self.board[2][0]:
            return self.board[0][2]

        return None

    def is_full(self):
        return all(cell != ' ' for row in self.board for cell in row)


def get_valid_input(board):
    while True:
        try:
            row = int(input("Enter row (0-2): "))
            col = int(input("Enter col (0-2): "))

            if row not in [0, 1, 2] or col not in [0, 1, 2]:
                print("❌ Only 0,1,2 allowed.")
                continue

            if board[row][col] != ' ':
                print("❌ Cell already taken.")
                continue

            return row, col

        except:
            print("❌ Enter numbers only!")


def main():
    game = TicTacToe()

    while True:
        game.print_board()
        player = game.current_player
        symbol = 'X' if player == 1 else 'O'

        print(f"Player {player} ({symbol}) turn")

        row, col = get_valid_input(game.board)
        game.make_move(row, col)

        winner = game.check_winner()
        if winner:
            game.print_board()
            print(f"🏆 Player {'1' if winner == 'X' else '2'} wins!")
            break

        if game.is_full():
            game.print_board()
            print("🤝 Draw!")
            break


if __name__ == "__main__":
    main()