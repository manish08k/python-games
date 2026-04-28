import os
import time
import random
import threading
import sys

if os.name == 'nt':
    import msvcrt
else:
    import tty
    import termios
    import select

MOLE    = "( ͡° ͜ʖ ͡°)"
HOLE    = "  (_____)  "
WHACKED = "  (x _ x)  "
EMPTY   = "           "

GRID_ROWS = 3
GRID_COLS = 3
TOTAL     = GRID_ROWS * GRID_COLS

KEYS = {
    '7':'0', '8':'1', '9':'2',
    '4':'3', '5':'4', '6':'5',
    '1':'6', '2':'7', '3':'8',
}

NUMPAD = """
  ┌───┬───┬───┐
  │ 7 │ 8 │ 9 │   ← top row
  ├───┼───┼───┤
  │ 4 │ 5 │ 6 │   ← middle row
  ├───┼───┼───┤
  │ 1 │ 2 │ 3 │   ← bottom row
  └───┴───┴───┘
"""

class GameState:
    def __init__(self, difficulty):
        self.holes        = [False] * TOTAL
        self.whacked      = [False] * TOTAL
        self.score        = 0
        self.misses       = 0
        self.combo        = 0
        self.max_combo    = 0
        self.hits         = 0
        self.total_moles  = 0
        self.running      = True
        self.lock         = threading.Lock()
        self.message      = ""
        self.msg_time     = 0

        configs = {
            'easy':   {'time': 30, 'speed': 1.5, 'max_moles': 2, 'points': 10},
            'medium': {'time': 45, 'speed': 1.0, 'max_moles': 3, 'points': 15},
            'hard':   {'time': 60, 'speed': 0.6, 'max_moles': 4, 'points': 20},
            'insane': {'time': 60, 'speed': 0.35,'max_moles': 5, 'points': 25},
        }
        cfg               = configs[difficulty]
        self.duration     = cfg['time']
        self.mole_speed   = cfg['speed']
        self.max_moles    = cfg['max_moles']
        self.points_each  = cfg['points']
        self.start_time   = time.time()
        self.difficulty   = difficulty

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def elapsed(gs):
    return time.time() - gs.start_time

def remaining(gs):
    return max(0, gs.duration - elapsed(gs))

def draw(gs):
    clear()
    time_left = remaining(gs)
    bar_len   = 30
    filled    = int((time_left / gs.duration) * bar_len)
    bar       = '█' * filled + '░' * (bar_len - filled)

    print("=" * 58)
    print("           🔨  W H A C K - A - M O L E  🔨")
    print("=" * 58)
    print(f"  ⏱  [{bar}] {time_left:5.1f}s")
    print(f"  🏆 Score : {gs.score:<8} 🔥 Combo : x{gs.combo}")
    print(f"  ✅ Hits  : {gs.hits:<8} ❌ Misses: {gs.misses}")
    print(f"  Difficulty: {gs.difficulty.upper():<10} Max combo: x{gs.max_combo}")
    print("=" * 58)
    print()

    for r in range(GRID_ROWS):
        top_row  = "  "
        mid_row  = "  "
        bot_row  = "  "
        for c in range(GRID_COLS):
            idx = r * GRID_COLS + c
            num = (GRID_ROWS - r - 1) * GRID_COLS + (c + 1)
            if num in [7,8,9]:   num_row = 0
            elif num in [4,5,6]: num_row = 1
            else:                num_row = 2
            actual_num = (2 - r) * 3 + c + 1 + 6 - (2-r)*3*2
            display_num = (GRID_ROWS - 1 - r) * GRID_COLS + c + 1 + 6 - (GRID_ROWS-1-r)*GRID_COLS

            key_num = r * GRID_COLS + c
            key_labels = ['7','8','9','4','5','6','1','2','3']
            key = key_labels[idx]

            if gs.whacked[idx]:
                mid_row += f" {WHACKED} "
            elif gs.holes[idx]:
                mid_row += f" {MOLE}  "
            else:
                mid_row += f" {HOLE}  "

            top_row += f"  [{key}]       "
            bot_row += "  ~~~~~~~~~~~  "

        print(top_row)
        print(mid_row)
        print(bot_row)
        print()

    print("=" * 58)
    now = time.time()
    if gs.message and (now - gs.msg_time) < 1.0:
        print(f"  {gs.message}")
    else:
        print("  Press numpad key to whack! Q to quit.")
    print("=" * 58)

def mole_controller(gs):
    while gs.running and remaining(gs) > 0:
        time.sleep(gs.mole_speed * random.uniform(0.7, 1.3))
        if not gs.running:
            break
        with gs.lock:
            active = [i for i in range(TOTAL) if gs.holes[i]]
            if len(active) < gs.max_moles:
                empty_holes = [i for i in range(TOTAL) if not gs.holes[i] and not gs.whacked[i]]
                if empty_holes:
                    idx = random.choice(empty_holes)
                    gs.holes[idx] = True
                    gs.total_moles += 1

        time.sleep(gs.mole_speed * random.uniform(1.0, 2.0))

        if not gs.running:
            break
        with gs.lock:
            active = [i for i in range(TOTAL) if gs.holes[i]]
            if active:
                idx = random.choice(active)
                gs.holes[idx] = False

