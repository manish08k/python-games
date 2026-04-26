import random

def get_winner(player, computer):
    # Winning conditions: (player_choice, computer_choice)
    wins = {
        # Scissors cuts Paper
        ("scissors", "paper"): "Scissors cut Paper!",
        ("scissors", "lizard"): "Scissors decapitate Lizard!",
        # Paper covers Rock
        ("paper", "rock"): "Paper covers Rock!",
        ("paper", "spock"): "Paper disproves Spock!",
        # Rock crushes Lizard and Scissors
        ("rock", "lizard"): "Rock crushes Lizard!",
        ("rock", "scissors"): "Rock crushes Scissors!",
        # Lizard poisons Spock
        ("lizard", "spock"): "Lizard poisons Spock!",
        ("lizard", "paper"): "Lizard eats Paper!",
        # Spock smashes Scissors and vaporizes Rock
        ("spock", "scissors"): "Spock smashes Scissors!",
        ("spock", "rock"): "Spock vaporizes Rock!"
    }
    if player == computer:
        return "tie", "It's a tie!"
    elif (player, computer) in wins:
        return "player", wins[(player, computer)]
    else:
        # The reverse condition means computer wins
        for (p, c), msg in wins.items():
            if p == computer and c == player:
                return "computer", msg
        return "computer", "Computer wins!"

def play_game():
    choices = ["rock", "paper", "scissors", "lizard", "spock"]
    player_score = 0
    computer_score = 0
    rounds = 0

    print("=" * 50)
    print("   Rock, Paper, Scissors, Lizard, Spock")
    print("=" * 50)
    print("Rules:")
    print("  ✂️ Scissors cuts Paper, ✂️ decapitates Lizard")
    print("  📄 Paper covers Rock, 📄 disproves Spock")
    print("  🪨 Rock crushes Lizard, 🪨 crushes Scissors")
    print("  🦎 Lizard poisons Spock, 🦎 eats Paper")
    print("  🖖 Spock smashes Scissors, 🖖 vaporizes Rock")
    print("-" * 50)

    while True:
        print(f"\n--- Round {rounds + 1} ---")
        print(f"Score: You {player_score} : {computer_score} Computer")
        print("\nChoices: rock, paper, scissors, lizard, spock")
        player_choice = input("Your choice: ").strip().lower()

        if player_choice not in choices:
            print("Invalid choice. Please choose from rock, paper, scissors, lizard, spock.\n")
            continue

        computer_choice = random.choice(choices)
        print(f"\nComputer chose: {computer_choice}")

        result, message = get_winner(player_choice, computer_choice)

        if result == "player":
            print(f"✅ {message} You win this round!")
            player_score += 1
        elif result == "computer":
            print(f"❌ {message} Computer wins this round!")
            computer_score += 1
        else:
            print(f"😐 {message}")

        rounds += 1

        # Ask to continue
        again = input("\nPlay another round? (y/n): ").strip().lower()
        if again != 'y':
            break
        print()

    # Final score
    print("\n" + "=" * 50)
    print("GAME OVER")
    print(f"Final Score: You {player_score} : {computer_score} Computer")
    if player_score > computer_score:
        print("🎉 Congratulations! You are the overall winner! 🎉")
    elif computer_score > player_score:
        print("😞 Computer wins the match. Better luck next time!")
    else:
        print("🤝 It's a tie match!")
    print("=" * 50)

if __name__ == "__main__":
    play_game()