import random

def display_hangman(tries):
    stages = [
        """
           --------
           |      |
           |      
           |    
           |      
           |     
           -
        """,
        """
           --------
           |      |
           |      O
           |    
           |      
           |     
           -
        """,
        """
           --------
           |      |
           |      O
           |      |
           |      
           |     
           -
        """,
        """
           --------
           |      |
           |      O
           |     /|
           |      
           |     
           -
        """,
        """
           --------
           |      |
           |      O
           |     /|\\
           |      
           |     
           -
        """,
        """
           --------
           |      |
           |      O
           |     /|\\
           |     /
           |     
           -
        """,
        """
           --------
           |      |
           |      O
           |     /|\\
           |     / \\
           |     
           -
        """
    ]
    return stages[tries]

def get_word():
    # ========== 250+ WORD LIST ==========
    words = [
        # Animals (50)
        "ELEPHANT", "GIRAFFE", "LION", "TIGER", "ZEBRA", "KANGAROO", "PANDA", "KOALA",
        "RHINOCEROS", "HIPPOPOTAMUS", "CROCODILE", "ALLIGATOR", "CHEETAH", "LEOPARD",
        "JAGUAR", "MONKEY", "GORILLA", "CHIMPANZEE", "ORANGUTAN", "SLOTH", "ANTEATER",
        "PENGUIN", "FLAMINGO", "OSTRICH", "EAGLE", "HAWK", "FALCON", "OWL", "PARROT",
        "DOLPHIN", "WHALE", "SHARK", "OCTOPUS", "JELLYFISH", "SEAHORSE", "CRAB", "LOBSTER",
        "SQUIRREL", "RABBIT", "HEDGEHOG", "BEAVER", "OTTER", "BAT", "FOX", "WOLF", "DEER",
        "MOOSE", "BUFFALO", "CAMEL", "LLAMA",
        # Fruits (30)
        "APPLE", "BANANA", "ORANGE", "GRAPE", "MANGO", "PINEAPPLE", "STRAWBERRY", "BLUEBERRY",
        "RASPBERRY", "BLACKBERRY", "WATERMELON", "CANTALOUPE", "HONEYDEW", "PEACH", "PLUM",
        "CHERRY", "KIWI", "PAPAYA", "GUAVA", "LYCHEE", "POMEGRANATE", "FIG", "DATE", "COCONUT",
        "LEMON", "LIME", "GRAPEFRUIT", "APRICOT", "NECTARINE", "CRANBERRY",
        # Vegetables (25)
        "CARROT", "BROCCOLI", "CAULIFLOWER", "SPINACH", "KALE", "LETTUCE", "CUCUMBER",
        "TOMATO", "POTATO", "SWEETPOTATO", "ONION", "GARLIC", "PEPPER", "CELERY", "ASPARAGUS",
        "ZUCCHINI", "EGGPLANT", "CABBAGE", "RADISH", "BEETROOT", "TURNIP", "PEA", "BEAN",
        "LENTIL", "OKRA",
        # Countries (30)
        "FRANCE", "GERMANY", "ITALY", "SPAIN", "PORTUGAL", "NETHERLANDS", "BELGIUM", "SWITZERLAND",
        "AUSTRIA", "SWEDEN", "NORWAY", "FINLAND", "DENMARK", "ICELAND", "IRELAND", "UNITEDKINGDOM",
        "CANADA", "MEXICO", "BRAZIL", "ARGENTINA", "PERU", "CHILE", "JAPAN", "CHINA", "INDIA",
        "AUSTRALIA", "NEWZEALAND", "SOUTHAFRICA", "EGYPT", "NIGERIA",
        # Programming (30)
        "PYTHON", "JAVA", "JAVASCRIPT", "RUBY", "PHP", "SWIFT", "KOTLIN", "TYPESCRIPT",
        "CSHARP", "CPLUSPLUS", "GO", "RUST", "SCALA", "PERL", "HASKELL", "LUA", "DART",
        "HTML", "CSS", "SQL", "MONGODB", "REACT", "ANGULAR", "VUE", "DJANGO", "FLASK",
        "SPRING", "NODEJS", "EXPRESS", "RUBYONRAILS",
        # Colors (20)
        "RED", "BLUE", "GREEN", "YELLOW", "ORANGE", "PURPLE", "PINK", "BROWN", "BLACK", "WHITE",
        "GRAY", "CYAN", "MAGENTA", "VIOLET", "INDIGO", "TURQUOISE", "CRIMSON", "SCARLET",
        "LAVENDER", "MAROON",
        # Sports (20)
        "FOOTBALL", "BASKETBALL", "TENNIS", "BASEBALL", "SOCCER", "VOLLEYBALL", "HOCKEY",
        "CRICKET", "RUGBY", "GOLF", "SWIMMING", "BOXING", "WRESTLING", "JUDO", "KARATE",
        "FENCING", "ARCHERY", "SKIING", "SNOWBOARDING", "SURFING",
        # Astronomy (20)
        "MERCURY", "VENUS", "EARTH", "MARS", "JUPITER", "SATURN", "URANUS", "NEPTUNE",
        "SUN", "MOON", "ASTEROID", "COMET", "GALAXY", "NEBULA", "SUPERNOVA", "BLACKHOLE",
        "TELESCOPE", "ASTRONAUT", "ROCKET", "SATELLITE",
        # Miscellaneous (25)
        "PIANO", "GUITAR", "VIOLIN", "DRUM", "TRUMPET", "FLUTE", "HARMONICA", "KEYBOARD",
        "COMPUTER", "LAPTOP", "MOBILE", "TABLET", "TELEVISION", "RADIO", "MICROWAVE",
        "REFRIGERATOR", "WASHINGMACHINE", "VACUUM", "CLOCK", "WATCH", "BICYCLE", "MOTORCYCLE",
        "AIRPLANE", "HELICOPTER", "SUBMARINE"
    ]
    return random.choice(words).upper()

def play_hangman():
    word = get_word()
    word_letters = set(word)
    guessed_letters = set()
    tries = 0
    max_tries = 6

    print("🎮 Welcome to Hangman!")
    print("Guess the word (letters only). You have 6 wrong guesses.\n")

    while tries < max_tries and len(word_letters) > 0:
        print(display_hangman(tries))
        print(f"Guessed letters: {' '.join(sorted(guessed_letters)) if guessed_letters else 'None'}")
        print(f"Remaining wrong guesses: {max_tries - tries}")
        
        # Show progress
        display_word = [letter if letter in guessed_letters else '_' for letter in word]
        print("Word: " + ' '.join(display_word))
        
        guess = input("Guess a letter: ").upper().strip()
        if not guess.isalpha() or len(guess) != 1:
            print("Invalid input. Please enter a single letter.\n")
            continue
        
        if guess in guessed_letters:
            print(f"You already guessed '{guess}'. Try another.\n")
            continue
        
        guessed_letters.add(guess)
        
        if guess in word_letters:
            word_letters.remove(guess)
            print(f"✅ Good guess! '{guess}' is in the word.\n")
        else:
            tries += 1
            print(f"❌ Wrong! '{guess}' is not in the word. {max_tries - tries} tries left.\n")
    
    # Game over
    if tries == max_tries:
        print(display_hangman(tries))
        print(f"😞 You lost! The word was: {word}")
    else:
        print(f"🎉 Congratulations! You guessed the word: {word}")

def main():
    while True:
        play_hangman()
        again = input("\nPlay again? (y/n): ").lower()
        if again != 'y':
            print("Thanks for playing!")
            break
        print("\n" + "=" * 50 + "\n")

if __name__ == "__main__":
    main()