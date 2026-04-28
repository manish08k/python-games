import os
import time
import random

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

SUITS  = ['♠', '♥', '♦', '♣']
RANKS  = ['2','3','4','5','6','7','8','9','10','J','Q','K','A']
RANK_NAMES = {
    '2':'Twos','3':'Threes','4':'Fours','5':'Fives','6':'Sixes',
    '7':'Sevens','8':'Eights','9':'Nines','10':'Tens',
    'J':'Jacks','Q':'Queens','K':'Kings','A':'Aces'
}

def make_deck():
    deck = [(r, s) for r in RANKS for s in SUITS]
    random.shuffle(deck)
    return deck

def card_str(card):
    r, s = card
    return f"{r}{s}"

def hand_str(hand):
    if not hand:
        return "(empty)"
    sorted_hand = sorted(hand, key=lambda c: RANKS.index(c[0]))
    return "  ".join(card_str(c) for c in sorted_hand)

def ranks_in_hand(hand):
    return list(set(c[0] for c in hand))

def count_rank(hand, rank):
    return sum(1 for c in hand if c[0] == rank)

def remove_rank(hand, rank):
    taken = [c for c in hand if c[0] == rank]
    hand[:] = [c for c in hand if c[0] != rank]
    return taken

def check_books(hand, books):
    for rank in RANKS:
        if count_rank(hand, rank) == 4:
            remove_rank(hand, rank)
            books.append(rank)
            return rank
    return None

def check_all_books(hand, books):
    found = []
    for rank in RANKS[:]:
        if count_rank(hand, rank) == 4:
            remove_rank(hand, rank)
            books.append(rank)
            found.append(rank)
    return found

def draw_card(deck, hand):
    if deck:
        card = deck.pop()
        hand.append(card)
        return card
    return None

def ai_choose_rank(ai_hand, player_hand_size, ai_books, player_books):
    rank_counts = {}
    for c in ai_hand:
        rank_counts[c[0]] = rank_counts.get(c[0], 0) + 1
    best = max(rank_counts, key=rank_counts.get)
    return best

def print_status(player_hand, ai_hand, deck, player_books, ai_books, player_name, round_num):
    clear()
    print("=" * 58)
    print("              🐟  G O   F I S H  🐟")
    print("=" * 58)
    print(f"  Round: {round_num:<6} Deck: {len(deck)} cards remaining")
    print("=" * 58)

    print(f"\n  🤖 Computer's hand : {len(ai_hand)} cards  (hidden)")
    print(f"  📚 Computer books  : {len(ai_books)}", end="")
    if ai_books:
        print(" →  " + "  ".join(f"[{RANK_NAMES[r]}]" for r in ai_books), end="")
    print()

    print("\n  " + "─" * 54)

    print(f"\n  👤 {player_name}'s hand  : {hand_str(player_hand)}")
    print(f"  📚 {player_name}'s books : {len(player_books)}", end="")
    if player_books:
        print(" →  " + "  ".join(f"[{RANK_NAMES[r]}]" for r in player_books), end="")
    print()
    print("\n  " + "─" * 54)

def player_turn(player_hand, ai_hand, deck, player_books, ai_books, player_name, round_num, log):
    print_status(player_hand, ai_hand, deck, player_books, ai_books, player_name, round_num)

    if log:
        print("\n  📋 Last events:")
        for entry in log[-4:]:
            print(f"     {entry}")

    if not player_hand:
        print("\n  ✋ You have no cards! Drawing from deck...")
        time.sleep(1.5)
        drawn = draw_card(deck, player_hand)
        if drawn:
            print(f"  Drew: {card_str(drawn)}")
            time.sleep(1)
        return

    available = sorted(set(c[0] for c in player_hand), key=lambda r: RANKS.index(r))
    print(f"\n  Your ranks: {', '.join(available)}")
    print("  Ask the computer for a rank.")
    print("  Type rank (e.g. A, K, Q, J, 10..9..2) | B = Books | Q = Quit")

    while True:
        choice = input("\n  Ask for: ").strip().upper()

        if choice == 'Q':
            return 'quit'
        if choice == 'B':
            print_status(player_hand, ai_hand, deck, player_books, ai_books, player_name, round_num)
            if log:
                print("\n  📋 Last events:")
                for entry in log[-4:]:
                    print(f"     {entry}")
            print(f"\n  Your ranks: {', '.join(available)}")
            continue
        if choice not in RANKS:
            print(f"  ❌ Invalid rank. Choose from: {', '.join(RANKS)}")
            continue
        if choice not in [c[0] for c in player_hand]:
            print(f"  ❌ You don't have any {RANK_NAMES.get(choice, choice)}! You must ask for a rank you hold.")
            continue

        # Ask AI
        if count_rank(ai_hand, choice) > 0:
            taken = remove_rank(ai_hand, choice)
            player_hand.extend(taken)
            msg = f"  ✅ Computer gave you {len(taken)} {RANK_NAMES[choice]}!"
            print(msg)
            log.append(f"You asked for {RANK_NAMES[choice]} → got {len(taken)} card(s)!")
            time.sleep(1.2)

            new_books = check_all_books(player_hand, player_books)
            for b in new_books:
                bm = f"  📚 BOOK! You completed {RANK_NAMES[b]}!"
                print(bm)
                log.append(f"You completed a book of {RANK_NAMES[b]}!")
                time.sleep(1)
        else:
            print("  🐟 GO FISH!")
            log.append(f"You asked for {RANK_NAMES[choice]} → Go Fish!")
            time.sleep(0.8)
            drawn = draw_card(deck, player_hand)
            if drawn:
                print(f"  Drew: {card_str(drawn)}")
                log.append(f"You drew: {card_str(drawn)}")
                time.sleep(1)
                if drawn[0] == choice:
                    print(f"  🍀 Lucky! Drew the rank you asked for!")
                    log.append("Lucky draw — got the rank you asked for!")
                    time.sleep(1)
                new_books = check_all_books(player_hand, player_books)
                for b in new_books:
                    print(f"  📚 BOOK! You completed {RANK_NAMES[b]}!")
                    log.append(f"You completed a book of {RANK_NAMES[b]}!")
                    time.sleep(1)
            else:
                print("  Deck is empty!")
                time.sleep(1)
        break

