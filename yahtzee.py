import os
import time
import random

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

DICE_ART = {
    1: ["┌─────┐","│     │","│  ●  │","│     │","└─────┘"],
    2: ["┌─────┐","│ ●   │","│     │","│   ● │","└─────┘"],
    3: ["┌─────┐","│ ●   │","│  ●  │","│   ● │","└─────┘"],
    4: ["┌─────┐","│ ● ● │","│     │","│ ● ● │","└─────┘"],
    5: ["┌─────┐","│ ● ● │","│  ●  │","│ ● ● │","└─────┘"],
    6: ["┌─────┐","│ ● ● │","│ ● ● │","│ ● ● │","└─────┘"],
}

CATEGORIES = [
    ('ones',       'Ones',            'Upper'),
    ('twos',       'Twos',            'Upper'),
    ('threes',     'Threes',          'Upper'),
    ('fours',      'Fours',           'Upper'),
    ('fives',      'Fives',           'Upper'),
    ('sixes',      'Sixes',           'Upper'),
    ('three_kind', 'Three of a Kind', 'Lower'),
    ('four_kind',  'Four of a Kind',  'Lower'),
    ('full_house', 'Full House',      'Lower'),
    ('sm_straight','Sm. Straight',    'Lower'),
    ('lg_straight','Lg. Straight',    'Lower'),
    ('yahtzee',    'YAHTZEE',         'Lower'),
    ('chance',     'Chance',          'Lower'),
]

def roll_dice(kept, current):
    return [current[i] if kept[i] else random.randint(1,6) for i in range(5)]

def print_dice(dice, kept):
    rows = [""]*5
    for i, d in enumerate(dice):
        art = DICE_ART[d]
        mark = " [KEEP]" if kept[i] else "       "
        for r in range(5):
            rows[r] += art[r] + mark + "  "
    print()
    for row in rows:
        print("  " + row)
    print()
    labels = ""
    for i in range(5):
        labels += f"    #{i+1}          "
    print("  " + labels)
    print()

def calc_score(cat, dice):
    counts = [dice.count(i) for i in range(7)]
    s = sum(dice)
    if cat == 'ones':       return counts[1]*1
    if cat == 'twos':       return counts[2]*2
    if cat == 'threes':     return counts[3]*3
    if cat == 'fours':      return counts[4]*4
    if cat == 'fives':      return counts[5]*5
    if cat == 'sixes':      return counts[6]*6
    if cat == 'three_kind': return s if any(c>=3 for c in counts) else 0
    if cat == 'four_kind':  return s if any(c>=4 for c in counts) else 0
    if cat == 'full_house':
        vals = set(dice)
        if len(vals)==2 and any(counts[v]==3 for v in vals): return 25
        return 0
    if cat == 'sm_straight':
        uniq = sorted(set(dice))
        for start in [1,2,3]:
            if all(x in uniq for x in range(start,start+4)): return 30
        return 0
    if cat == 'lg_straight':
        if sorted(dice)==[1,2,3,4,5] or sorted(dice)==[2,3,4,5,6]: return 40
        return 0
    if cat == 'yahtzee':    return 50 if len(set(dice))==1 else 0
    if cat == 'chance':     return s
    return 0

def upper_bonus(scorecard):
    upper_total = sum(
        scorecard[c] for c in ['ones','twos','threes','fours','fives','sixes']
        if scorecard[c] is not None
    )
    return 35 if upper_total >= 63 else 0

def total_score(scorecard):
    base = sum(v for v in scorecard.values() if v is not None)
    return base + upper_bonus(scorecard)

