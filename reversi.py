import copy
import time
import random

RESET   = "\033[0m"
BOLD    = "\033[1m"
CYAN    = "\033[96m"
YELLOW  = "\033[93m"
GREEN   = "\033[92m"
RED     = "\033[91m"
GREY    = "\033[90m"
WHITE   = "\033[97m"
MAGENTA = "\033[95m"
ORANGE  = "\033[38;5;214m"
BG_BOARD= "\033[48;5;22m"

def c(text, color):
    return f"{color}{BOLD}{text}{RESET}"

def clear():
    print("\033[2J\033[H", end="")

# ── Constants ─────────────────────────────────────────────────────────────────
BLACK  = 1
WHITE_P= 2
EMPTY  = 0
SIZE   = 8

DIRS = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]

# Corner and edge weights for AI evaluation
WEIGHTS = [
    [100, -20,  10,   5,   5,  10, -20, 100],
    [-20, -50,  -2,  -2,  -2,  -2, -50, -20],
    [ 10,  -2,   5,   1,   1,   5,  -2,  10],
    [  5,  -2,   1,   0,   0,   1,  -2,   5],
    [  5,  -2,   1,   0,   0,   1,  -2,   5],
    [ 10,  -2,   5,   1,   1,   5,  -2,  10],
    [-20, -50,  -2,  -2,  -2,  -2, -50, -20],
    [100, -20,  10,   5,   5,  10, -20, 100],
]

# ── Board logic ───────────────────────────────────────────────────────────────

def make_board():
    board = [[EMPTY]*SIZE for _ in range(SIZE)]
    mid   = SIZE // 2
    board[mid-1][mid-1] = WHITE_P
    board[mid-1][mid]   = BLACK
    board[mid][mid-1]   = BLACK
    board[mid][mid]     = WHITE_P
    return board

def in_bounds(r, col):
    return 0 <= r < SIZE and 0 <= col < SIZE

def get_flips(board, r, col, player):
    if board[r][col] != EMPTY:
        return []
    opponent = WHITE_P if player == BLACK else BLACK
    all_flips = []
    for dr, dc in DIRS:
        flips = []
        nr, nc = r+dr, col+dc
        while in_bounds(nr, nc) and board[nr][nc] == opponent:
            flips.append((nr, nc))
            nr += dr
            nc += dc
        if flips and in_bounds(nr, nc) and board[nr][nc] == player:
            all_flips.extend(flips)
    return all_flips

def valid_moves(board, player):
    moves = []
    for r in range(SIZE):
        for col in range(SIZE):
            if get_flips(board, r, col, player):
                moves.append((r, col))
    return moves

def apply_move(board, r, col, player):
    new_board = copy.deepcopy(board)
    flips     = get_flips(new_board, r, col, player)
    new_board[r][col] = player
    for fr, fc in flips:
        new_board[fr][fc] = player
    return new_board, len(flips)

def count_pieces(board):
    black = sum(board[r][c] == BLACK  for r in range(SIZE) for c in range(SIZE))
    white = sum(board[r][c] == WHITE_P for r in range(SIZE) for c in range(SIZE))
    return black, white

# ── AI ────────────────────────────────────────────────────────────────────────

def evaluate(board, player):
    opponent = WHITE_P if player == BLACK else BLACK
    score    = 0
    # Positional weight
    for r in range(SIZE):
        for col in range(SIZE):
            if board[r][col] == player:
                score += WEIGHTS[r][col]
            elif board[r][col] == opponent:
                score -= WEIGHTS[r][col]
    # Mobility
    my_moves  = len(valid_moves(board, player))
    opp_moves = len(valid_moves(board, opponent))
    score    += 10 * (my_moves - opp_moves)
    # Piece count (only weight heavily near end)
    bc, wc   = count_pieces(board)
    total    = bc + wc
    if total > 50:
        piece_score = (bc - wc) if player == BLACK else (wc - bc)
        score += 3 * piece_score
    return score

