import random

def get_feedback(secret, guess):
    feedback = []
    for i in range(4):
        if guess[i] == secret[i]:
            feedback.append('🟩')  # Correct digit, correct position
        elif guess[i] in secret:
            feedback.append('🟨')  # Correct digit, wrong position
        else:
            feedback.append('⬛')  # Digit not in number
    return feedback

def play():
    secret = [str(random.randint(0, 9)) for _ in range(4)]
    attempts = 6
    print("🔢 Number Wordle — Guess the 4-digit number (digits 0-9, repeats allowed)")
    print(f"You have {attempts} attempts.\n")

    for attempt in range(1, attempts + 1):
        while True:
            guess = input(f"Attempt {attempt}/{attempts}: ").strip()
            if len(guess) == 4 and guess.isdigit():
                break
            print("Enter exactly 4 digits.")

        guess_list = list(guess)
        feedback = get_feedback(secret, guess_list)
        print("  " + " ".join(feedback))

        if guess_list == secret:
            print(f"\n🎉 Correct! You guessed it in {attempt} attempt(s)!")
            return

    print(f"\n💀 Game over! The number was {''.join(secret)}")

if __name__ == "__main__":
    while True:
        play()
        again = input("\nPlay again? (y/n): ").strip().lower()
        if again != 'y':
            break