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

def c(text, color):
    return f"{color}{BOLD}{text}{RESET}"

def clear():
    print("\033[2J\033[H", end="")

# ── Board layout ──────────────────────────────────────────────────────────────
# Pits: indices 0-5 = Player 1 pits (left to right)
#       index   6   = Player 1 store (Mancala)
#       indices 7-12= Player 2 pits (right to left, so 7 is opposite pit 5)
#       index   13  = Player 2 store (Mancala)

SEEDS       = 4
P1_PITS     = list(range(0, 6))
P1_STORE    = 6
P2_PITS     = list(range(7, 13))
P2_STORE    = 13
TOTAL_PITS  = 14

def make_board():
    board = [SEEDS] * TOTAL_PITS
    board[P1_STORE] = 0
    board[P2_STORE] = 0
    return board

def opposite(pit):
    return 12 - pit   # pit 0 <-> 12, 1 <-> 11, ... 5 <-> 7

def next_pit(pit, player):
    """Advance one pit, skipping opponent's store."""
    nxt = (pit + 1) % TOTAL_PITS
    if player == 1 and nxt == P2_STORE:
        nxt = 0
    if player == 2 and nxt == P1_STORE:
        nxt = 7
    return nxt

# ── Move logic ────────────────────────────────────────────────────────────────

def valid_moves(board, player):
    pits = P1_PITS if player == 1 else P2_PITS
    return [p for p in pits if board[p] > 0]

def apply_move(board, pit, player):
    """
    Sow seeds from pit. Returns (new_board, extra_turn, capture).
    extra_turn = True if last seed lands in own store.
    capture    = number of seeds captured (if last seed lands in empty own pit).
    """
    board      = list(board)
    seeds      = board[pit]
    board[pit] = 0
    capture    = 0
    extra_turn = False

    cur = pit
    while seeds > 0:
        cur    = next_pit(cur, player)
        board[cur] += 1
        seeds  -= 1

    # Extra turn: last seed in own store
    store = P1_STORE if player == 1 else P2_STORE
    if cur == store:
        extra_turn = True

    # Capture: last seed in own empty pit (was 1 after drop), opposite has seeds
    own_pits = P1_PITS if player == 1 else P2_PITS
    if cur in own_pits and board[cur] == 1:
        opp = opposite(cur)
        if board[opp] > 0:
            capture      = board[opp] + 1
            board[store] += capture
            board[cur]   = 0
            board[opp]   = 0

    return board, extra_turn, capture

def check_game_over(board):
    p1_empty = all(board[p] == 0 for p in P1_PITS)
    p2_empty = all(board[p] == 0 for p in P2_PITS)
    if p1_empty or p2_empty:
        # Sweep remaining seeds to respective stores
        for p in P1_PITS:
            board[P1_STORE] += board[p]
            board[p] = 0
        for p in P2_PITS:
            board[P2_STORE] += board[p]
            board[p] = 0
        return True, board
    return False, board

# ── AI (Minimax with alpha-beta) ──────────────────────────────────────────────

def evaluate(board, player):
    store      = P1_STORE if player == 1 else P2_STORE
    opp_store  = P2_STORE if player == 1 else P1_STORE
    return board[store] - board[opp_store]

def minimax(board, depth, alpha, beta, player, maximizing_player, orig_player):
    over, board = check_game_over(list(board))
    if over or depth == 0:
        return evaluate(board, orig_player), None

    moves = valid_moves(board, player)
    if not moves:
        return evaluate(board, orig_player), None

    opponent = 2 if player == 1 else 1
    best_move = None

    if maximizing_player:
        best = -10**9
        for pit in moves:
            nb, extra, _ = apply_move(list(board), pit, player)
            if extra:
                val, _ = minimax(nb, depth, alpha, beta, player, True, orig_player)
            else:
                val, _ = minimax(nb, depth-1, alpha, beta, opponent, False, orig_player)
            if val > best:
                best      = val
                best_move = pit
            alpha = max(alpha, val)
            if beta <= alpha:
                break
        return best, best_move
    else:
        best = 10**9
        for pit in moves:
            nb, extra, _ = apply_move(list(board), pit, player)
            if extra:
                val, _ = minimax(nb, depth, alpha, beta, player, False, orig_player)
            else:
                val, _ = minimax(nb, depth-1, alpha, beta, opponent, True, orig_player)
            if val < best:
                best      = val
                best_move = pit
            beta = min(beta, val)
            if beta <= alpha:
                break
        return best, best_move