def minimax(board, depth, alpha, beta, maximizing, player, opponent):
    moves = valid_moves(board, player if maximizing else opponent)
    if depth == 0 or (not moves and not valid_moves(board, opponent if maximizing else player)):
        return evaluate(board, player), None

    if not moves:
        val, _ = minimax(board, depth-1, alpha, beta, not maximizing, player, opponent)
        return val, None

    best_move = None
    if maximizing:
        best = -10**9
        for r, col in moves:
            nb, _ = apply_move(board, r, col, player)
            val, _ = minimax(nb, depth-1, alpha, beta, False, player, opponent)
            if val > best:
                best      = val
                best_move = (r, col)
            alpha = max(alpha, val)
            if beta <= alpha:
                break
        return best, best_move
    else:
        best = 10**9
        for r, col in moves:
            nb, _ = apply_move(board, r, col, opponent)
            val, _ = minimax(nb, depth-1, alpha, beta, True, player, opponent)
            if val < best:
                best      = val
                best_move = (r, col)
            beta = min(beta, val)
            if beta <= alpha:
                break
        return best, best_move

def ai_move(board, player, difficulty):
    moves = valid_moves(board, player)
    if not moves:
        return None
    if difficulty == '1':           # Easy — random
        return random.choice(moves)
    elif difficulty == '2':         # Medium — depth 2
        _, move = minimax(board, 2, -10**9, 10**9, True, player,
                          WHITE_P if player == BLACK else BLACK)
        return move or random.choice(moves)
    elif difficulty == '3':         # Hard — depth 4
        _, move = minimax(board, 4, -10**9, 10**9, True, player,
                          WHITE_P if player == BLACK else BLACK)
        return move or random.choice(moves)
    else:                           # Expert — depth 6
        _, move = minimax(board, 6, -10**9, 10**9, True, player,
                          WHITE_P if player == BLACK else BLACK)
        return move or random.choice(moves)

# ── Render ────────────────────────────────────────────────────────────────────

DISK_BLACK = c("●", "\033[30m\033[47m") + RESET   # black disk
DISK_WHITE = c("○", WHITE)                          # white disk
DISK_HINT  = c("·", YELLOW)
DISK_EMPTY = " "

def render(board, current_player, moves, last_move, black_name, white_name,
           b_count, w_count, show_hints, turn_num, start_time, message=""):
    clear()
    elapsed   = int(time.time() - start_time)
    mins, sec = divmod(elapsed, 60)
    hint_set  = set(moves) if show_hints else set()

    print(c("\n  ╔══════════════════════════════════════════╗", CYAN))
    print(c("  ║      ⚫⚪  R E V E R S I  /  O T H E L L O ║", CYAN))
    print(c("  ╚══════════════════════════════════════════╝\n", CYAN))

    # Score bar
    total   = b_count + w_count
    b_bar   = int((b_count / max(total, 1)) * 20)
    w_bar   = 20 - b_bar
    bar     = c("█" * b_bar, GREY) + c("█" * w_bar, WHITE)
    print(f"  {c('⚫ '+black_name, GREY)} {c(str(b_count).rjust(2), YELLOW)} │{bar}│ {c(str(w_count).rjust(2), YELLOW)} {c('⚪ '+white_name, WHITE)}")
    print()

    # Current turn indicator
    if current_player == BLACK:
        turn_str = c("⚫  " + black_name + "'s turn", GREY)
    else:
        turn_str = c("⚪  " + white_name + "'s turn", WHITE)
    print(f"  {turn_str}   Turn: {c(str(turn_num), YELLOW)}   Time: {c(f'{mins:02d}:{sec:02d}', CYAN)}")
    if message:
        print(f"  {c(message, MAGENTA)}")
    print()

    # Column headers
    col_hdr = "      " + "  ".join(c(str(i+1), GREY) for i in range(SIZE))
    print(col_hdr)
    print(c("    ┌" + "───┬"*(SIZE-1) + "───┐", GREY))

    for r in range(SIZE):
        row_label = c(str(r+1), GREY)
        row_str   = f"  {row_label} │"
        for col in range(SIZE):
            cell = board[r][col]
            is_last = last_move == (r, col)
            if cell == BLACK:
                disk = c("●", GREY) if not is_last else c("●", GREEN)
                row_str += f" {disk} │"
            elif cell == WHITE_P:
                disk = c("○", WHITE) if not is_last else c("○", GREEN)
                row_str += f" {disk} │"
            elif (r, col) in hint_set:
                row_str += f" {c('·', YELLOW)} │"
            else:
                row_str += f"   │"
        print(row_str)
        if r < SIZE - 1:
            print(c("    ├" + "───┼"*(SIZE-1) + "───┤", GREY))
    print(c("    └" + "───┴"*(SIZE-1) + "───┘", GREY))
    print()

    if show_hints and moves:
        move_strs = ", ".join(f"{r+1},{col+1}" for r,col in moves)
        print(c(f"  💡 Valid moves: {move_strs}", YELLOW))
    elif not moves:
        print(c("  ⚠  No valid moves — turn passes!", RED))
    print()
    print(c("  Input: <row> <col>  (e.g. 3 4)  |  H = hints  |  Q = quit", GREY))
    print()

