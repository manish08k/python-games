import random
import time
import os

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def memory_sequence_game():
    numbers = list(range(1, 11))   # 1 through 10
    sequence = []
    score = 0
    round_num = 1

    print("🎮 Memory Sequence Game (No consecutive repeats!)")
    print("Numbers 1–10 appear one by one.")
    print("Same number never appears twice in a row.")
    print("Repeat the entire sequence from start.\n")
    input("Press Enter to begin...")

    while True:
        clear_screen()
        print(f"=== Round {round_num} ===")

        # Choose next number: cannot equal the previous one
        if not sequence:
            next_num = random.choice(numbers)
        else:
            possible = [n for n in numbers if n != sequence[-1]]
            next_num = random.choice(possible)
        sequence.append(next_num)

        # Display the sequence
        print("Watch carefully...")
        time.sleep(1)
        for num in sequence:
            print(f"👉 {num}")
            time.sleep(1.0)
            clear_screen()

        # Player repeats
        print("Your turn. Enter each number in order:")
        player_seq = []
        correct = True
        for i, expected in enumerate(sequence):
            try:
                guess = int(input(f"Position {i+1}: "))
                if guess != expected:
                    correct = False
                    break
                player_seq.append(guess)
            except ValueError:
                correct = False
                break

        if not correct:
            print(f"\n❌ Wrong! You missed '{expected}'.")
            print(f"Final score: {score} round(s) completed.")
            print(f"Full sequence: {' → '.join(map(str, sequence))}")
            replay = input("\nPlay again? (y/n): ").lower()
            if replay == 'y':
                memory_sequence_game()
            else:
                print("Thanks for playing!")
            return

        # Correct
        score += 1
        round_num += 1
        print("\n✅ Correct! Next round...\n")
        time.sleep(1.5)

if __name__ == "__main__":
    memory_sequence_game()