def ai_best_move(board, player, difficulty):
    moves = valid_moves(board, player)
    if not moves:
        return None
    if difficulty == '1':
        return random.choice(moves)
    depths = {'2': 3, '3': 6, '4': 9}
    depth  = depths.get(difficulty, 3)
    _, move = minimax(board, depth, -10**9, 10**9, player, True, player)
    return move if move is not None else random.choice(moves)

# ── Render ────────────────────────────────────────────────────────────────────

PIT_COLORS = [CYAN, YELLOW, GREEN, ORANGE, MAGENTA, RED]

def seed_str(n):
    if n == 0:
        return c(" 0 ", GREY)
    col = GREEN if n <= 4 else YELLOW if n <= 8 else RED
    return c(f"{n:2d} ", col)

def pit_label(pit, player, highlight_pits):
    col = CYAN if player == 1 else MAGENTA
    idx = pit if player == 1 else pit - 7
    num = idx + 1
    if pit in highlight_pits:
        return c(f"[{num}]", YELLOW)
    return c(f" {num} ", col)

def render(board, current_player, p1_name, p2_name, last_pit,
           extra_turn, capture, turn_num, start_time, highlight=[]):
    clear()
    elapsed   = int(time.time() - start_time)
    mins, sec = divmod(elapsed, 60)

    print(c("\n  ╔══════════════════════════════════════════════╗", CYAN))
    print(c("  ║          🌰  M A N C A L A                   ║", CYAN))
    print(c("  ╚══════════════════════════════════════════════╝\n", CYAN))

    p1s = board[P1_STORE]
    p2s = board[P2_STORE]
    total = p1s + p2s + sum(board[i] for i in P1_PITS) + sum(board[i] for i in P2_PITS)
    b1 = int((p1s / max(total,1)) * 24)
    b2 = 24 - b1
    bar = c("█"*b1, CYAN) + c("█"*b2, MAGENTA)
    print(f"  {c(p1_name, CYAN)} {c(str(p1s).rjust(2), YELLOW)} │{bar}│ {c(str(p2s).rjust(2), YELLOW)} {c(p2_name, MAGENTA)}")
    print()

    turn_col  = CYAN if current_player == 1 else MAGENTA
    turn_name = p1_name if current_player == 1 else p2_name
    print(f"  Turn: {c(str(turn_num), YELLOW)}   Time: {c(f'{mins:02d}:{sec:02d}', WHITE)}   {c('▶ ' + turn_name, turn_col)}")

    msg = ""
    if extra_turn:
        msg = c("  ✨ Extra turn!", GREEN)
    if capture:
        msg += c(f"  🎯 Captured {capture} seeds!", ORANGE)
    if msg:
        print(msg)
    print()

    # Board drawing
    # Top border
    print(c("  ┌──────┬" + "──────┬"*6 + "──────┐", GREY))

    # P2 name row
    p2_label = c(f"  {p2_name[:4]:^4}  ", MAGENTA)
    print(c("  │      │", GREY) +
          "".join(c("      │", GREY) for _ in range(5)) +
          c("      │", GREY) +
          c("      │", GREY))

    # P2 pit numbers (reversed: pit 12 down to 7)
    p2_pit_row = c("  │      │", GREY)
    for pit in reversed(P2_PITS):
        lbl = pit_label(pit, 2, highlight)
        p2_pit_row += f"  {lbl} " + c("│", GREY)
    p2_pit_row += c("      │", GREY)
    print(p2_pit_row)

    # P2 seeds row
    p2_seed_row = c("  │", GREY) + c(f"  {board[P2_STORE]:^3} │", MAGENTA)
    for pit in reversed(P2_PITS):
        p2_seed_row += f"  {seed_str(board[pit])}" + c("│", GREY)
    p2_seed_row += c("      │", GREY)
    print(p2_seed_row)

    # Middle divider
    print(c("  │      ├" + "──────┼"*5 + "──────┤", GREY) + c("      │", GREY))

    # P1 seeds row
    p1_seed_row = c("  │      │", GREY)
    for pit in P1_PITS:
        p1_seed_row += f"  {seed_str(board[pit])}" + c("│", GREY)
    p1_seed_row += c("  " + c(f"{board[P1_STORE]:^3}", CYAN) + " │", GREY)
    print(p1_seed_row)

    # P1 pit numbers
    p1_pit_row = c("  │      │", GREY)
    for pit in P1_PITS:
        lbl = pit_label(pit, 1, highlight)
        p1_pit_row += f"  {lbl} " + c("│", GREY)
    p1_pit_row += c("      │", GREY)
    print(p1_pit_row)

    print(c("  │      │", GREY) +
          "".join(c("      │", GREY) for _ in range(6)) +
          c("      │", GREY))

    # Bottom border
    print(c("  └──────┴" + "──────┴"*6 + "──────┘", GREY))
    print()

    # Store labels
    print(f"  {c('  P2 Store', MAGENTA)}" +
          " " * 43 +
          f"{c('P1 Store  ', CYAN)}")
    print()

    # Legend
    valid = valid_moves(board, current_player)
    if current_player == 1:
        valid_str = "  ".join(c(f"[{p+1}]", YELLOW) for p in valid)
        print(c(f"  {p1_name}'s pits (bottom row): ", CYAN) + valid_str)
    else:
        valid_str = "  ".join(c(f"[{p-6}]", YELLOW) for p in valid)
        print(c(f"  {p2_name}'s pits (top row): ", MAGENTA) + valid_str)
    print()
    print(c("  Enter pit number (1-6)  |  H = hint  |  Q = quit", GREY))
    print()