# ── Get input ─────────────────────────────────────────────────────────────────

def get_player_move(board, player, show_hints, black_name, white_name,
                    b_count, w_count, turn_num, start_time, last_move):
    moves = valid_moves(board, player)
    while True:
        render(board, player, moves, last_move, black_name, white_name,
               b_count, w_count, show_hints, turn_num, start_time)
        if not moves:
            input(c("  No moves available. Press ENTER to pass...", RED))
            return None, show_hints

        raw = input("  > ").strip().lower()
        if raw == 'q':
            return "quit", show_hints
        if raw == 'h':
            show_hints = not show_hints
            continue
        parts = raw.split()
        if len(parts) == 2:
            try:
                r   = int(parts[0]) - 1
                col = int(parts[1]) - 1
                if (r, col) in moves:
                    return (r, col), show_hints
                else:
                    pass
            except ValueError:
                pass
        # Also accept "34" or "3,4"
        if len(raw) == 2 and raw.isdigit():
            r, col = int(raw[0])-1, int(raw[1])-1
            if (r, col) in moves:
                return (r, col), show_hints
        print(c("  Invalid move. Try again.", RED))
        time.sleep(0.6)

# ── Setup menus ───────────────────────────────────────────────────────────────

def choose_game_mode():
    clear()
    print(c("\n  ╔══════════════════════════════╗", CYAN))
    print(c("  ║       Choose Game Mode       ║", CYAN))
    print(c("  ╚══════════════════════════════╝\n", CYAN))
    print(f"  {c('1', YELLOW)}.  {c('vs Computer', RED)}   — you vs AI")
    print(f"  {c('2', YELLOW)}.  {c('2 Players',   GREEN)} — local multiplayer")
    print(f"  {c('3', YELLOW)}.  {c('AI vs AI',    MAGENTA)} — watch two AIs play")
    print()
    while True:
        ch = input("  Choose (1-3): ").strip()
        if ch in ('1','2','3'):
            return ch
        print(c("  Invalid.", RED))

def choose_ai_difficulty(label="AI"):
    clear()
    print(c(f"\n  ╔══════════════════════════════╗", CYAN))
    print(c(f"  ║  Choose {label:<6} Difficulty   ║", CYAN))
    print(c(f"  ╚══════════════════════════════╝\n", CYAN))
    print(f"  {c('1', GREEN)}.   Easy    — random moves")
    print(f"  {c('2', YELLOW)}.   Medium  — looks 2 moves ahead")
    print(f"  {c('3', RED)}.   Hard    — looks 4 moves ahead")
    print(f"  {c('4', MAGENTA)}.   Expert  — looks 6 moves ahead")
    print()
    while True:
        ch = input("  Choose (1-4): ").strip()
        if ch in ('1','2','3','4'):
            return ch
        print(c("  Invalid.", RED))

def choose_color():
    clear()
    print(c("\n  ╔══════════════════════════════╗", CYAN))
    print(c("  ║       Choose Your Color      ║", CYAN))
    print(c("  ╚══════════════════════════════╝\n", CYAN))
    print(f"  {c('1', GREY)}.  {c('⚫ Black', GREY)}  (moves first)")
    print(f"  {c('2', WHITE)}.  {c('⚪ White', WHITE)}  (moves second)")
    print()
    while True:
        ch = input("  Choose (1/2): ").strip()
        if ch == '1': return BLACK
        if ch == '2': return WHITE_P
        print(c("  Invalid.", RED))

# ── Main game ─────────────────────────────────────────────────────────────────