def print_scorecard(scorecard, dice=None, player_name="Player"):
    print(f"\n  {'─'*46}")
    print(f"  📋  {player_name}'s Scorecard")
    print(f"  {'─'*46}")

    upper_sum = 0
    print("  ── UPPER SECTION ──────────────────────────")
    for cat, label, section in CATEGORIES:
        if section != 'Upper': continue
        val = scorecard[cat]
        pot = calc_score(cat, dice) if dice else None
        score_str = f"{val:>4}" if val is not None else (f"({pot:>3})" if pot is not None else "    ")
        star = " ✓" if val is not None else ("  " if pot is None else " ?")
        print(f"  {label:<20} {score_str}{star}")
        if val is not None:
            upper_sum += val

    bonus = upper_bonus(scorecard)
    needed = max(0, 63 - upper_sum)
    bonus_str = f"{bonus}" if bonus else (f"need {needed} more" if needed else "35")
    print(f"  {'Bonus (63+)':<20} {'35':>4}  [{bonus_str}]")

    print("  ── LOWER SECTION ──────────────────────────")
    for cat, label, section in CATEGORIES:
        if section != 'Lower': continue
        val = scorecard[cat]
        pot = calc_score(cat, dice) if dice else None
        score_str = f"{val:>4}" if val is not None else (f"({pot:>3})" if pot is not None else "    ")
        star = " ✓" if val is not None else ("  " if pot is None else " ?")
        print(f"  {label:<20} {score_str}{star}")

    total = total_score(scorecard)
    print(f"  {'─'*46}")
    print(f"  {'TOTAL':>20} {total:>4}")
    print(f"  {'─'*46}\n")

def choose_category(scorecard, dice, player_name):
    available = [(i, cat, label) for i,(cat,label,_) in enumerate(CATEGORIES) if scorecard[cat] is None]
    print("  Available categories:")
    print(f"  {'#':<4} {'Category':<22} {'Score'}")
    print("  " + "─"*36)
    for i, cat, label in available:
        pot = calc_score(cat, dice)
        print(f"  {i+1:<4} {label:<22} {pot}")
    print()

    while True:
        raw = input("  Enter category number (or S for scorecard): ").strip().upper()
        if raw == 'S':
            print_scorecard(scorecard, dice, player_name)
            continue
        try:
            num = int(raw) - 1
            cat, label, _ = CATEGORIES[num]
            if scorecard[cat] is not None:
                print(f"  ❌ {label} already scored!")
                continue
            score = calc_score(cat, dice)
            return cat, label, score
        except (ValueError, IndexError):
            print("  ❌ Invalid choice.")

def player_turn(scorecard, player_name, turn_num, total_turns):
    dice  = [random.randint(1,6) for _ in range(5)]
    kept  = [False]*5
    rolls = 1

    while True:
        clear()
        print("=" * 58)
        print("              🎲  Y A H T Z E E  🎲")
        print("=" * 58)
        print(f"  Player: {player_name:<20} Turn: {turn_num}/{total_turns}")
        print(f"  Roll  : {rolls}/3")
        print("=" * 58)
        print_dice(dice, kept)

        if rolls == 3:
            print("  No more rolls! Choose a category.")
            print_scorecard(scorecard, dice, player_name)
            cat, label, score = choose_category(scorecard, dice, player_name)
            scorecard[cat] = score
            print(f"\n  ✅ Scored {score} in {label}!")
            time.sleep(1.5)
            return

        print("  Commands:")
        print("   K 1 3 5  = Keep dice #1, #3, #5")
        print("   R        = Roll unkept dice")
        print("   S        = View scorecard")
        print("   C        = Choose category now (skip roll)")
        print()

        cmd = input("  > ").strip().upper()

        if cmd == 'S':
            print_scorecard(scorecard, dice, player_name)
            input("  Press Enter to continue...")
            continue

        if cmd == 'C' or cmd == '':
            if rolls >= 1:
                print_scorecard(scorecard, dice, player_name)
                cat, label, score = choose_category(scorecard, dice, player_name)
                scorecard[cat] = score
                print(f"\n  ✅ Scored {score} in {label}!")
                time.sleep(1.5)
                return

        if cmd.startswith('K'):
            parts = cmd.split()
            kept = [False]*5
            for p in parts[1:]:
                try:
                    idx = int(p)-1
                    if 0 <= idx < 5:
                        kept[idx] = True
                except ValueError:
                    pass
            print(f"  Keeping: {[i+1 for i in range(5) if kept[i]]}")
            time.sleep(0.4)
            continue

        if cmd == 'R':
            dice  = roll_dice(kept, dice)
            kept  = [False]*5
            rolls += 1
            if calc_score('yahtzee', dice) == 50:
                print("\n  🎉🎉 YAHTZEE! 🎉🎉")
                time.sleep(1.5)
            continue

        print("  ❌ Unknown command.")
        time.sleep(0.5)

