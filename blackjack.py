import random

# Card suits and values
SUITS = ['♠', '♥', '♦', '♣']
RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']

def create_deck():
    return [f"{rank}{suit}" for suit in SUITS for rank in RANKS]

def card_value(card):
    rank = card[:-1]  # Remove suit symbol
    if rank in ['J', 'Q', 'K']:
        return 10
    elif rank == 'A':
        return 11
    else:
        return int(rank)

def hand_value(hand):
    value = sum(card_value(c) for c in hand)
    aces = sum(1 for c in hand if c[:-1] == 'A')
    while value > 21 and aces:
        value -= 10
        aces -= 1
    return value

def display_hand(name, hand, hide_second=False):
    if hide_second:
        print(f"{name}'s hand: {hand[0]}  [hidden]")
    else:
        print(f"{name}'s hand: {' '.join(hand)}  (Total: {hand_value(hand)})")

def play_blackjack():
    print("\n" + "=" * 50)
    print("      ♠ ♥  BLACKJACK  ♦ ♣")
    print("=" * 50)

    balance = 1000
    print(f"Starting balance: ${balance}")

    while balance > 0:
        print(f"\n{'─' * 50}")
        print(f"Balance: ${balance}")

        # Get bet
        while True:
            try:
                bet = int(input(f"Place your bet (1-{balance}): $"))
                if 1 <= bet <= balance:
                    break
                print("Invalid bet amount.")
            except ValueError:
                print("Please enter a number.")

        # Setup
        deck = create_deck()
        random.shuffle(deck)

        player = [deck.pop(), deck.pop()]
        dealer = [deck.pop(), deck.pop()]

        print()
        display_hand("Dealer", dealer, hide_second=True)
        display_hand("You", player)

        # Check natural blackjack
        if hand_value(player) == 21:
            print("\n🎉 BLACKJACK! You win!")
            balance += int(bet * 1.5)
            print(f"Balance: ${balance}")
            if not play_again():
                break
            continue

        # Player's turn
        bust = False
        while hand_value(player) < 21:
            move = input("\n[H]it or [S]tand? ").strip().lower()
            if move == 'h':
                player.append(deck.pop())
                display_hand("You", player)
                if hand_value(player) > 21:
                    print("💥 BUST! You went over 21.")
                    bust = True
                    break
            elif move == 's':
                break
            else:
                print("Enter H or S.")

        # Dealer's turn
        if not bust:
            print()
            display_hand("Dealer", dealer)
            while hand_value(dealer) < 17:
                dealer.append(deck.pop())
                display_hand("Dealer", dealer)

        # Result
        pv = hand_value(player)
        dv = hand_value(dealer)
        print("\n" + "─" * 30)
        display_hand("You", player)
        display_hand("Dealer", dealer)

        if bust or (not bust and dv <= 21 and dv > pv):
            print("❌ You lose!")
            balance -= bet
        elif dv > 21 or pv > dv:
            print("✅ You win!")
            balance += bet
        else:
            print("🤝 It's a tie! Bet returned.")

        print(f"Balance: ${balance}")

        if balance <= 0:
            print("\n💸 You're out of money! Game over.")
            break

        if not play_again():
            break

    print(f"\nThanks for playing! Final balance: ${balance}")
    print("=" * 50)

def play_again():
    ans = input("\nPlay again? [Y/N]: ").strip().lower()
    return ans == 'y'

if __name__ == "__main__":
    play_blackjack()