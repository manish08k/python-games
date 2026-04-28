import random
import time

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

# ── Nim logic ─────────────────────────────────────────────────────────────────

def nim_value(piles):
    """XOR of all pile sizes — the key to optimal Nim strategy."""
    result = 0
    for p in piles:
        result ^= p
    return result

def ai_move_hard(piles):
    """Perfect play: find a move that leaves nim_value == 0."""
    xor_sum = nim_value(piles)
    if xor_sum == 0:
        # Already losing position — just remove 1 from largest pile
        idx = max(range(len(piles)), key=lambda i: piles[i])
        return idx, 1
    for i, p in enumerate(piles):
        target = p ^ xor_sum
        if target < p:
            return i, p - target
    idx = max(range(len(piles)), key=lambda i: piles[i])
    return idx, 1

def ai_move_medium(piles):
    """Medium: plays optimally 65% of the time, random otherwise."""
    if random.random() < 0.65:
        return ai_move_hard(piles)
    non_empty = [i for i, p in enumerate(piles) if p > 0]
    idx = random.choice(non_empty)
    amount = random.randint(1, piles[idx])
    return idx, amount

def ai_move_easy(piles):
    """Easy: mostly random with occasional mistakes."""
    non_empty = [i for i, p in enumerate(piles) if p > 0]
    idx = random.choice(non_empty)
    amount = random.randint(1, piles[idx])
    return idx, amount

# ── Display ───────────────────────────────────────────────────────────────────

STICK   = c("| ", YELLOW)
EMPTY   = c("  ", GREY)
PILE_COLORS = [CYAN, MAGENTA, GREEN, ORANGE, RED]

def render_board(piles, last_move=None, misere=False):
    clear()
    print(c("\n  ╔══════════════════════════════════════╗", CYAN))
    print(c("  ║         🎋  N I M  G A M E           ║", CYAN))
    mode_str = c("Misère", RED) if misere else c("Normal", GREEN)
    print(f"  ║  Mode: {mode_str:<30}{CYAN}{BOLD}║{RESET}")
    print(c("  ╚══════════════════════════════════════╝\n", CYAN))

    max_pile = max(piles) if piles else 0
    total    = sum(piles)

    for i, pile in enumerate(piles):
        col      = PILE_COLORS[i % len(PILE_COLORS)]
        label    = c(f"Pile {i+1}", col)
        sticks   = STICK * pile + EMPTY * (max_pile - pile)
        count    = c(f"({pile})", col)
        marker   = c("  ◀ last move", GREY) if last_move and last_move[0] == i else ""
        print(f"  {label}  {sticks} {count}{marker}")

    print()
    xor = nim_value(piles)
    xor_col = RED if xor == 0 else GREEN
    print(f"  Total sticks: {c(str(total), YELLOW)}   Nim-value (XOR): {c(str(xor), xor_col)}")
    print()

def render_hint(piles, misere):
    xor = nim_value(piles)
    non_empty = sum(1 for p in piles if p > 0)
    if misere:
        # Misère: if only 1 non-empty pile, take all but 1 (or all if odd piles)
        if non_empty == 1:
            tip = "Only one pile left — take ALL sticks to win (misère)!"
        elif xor == 0:
            tip = "You're in a LOSING position. Try any move and hope AI slips!"
        else:
            tip = "You're in a WINNING position — play optimally!"
    else:
        if xor == 0:
            tip = "You're in a LOSING position (XOR=0). Hope AI makes a mistake!"
        else:
            tip = f"You're in a WINNING position (XOR={xor}). Make XOR=0 to win!"
    print(c(f"  💡 Hint: {tip}", MAGENTA))
    print()

# ── Modes & config ────────────────────────────────────────────────────────────

PRESET_CONFIGS = {
    "1": {"name": "Classic 3-Pile",    "piles": [3, 5, 7]},
    "2": {"name": "Four Piles",        "piles": [1, 3, 5, 7]},
    "3": {"name": "Triangle",          "piles": [1, 2, 3, 4, 5]},
    "4": {"name": "Big Game",          "piles": [7, 9, 11, 13]},
    "5": {"name": "Single Pile (10)",  "piles": [10]},
    "6": {"name": "Custom",            "piles": None},
}