# ── Hint ──────────────────────────────────────────────────────────────────────

def get_hint(board, player, difficulty):
    move = ai_best_move(board, player, '3')   # always use hard for hints
    if move is None:
        return None
    idx = move + 1 if player == 1 else move - 6
    return move, idx

# ── Menus ─────────────────────────────────────────────────────────────────────

def choose_mode():
    clear()
    print(c("\n  ╔══════════════════════════════╗", CYAN))
    print(c("  ║      Choose Game Mode        ║", CYAN))
    print(c("  ╚══════════════════════════════╝\n", CYAN))
    print(f"  {c('1', YELLOW)}.  {c('vs Computer', RED)}   — you vs AI")
    print(f"  {c('2', YELLOW)}.  {c('2 Players',   GREEN)} — local multiplayer")
    print(f"  {c('3', YELLOW)}.  {c('AI vs AI',    MAGENTA)} — watch two AIs")
    print()
    while True:
        ch = input("  Choose (1-3): ").strip()
        if ch in ('1','2','3'):
            return ch
        print(c("  Invalid.", RED))

def choose_difficulty(label="AI"):
    clear()
    print(c(f"\n  ╔══════════════════════════════╗", CYAN))
    print(c(f"  ║  {label:<6} Difficulty           ║", CYAN))
    print(c(f"  ╚══════════════════════════════╝\n", CYAN))
    print(f"  {c('1', GREEN)}.   Easy    — random moves")
    print(f"  {c('2', YELLOW)}.   Medium  — depth 3")
    print(f"  {c('3', RED)}.   Hard    — depth 6")
    print(f"  {c('4', MAGENTA)}.   Expert  — depth 9")
    print()
    while True:
        ch = input("  Choose (1-4): ").strip()
        if ch in ('1','2','3','4'):
            return ch
        print(c("  Invalid.", RED))

# ── Game loop ─────────────────────────────────────────────────────────────────

