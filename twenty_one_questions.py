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

def c(text, color):
    return f"{color}{BOLD}{text}{RESET}"

def clear():
    print("\033[2J\033[H", end="")

# ── Knowledge Base ────────────────────────────────────────────────────────────

THINGS = [
    # Animals
    {"name": "Elephant",    "category": "animal",  "living": True,  "animal": True,  "mammal": True,  "big": True,  "domestic": False, "flies": False, "water": False, "has_legs": True,  "has_wings": False, "carnivore": False, "found_in_wild": True,  "nocturnal": False, "has_tail": True},
    {"name": "Eagle",       "category": "animal",  "living": True,  "animal": True,  "mammal": False, "big": False, "domestic": False, "flies": True,  "water": False, "has_legs": True,  "has_wings": True,  "carnivore": True,  "found_in_wild": True,  "nocturnal": False, "has_tail": True},
    {"name": "Shark",       "category": "animal",  "living": True,  "animal": True,  "mammal": False, "big": True,  "domestic": False, "flies": False, "water": True,  "has_legs": False, "has_wings": False, "carnivore": True,  "found_in_wild": True,  "nocturnal": False, "has_tail": True},
    {"name": "Dog",         "category": "animal",  "living": True,  "animal": True,  "mammal": True,  "big": False, "domestic": True,  "flies": False, "water": False, "has_legs": True,  "has_wings": False, "carnivore": True,  "found_in_wild": False, "nocturnal": False, "has_tail": True},
    {"name": "Cat",         "category": "animal",  "living": True,  "animal": True,  "mammal": True,  "big": False, "domestic": True,  "flies": False, "water": False, "has_legs": True,  "has_wings": False, "carnivore": True,  "found_in_wild": False, "nocturnal": True,  "has_tail": True},
    {"name": "Butterfly",   "category": "animal",  "living": True,  "animal": True,  "mammal": False, "big": False, "domestic": False, "flies": True,  "water": False, "has_legs": True,  "has_wings": True,  "carnivore": False, "found_in_wild": True,  "nocturnal": False, "has_tail": False},
    {"name": "Dolphin",     "category": "animal",  "living": True,  "animal": True,  "mammal": True,  "big": True,  "domestic": False, "flies": False, "water": True,  "has_legs": False, "has_wings": False, "carnivore": True,  "found_in_wild": True,  "nocturnal": False, "has_tail": True},
    {"name": "Owl",         "category": "animal",  "living": True,  "animal": True,  "mammal": False, "big": False, "domestic": False, "flies": True,  "water": False, "has_legs": True,  "has_wings": True,  "carnivore": True,  "found_in_wild": True,  "nocturnal": True,  "has_tail": True},
    {"name": "Horse",       "category": "animal",  "living": True,  "animal": True,  "mammal": True,  "big": True,  "domestic": True,  "flies": False, "water": False, "has_legs": True,  "has_wings": False, "carnivore": False, "found_in_wild": True,  "nocturnal": False, "has_tail": True},
    {"name": "Penguin",     "category": "animal",  "living": True,  "animal": True,  "mammal": False, "big": False, "domestic": False, "flies": False, "water": True,  "has_legs": True,  "has_wings": True,  "carnivore": True,  "found_in_wild": True,  "nocturnal": False, "has_tail": False},
    {"name": "Tiger",       "category": "animal",  "living": True,  "animal": True,  "mammal": True,  "big": True,  "domestic": False, "flies": False, "water": False, "has_legs": True,  "has_wings": False, "carnivore": True,  "found_in_wild": True,  "nocturnal": True,  "has_tail": True},
    {"name": "Crocodile",   "category": "animal",  "living": True,  "animal": True,  "mammal": False, "big": True,  "domestic": False, "flies": False, "water": True,  "has_legs": True,  "has_wings": False, "carnivore": True,  "found_in_wild": True,  "nocturnal": False, "has_tail": True},
    # Objects
    {"name": "Car",         "category": "vehicle", "living": False, "animal": False, "mammal": False, "big": True,  "domestic": False, "flies": False, "water": False, "has_legs": False, "has_wings": False, "carnivore": False, "found_in_wild": False, "nocturnal": False, "has_tail": False},
    {"name": "Airplane",    "category": "vehicle", "living": False, "animal": False, "mammal": False, "big": True,  "domestic": False, "flies": True,  "water": False, "has_legs": False, "has_wings": True,  "carnivore": False, "found_in_wild": False, "nocturnal": False, "has_tail": True},
    {"name": "Bicycle",     "category": "vehicle", "living": False, "animal": False, "mammal": False, "big": False, "domestic": False, "flies": False, "water": False, "has_legs": False, "has_wings": False, "carnivore": False, "found_in_wild": False, "nocturnal": False, "has_tail": False},
    {"name": "Submarine",   "category": "vehicle", "living": False, "animal": False, "mammal": False, "big": True,  "domestic": False, "flies": False, "water": True,  "has_legs": False, "has_wings": False, "carnivore": False, "found_in_wild": False, "nocturnal": False, "has_tail": False},
    # Fruits
    {"name": "Apple",       "category": "fruit",   "living": False, "animal": False, "mammal": False, "big": False, "domestic": False, "flies": False, "water": False, "has_legs": False, "has_wings": False, "carnivore": False, "found_in_wild": True,  "nocturnal": False, "has_tail": False},
    {"name": "Watermelon",  "category": "fruit",   "living": False, "animal": False, "mammal": False, "big": True,  "domestic": False, "flies": False, "water": False, "has_legs": False, "has_wings": False, "carnivore": False, "found_in_wild": True,  "nocturnal": False, "has_tail": False},
    {"name": "Banana",      "category": "fruit",   "living": False, "animal": False, "mammal": False, "big": False, "domestic": False, "flies": False, "water": False, "has_legs": False, "has_wings": False, "carnivore": False, "found_in_wild": True,  "nocturnal": False, "has_tail": False},
    # Household
    {"name": "Refrigerator","category": "appliance","living": False,"animal": False, "mammal": False, "big": True,  "domestic": True,  "flies": False, "water": False, "has_legs": False, "has_wings": False, "carnivore": False, "found_in_wild": False, "nocturnal": False, "has_tail": False},
    {"name": "Telephone",   "category": "appliance","living": False,"animal": False, "mammal": False, "big": False, "domestic": True,  "flies": False, "water": False, "has_legs": False, "has_wings": False, "carnivore": False, "found_in_wild": False, "nocturnal": False, "has_tail": False},
    {"name": "Umbrella",    "category": "object",  "living": False, "animal": False, "mammal": False, "big": False, "domestic": True,  "flies": False, "water": False, "has_legs": False, "has_wings": False, "carnivore": False, "found_in_wild": False, "nocturnal": False, "has_tail": False},
    {"name": "Book",        "category": "object",  "living": False, "animal": False, "mammal": False, "big": False, "domestic": True,  "flies": False, "water": False, "has_legs": False, "has_wings": False, "carnivore": False, "found_in_wild": False, "nocturnal": False, "has_tail": False},
    {"name": "Guitar",      "category": "object",  "living": False, "animal": False, "mammal": False, "big": False, "domestic": True,  "flies": False, "water": False, "has_legs": False, "has_wings": False, "carnivore": False, "found_in_wild": False, "nocturnal": False, "has_tail": False},
    {"name": "Clock",       "category": "object",  "living": False, "animal": False, "mammal": False, "big": False, "domestic": True,  "flies": False, "water": False, "has_legs": False, "has_wings": False, "carnivore": False, "found_in_wild": False, "nocturnal": False, "has_tail": False},
    {"name": "Mirror",      "category": "object",  "living": False, "animal": False, "mammal": False, "big": False, "domestic": True,  "flies": False, "water": False, "has_legs": False, "has_wings": False, "carnivore": False, "found_in_wild": False, "nocturnal": False, "has_tail": False},
    {"name": "Candle",      "category": "object",  "living": False, "animal": False, "mammal": False, "big": False, "domestic": True,  "flies": False, "water": False, "has_legs": False, "has_wings": False, "carnivore": False, "found_in_wild": False, "nocturnal": False, "has_tail": False},
]

