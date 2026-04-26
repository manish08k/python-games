import random
import sys

def get_secret_number():
    """Return a 3-digit string with no repeated digits."""
    digits = list('0123456789')
    random.shuffle(digits)
    # first digit cannot be '0'
    if digits[0] == '0':
        digits[0], digits[1] = digits[1], digits[0]
    return ''.join(digits[:3])

def get_clues(guess, secret):
    """Return a string with Fermi, Pico, and Bagels clues."""
    if guess == secret:
        return "You got it!"

    clues = []
    for i in range(3):
        if guess[i] == secret[i]:
            clues.append("Fermi")
        elif guess[i] in secret:
            clues.append("Pico")
    if not clues:
        return "Bagels"
    clues.sort()
    return ' '.join(clues)

def play_again():
    """Ask if player wants another round."""
    print("\nDo you want to play again? (yes / no)")
    return input().lower().startswith('y')

def main():
    print("""
    =====================================
              B A G E L S
    =====================================
    I'm thinking of a 3-digit number.
    Try to guess it. Here are some clues:
    
    Fermi   → correct digit in correct place
    Pico    → correct digit in wrong place
    Bagels  → no digit is correct
    
    You have 10 guesses per round.
    """)
    
    while True:
        secret = get_secret_number()
        print("\n🔢 I have chosen a number. Start guessing!")
        guesses_left = 10
        
        while guesses_left > 0:
            print(f"\nYou have {guesses_left} guesses left.")
            guess = input("> ").strip()
            
            # input validation
            if len(guess) != 3 or not guess.isdigit():
                print("Please enter a 3-digit number (e.g., 123).")
                continue
            if len(set(guess)) != 3:
                print("Digits must be unique (no repeats).")
                continue
            if guess[0] == '0':
                print("The first digit cannot be zero.")
                continue
            
            guesses_left -= 1
            
            clue = get_clues(guess, secret)
            print(clue)
            
            if guess == secret:
                print("\n🎉 Congratulations! You guessed it! 🎉")
                break
        else:
            print(f"\n😞 Out of guesses! The number was {secret}.")
        
        if not play_again():
            print("\nThanks for playing Bagels! Goodbye.")
            sys.exit()
        print("\n" + "=" * 40)

if __name__ == "__main__":
    main()