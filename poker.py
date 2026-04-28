import random
from collections import Counter

SUITS = ['♠', '♥', '♦', '♣']
RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
RANK_VALUES = {r: i for i, r in enumerate(RANKS, 2)}

def create_deck():
    return [f"{r}{s}" for s in SUITS for r in RANKS]

def get_rank(card):
    return card[:-1]

def get_suit(card):
    return card[-1]

def rank_val(card):
    return RANK_VALUES[get_rank(card)]

def hand_rank(hand):
    ranks = sorted([rank_val(c) for c in hand], reverse=True)
    suits = [get_suit(c) for c in hand]
    rank_counts = Counter(ranks)
    counts = sorted(rank_counts.values(), reverse=True)
    is_flush = len(set(suits)) == 1
    is_straight = (len(set(ranks)) == 5 and (max(ranks) - min(ranks) == 4))
    # Special straight: A-2-3-4-5
    if set(ranks) == {14, 2, 3, 4, 5}:
        is_straight = True
        ranks = [5, 4, 3, 2, 1]

    if is_straight and is_flush:
        return (8, ranks)
    if counts == [4, 1]:
        return (7, ranks)
    if counts == [3, 2]:
        return (6, ranks)
    if is_flush:
        return (5, ranks)
    if is_straight:
        return (4, ranks)
    if counts == [3, 1, 1]:
        return (3, ranks)
    if counts == [2, 2, 1]:
        return (2, ranks)
    if counts == [2, 1, 1, 1]:
        return (1, ranks)
    return (0, ranks)

HAND_NAMES = {
    8: "Straight Flush",
    7: "Four of a Kind",
    6: "Full House",
    5: "Flush",
    4: "Straight",
    3: "Three of a Kind",
    2: "Two Pair",
    1: "One Pair",
    0: "High Card"
}

def display_hand(name, hand, hide=False):
    if hide:
        print(f"  {name}: [??] [??] [??] [??] [??]")
    else:
        cards = "  ".join(f"[{c}]" for c in hand)
        score = hand_rank(hand)[0]
        print(f"  {name}: {cards}  → {HAND_NAMES[score]}")

def display_table(player_hand, ai_hands, pot, player_chips, round_name, hide_ai=True):
    print(f"\n{'═'*58}")
    print(f"  🃏  {round_name}   |   Pot: ${pot}   |   Your Chips: ${player_chips}")
    print(f"{'─'*58}")
    display_hand("You      ", player_hand)
    print(f"{'─'*58}")
    for i, hand in enumerate(ai_hands):
        display_hand(f"CPU {i+1}   ", hand, hide=hide_ai)
    print(f"{'═'*58}")

def betting_round(player_chips, pot, current_bet, label=""):
    print(f"\n  [{label}] Current bet: ${current_bet}  |  Your chips: ${player_chips}")
    while True:
        print("  Actions: [C]all  [R]aise  [F]old")
        action = input("  Your move: ").strip().lower()
        if action == 'f':
            return player_chips, pot, True  # folded
        elif action == 'c':
            call_amt = min(current_bet, player_chips)
            player_chips -= call_amt
            pot += call_amt
            return player_chips, pot, False
        elif action == 'r':
            try:
                raise_amt = int(input(f"  Raise by how much? (min 1, max {player_chips}): $"))
                if 1 <= raise_amt <= player_chips:
                    player_chips -= raise_amt
                    pot += raise_amt
                    current_bet = raise_amt
                    return player_chips, pot, False
                else:
                    print("  Invalid amount.")
            except ValueError:
                print("  Enter a number.")
        else:
            print("  Invalid input.")

