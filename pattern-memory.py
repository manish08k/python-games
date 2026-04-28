import random
import time

def display_pattern(pattern):
    print("\nMemorize this pattern:")
    print(" -> ".join(pattern))
    time.sleep(len(pattern) * 0.8 + 1)
    print("\033[2J\033[H", end="")

def get_user_input(length):
    colors = ["RED", "BLUE", "GREEN", "YELLOW", "PURPLE", "ORANGE"]
    print(f"Enter {length} colors in order:")
    print(f"Options: {', '.join(colors)}")
    user_pattern = []
    for i in range(length):
        while True:
            color = input(f"  Step {i+1}: ").strip().upper()
            if color in colors:
                user_pattern.append(color)
                break
            print(f"  Invalid! Choose from: {', '.join(colors)}")
    return user_pattern

def pattern_memory_game():
    colors = ["RED", "BLUE", "GREEN", "YELLOW", "PURPLE", "ORANGE"]
    print("=== Pattern Memory Game ===")
    print("Memorize and repeat the color pattern!\n")
    
    pattern = []
    level = 1
    score = 0

    while True:
        print(f"\n--- Level {level} | Score: {score} ---")
        pattern.append(random.choice(colors))
        
        display_pattern(pattern)
        
        user_input = get_user_input(len(pattern))
        
        if user_input == pattern:
            score += level * 10
            print(f"\n✅ Correct! +{level * 10} points | Total: {score}")
            level += 1
            time.sleep(1)
        else:
            print(f"\n❌ Wrong!")
            print(f"Pattern was: {' -> '.join(pattern)}")
            print(f"You entered: {' -> '.join(user_input)}")
            print(f"\n🏁 Game Over!")
            print(f"   Level reached: {level}")
            print(f"   Final score:   {score}")
            
            if level <= 3:
                rating = "🌱 Beginner"
            elif level <= 6:
                rating = "⚡ Getting There"
            elif level <= 10:
                rating = "🧠 Sharp Mind"
            else:
                rating = "🏆 Memory Master"
            print(f"   Rating:        {rating}")
            
            play_again = input("\nPlay again? (y/n): ").strip().lower()
            if play_again == 'y':
                pattern = []
                level = 1
                score = 0
                print("\033[2J\033[H", end="")
            else:
                print("Thanks for playing!")
                break

if __name__ == "__main__":
    pattern_memory_game()