import os
import time
import random

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

COLORS = {
    'R': ('Red',     '🔴'),
    'G': ('Green',   '🟢'),
    'B': ('Blue',    '🔵'),
    'Y': ('Yellow',  '🟡'),
    'W': ('White',   '⚪'),
    'P': ('Purple',  '🟣'),
    'O': ('Orange',  '🟠'),
    'C': ('Cyan',    '🩵'),
}

def make_secret(length=4, allow_duplicates=True, colors='RGBYWP'):
    pool = list(colors)
    if allow_duplicates:
        return [random.choice(pool) for _ in range(length)]
    else:
        return random.sample(pool, length)

def evaluate_guess(secret, guess):
    exact = sum(s == g for s, g in zip(secret, guess))
    secret_counts = {}
    guess_counts  = {}
    for s, g in zip(secret, guess):
        if s != g:
            secret_counts[s] = secret_counts.get(s, 0) + 1
            guess_counts[g]  = guess_counts.get(g, 0) + 1
    misplaced = sum(min(secret_counts.get(c,0), guess_counts.get(c,0)) for c in guess_counts)
    return exact, misplaced

def color_row(code, length):
    row = ""
    for c in code:
        emoji = COLORS[c][1] if c in COLORS else '⬜'
        row += emoji + " "
    return row.strip()

def peg_display(exact, misplaced, length):
    pegs = '⬛' * exact + '⬜' * misplaced + '  ' * (length - exact - misplaced)
    return pegs

def print_header(length, colors_used, allow_dup, max_guesses, difficulty):
    print("=" * 56)
    print("          🎯  M A S T E R M I N D  🎯")
    print("=" * 56)
    print(f"  Difficulty : {difficulty}")
    print(f"  Code length: {length}   Max guesses: {max_guesses}")
    print(f"  Duplicates : {'Yes' if allow_dup else 'No'}")
    print(f"  Colors     : {' '.join(COLORS[c][1] + c for c in colors_used)}")
    print("=" * 56)

def print_board(history, length):
    print(f"\n  {'#':<4} {'Guess':<{length*3+2}} {'⬛=Exact  ⬜=Misplaced':>22}")
    print("  " + "─" * 50)
    for i, (guess, exact, misplaced) in enumerate(history, 1):
        guess_str  = color_row(guess, length)
        pegs_str   = peg_display(exact, misplaced, length)
        hint_text  = f"{exact} exact, {misplaced} misplaced"
        print(f"  {i:<4} {guess_str:<{length*3+2}}  {pegs_str}  {hint_text}")
    print("  " + "─" * 50)

def print_color_key(colors_used):
    print("\n  Color key:")
    for c in colors_used:
        name, emoji = COLORS[c]
        print(f"   {c} = {emoji} {name}")

def get_guess(length, colors_used, history, max_guesses):
    guesses_left = max_guesses - len(history)
    print(f"\n  Guesses left: {guesses_left}")
    print(f"  Enter {length} color codes (e.g. {''.join(colors_used[:length])})")
    print("  H = Hint  |  Q = Quit  |  N = New Game")
    raw = input("  Your guess: ").strip().upper()
    return raw

def hint_filter(secret_len, colors_used, history, allow_dup):
    pool = list(colors_used)
    if allow_dup:
        candidates = []
        def gen(curr):
            if len(curr) == secret_len:
                candidates.append(curr[:])
                return
            for c in pool:
                curr.append(c)
                gen(curr)
                curr.pop()
        gen([])
    else:
        from itertools import permutations
        candidates = [list(p) for p in permutations(pool, secret_len)]

    for guess, exact, misplaced in history:
        candidates = [c for c in candidates if evaluate_guess(c, guess) == (exact, misplaced)]

    if candidates:
        suggestion = random.choice(candidates)
        return ''.join(suggestion), len(candidates)
    return None, 0

def show_scores(scores):
    print("\n  🏆 Score Board:")
    print("  " + "─" * 30)
    if not scores:
        print("  No games played yet.")
    else:
        for diff, games in scores.items():
            wins  = [g for g in games if g['won']]
            total = len(games)
            avg   = sum(g['guesses'] for g in wins) / len(wins) if wins else 0
            print(f"  {diff:<12}: {len(wins)}/{total} wins | Avg guesses: {avg:.1f}")
    print("  " + "─" * 30)