def choose_config():
    clear()
    print(c("\n  ╔══════════════════════════════╗", CYAN))
    print(c("  ║   Choose Pile Configuration  ║", CYAN))
    print(c("  ╚══════════════════════════════╝\n", CYAN))
    for k, v in PRESET_CONFIGS.items():
        piles_str = str(v["piles"]) if v["piles"] else "[you decide]"
        print(f"  {c(k, YELLOW)}. {v['name']:<22} {c(piles_str, GREY)}")
    print()
    while True:
        ch = input("  Choose (1-6): ").strip()
        if ch not in PRESET_CONFIGS:
            print(c("  Invalid.", RED))
            continue
        if ch == "6":
            while True:
                try:
                    raw = input("  Enter pile sizes (e.g. 3 5 7): ").strip()
                    piles = list(map(int, raw.split()))
                    if not piles or any(p <= 0 for p in piles):
                        raise ValueError
                    return piles, "Custom"
                except ValueError:
                    print(c("  Enter positive integers separated by spaces.", RED))
        return list(PRESET_CONFIGS[ch]["piles"]), PRESET_CONFIGS[ch]["name"]

def choose_difficulty():
    clear()
    print(c("\n  ╔══════════════════════════════╗", CYAN))
    print(c("  ║     Choose AI Difficulty     ║", CYAN))
    print(c("  ╚══════════════════════════════╝\n", CYAN))
    print(f"  {c('1', GREEN)}.   Easy    — random moves")
    print(f"  {c('2', YELLOW)}.   Medium  — 65% optimal")
    print(f"  {c('3', RED)}.   Hard    — perfect play (unbeatable)")
    print(f"  {c('4', CYAN)}.   2 Player — local multiplayer")
    print()
    while True:
        ch = input("  Choose (1-4): ").strip()
        if ch in ('1','2','3','4'):
            return ch
        print(c("  Invalid.", RED))

def choose_mode():
    clear()
    print(c("\n  ╔══════════════════════════════╗", CYAN))
    print(c("  ║       Choose Game Mode       ║", CYAN))
    print(c("  ╚══════════════════════════════╝\n", CYAN))
    print(f"  {c('1', GREEN)}.  {c('Normal', GREEN)}   — last to take a stick WINS")
    print(f"  {c('2', RED)}.  {c('Misère', RED)}   — last to take a stick LOSES")
    print()
    while True:
        ch = input("  Choose (1/2): ").strip()
        if ch == '1': return False
        if ch == '2': return True
        print(c("  Invalid.", RED))

# ── Player turn ───────────────────────────────────────────────────────────────

def player_turn(piles, player_name, hints, misere):
    while True:
        render_board(piles, misere=misere)
        if hints:
            render_hint(piles, misere)
        print(c(f"  {player_name}'s turn", CYAN))
        print(c("  Enter:  <pile number> <amount>  (e.g. 2 3)  |  H = hint  |  Q = quit\n", GREY))
        raw = input("  > ").strip().lower()

        if raw == 'q':
            return None, None, "quit"
        if raw == 'h':
            hints = True
            continue

        parts = raw.split()
        if len(parts) != 2:
            print(c("  Enter pile number and amount, e.g.:  2 3", RED))
            time.sleep(1)
            continue
        try:
            pile_num = int(parts[0]) - 1
            amount   = int(parts[1])
        except ValueError:
            print(c("  Numbers only.", RED))
            time.sleep(1)
            continue

        if pile_num < 0 or pile_num >= len(piles):
            print(c(f"  Pile must be 1–{len(piles)}.", RED))
            time.sleep(1)
            continue
        if amount < 1 or amount > piles[pile_num]:
            print(c(f"  Must take 1–{piles[pile_num]} from pile {pile_num+1}.", RED))
            time.sleep(1)
            continue

        return pile_num, amount, "ok"

# ── AI turn ───────────────────────────────────────────────────────────────────

def ai_turn(piles, difficulty, misere):
    non_empty = [i for i, p in enumerate(piles) if p > 0]
    if not non_empty:
        return 0, 0

    if misere:
        # Misère strategy: play normal Nim UNTIL only single-stick piles remain,
        # then invert the goal (leave odd number of 1-piles)
        multi = [p for p in piles if p > 1]
        if not multi:
            # All piles are 0 or 1 — take from a pile to leave ODD number of 1-piles
            ones = sum(1 for p in piles if p == 1)
            # We want to leave even number of 1-piles for opponent (so they take last)
            idx  = next(i for i, p in enumerate(piles) if p == 1)
            return idx, 1
        # Normal Nim strategy otherwise
        if difficulty == '1':
            return ai_move_easy(piles)
        elif difficulty == '2':
            return ai_move_medium(piles)
        else:
            return ai_move_hard(piles)
    else:
        if difficulty == '1':
            return ai_move_easy(piles)
        elif difficulty == '2':
            return ai_move_medium(piles)
        else:
            return ai_move_hard(piles)

