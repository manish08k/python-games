import random
from collections import Counter

LETTER_VALUES = {
    'A':1,'B':3,'C':3,'D':2,'E':1,'F':4,'G':2,'H':4,'I':1,'J':8,
    'K':5,'L':1,'M':3,'N':1,'O':1,'P':3,'Q':10,'R':1,'S':1,'T':1,
    'U':1,'V':4,'W':4,'X':8,'Y':4,'Z':10,'?':0
}

LETTER_DIST = {
    'A':9,'B':2,'C':2,'D':4,'E':12,'F':2,'G':3,'H':2,'I':9,'J':1,
    'K':1,'L':4,'M':2,'N':6,'O':8,'P':2,'Q':1,'R':6,'S':4,'T':6,
    'U':4,'V':2,'W':2,'X':1,'Y':2,'Z':1,'?':2
}

BOARD_SIZE = 15
PREMIUM_SQUARES = {
    'TW': [(0,0),(0,7),(0,14),(7,0),(7,14),(14,0),(14,7),(14,14)],
    'DW': [(1,1),(2,2),(3,3),(4,4),(1,13),(2,12),(3,11),(4,10),
           (13,1),(12,2),(11,3),(10,4),(13,13),(12,12),(11,11),(10,10),(7,7)],
    'TL': [(1,5),(1,9),(5,1),(5,5),(5,9),(5,13),(9,1),(9,5),(9,9),(9,13),(13,5),(13,9)],
    'DL': [(0,3),(0,11),(2,6),(2,8),(3,0),(3,7),(3,14),(6,2),(6,6),(6,8),(6,12),
           (7,3),(7,11),(8,2),(8,6),(8,8),(8,12),(11,0),(11,7),(11,14),(12,6),(12,8),(14,3),(14,11)]
}

def create_bag():
    bag = []
    for letter, count in LETTER_DIST.items():
        bag.extend([letter] * count)
    random.shuffle(bag)
    return bag