def whack_cleaner(gs):
    while gs.running:
        time.sleep(0.4)
        with gs.lock:
            for i in range(TOTAL):
                gs.whacked[i] = False

def get_key_nonblock():
    if os.name == 'nt':
        if msvcrt.kbhit():
            ch = msvcrt.getch()
            try:
                return ch.decode('utf-8')
            except:
                return ''
        return None
    else:
        rlist, _, _ = select.select([sys.stdin], [], [], 0.05)
        if rlist:
            return sys.stdin.read(1)
        return None

def play(difficulty):
    gs = GameState(difficulty)

    mole_thread    = threading.Thread(target=mole_controller, args=(gs,), daemon=True)
    cleaner_thread = threading.Thread(target=whack_cleaner,   args=(gs,), daemon=True)
    mole_thread.start()
    cleaner_thread.start()

    old_settings = None
    if os.name != 'nt':
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        tty.setcbreak(fd)

    try:
        last_draw = 0
        while remaining(gs) > 0:
            now = time.time()
            if now - last_draw >= 0.1:
                with gs.lock:
                    draw(gs)
                last_draw = now

            ch = get_key_nonblock()
            if ch is None:
                continue

            ch = ch.upper()
            if ch == 'Q':
                gs.running = False
                break

            if ch in KEYS:
                idx = int(KEYS[ch])
                with gs.lock:
                    if gs.holes[idx]:
                        gs.holes[idx]   = False
                        gs.whacked[idx] = True
                        gs.hits        += 1
                        gs.combo       += 1
                        gs.max_combo    = max(gs.max_combo, gs.combo)
                        bonus           = gs.combo // 3
                        pts             = gs.points_each + bonus * 5
                        gs.score       += pts
                        if gs.combo >= 5:
                            gs.message  = f"🔥 COMBO x{gs.combo}! +{pts} pts!"
                        elif gs.combo >= 3:
                            gs.message  = f"⚡ Nice combo! +{pts} pts!"
                        else:
                            gs.message  = f"✅ Whack! +{pts} pts!"
                        gs.msg_time = time.time()
                    else:
                        gs.misses += 1
                        gs.combo   = 0
                        gs.message = "❌ Miss!"
                        gs.msg_time = time.time()

    finally:
        gs.running = False
        if os.name != 'nt' and old_settings:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    with gs.lock:
        draw(gs)

    clear()
    print("=" * 50)
    print("         🔨  GAME OVER!  🔨")
    print("=" * 50)
    acc = (gs.hits / (gs.hits + gs.misses) * 100) if (gs.hits + gs.misses) > 0 else 0
    print(f"""
  Difficulty  : {gs.difficulty.upper()}
  Final Score : {gs.score}
  Hits        : {gs.hits}
  Misses      : {gs.misses}
  Accuracy    : {acc:.1f}%
  Max Combo   : x{gs.max_combo}
  Total Moles : {gs.total_moles}
""")
    if acc >= 80:
        print("  ⭐ OUTSTANDING accuracy!")
    elif acc >= 60:
        print("  👍 Good job!")
    elif acc >= 40:
        print("  😅 Keep practicing!")
    else:
        print("  😬 Moles win this round...")

    if gs.score >= 500:
        print("  🏆 INCREDIBLE SCORE!")
    elif gs.score >= 300:
        print("  🥇 Great score!")
    elif gs.score >= 150:
        print("  🥈 Not bad!")
    else:
        print("  🥉 Room to improve!")

    print("=" * 50)
    input("\n  Press Enter to return to menu...")

def main():
    while True:
        clear()
        print("=" * 50)
        print("       🔨  W H A C K - A - M O L E  🔨")
        print("=" * 50)
        print("""
  How to play:
  • Moles pop up in the 3x3 grid
  • Press the matching numpad key to whack!
  • Build combos for bonus points
  • Miss = combo reset!
""")
        print("  Numpad layout:")
        print(NUMPAD)
        print("  Difficulty:")
        print("   1. Easy   (slow moles, 30s)")
        print("   2. Medium (normal,     45s)")
        print("   3. Hard   (fast,       60s)")
        print("   4. Insane (chaos,      60s)")
        print("   Q. Quit")
        print()

        choice = input("  Choose: ").strip().upper()

        if choice == '1':   play('easy')
        elif choice == '2': play('medium')
        elif choice == '3': play('hard')
        elif choice == '4': play('insane')
        elif choice == 'Q':
            print("\n  Thanks for playing! 🔨 Goodbye!")
            break
        else:
            print("  Invalid choice.")
            time.sleep(0.5)

if __name__ == "__main__":
    main()