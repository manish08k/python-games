import random
import string
import time

RESET  = "\033[0m"
BOLD   = "\033[1m"
CYAN   = "\033[96m"
YELLOW = "\033[93m"
GREEN  = "\033[92m"
RED    = "\033[91m"
GREY   = "\033[90m"
WHITE  = "\033[97m"
MAGENTA= "\033[95m"

def c(text, color):
    return f"{color}{BOLD}{text}{RESET}"

QUOTES = [
    ("The only way to do great work is to love what you do.", "Steve Jobs"),
    ("In the middle of every difficulty lies opportunity.", "Albert Einstein"),
    ("It does not matter how slowly you go as long as you do not stop.", "Confucius"),
    ("Life is what happens when you are busy making other plans.", "John Lennon"),
    ("The future belongs to those who believe in the beauty of their dreams.", "Eleanor Roosevelt"),
    ("Spread love everywhere you go. Let no one ever come to you without leaving happier.", "Mother Teresa"),
    ("When you reach the end of your rope, tie a knot in it and hang on.", "Franklin D. Roosevelt"),
    ("Always remember that you are absolutely unique. Just like everyone else.", "Margaret Mead"),
    ("Do not go where the path may lead, go instead where there is no path and leave a trail.", "Ralph Waldo Emerson"),
    ("You will face many defeats in life, but never let yourself be defeated.", "Maya Angelou"),
    ("The greatest glory in living lies not in never falling, but in rising every time we fall.", "Nelson Mandela"),
    ("In the end, it is not the years in your life that count. It is the life in your years.", "Abraham Lincoln"),
    ("Never let the fear of striking out keep you from playing the game.", "Babe Ruth"),
    ("Life is either a daring adventure or nothing at all.", "Helen Keller"),
    ("Many of life's failures are people who did not realize how close they were to success when they gave up.", "Thomas Edison"),
]

def make_cipher():
    letters = list(string.ascii_uppercase)
    shuffled = letters[:]
    while True:
        random.shuffle(shuffled)
        if all(shuffled[i] != letters[i] for i in range(26)):
            break
    return dict(zip(letters, shuffled))

def encode(text, cipher):
    result = []
    for ch in text.upper():
        if ch.isalpha():
            result.append(cipher[ch])
        else:
            result.append(ch)
    return "".join(result)

def clear():
    print("\033[2J\033[H", end="")

def display_board(encoded, solved_map, original, hint_set, mistakes, max_mistakes):
    print(c("╔══════════════════════════════════════════════════╗", CYAN))
    print(c("║              C R Y P T O G R A M                ║", CYAN))
    print(c("╚══════════════════════════════════════════════════╝", CYAN))
    print()

    # Mistakes
    hearts = (c("♥ ", GREEN) * (max_mistakes - mistakes)) + (c("♥ ", RED) * mistakes)
    print(f"  Mistakes: {hearts}  ({mistakes}/{max_mistakes})")
    print(f"  Hints used: {c(str(len(hint_set)), YELLOW)}")
    print()

    # Encoded puzzle line (cipher letters)
    enc_line  = ""
    dec_line  = ""
    for ch in encoded:
        if ch.isalpha():
            enc_line += c(f" {ch} ", YELLOW)
            decoded = solved_map.get(ch, " ")
            if decoded != " ":
                dec_line += c(f" {decoded} ", GREEN)
            else:
                dec_line += c(f" _ ", GREY)
        else:
            enc_line += f" {ch} "
            dec_line += f" {ch} "

    # Word-wrap at ~60 chars worth of tokens
    words_enc = encoded.split()
    words_orig = original.upper().split()

    print(c("  Cipher text:", CYAN))
    line_e, line_d, width = "", "", 0
    for we, wo in zip(words_enc, words_orig):
        seg_e = " ".join(c(f"{ch}", YELLOW) if ch.isalpha() else ch for ch in we) + "  "
        seg_d = ""
        for ch in we:
            if ch.isalpha():
                decoded = solved_map.get(ch, "_")
                col = GREEN if decoded != "_" else GREY
                seg_d += c(decoded, col)
            else:
                seg_d += ch
        seg_d += "  "

        if width + len(we) + 1 > 45:
            print("  " + line_e)
            print("  " + line_d)
            print()
            line_e, line_d, width = "", "", 0

        line_e += " ".join(c(ch, YELLOW) if ch.isalpha() else ch for ch in we) + "  "
        for ch in we:
            if ch.isalpha():
                decoded = solved_map.get(ch, "_")
                col = GREEN if decoded != "_" else GREY
                line_d += c(decoded, col)
            else:
                line_d += ch
        line_d += "  "
        width += len(we) + 1

    if line_e:
        print("  " + line_e)
        print("  " + line_d)

    print()
    # Alphabet reference
    print(c("  Cipher → Your guess:", CYAN))
    row = ""
    for cipher_letter in sorted(set(ch for ch in encoded if ch.isalpha())):
        guess = solved_map.get(cipher_letter, "_")
        col   = GREEN if guess != "_" else GREY
        row  += f"  {c(cipher_letter, YELLOW)}={c(guess, col)}"
    print(row)
    print()