QUESTIONS = [
    ("Is it a living thing?",           "living"),
    ("Is it an animal?",                "animal"),
    ("Is it a mammal?",                 "mammal"),
    ("Is it bigger than a microwave?",  "big"),
    ("Can it fly?",                     "flies"),
    ("Does it live in water?",          "water"),
    ("Is it a domestic / pet animal?",  "domestic"),
    ("Does it have legs?",              "has_legs"),
    ("Does it have wings?",             "has_wings"),
    ("Is it a carnivore?",              "carnivore"),
    ("Is it found in the wild?",        "found_in_wild"),
    ("Is it nocturnal?",                "nocturnal"),
    ("Does it have a tail?",            "has_tail"),
]

# ── Computer guesses the player's thing ──────────────────────────────────────

def computer_guesses():
    clear()
    print(c("\n  ╔══════════════════════════════════════╗", CYAN))
    print(c("  ║   🤖  COMPUTER WILL GUESS YOUR THING  ║", CYAN))
    print(c("  ╚══════════════════════════════════════╝\n", CYAN))
    print("  Think of any thing from the list below (or anything similar):")
    categories = {}
    for t in THINGS:
        categories.setdefault(t["category"], []).append(t["name"])
    for cat, items in categories.items():
        print(f"  {c(cat.capitalize()+':', YELLOW)} {', '.join(items)}")
    print()
    input(c("  Got it? Press ENTER when ready...\n", GREY))

    candidates   = list(THINGS)
    asked        = []
    max_q        = 21

    for q_num in range(1, max_q + 1):
        if len(candidates) == 1:
            break

        # Pick the most discriminating question not yet asked
        best_q, best_key, best_score = None, None, -1
        for q_text, q_key in QUESTIONS:
            if q_key in asked:
                continue
            yes_count = sum(1 for t in candidates if t.get(q_key))
            no_count  = len(candidates) - yes_count
            score     = min(yes_count, no_count)
            if score > best_score:
                best_score = score
                best_q     = q_text
                best_key   = q_key

        if not best_q:
            break

        asked.append(best_key)

        clear()
        print(c(f"\n  Question {q_num} of {max_q}  |  {len(candidates)} possibilities left\n", CYAN))
        print(f"  {c('Q:', YELLOW)} {best_q}")
        print()

        while True:
            ans = input(c("  Your answer (yes / no / maybe): ", WHITE)).strip().lower()
            if ans in ("yes", "y"):
                candidates = [t for t in candidates if t.get(best_key)]
                break
            elif ans in ("no", "n"):
                candidates = [t for t in candidates if not t.get(best_key)]
                break
            elif ans in ("maybe", "m", "sometimes"):
                break  # don't filter
            else:
                print(c("  Please answer yes, no, or maybe.", RED))

        if not candidates:
            print(c("\n  Hmm, I've run out of candidates. You stumped me! 🤔\n", RED))
            return

    # Final guess
    clear()
    guess = candidates[0] if candidates else None
    print(c("\n  ╔══════════════════════════════════╗", MAGENTA))
    print(c("  ║       🤔  MY FINAL GUESS          ║", MAGENTA))
    print(c("  ╚══════════════════════════════════╝\n", MAGENTA))

    if guess:
        print(f"  I think you are thinking of...")
        time.sleep(1)
        print(f"\n  {c('👉  ' + guess['name'].upper(), YELLOW)}\n")
    else:
        print(c("  I couldn't figure it out. You win! 🎉\n", GREEN))
        return

    result = input(c("  Was I right? (yes / no): ", WHITE)).strip().lower()
    if result in ("yes", "y"):
        print(c("\n  🎉  Got it! I win this round!\n", GREEN))
    else:
        print(c("\n  😮  You stumped me! Well played!\n", RED))

