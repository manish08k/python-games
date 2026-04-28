import time
import random

def reaction_time_test():
    print("=== Reaction Time Tester ===")
    print("Press ENTER as soon as you see 'GO!'")
    print("Press ENTER to start each round\n")
    
    results = []
    rounds = 5
    
    for i in range(1, rounds + 1):
        input(f"Round {i}/{rounds} - Press ENTER to begin...")
        
        delay = random.uniform(2, 5)
        time.sleep(delay)
        
        print("GO!")
        start = time.time()
        input()
        end = time.time()
        
        reaction = (end - start) * 1000
        results.append(reaction)
        print(f"  ⚡ {reaction:.1f} ms\n")
    
    print("=" * 30)
    print(f"  Best:    {min(results):.1f} ms")
    print(f"  Worst:   {max(results):.1f} ms")
    print(f"  Average: {sum(results)/len(results):.1f} ms")
    
    avg = sum(results) / len(results)
    if avg < 200:
        grade = "🏆 Elite"
    elif avg < 250:
        grade = "🥇 Excellent"
    elif avg < 300:
        grade = "🥈 Good"
    elif avg < 400:
        grade = "🥉 Average"
    else:
        grade = "💪 Keep practicing"
    
    print(f"  Rating:  {grade}")
    print("=" * 30)

if __name__ == "__main__":
    reaction_time_test()