def get_hint(encoded, solved_map, reverse_cipher):
    unsolved = [ch for ch in set(encoded) if ch.isalpha() and ch not in solved_map]
    if not unsolved:
        return None, None
    ch = random.choice(unsolved)
    return ch, reverse_cipher[ch]

def play():
    quote, author = random.choice(QUOTES)
    cipher        = make_cipher()
    reverse       = {v: k for k, v in cipher.items()}
    encoded       = encode(quote, cipher)
    solved_map    = {}   # cipher_letter -> plain_letter
    hint_set      = set()
    mistakes      = 0
    max_mistakes  = 6
    start_time    = time.time()

    while True:
        clear()
        display_board(encoded, solved_map, quote, hint_set, mistakes, max_mistakes)

        # Check win
        all_solved = all(
            solved_map.get(ch) == reverse[ch]
            for ch in set(encoded) if ch.isalpha()
        )
        if all_solved:
            elapsed = int(time.time() - start_time)
            print(c("  ✅  SOLVED!", GREEN))
            print(f"  Quote by: {c(author, MAGENTA)}")
            print(f"  Time: {c(str(elapsed)+'s', YELLOW)}  |  Mistakes: {c(str(mistakes), RED)}  |  Hints: {c(str(len(hint_set)), YELLOW)}")
            print()
            return True

        if mistakes >= max_mistakes:
            print(c("  ❌  GAME OVER!", RED))
            print(f"  The answer was: {c(quote, GREEN)}")
            print(f"  — {c(author, MAGENTA)}")
            print()
            return False

        print(c("  Commands:", CYAN))
        print("   <cipher>=<plain>   e.g.  X=A  to map cipher X → plain A")
        print("   hint               reveal a random letter")
        print("   reset              clear all your guesses")
        print("   quit               exit game")
        print()

        cmd = input("  > ").strip().upper()

        if cmd == "QUIT":
            print(c("\n  Thanks for playing!\n", CYAN))
            exit()

        elif cmd == "RESET":
            solved_map.clear()
            hint_set.clear()

        elif cmd == "HINT":
            ch, plain = get_hint(encoded, solved_map, reverse)
            if ch:
                solved_map[ch] = plain
                hint_set.add(ch)
            else:
                print(c("  All letters already solved!", GREEN))
                time.sleep(1)

        elif "=" in cmd and len(cmd) == 3:
            cipher_ch, plain_ch = cmd[0], cmd[2]
            if cipher_ch.isalpha() and plain_ch.isalpha():
                # remove old mapping if plain_ch was already used
                for k in list(solved_map):
                    if solved_map[k] == plain_ch and k != cipher_ch:
                        del solved_map[k]
                solved_map[cipher_ch] = plain_ch
                # check correctness
                if reverse.get(cipher_ch) != plain_ch and cipher_ch not in hint_set:
                    mistakes += 1
            else:
                print(c("  Use format like:  X=A", RED))
                time.sleep(0.8)
        else:
            print(c("  Invalid command. Use  X=A  format or type  hint / reset / quit", RED))
            time.sleep(0.8)

def main():
    clear()
    print(c("\n  Welcome to CRYPTOGRAM!", CYAN))
    print("  Each letter has been substituted with another.")
    print("  Decode the famous quote by mapping cipher → plain letters.")
    print()
    input("  Press ENTER to start...")

    while True:
        won = play()
        again = input("  Play again? (y/n): ").strip().lower()
        if again != "y":
            print(c("\n  Goodbye!\n", CYAN))
            break
        clear()

if __name__ == "__main__":
    main()
