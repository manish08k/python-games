import random

def number_guessing_game():
    """A simple number guessing game."""
    
    # Game settings
    lower_bound = 1
    upper_bound = 100
    secret_number = random.randint(lower_bound, upper_bound)
    attempts = 0
    max_attempts = 10
    
    print(f"🎯 Welcome to the Number Guessing Game!")
    print(f"I'm thinking of a number between {lower_bound} and {upper_bound}.")
    print(f"You have {max_attempts} attempts to guess it.\n")
    
    while attempts < max_attempts:
        try:
            guess = int(input(f"Attempt #{attempts + 1}: Enter your guess: "))
            attempts += 1
            
            if guess < lower_bound or guess > upper_bound:
                print(f"Please guess between {lower_bound} and {upper_bound}.\n")
                continue
                
            if guess < secret_number:
                print("Too low! Try again.\n")
            elif guess > secret_number:
                print("Too high! Try again.\n")
            else:
                print(f"🎉 Congratulations! You guessed the number {secret_number} correctly!")
                print(f"It took you {attempts} attempt(s).")
                break
        except ValueError:
            print("Invalid input! Please enter a valid number.\n")
    
    else:
        print(f"😞 Sorry, you've used all {max_attempts} attempts.")
        print(f"The secret number was {secret_number}. Better luck next time!")
    
    # Ask for replay
    play_again = input("\nDo you want to play again? (y/n): ").lower()
    if play_again == 'y':
        number_guessing_game()
    else:
        print("Thanks for playing! Goodbye.")

# Run the game
if __name__ == "__main__":
    number_guessing_game()