def play():
    mode = choose_game_mode()

    if mode == '1':
        human_color = choose_color()
        diff        = choose_ai_difficulty("AI")
        ai_color    = WHITE_P if human_color == BLACK else BLACK
        black_name  = "You"    if human_color == BLACK else "AI"
        white_name  = "AI"     if human_color == BLACK else "You"
        diff_names  = {'1':'Easy','2':'Medium','3':'Hard','4':'Expert'}
        ai_label    = f"AI ({diff_names[diff]})"
        if human_color == BLACK:
            white_name = ai_label
        else:
            black_name = ai_label
    elif mode == '2':
        human_color = BLACK
        ai_color    = None
        black_name  = "Player 1"
        white_name  = "Player 2"
        diff        = None
    else:
        diff1       = choose_ai_difficulty("AI-1")
        diff2       = choose_ai_difficulty("AI-2")
        diff_names  = {'1':'Easy','2':'Medium','3':'Hard','4':'Expert'}
        black_name  = f"AI-1 ({diff_names[diff1]})"
        white_name  = f"AI-2 ({diff_names[diff2]})"
        human_color = None
        ai_color    = None

    board      = make_board()
    current    = BLACK
    show_hints = True
    last_move  = None
    turn_num   = 1
    start_time = time.time()
    passed     = 0
    message    = ""

    while True:
        b_count, w_count = count_pieces(board)
        moves            = valid_moves(board, current)

        if not moves:
            passed += 1
            other   = WHITE_P if current == BLACK else BLACK
            if not valid_moves(board, other):
                break   # both pass — game over
            # Show pass message briefly
            render(board, current, [], last_move, black_name, white_name,
                   b_count, w_count, False, turn_num, start_time,
                   message="No valid moves — turn passes!")
            time.sleep(1.5)
            current = other
            continue
        else:
            passed = 0

        # Determine who moves
        is_human_turn = (
            mode == '2' or
            (mode == '1' and current == human_color)
        )
        is_ai_turn = not is_human_turn

        if mode == '3':
            is_ai_turn   = True
            is_human_turn = False

        if is_human_turn:
            move, show_hints = get_player_move(
                board, current, show_hints,
                black_name, white_name, b_count, w_count,
                turn_num, start_time, last_move
            )
            if move == "quit":
                clear()
                print(c("\n  Thanks for playing Reversi!\n", CYAN))
                return
        else:
            # AI move
            d    = diff if mode == '1' else (diff1 if current == BLACK else diff2)
            render(board, current, [], last_move, black_name, white_name,
                   b_count, w_count, False, turn_num, start_time,
                   message="🤖 AI is thinking...")
            time.sleep(0.6 if d in ('1','2') else 1.2)
            move = ai_move(board, current, d)

        if move:
            board, flipped = apply_move(board, move[0], move[1], current)
            last_move      = move
            message        = f"+{flipped} disk{'s' if flipped!=1 else ''} flipped"

        turn_num += 1
        current   = WHITE_P if current == BLACK else BLACK

    # ── Game over ─────────────────────────────────────────────────────────────
    b_count, w_count = count_pieces(board)
    elapsed          = int(time.time() - start_time)
    mins, secs       = divmod(elapsed, 60)

    render(board, current, [], last_move, black_name, white_name,
           b_count, w_count, False, turn_num, start_time, message="Game Over!")

    print(c("  ╔══════════════════════════════════════╗", CYAN))
    if b_count > w_count:
        winner = black_name
        print(c(f"  ║  🏆  {winner:<32}WINS! ║", GREEN))
    elif w_count > b_count:
        winner = white_name
        print(c(f"  ║  🏆  {winner:<32}WINS! ║", GREEN))
    else:
        print(c("  ║           🤝  IT'S A DRAW!           ║", YELLOW))
    print(c("  ╚══════════════════════════════════════╝\n", CYAN))

    print(f"  {c('⚫ '+black_name, GREY)} : {c(str(b_count), YELLOW)}   {c('⚪ '+white_name, WHITE)} : {c(str(w_count), YELLOW)}")
    print(f"  Turns played : {c(str(turn_num), YELLOW)}")
    print(f"  Time         : {c(f'{mins:02d}:{secs:02d}', CYAN)}")
    print()
    input(c("  Press ENTER to continue...", GREY))

def main():
    clear()
    print(c("\n  ╔══════════════════════════════════════════╗", CYAN))
    print(c("  ║    ⚫⚪  R E V E R S I  /  O T H E L L O  ║", CYAN))
    print(c("  ╚══════════════════════════════════════════╝\n", CYAN))
    print("  Flip your opponent's disks by sandwiching them.")
    print("  The player with the most disks at the end wins!\n")
    print(f"  {c('⚫', GREY)} Black moves first.")
    print(f"  {c('·', YELLOW)} Yellow dots show valid moves (toggle with H).")
    print()
    input(c("  Press ENTER to start...", GREY))

    while True:
        play()
        again = input(c("  Play again? (y/n): ", WHITE)).strip().lower()
        if again != 'y':
            print(c("\n  Goodbye! ⚫⚪\n", CYAN))
            break

if __name__ == "__main__":
    main()
