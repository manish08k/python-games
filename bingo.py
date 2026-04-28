import random

def generate_bingo_card():
    card = []
    ranges = [(1,15), (16,30), (31,45), (46,60), (61,75)]
    for i, (low, high) in enumerate(ranges):
        col = random.sample(range(low, high+1), 5)
        if i == 2:
            col[2] = 'FREE'
        card.append(col)
    return card

def print_card(card, called):
    print("\n  B    I    N    G    O")
    print("-" * 27)
    for row in range(5):
        for col in range(5):
            val = card[col][row]
            if val == 'FREE' or val in called:
                print(f"[{'X':^3}]", end="")
            else:
                print(f"[{val:^3}]", end="")
        print()
    print("-" * 27)

def check_bingo(card, called):
    # Check rows
    for row in range(5):
        if all(card[col][row] == 'FREE' or card[col][row] in called for col in range(5)):
            return True
    # Check columns
    for col in range(5):
        if all(card[col][row] == 'FREE' or card[col][row] in called for row in range(5)):
            return True
    # Check diagonals
    if all(card[i][i] == 'FREE' or card[i][i] in called for i in range(5)):
        return True
    if all(card[4-i][i] == 'FREE' or card[4-i][i] in called for i in range(5)):
        return True
    return False

def play_bingo():
    print("🎱 Welcome to BINGO!")
    try:
        num_players = int(input("Enter number of players (1-4): "))
        num_players = max(1, min(4, num_players))
    except ValueError:
        num_players = 1

    players = {f"Player {i+1}": generate_bingo_card() for i in range(num_players)}
    pool = list(range(1, 76))
    random.shuffle(pool)
    called = set()
    letters = {range(1,16):'B', range(16,31):'I', range(31,46):'N', range(46,61):'G', range(61,76):'O'}

    def get_letter(n):
        for r, l in letters.items():
            if n in r:
                return l
        return '?'

    print("\n🃏 Your Cards:")
    for name, card in players.items():
        print(f"\n{name}'s Card:")
        print_card(card, called)

    round_num = 0
    while pool:
        input("\nPress Enter to draw next number...")
        num = pool.pop(0)
        called.add(num)
        letter = get_letter(num)
        round_num += 1
        print(f"\n🔔 Called: {letter}-{num}  (Round {round_num})")
        print(f"All called: {sorted(called)}")

        winners = []
        for name, card in players.items():
            print(f"\n{name}'s Card:")
            print_card(card, called)
            if check_bingo(card, called):
                winners.append(name)

        if winners:
            print(f"\n🎉 BINGO! Winner(s): {', '.join(winners)}!")
            break
    else:
        print("\n🎱 All numbers called! No winner.")

if __name__ == "__main__":
    play_bingo()