# ── Player guesses computer's thing ──────────────────────────────────────────

def player_guesses():
    clear()
    secret = random.choice(THINGS)
    print(c("\n  ╔══════════════════════════════════════╗", CYAN))
    print(c("  ║   🧠  YOU WILL GUESS MY THING         ║", CYAN))
    print(c("  ╚══════════════════════════════════════╝\n", CYAN))
    print("  I've thought of something. Ask me up to 21 yes/no questions!")
    print(c("  Type your question or guess the answer with:  guess: <answer>\n", GREY))
    input(c("  Press ENTER to start...\n", GREY))

    q_count  = 0
    max_q    = 21
    history  = []

    while q_count < max_q:
        clear()
        print(c(f"\n  Questions asked: {q_count}/{max_q}\n", CYAN))

        if history:
            print(c("  ── History ───────────────────────────────", GREY))
            for i, (q, a) in enumerate(history[-6:], 1):
                col = GREEN if a == "Yes" else RED if a == "No" else YELLOW
                print(f"  {c(str(i+max(0,len(history)-6))+'.', GREY)} {q}  →  {c(a, col)}")
            print()

        user_input = input(c("  Your question (or 'guess: <answer>'): ", WHITE)).strip()

        if not user_input:
            continue

        # Player makes a final guess
        if user_input.lower().startswith("guess:"):
            guess_word = user_input[6:].strip().lower()
            if guess_word == secret["name"].lower():
                print(c(f"\n  ✅  Correct! It was {secret['name']}! You win! 🎉\n", GREEN))
            else:
                print(c(f"\n  ❌  Wrong! It was {c(secret['name'], YELLOW)}{RED}. Better luck next time!\n", RED))
            return

        q_count += 1

        # Check against known questions
        answer = "I'm not sure"
        q_lower = user_input.lower()

        for q_text, q_key in QUESTIONS:
            keywords = q_text.lower().replace("?", "").split()
            matches  = sum(1 for kw in keywords if kw in q_lower and len(kw) > 3)
            if matches >= 2:
                answer = "Yes" if secret.get(q_key) else "No"
                break
        else:
            # Keyword fallback
            if any(w in q_lower for w in ["animal", "creature", "beast"]):
                answer = "Yes" if secret.get("animal") else "No"
            elif any(w in q_lower for w in ["fly", "flies", "air"]):
                answer = "Yes" if secret.get("flies") else "No"
            elif any(w in q_lower for w in ["water", "swim", "ocean", "sea"]):
                answer = "Yes" if secret.get("water") else "No"
            elif any(w in q_lower for w in ["big", "large", "huge", "giant"]):
                answer = "Yes" if secret.get("big") else "No"
            elif any(w in q_lower for w in ["living", "alive", "life"]):
                answer = "Yes" if secret.get("living") else "No"
            elif any(w in q_lower for w in ["mammal"]):
                answer = "Yes" if secret.get("mammal") else "No"
            elif any(w in q_lower for w in ["wing", "wings"]):
                answer = "Yes" if secret.get("has_wings") else "No"
            elif any(w in q_lower for w in ["leg", "legs"]):
                answer = "Yes" if secret.get("has_legs") else "No"
            elif any(w in q_lower for w in ["tail"]):
                answer = "Yes" if secret.get("has_tail") else "No"
            elif any(w in q_lower for w in ["night", "nocturnal"]):
                answer = "Yes" if secret.get("nocturnal") else "No"
            elif any(w in q_lower for w in ["wild", "jungle", "forest"]):
                answer = "Yes" if secret.get("found_in_wild") else "No"
            elif any(w in q_lower for w in ["meat", "carnivore", "hunt"]):
                answer = "Yes" if secret.get("carnivore") else "No"
            elif any(w in q_lower for w in ["pet", "domestic", "home"]):
                answer = "Yes" if secret.get("domestic") else "No"
            else:
                answer = random.choice(["Yes", "No", "Sometimes"])

        col = GREEN if answer == "Yes" else RED if answer == "No" else YELLOW
        print(f"\n  {c('Answer:', CYAN)} {c(answer, col)}\n")
        history.append((user_input, answer))
        time.sleep(0.5)

    # Out of questions
    clear()
    print(c(f"\n  ⏰  Out of questions! The answer was: {c(secret['name'], YELLOW)}\n", RED))

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    while True:
        clear()
        print(c("\n  ╔══════════════════════════════════════╗", CYAN))
        print(c("  ║     2 1   Q U E S T I O N S           ║", CYAN))
        print(c("  ╚══════════════════════════════════════╝\n", CYAN))
        print(f"  {c('1', YELLOW)}. 🤖 Computer guesses YOUR thing")
        print(f"  {c('2', YELLOW)}. 🧠 YOU guess the Computer's thing")
        print(f"  {c('3', YELLOW)}. ❌ Quit")
        print()

        ch = input("  Choose (1/2/3): ").strip()

        if ch == "1":
            computer_guesses()
        elif ch == "2":
            player_guesses()
        elif ch == "3":
            print(c("\n  Thanks for playing 21 Questions!\n", CYAN))
            break
        else:
            print(c("  Invalid choice.", RED))
            time.sleep(0.8)
            continue

        print()
        again = input(c("  Play again? (y/n): ", WHITE)).strip().lower()
        if again != "y":
            print(c("\n  Goodbye! 👋\n", CYAN))
            break

if __name__ == "__main__":
    main()