# ── Main game loop ────────────────────────────────────────────────────────────

def play():
    misere     = choose_mode()
    piles, config_name = choose_config()
    difficulty = choose_difficulty()

    ai_names   = {'1': 'Easy AI', '2': 'Medium AI', '3': 'Hard AI', '4': 'Player 2'}
    p1_name    = c("Player 1", CYAN)
    p2_name    = c(ai_names[difficulty], RED) if difficulty != '4' else c("Player 2", MAGENTA)

    hints_on   = False
    turn       = 0          # 0 = player 1, 1 = player 2 / AI
    last_move  = None
    history    = []
    start_time = time.time()

    while True:
        if sum(piles) == 0:
            # Game over — determine winner
            # The player who just moved took the last stick
            last_player = 1 - turn   # who just moved
            if misere:
                # Last to take LOSES — so last_player loses
                winner = turn
            else:
                winner = last_player
            break

        if turn == 0:
            pile_idx, amount, status = player_turn(piles, "Player 1", hints_on, misere)
            if status == "quit":
                clear()
                print(c("\n  Thanks for playing Nim! 🎋\n", CYAN))
                return False
        else:
            if difficulty == '4':
                pile_idx, amount, status = player_turn(piles, "Player 2", hints_on, misere)
                if status == "quit":
                    clear()
                    print(c("\n  Thanks for playing Nim! 🎋\n", CYAN))
                    return False
            else:
                pile_idx, amount = ai_turn(piles, difficulty, misere)
                status = "ok"
                # Show AI move
                render_board(piles, misere=misere)
                ai_col = PILE_COLORS[pile_idx % len(PILE_COLORS)]
                print(c(f"  🤖 {ai_names[difficulty]} takes {amount} from Pile {pile_idx+1}", RED))
                time.sleep(1.4)

        if status != "ok":
            continue

        history.append((turn, pile_idx, amount, list(piles)))
        piles[pile_idx] -= amount
        last_move = (pile_idx, amount)
        turn = 1 - turn

    # ── Show result ───────────────────────────────────────────────────────────
    elapsed       = int(time.time() - start_time)
    mins, secs    = divmod(elapsed, 60)
    winner_name   = p1_name if winner == 0 else p2_name

    render_board(piles, last_move=last_move, misere=misere)
    if winner == 0:
        print(c("  ╔══════════════════════════════╗", GREEN))
        print(c("  ║   🎉  PLAYER 1 WINS!          ║", GREEN))
        print(c("  ╚══════════════════════════════╝\n", GREEN))
    else:
        print(c("  ╔══════════════════════════════╗", RED))
        print(c(f"  ║   🏆  {ai_names[difficulty].upper()} WINS!        ║", RED))
        print(c("  ╚══════════════════════════════╝\n", RED))

    print(f"  Moves played : {c(str(len(history)), YELLOW)}")
    print(f"  Time elapsed : {c(f'{mins:02d}:{secs:02d}', WHITE)}")
    print(f"  Config       : {c(config_name, MAGENTA)}")
    mode_str = c("Misère", RED) if misere else c("Normal", GREEN)
    print(f"  Mode         : {mode_str}")
    print()
    return True

def main():
    clear()
    print(c("\n  ╔══════════════════════════════════════╗", CYAN))
    print(c("  ║         🎋  N I M  G A M E           ║", CYAN))
    print(c("  ╚══════════════════════════════════════╝\n", CYAN))
    print("  Take turns removing sticks from piles.")
    print(f"  {c('Normal mode:', GREEN)}  Last player to take a stick WINS.")
    print(f"  {c('Misère mode:', RED)}   Last player to take a stick LOSES.")
    print()
    input(c("  Press ENTER to start...", GREY))

    while True:
        play()
        again = input(c("  Play again? (y/n): ", WHITE)).strip().lower()
        if again != 'y':
            print(c("\n  Goodbye! 🎋\n", CYAN))
            break

if __name__ == "__main__":
    main()