def create_board():
    board = [[' ' for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
    board[7][7] = '*'
    return board

def get_square_type(r, c):
    for sq_type, positions in PREMIUM_SQUARES.items():
        if (r, c) in positions:
            return sq_type
    return None

def print_board(board):
    print("\n    " + "  ".join(f"{i:2}" for i in range(BOARD_SIZE)))
    print("   +" + "---" * BOARD_SIZE + "+")
    for r in range(BOARD_SIZE):
        row_str = f"{r:2} |"
        for c in range(BOARD_SIZE):
            cell = board[r][c]
            if cell not in (' ', '*'):
                row_str += f" {cell} "
            else:
                sq = get_square_type(r, c)
                if sq == 'TW':
                    row_str += "TW "
                elif sq == 'DW' or cell == '*':
                    row_str += "DW "
                elif sq == 'TL':
                    row_str += "TL "
                elif sq == 'DL':
                    row_str += "DL "
                else:
                    row_str += " . "
        row_str += "|"
        print(row_str)
    print("   +" + "---" * BOARD_SIZE + "+")

def print_rack(rack):
    print("\nYour rack:", " ".join(rack))
    print("Values:   ", " ".join(str(LETTER_VALUES.get(l, 0)) for l in rack))

def draw_tiles(bag, rack, count=7):
    while len(rack) < 7 and bag:
        rack.append(bag.pop())
    return rack

def calculate_score(word, positions, board):
    score = 0
    word_mult = 1
    for i, (r, c) in enumerate(positions):
        letter = word[i]
        letter_val = LETTER_VALUES.get(letter, 0)
        sq = get_square_type(r, c)
        cell_was_empty = board[r][c] in (' ', '*')
        if cell_was_empty:
            if sq == 'DL':
                letter_val *= 2
            elif sq == 'TL':
                letter_val *= 3
            elif sq == 'DW' or board[r][c] == '*':
                word_mult *= 2
            elif sq == 'TW':
                word_mult *= 3
        score += letter_val
    return score * word_mult

def is_valid_placement(word, row, col, direction, board):
    positions = []
    r, c = row, col
    for letter in word:
        if r >= BOARD_SIZE or c >= BOARD_SIZE:
            return False, [], "Word goes out of bounds"
        positions.append((r, c))
        if direction == 'H':
            c += 1
        else:
            r += 1

    first_move = all(board[r][c] in (' ', '*') for r in range(BOARD_SIZE) for c in range(BOARD_SIZE) if board[r][c] not in (' ', '*')) == False
    center_covered = any((r, c) == (7, 7) for r, c in positions)
    board_empty = all(board[r][c] in (' ', '*') for r in range(BOARD_SIZE) for c in range(BOARD_SIZE))

    if board_empty and not center_covered:
        return False, [], "First word must cover center (7,7)"

    return True, positions, ""

def place_word(word, positions, board, rack):
    used_letters = list(word)
    rack_copy = rack[:]
    for letter in used_letters:
        if letter in rack_copy:
            rack_copy.remove(letter)
        elif '?' in rack_copy:
            rack_copy.remove('?')
        else:
            return False, rack, "Not enough letters in rack"
    for i, (r, c) in enumerate(positions):
        board[r][c] = word[i]
    return True, rack_copy, ""

def exchange_tiles(rack, bag):
    if len(bag) < 7:
        return rack, bag, "Not enough tiles in bag to exchange"
    print_rack(rack)
    tiles = input("Enter tiles to exchange (e.g. AEI): ").upper().strip()
    new_rack = rack[:]
    returned = []
    for t in tiles:
        if t in new_rack:
            new_rack.remove(t)
            returned.append(t)
        else:
            return rack, bag, f"Tile {t} not in rack"
    bag.extend(returned)
    random.shuffle(bag)
    draw_tiles(bag, new_rack)
    return new_rack, bag, f"Exchanged {tiles}"

def play_scrabble():
    print("=" * 50)
    print("       🔤 Welcome to SCRABBLE! 🔤")
    print("=" * 50)
    
    try:
        num_players = int(input("Number of players (1-4): "))
        num_players = max(1, min(4, num_players))
    except ValueError:
        num_players = 2

    player_names = []
    for i in range(num_players):
        name = input(f"Enter name for Player {i+1}: ").strip() or f"Player {i+1}"
        player_names.append(name)

    bag = create_bag()
    board = create_board()
    racks = {name: [] for name in player_names}
    scores = {name: 0 for name in player_names}
    passes = {name: 0 for name in player_names}

    for name in player_names:
        draw_tiles(bag, racks[name])

    print(f"\n🎯 Game started! {len(bag)} tiles in bag.")
    print("Commands: PLAY, EXCHANGE, PASS, SCORE, QUIT")

    consecutive_passes = 0
    turn = 0

    while True:
        name = player_names[turn % num_players]
        rack = racks[name]

        if not rack and not bag:
            print(f"\n{name} has no tiles left! Game Over!")
            break

        print("\n" + "=" * 50)
        print(f"  {name}'s Turn | Score: {scores[name]} | Tiles in bag: {len(bag)}")
        print("=" * 50)
        print_board(board)
        print_rack(rack)

        cmd = input("\nCommand (PLAY/EXCHANGE/PASS/SCORE/QUIT): ").upper().strip()

        if cmd == 'QUIT':
            print("Thanks for playing!")
            break

        elif cmd == 'SCORE':
            print("\n📊 Scoreboard:")
            for n in player_names:
                print(f"  {n}: {scores[n]} points")
            continue

        elif cmd == 'PASS':
            consecutive_passes += 1
            passes[name] += 1
            print(f"{name} passes.")
            if consecutive_passes >= num_players * 2:
                print("Too many consecutive passes. Game Over!")
                break

        elif cmd == 'EXCHANGE':
            new_rack, bag, msg = exchange_tiles(rack, bag)
            racks[name] = new_rack
            print(f"✅ {msg}")
            consecutive_passes += 1

        elif cmd == 'PLAY':
            word = input("Enter word: ").upper().strip()
            try:
                row = int(input("Starting row (0-14): "))
                col = int(input("Starting col (0-14): "))
                direction = input("Direction (H/V): ").upper().strip()
                if direction not in ('H', 'V'):
                    print("❌ Invalid direction")
                    continue
            except ValueError:
                print("❌ Invalid input")
                continue

            valid, positions, err = is_valid_placement(word, row, col, direction, board)
            if not valid:
                print(f"❌ {err}")
                continue

            success, new_rack, err = place_word(word, positions, board, rack)
            if not success:
                print(f"❌ {err}")
                continue

            word_score = calculate_score(word, positions, board)
            if len(word) == 7:
                word_score += 50
                print("🌟 BINGO! +50 bonus points!")

            scores[name] += word_score
            racks[name] = new_rack
            draw_tiles(bag, racks[name])
            consecutive_passes = 0
            print(f"✅ '{word}' placed for {word_score} points! Total: {scores[name]}")

        else:
            print("❌ Unknown command")
            continue

        turn += 1

    print("\n🏆 Final Scores:")
    winner = max(scores, key=scores.get)
    for n in player_names:
        print(f"  {n}: {scores[n]} points")
    print(f"\n🥇 Winner: {winner} with {scores[winner]} points!")

if __name__ == "__main__":
    play_scrabble()