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
BLUE    = "\033[94m"
ORANGE  = "\033[38;5;214m"

COLOR_MAP = {
    "R": (RED,     "R", "Red"),
    "G": (GREEN,   "G", "Green"),
    "B": (BLUE,    "B", "Blue"),
    "Y": (YELLOW,  "Y", "Yellow"),
    "M": (MAGENTA, "M", "Magenta"),
    "C": (CYAN,    "C", "Cyan"),
    "O": (ORANGE,  "O", "Orange"),
    "W": (WHITE,   "W", "White"),
}

def c(text, color):
    return f"{color}{BOLD}{text}{RESET}"

def clear():
    print("\033[2J\033[H", end="")

def colored_code(code):
    return " ".join(c(f"[{ch}]", COLOR_MAP[ch][0]) for ch in code)

def get_feedback(secret, guess):
    exact  = sum(s == g for s, g in zip(secret, guess))
    total  = sum(min(secret.count(col), guess.count(col)) for col in set(secret))
    misplaced = total - exact
    return exact, misplaced

def print_history(history, code_len):
    if not history:
        return
    print(c("  ┌─ Guess History ─────────────────────────────┐", CYAN))
    for i, (guess, exact, misplaced) in enumerate(history, 1):
        bulls  = c("●" * exact,             GREEN)  + c("●" * (code_len - exact),    GREY)
        cows   = c("○" * misplaced,          YELLOW) + c("○" * (code_len - misplaced), GREY)
        row    = colored_code(guess)
        print(f"  │ {str(i).rjust(2)}.  {row}   {bulls}  {cows} │")
    print(c("  └──────────────────────────────────────────────┘", CYAN))
    print()

def choose_difficulty():
    clear()
    print(c("\n  ╔══════════════════════════════════╗", CYAN))
    print(c("  ║     C R A C K E R  G A M E      ║", CYAN))
    print(c("  ║       (Code Breaker / Mastermind)║", CYAN))
    print(c("  ╚══════════════════════════════════╝\n", CYAN))
    print(c("  Choose Difficulty:\n", WHITE))
    print(f"  {c('1', YELLOW)}. {c('Easy',   GREEN)}   — 4 colors, 6 colors pool, 10 guesses")
    print(f"  {c('2', YELLOW)}. {c('Medium', YELLOW)}  — 4 colors, 8 colors pool,  8 guesses")
    print(f"  {c('3', YELLOW)}. {c('Hard',   RED)}    — 5 colors, 8 colors pool,  7 guesses")
    print(f"  {c('4', YELLOW)}. {c('Expert', MAGENTA)} — 6 colors, 8 colors pool,  6 guesses")
    print()
    while True:
        ch = input("  Enter choice (1-4): ").strip()
        if ch == "1": return 4, list("RGBYMC"),    10, "Easy"
        if ch == "2": return 4, list("RGBYMCOW"),   8, "Medium"
        if ch == "3": return 5, list("RGBYMCOW"),   7, "Hard"
        if ch == "4": return 6, list("RGBYMCOW"),   6, "Expert"
        print(c("  Invalid choice.", RED))

def print_legend(pool):
    print(c("  Color Pool:", CYAN))
    row = "  " + "  ".join(c(f"[{ch}] {COLOR_MAP[ch][2]}", COLOR_MAP[ch][0]) for ch in pool)
    print(row)
    print()

def play():
    code_len, pool, max_guesses, diff_name = choose_difficulty()
    secret    = [random.choice(pool) for _ in range(code_len)]
    history   = []
    start     = time.time()

    while True:
        clear()
        print(c(f"\n  CRACKER — {diff_name} Mode  |  Code length: {code_len}  |  Guesses left: {max_guesses - len(history)}", CYAN))
        print()
        print_legend(pool)

        if history:
            print_history(history, code_len)

        print(c("  Feedback key:", GREY))
        print(f"  {c('●', GREEN)} = Right color, right position (Bull)")
        print(f"  {c('○', YELLOW)} = Right color, wrong position (Cow)")
        print()

        # Input
        print(c(f"  Enter your guess ({code_len} letters, e.g. {''.join(pool[:code_len])}):", WHITE))
        print(c("  Type  hint  for a hint  |  quit  to exit\n", GREY))
        raw = input("  > ").strip().upper()

        if raw == "QUIT":
            print(c(f"\n  The secret was: {colored_code(secret)}\n", YELLOW))
            return False, 0

        if raw == "HINT":
            pos   = random.randint(0, code_len - 1)
            print(c(f"\n  Hint: Position {pos+1} is {COLOR_MAP[secret[pos]][2]}!", MAGENTA))
            time.sleep(2)
            continue

        # Validate
        if len(raw) != code_len or not all(ch in pool for ch in raw):
            valid = " ".join(pool)
            print(c(f"\n  Invalid! Enter exactly {code_len} letters from: {valid}", RED))
            time.sleep(1.5)
            continue

        guess            = list(raw)
        exact, misplaced = get_feedback(secret, guess)
        history.append((guess, exact, misplaced))

        # Win
        if exact == code_len:
            clear()
            elapsed = int(time.time() - start)
            print(c("\n  ╔══════════════════════════════════╗", GREEN))
            print(c("  ║       🎉  YOU CRACKED IT!        ║", GREEN))
            print(c("  ╚══════════════════════════════════╝\n", GREEN))
            print(f"  Secret code : {colored_code(secret)}")
            print(f"  Guesses used: {c(str(len(history)), YELLOW)} / {max_guesses}")
            print(f"  Time taken  : {c(str(elapsed)+'s', CYAN)}")
            print()
            guesses_used = len(history)
            if guesses_used <= 2:
                rating = c("🏆 Legendary!", YELLOW)
            elif guesses_used <= 4:
                rating = c("🥇 Excellent",  GREEN)
            elif guesses_used <= 6:
                rating = c("🥈 Good",       CYAN)
            else:
                rating = c("🥉 Keep going", WHITE)
            print(f"  Rating      : {rating}")
            print()
            return True, len(history)

        # Lose
        if len(history) >= max_guesses:
            clear()
            print(c("\n  ╔══════════════════════════════════╗", RED))
            print(c("  ║        ❌  GAME OVER!             ║", RED))
            print(c("  ╚══════════════════════════════════╝\n", RED))
            print_history(history, code_len)
            print(f"  The secret was: {colored_code(secret)}")
            print()
            return False, len(history)

def main():
    wins = losses = 0
    while True:
        won, guesses = play()
        if won:
            wins += 1
        else:
            losses += 1

        print(c(f"  Session: {wins}W / {losses}L", CYAN))
        again = input("  Play again? (y/n): ").strip().lower()
        if again != "y":
            print(c("\n  Thanks for playing Cracker!\n", CYAN))
            break

if __name__ == "__main__":
    main()