def ai_turn(scorecard, turn_num, total_turns):
    dice  = [random.randint(1,6) for _ in range(5)]
    kept  = [False]*5

    for roll_num in range(1, 4):
        if roll_num > 1:
            dice = roll_dice(kept, dice)

        best_cat  = None
        best_score = -1
        for cat, label, _ in CATEGORIES:
            if scorecard[cat] is None:
                s = calc_score(cat, dice)
                if s > best_score:
                    best_score = s
                    best_cat   = cat

        if best_score >= 25 or roll_num == 3:
            scorecard[best_cat] = best_score
            label = next(l for c,l,_ in CATEGORIES if c==best_cat)
            return best_cat, label, best_score

        kept = [False]*5
        for i, d in enumerate(dice):
            cnt = dice.count(d)
            if cnt >= 2:
                kept[i] = True

    scorecard[best_cat] = best_score
    label = next(l for c,l,_ in CATEGORIES if c==best_cat)
    return best_cat, label, best_score

def final_scores(players, scorecards):
    clear()
    print("=" * 58)
    print("              🎲  Y A H T Z E E  🎲")
    print("=" * 58)
    print("  🏁 FINAL SCORES")
    print("=" * 58)

    totals = {}
    for p in players:
        t = total_score(scorecards[p])
        totals[p] = t
        print(f"\n  {p}:")
        print_scorecard(scorecards[p], player_name=p)

    print("=" * 58)
    ranked = sorted(totals.items(), key=lambda x: x[1], reverse=True)
    print("  🏆 Rankings:")
    medals = ['🥇','🥈','🥉']
    for i,(name,score) in enumerate(ranked):
        medal = medals[i] if i < 3 else '  '
        print(f"   {medal} {name}: {score} points")

    winner = ranked[0][0]
    print(f"\n  🎉 {winner} WINS! Congratulations!")
    print("=" * 58)

def main():
    while True:
        clear()
        print("=" * 50)
        print("          🎲  Y A H T Z E E  🎲")
        print("=" * 50)
        print("""
  How to play:
  • Roll 5 dice up to 3 times per turn
  • Keep any dice between rolls
  • Score in one of 13 categories per turn
  • 13 turns total — highest score wins!

  Scoring:
  • Upper: Sum of matching numbers (bonus +35 if ≥63)
  • Three/Four of a Kind: Sum of all dice
  • Full House: 25 pts
  • Sm. Straight (4 seq): 30 pts
  • Lg. Straight (5 seq): 40 pts
  • YAHTZEE (5 same): 50 pts
  • Chance: Sum of all dice
""")
        print("  Options:")
        print("   1. 1 Player")
        print("   2. 2 Players")
        print("   3. vs Computer")
        print("   Q. Quit")
        print()

        choice = input("  Choose: ").strip().upper()

        if choice == 'Q':
            print("\n  Thanks for playing Yahtzee! 🎲 Goodbye!")
            break

        players    = []
        scorecards = {}
        ai_players = set()

        if choice == '1':
            name = input("  Your name: ").strip() or "Player"
            players = [name]
        elif choice == '2':
            n1 = input("  Player 1 name: ").strip() or "Player 1"
            n2 = input("  Player 2 name: ").strip() or "Player 2"
            players = [n1, n2]
        elif choice == '3':
            name = input("  Your name: ").strip() or "Player"
            players = [name, "Computer"]
            ai_players.add("Computer")
        else:
            print("  Invalid choice.")
            time.sleep(0.5)
            continue

        for p in players:
            scorecards[p] = {cat: None for cat,_,_ in CATEGORIES}

        total_turns = 13
        for turn in range(1, total_turns+1):
            for p in players:
                if p in ai_players:
                    clear()
                    print("=" * 58)
                    print("              🎲  Y A H T Z E E  🎲")
                    print("=" * 58)
                    print(f"  🤖 Computer's turn {turn}/{total_turns}...")
                    time.sleep(1)
                    cat, label, score = ai_turn(scorecards[p], turn, total_turns)
                    print(f"  🤖 Computer scored {score} in {label}!")
                    print_scorecard(scorecards[p], player_name=p)
                    time.sleep(2)
                else:
                    player_turn(scorecards[p], p, turn, total_turns)

        final_scores(players, scorecards)
        input("\n  Press Enter to return to menu...")

if __name__ == "__main__":
    main()