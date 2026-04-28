import itertools

def load_words():
    try:
        with open("/usr/share/dict/words", "r") as f:
            return set(w.strip().lower() for w in f if w.strip().isalpha())
    except FileNotFoundError:
        # fallback mini dictionary
        return {
            "eat", "ate", "tea", "eta", "tae",
            "listen", "silent", "enlist", "tinsel", "inlets",
            "race", "care", "acre", "acer",
            "post", "stop", "tops", "pots", "spot", "opts",
            "night", "thing",
            "dusty", "study",
            "cat", "act",
            "dog", "god",
            "evil", "vile", "live", "veil",
            "rat", "tar", "art",
            "name", "mane", "amen", "mean",
            "parts", "strap", "traps", "tarps",
            "below", "elbow",
            "state", "taste", "tates",
            "notes", "stone", "tones", "snote",
            "time", "emit", "mite", "item",
            "sauce", "cause",
            "least", "slate", "stale", "tales", "steal", "tesla",
        }

def get_anagrams(word, dictionary):
    word = word.lower().strip()
    sorted_word = sorted(word)
    anagrams = set()
    for perm in itertools.permutations(word):
        candidate = "".join(perm)
        if candidate != word and candidate in dictionary:
            anagrams.add(candidate)
    return sorted(anagrams)

def get_sub_anagrams(word, dictionary, min_len=3):
    word = word.lower().strip()
    found = set()
    for length in range(min_len, len(word)):
        for combo in itertools.combinations(word, length):
            for perm in itertools.permutations(combo):
                candidate = "".join(perm)
                if candidate in dictionary:
                    found.add(candidate)
    return sorted(found, key=lambda x: (-len(x), x))

def print_banner():
    print("\033[96m\033[1m")
    print("╔══════════════════════════════╗")
    print("║      ANAGRAM  SOLVER         ║")
    print("╚══════════════════════════════╝")
    print("\033[0m")

def main():
    print_banner()
    print("Loading dictionary...", end=" ", flush=True)
    dictionary = load_words()
    print(f"\033[92mdone ({len(dictionary):,} words)\033[0m\n")

    while True:
        print("\033[1mOptions:\033[0m")
        print("  1. Full anagrams (same length)")
        print("  2. Sub-anagrams (shorter words too)")
        print("  3. Quit")
        print()

        choice = input("Choose (1/2/3): ").strip()

        if choice == "3":
            print("\n\033[96mThanks for using Anagram Solver!\033[0m\n")
            break

        if choice not in ("1", "2"):
            print("\033[91mInvalid choice.\033[0m\n")
            continue

        word = input("Enter a word: ").strip()
        if not word.isalpha():
            print("\033[91mLetters only please.\033[0m\n")
            continue

        print()

        if choice == "1":
            results = get_anagrams(word, dictionary)
            label   = "Full anagrams"
        else:
            results = get_sub_anagrams(word, dictionary)
            label   = "Sub-anagrams"

        print(f"\033[1m{label} of '\033[93m{word}\033[0m\033[1m':\033[0m")

        if results:
            # group by length
            from itertools import groupby
            for length, group in groupby(results, key=len):
                words = list(group)
                line  = "  \033[92m" + "  ".join(f"{w}" for w in words) + "\033[0m"
                print(f"  [{length} letters]  " + "  ".join(f"\033[92m{w}\033[0m" for w in words))
            print(f"\n  \033[93mFound {len(results)} word(s).\033[0m")
        else:
            print("  \033[91mNo anagrams found.\033[0m")

        print()

if __name__ == "__main__":
    main()