def play(difficulty, scores):
    settings = {
        'Easy':   {'length': 4, 'colors': 'RGBYWP', 'max': 12, 'dup': True},
        'Medium': {'length': 4, 'colors': 'RGBYWP', 'max': 10, 'dup': False},
        'Hard':   {'length': 5, 'colors': 'RGBYWPC', 'max': 8,  'dup': False},
        'Expert': {'length': 6, 'colors': 'RGBYWPOC', 'max': 8, 'dup': True},
    }
    s          = settings[difficulty]
    length     = s['length']
    colors     = s['colors']
    max_g      = s['max']
    allow_dup  = s['dup']

    secret  = make_secret(length, allow_dup, colors)
    history = []
    won     = False

    while len(history) < max_g:
        clear()
        print_header(length, colors, allow_dup, max_g, difficulty)
        print_board(history, length)
        print_color_key(colors)

        raw = get_guess(length, colors, history, max_g)

        if raw == 'Q':
            print(f"\n  Secret was: {color_row(secret, length)}")
            time.sleep(2)
            return

        if raw == 'N':
            return

        if raw == 'H':
            suggestion, remaining = hint_filter(length, colors, history, allow_dup)
            if suggestion:
                print(f"\n  💡 Hint: Try {color_row(list(suggestion), length)}  ({suggestion})")
                print(f"     ({remaining} possible codes remain)")
            else:
                print("  💡 No hint available.")
            input("  Press Enter to continue...")
            continue

        if len(raw) != length:
            print(f"  ❌ Enter exactly {length} letters.")
            time.sleep(1)
            continue

        invalid = [c for c in raw if c not in colors]
        if invalid:
            print(f"  ❌ Invalid color(s): {' '.join(invalid)}")
            time.sleep(1)
            continue

        if not allow_dup and len(set(raw)) != len(raw):
            print("  ❌ Duplicates not allowed in this mode!")
            time.sleep(1)
            continue

        guess = list(raw)
        exact, misplaced = evaluate_guess(secret, guess)
        history.append((guess, exact, misplaced))

        if exact == length:
            won = True
            break

    clear()
    print_header(length, colors, allow_dup, max_g, difficulty)
    print_board(history, length)

    if won:
        print(f"\n  🎉 YOU CRACKED THE CODE in {len(history)} guesses!")
        print(f"  Secret: {color_row(secret, length)}")
        if len(history) <= 4:
            print("  ⭐ OUTSTANDING!")
        elif len(history) <= 6:
            print("  👍 Well done!")
        else:
            print("  😅 Got there eventually!")
    else:
        print(f"\n  💀 GAME OVER! The secret was:")
        print(f"  {color_row(secret, length)}  ({' '.join(secret)})")

    if difficulty not in scores:
        scores[difficulty] = []
    scores[difficulty].append({'won': won, 'guesses': len(history)})

    input("\n  Press Enter to continue...")

def main():
    scores = {}
    while True:
        clear()
        print("=" * 50)
        print("       🎯  M A S T E R M I N D  🎯")
        print("=" * 50)
        print("""
  How to play:
  • Guess the secret color code
  • ⬛ = right color, right position
  • ⬜ = right color, wrong position
  • Use the clues to narrow it down!
""")
        print("  Difficulty:")
        print("   1. Easy   (4 colors, 6 choices, duplicates, 12 guesses)")
        print("   2. Medium (4 colors, 6 choices, no duplicates, 10 guesses)")
        print("   3. Hard   (5 colors, 7 choices, no duplicates, 8 guesses)")
        print("   4. Expert (6 colors, 8 choices, duplicates, 8 guesses)")
        print("   S. Scores")
        print("   Q. Quit")
        print()

        choice = input("  Choose: ").strip().upper()

        if choice == '1':
            play('Easy', scores)
        elif choice == '2':
            play('Medium', scores)
        elif choice == '3':
            play('Hard', scores)
        elif choice == '4':
            play('Expert', scores)
        elif choice == 'S':
            clear()
            show_scores(scores)
            input("\n  Press Enter to continue...")
        elif choice == 'Q':
            print("\n  Thanks for playing Mastermind! 👋")
            break
        else:
            print("  Invalid choice.")
            time.sleep(0.5)

if __name__ == "__main__":
    main()