def ai_turn(player_hand, ai_hand, deck, player_books, ai_books, player_name, round_num, log):
    print_status(player_hand, ai_hand, deck, player_books, ai_books, player_name, round_num)

    if not ai_hand:
        print("\n  🤖 Computer has no cards, drawing...")
        time.sleep(1.5)
        drawn = draw_card(deck, ai_hand)
        if drawn:
            log.append("Computer drew a card (empty hand).")
        return

    choice = ai_choose_rank(ai_hand, len(player_hand), ai_books, player_books)
    print(f"\n  🤖 Computer asks: Do you have any {RANK_NAMES[choice]}?")
    log.append(f"Computer asked for {RANK_NAMES[choice]}")
    time.sleep(1.5)

    if count_rank(player_hand, choice) > 0:
        taken = remove_rank(player_hand, choice)
        ai_hand.extend(taken)
        print(f"  😬 You give {len(taken)} {RANK_NAMES[choice]} to the computer!")
        log.append(f"Computer got {len(taken)} {RANK_NAMES[choice]} from you!")
        time.sleep(1.5)
        new_books = check_all_books(ai_hand, ai_books)
        for b in new_books:
            print(f"  📚 Computer completed a book of {RANK_NAMES[b]}!")
            log.append(f"Computer completed a book of {RANK_NAMES[b]}!")
            time.sleep(1.2)
    else:
        print("  🐟 GO FISH! Computer draws a card.")
        log.append("Computer went fishing!")
        time.sleep(1.2)
        drawn = draw_card(deck, ai_hand)
        if drawn:
            if drawn[0] == choice:
                print(f"  😲 Computer drew the rank it wanted!")
                log.append("Computer got lucky — drew what it asked for!")
                time.sleep(1)
            new_books = check_all_books(ai_hand, ai_books)
            for b in new_books:
                print(f"  📚 Computer completed a book of {RANK_NAMES[b]}!")
                log.append(f"Computer completed a book of {RANK_NAMES[b]}!")
                time.sleep(1.2)
        else:
            print("  Deck is empty!")
            time.sleep(1)

    input("\n  Press Enter for your turn...")

def game_over(player_books, ai_books, player_name, rounds):
    clear()
    print("=" * 58)
    print("              🐟  G O   F I S H  🐟")
    print("=" * 58)
    print(f"\n  Game over after {rounds} rounds!\n")
    print(f"  👤 {player_name} : {len(player_books)} books")
    for b in player_books:
        print(f"      📚 {RANK_NAMES[b]}")
    print(f"\n  🤖 Computer    : {len(ai_books)} books")
    for b in ai_books:
        print(f"      📚 {RANK_NAMES[b]}")
    print()
    if len(player_books) > len(ai_books):
        print(f"  🏆 {player_name} WINS! 🎉")
    elif len(ai_books) > len(player_books):
        print("  🤖 Computer wins! Better luck next time!")
    else:
        print("  🤝 It's a TIE!")
    print()

def play(player_name, hand_size):
    deck         = make_deck()
    player_hand  = [deck.pop() for _ in range(hand_size)]
    ai_hand      = [deck.pop() for _ in range(hand_size)]
    player_books = []
    ai_books     = []
    log          = []
    round_num    = 1

    check_all_books(player_hand, player_books)
    check_all_books(ai_hand, ai_books)

    while True:
        if not deck and not player_hand and not ai_hand:
            break
        if len(player_books) + len(ai_books) == 13:
            break

        result = player_turn(player_hand, ai_hand, deck, player_books, ai_books, player_name, round_num, log)
        if result == 'quit':
            print("\n  Thanks for playing!")
            time.sleep(1)
            return

        if not deck and not player_hand and not ai_hand:
            break
        if len(player_books) + len(ai_books) == 13:
            break

        ai_turn(player_hand, ai_hand, deck, player_books, ai_books, player_name, round_num, log)
        round_num += 1

    game_over(player_books, ai_books, player_name, round_num)
    input("  Press Enter to return to menu...")

def main():
    while True:
        clear()
        print("=" * 50)
        print("           🐟  G O   F I S H  🐟")
        print("=" * 50)
        print("""
  How to play:
  • Ask the computer for a rank you hold
  • If they have it, you take their cards
  • If not, GO FISH — draw from the deck
  • Collect all 4 of a rank to make a BOOK
  • Most books at the end wins!
""")
        print("  Options:")
        print("   1. Play (7 cards each) - Standard")
        print("   2. Play (5 cards each) - Quick")
        print("   Q. Quit")
        print()

        choice = input("  Choose: ").strip().upper()

        if choice == '1':
            name = input("  Your name: ").strip() or "Player"
            play(name, 7)
        elif choice == '2':
            name = input("  Your name: ").strip() or "Player"
            play(name, 5)
        elif choice == 'Q':
            print("\n  Thanks for playing Go Fish! 🐟 Goodbye!")
            break
        else:
            print("  Invalid choice.")
            time.sleep(0.5)

if __name__ == "__main__":
    main()