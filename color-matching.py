import random
import time

COLORS = {
    "RED":     "\033[91m",
    "GREEN":   "\033[92m",
    "YELLOW":  "\033[93m",
    "BLUE":    "\033[94m",
    "MAGENTA": "\033[95m",
    "CYAN":    "\033[96m",
    "WHITE":   "\033[97m",
}
RESET = "\033[0m"
BOLD  = "\033[1m"

def colored(text, color):
    return f"{COLORS.get(color, '')}{BOLD}{text}{RESET}"

def clear():
    print("\033[2J\033[H", end="")

def stroop_round(congruent):
    names = list(COLORS.keys())
    word  = random.choice(names)
    if congruent:
        ink = word
    else:
        ink = random.choice([c for c in names if c != word])
    return word, ink

def play_game():
    clear()
    print(colored("=== COLOR MATCHING GAME ===", "CYAN"))
    print()
    print("You'll see a color  W O R D  printed in colored ink.")
    print()
    print(colored("CONGRUENT  round", "GREEN")  + " → type the  INK COLOR  (what color you SEE)")
    print(colored("INCONGRUENT round", "RED")   + " → type the  WORD       (what it SAYS)")
    print()
    print("Options: " + "  ".join(colored(c, c) for c in COLORS))
    print()
    input("Press ENTER to start...")

    rounds      = 10
    score       = 0
    total_time  = 0
    results     = []

    for i in range(1, rounds + 1):
        congruent = random.choice([True, False])
        word, ink = stroop_round(congruent)

        clear()
        print(colored("=== COLOR MATCHING GAME ===", "CYAN"))
        print(f"\nRound {i}/{rounds}  |  Score: {score}\n")

        if congruent:
            print(colored("Task: type the  INK COLOR", "GREEN"))
        else:
            print(colored("Task: type the  WORD", "RED"))

        print()
        print("   " + colored(word, ink) + "   ")
        print()

        start   = time.time()
        answer  = input("Your answer: ").strip().upper()
        elapsed = (time.time() - start) * 1000

        correct_answer = ink if congruent else word
        correct        = answer == correct_answer

        if correct:
            score      += max(10, int(500 - elapsed // 10))
            total_time += elapsed
            results.append(elapsed)
            print(colored(f"\n✅  Correct!  ({elapsed:.0f} ms)", "GREEN"))
        else:
            print(colored(f"\n❌  Wrong!  Answer was: {correct_answer}", "RED"))

        time.sleep(0.9)

    clear()
    print(colored("=== RESULTS ===", "CYAN"))
    print()
    correct_count = len(results)
    accuracy      = correct_count / rounds * 100
    avg_time      = (sum(results) / correct_count) if results else 0

    print(f"  Rounds played : {rounds}")
    print(f"  Correct       : {correct_count}/{rounds}  ({accuracy:.0f}%)")
    print(f"  Avg resp time : {avg_time:.0f} ms")
    print(f"  Final score   : {colored(str(score), 'YELLOW')}")
    print()

    if accuracy == 100 and avg_time < 800:
        rating = colored("🏆 Stroop Master!", "YELLOW")
    elif accuracy >= 80:
        rating = colored("🧠 Sharp Focus",   "GREEN")
    elif accuracy >= 60:
        rating = colored("⚡ Keep Practicing","CYAN")
    else:
        rating = colored("🌱 Just Starting", "WHITE")

    print(f"  Rating        : {rating}")
    print()

    return input("Play again? (y/n): ").strip().lower() == "y"

def main():
    while True:
        again = play_game()
        if not again:
            print(colored("\nThanks for playing!\n", "CYAN"))
            break

if __name__ == "__main__":
    main()