def play_poker():
    print("\n" + "═"*58)
    print("       ♠ ♥  5-CARD DRAW POKER  ♦ ♣")
    print("═"*58)
    print("  Beat the CPUs to win their chips!")

    player_chips = 1000
    ai_chips = [500, 500, 500]
    num_ai = 3
    round_num = 0

    while player_chips > 0:
        round_num += 1
        active_ai = [i for i in range(num_ai) if ai_chips[i] > 0]
        if not active_ai:
            print("\n🏆 All CPUs are broke! YOU WIN THE GAME!")
            break

        print(f"\n\n{'━'*58}")
        print(f"  ROUND {round_num}  |  Your chips: ${player_chips}")
        for i in active_ai:
            print(f"  CPU {i+1} chips: ${ai_chips[i]}")

        # Ante
        ante = 20
        if player_chips < ante:
            print(f"\n💸 Not enough chips for ante (${ante}). Game over!")
            break
        player_chips -= ante
        pot = ante
        for i in active_ai:
            contrib = min(ante, ai_chips[i])
            ai_chips[i] -= contrib
            pot += contrib

        # Deal
        deck = create_deck()
        random.shuffle(deck)
        player_hand = [deck.pop() for _ in range(5)]
        ai_hands = [[deck.pop() for _ in range(5)] for _ in range(num_ai)]

        display_table(player_hand, ai_hands, pot, player_chips, "PRE-DRAW")

        # First betting round
        player_chips, pot, folded = betting_round(player_chips, pot, 20, "1st Bet")
        if folded:
            print(f"\n  You folded. Lost ante. Pot goes to CPU.")
            ai_chips[active_ai[0]] += pot
            if not play_again():
                break
            continue

        # Draw phase
        print(f"\n{'─'*58}")
        print("  DRAW PHASE — Enter card positions to discard (e.g. 1 3 5)")
        print("  Or press Enter to keep all cards.")
        display_hand("Your hand", player_hand)
        discard_input = input("  Discard positions: ").strip()
        if discard_input:
            try:
                positions = [int(x)-1 for x in discard_input.split()]
                positions = [p for p in positions if 0 <= p < 5]
                for p in positions:
                    player_hand[p] = deck.pop()
            except:
                print("  Invalid input, keeping hand.")

        # AI draw (random discard)
        for i in range(num_ai):
            if i in active_ai:
                discard_count = random.randint(0, 3)
                positions = random.sample(range(5), discard_count)
                for p in positions:
                    ai_hands[i][p] = deck.pop() if deck else ai_hands[i][p]

        display_table(player_hand, ai_hands, pot, player_chips, "POST-DRAW")

        # Second betting round
        player_chips, pot, folded = betting_round(player_chips, pot, 40, "2nd Bet")
        if folded:
            print(f"\n  You folded. Pot goes to CPU.")
            ai_chips[active_ai[0]] += pot
            if not play_again():
                break
            continue

        # Showdown
        print(f"\n{'═'*58}")
        print("  ★  SHOWDOWN  ★")
        display_table(player_hand, ai_hands, pot, player_chips, "SHOWDOWN", hide_ai=False)

        # Determine winner
        player_score = hand_rank(player_hand)
        results = [("You", player_score, "player")]
        for i in active_ai:
            results.append((f"CPU {i+1}", hand_rank(ai_hands[i]), i))

        results.sort(key=lambda x: x[1], reverse=True)
        winner_name, winner_score, winner_id = results[0]

        print(f"\n  🏆 Winner: {winner_name} with {HAND_NAMES[winner_score[0]]}!")

        if winner_id == "player":
            player_chips += pot
            print(f"  💰 You win ${pot}! New balance: ${player_chips}")
        else:
            ai_chips[winner_id] += pot
            print(f"  ❌ You lose the pot. CPU {winner_id+1} wins ${pot}.")

        # Eliminate broke AIs
        for i in range(num_ai):
            if ai_chips[i] <= 0 and i in active_ai:
                print(f"  CPU {i+1} is eliminated!")

        if not play_again():
            break

    print(f"\n{'═'*58}")
    print(f"  Game Over! Final chips: ${player_chips}")
    print("  Thanks for playing Poker! ♠ ♥ ♦ ♣")
    print(f"{'═'*58}\n")

def play_again():
    ans = input("\n  Play next round? [Y/N]: ").strip().lower()
    return ans == 'y'

if __name__ == "__main__":
    play_poker()