def play():
    mode = choose_mode()

    if mode == '1':
        human  = 1
        diff   = choose_difficulty("AI")
        dnames = {'1':'Easy','2':'Medium','3':'Hard','4':'Expert'}
        p1name = "You"
        p2name = f"AI ({dnames[diff]})"
    elif mode == '2':
        human  = None
        diff   = None
        p1name = "Player 1"
        p2name = "Player 2"
    else:
        human  = None
        diff1  = choose_difficulty("AI-1")
        diff2  = choose_difficulty("AI-2")
        dnames = {'1':'Easy','2':'Medium','3':'Hard','4':'Expert'}
        p1name = f"AI-1 ({dnames[diff1]})"
        p2name = f"AI-2 ({dnames[diff2]})"
        diff   = None

    board      = make_board()
    current    = 1
    last_pit   = None
    extra_turn = False
    capture    = 0
    turn_num   = 1
    start_time = time.time()
    show_hint  = False

    while True:
        over, board = check_game_over(list(board))
        if over:
            break

        moves = valid_moves(board, current)
        if not moves:
            current = 2 if current == 1 else 1
            continue

        is_human = (mode == '2') or (mode == '1' and current == human)
        is_ai    = not is_human

        highlight = moves if show_hint else []
        render(board, current, p1name, p2name, last_pit,
               extra_turn, capture, turn_num, start_time, highlight)
        extra_turn = False
        capture    = 0

        if is_ai:
            d = diff if mode == '1' else (diff1 if current == 1 else diff2)
            print(c("  🤖 AI is thinking...", MAGENTA))
            time.sleep(0.5 if d in ('1','2') else 1.0)
            pit = ai_best_move(board, current, d)
        else:
            # Human input
            while True:
                raw = input("  > ").strip().lower()
                if raw == 'q':
                    clear()
                    print(c("\n  Thanks for playing Mancala! 🌰\n", CYAN))
                    return
                if raw == 'h':
                    show_hint = True
                    highlight = moves
                    render(board, current, p1name, p2name, last_pit,
                           False, 0, turn_num, start_time, highlight)
                    hint_result = get_hint(board, current, '3')
                    if hint_result:
                        _, idx = hint_result
                        print(c(f"  💡 Hint: try pit {idx}", YELLOW))
                    continue
                if raw.isdigit():
                    idx = int(raw)
                    if 1 <= idx <= 6:
                        pit = (idx - 1) if current == 1 else (idx + 6)
                        if pit in moves:
                            break
                print(c("  Invalid. Enter 1-6.", RED))
            show_hint = False

        board, got_extra, got_capture = apply_move(list(board), pit, current)
        last_pit   = pit
        extra_turn = got_extra
        capture    = got_capture

        if not got_extra:
            current = 2 if current == 1 else 1
            turn_num += 1

    # ── End game ──────────────────────────────────────────────────────────────
    elapsed      = int(time.time() - start_time)
    mins, secs   = divmod(elapsed, 60)
    p1s          = board[P1_STORE]
    p2s          = board[P2_STORE]

    render(board, current, p1name, p2name, last_pit,
           False, 0, turn_num, start_time)

    print(c("  ╔══════════════════════════════════════╗", CYAN))
    if p1s > p2s:
        print(c(f"  ║  🏆  {p1name:<34}WINS! ║", GREEN))
    elif p2s > p1s:
        print(c(f"  ║  🏆  {p2name:<34}WINS! ║", GREEN))
    else:
        print(c("  ║           🤝  IT'S A DRAW!           ║", YELLOW))
    print(c("  ╚══════════════════════════════════════╝\n", CYAN))

    print(f"  {c(p1name, CYAN)} store : {c(str(p1s), YELLOW)}")
    print(f"  {c(p2name, MAGENTA)} store : {c(str(p2s), YELLOW)}")
    print(f"  Turns  : {c(str(turn_num), YELLOW)}   Time: {c(f'{mins:02d}:{secs:02d}', WHITE)}")
    print()
    input(c("  Press ENTER to continue...", GREY))

def main():
    clear()
    print(c("\n  ╔══════════════════════════════════════════════╗", CYAN))
    print(c("  ║          🌰  M A N C A L A                   ║", CYAN))
    print(c("  ╚══════════════════════════════════════════════╝\n", CYAN))
    print("  Sow seeds around the board and collect the most")
    print("  seeds in your store (Mancala) to win!\n")
    print(f"  {c('Rules:', WHITE)}")
    print("  • Pick a pit on your side and sow seeds counter-clockwise")
    print("  • Land in your store → get an extra turn  ✨")
    print("  • Land in empty own pit → capture opposite pit's seeds  🎯")
    print("  • Game ends when one side is empty — sweep rest to stores")
    print()
    input(c("  Press ENTER to start...", GREY))

    while True:
        play()
        again = input(c("  Play again? (y/n): ", WHITE)).strip().lower()
        if again != 'y':
            print(c("\n  Goodbye! 🌰\n", CYAN))
            break

if __name__ == "__main__":
    main()