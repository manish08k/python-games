import os
import time
import random
import sys
import threading

if os.name == 'nt':
    import msvcrt
else:
    import tty
    import termios
    import select

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')


WIDTH  = 40
HEIGHT = 14

FROG    = '🐸'
CAR1    = '🚗'
CAR2    = '🚕'
TRUCK   = '🚛'
LOG     = '🪵'
WATER   = '🌊'
ROAD    = '░'
SAFE    = '▓'
GOAL    = '🏠'
DEAD    = '💀'
LILY    = '🌸'

LANES = [
    {'type':'safe',  'row':13, 'speed':0,    'dir':0,  'obj':None,   'density':0},
    {'type':'road',  'row':12, 'speed':0.35, 'dir':-1, 'obj':CAR1,   'density':5},
    {'type':'road',  'row':11, 'speed':0.25, 'dir': 1, 'obj':CAR2,   'density':4},
    {'type':'road',  'row':10, 'speed':0.40, 'dir':-1, 'obj':TRUCK,  'density':3},
    {'type':'road',  'row': 9, 'speed':0.20, 'dir': 1, 'obj':CAR1,   'density':5},
    {'type':'road',  'row': 8, 'speed':0.45, 'dir':-1, 'obj':CAR2,   'density':4},
    {'type':'safe',  'row': 7, 'speed':0,    'dir':0,  'obj':None,   'density':0},
    {'type':'water', 'row': 6, 'speed':0.30, 'dir': 1, 'obj':LOG,    'density':4},
    {'type':'water', 'row': 5, 'speed':0.20, 'dir':-1, 'obj':LOG,    'density':3},
    {'type':'water', 'row': 4, 'speed':0.35, 'dir': 1, 'obj':LOG,    'density':4},
    {'type':'water', 'row': 3, 'speed':0.15, 'dir':-1, 'obj':LOG,    'density':3},
    {'type':'water', 'row': 2, 'speed':0.25, 'dir': 1, 'obj':LOG,    'density':4},
    {'type':'safe',  'row': 1, 'speed':0,    'dir':0,  'obj':None,   'density':0},
    {'type':'goal',  'row': 0, 'speed':0,    'dir':0,  'obj':None,   'density':0},
]

class Lane:
    def __init__(self, cfg, width):
        self.type    = cfg['type']
        self.row     = cfg['row']
        self.speed   = cfg['speed']
        self.dir     = cfg['dir']
        self.obj     = cfg['obj']
        self.width   = width
        self.objects = []
        self.offset  = 0.0
        self.last_t  = time.time()
        self._init_objects(cfg['density'])

    def _init_objects(self, density):
        if self.type in ('safe','goal'):
            return
        spacing = self.width // max(density, 1)
        for i in range(density):
            pos = (i * spacing + random.randint(0, spacing-1)) % self.width
            length = 3 if self.obj == TRUCK else (4 if self.obj == LOG else 2)
            self.objects.append({'pos': float(pos), 'len': length})

    def update(self):
        now  = time.time()
        dt   = now - self.last_t
        self.last_t = now
        dist = self.speed * self.dir * dt * 8
        for obj in self.objects:
            obj['pos'] = (obj['pos'] + dist) % self.width



    def get_cells(self):
        cells = {}
        for obj in self.objects:
            p = int(obj['pos'])
            for i in range(obj['len']):
                col = (p + i) % self.width
                cells[col] = self.obj
        return cells

    def on_log(self, col):
        if self.type != 'water':
            return False, 0
        cells = self.get_cells()
        if col in cells:
            for obj in self.objects:
                p = int(obj['pos'])
                for i in range(obj['len']):
                    if (p + i) % self.width == col:
                        return True, self.speed * self.dir * 8
        return False, 0

class Game:
    def __init__(self, difficulty):
        configs = {
            'easy':   {'lives':5, 'speed_mult':0.6, 'time':90},
            'medium': {'lives':3, 'speed_mult':1.0, 'time':60},
            'hard':   {'lives':2, 'speed_mult':1.5, 'time':45},
        }
        cfg              = configs[difficulty]
        self.difficulty  = difficulty
        self.lives       = cfg['lives']
        self.time_limit  = cfg['time']
        self.speed_mult  = cfg['speed_mult']
        self.score       = 0
        self.level       = 1
        self.goals_hit   = 0
        self.goals_needed= 3
        self.running     = True
        self.dead        = False
        self.won         = False
        self.message     = ''
        self.msg_time    = 0
        self.start_time  = time.time()
        self.lock        = threading.Lock()
        self.frog_col    = WIDTH // 2
        self.frog_row    = HEIGHT - 1
        self.best_row    = self.frog_row
        self.goals       = [False] * 5
        self._init_lanes()

    def _init_lanes(self):
        self.lanes = []
        for cfg in LANES:
            c = cfg.copy()
            c['speed'] = c['speed'] * self.speed_mult
            self.lanes.append(Lane(c, WIDTH))

    def get_lane(self, row):
        for l in self.lanes:
            if l.row == row:
                return l
        return None

    def reset_frog(self):
        self.frog_col = WIDTH // 2
        self.frog_row = HEIGHT - 1
        self.best_row = self.frog_row
        self.dead     = False

    def move(self, dr, dc):
        nr = self.frog_row + dr
        nc = self.frog_col + dc
        if nc < 0 or nc >= WIDTH:
            return
        if nr < 0 or nr >= HEIGHT:
            return
        self.frog_row = nr
        self.frog_col = nc
        if self.frog_row < self.best_row:
            pts = (self.best_row - self.frog_row) * 10
            self.score    += pts
            self.best_row  = self.frog_row

    def update(self):
        for lane in self.lanes:
            lane.update()

        lane = self.get_lane(self.frog_row)
        if lane:
            if lane.type == 'water':
                on, vel = lane.on_log(self.frog_col)
                if on:
                    self.frog_col = int((self.frog_col + vel * 0.016)) % WIDTH
                else:
                    self.kill('Splashed! 🌊')
                    return

            elif lane.type == 'road':
                cells = lane.get_cells()
                if self.frog_col in cells:
                    self.kill('Roadkill! 🚗')
                    return

            elif lane.type == 'goal':
                slot = self.frog_col // (WIDTH // 5)
                slot = min(slot, 4)
                if not self.goals[slot]:
                    self.goals[slot] = True
                    self.goals_hit  += 1
                    self.score      += 200 + int(self.time_remaining() * 2)
                    self.message     = f'🏠 HOME! +200 pts!'
                    self.msg_time    = time.time()
                    self.reset_frog()
                    if self.goals_hit >= self.goals_needed:
                        self.score += 500
                        self.won    = True
                        self.running= False
                else:
                    self.kill('Occupied! 🏠')

    def kill(self, msg):
        self.lives  -= 1
        self.message = f'💀 {msg} Lives left: {self.lives}'
        self.msg_time= time.time()
        self.dead    = True
        self.score   = max(0, self.score - 50)
        if self.lives <= 0:
            self.running = False

    def time_remaining(self):
        return max(0, self.time_limit - (time.time() - self.start_time))

def render(game):
    clear()
    tr = game.time_remaining()
    bar_len = 25
    filled  = int((tr / game.time_limit) * bar_len)
    bar     = '█' * filled + '░' * (bar_len - filled)

    print("=" * 52)
    print("          🐸  F R O G G E R  🐸")
    print("=" * 52)
    print(f"  ⏱ [{bar}] {tr:4.0f}s  |  🏆 {game.score}  |  ❤️  {'♥ '*game.lives}")
    print(f"  Level: {game.level}  Goals: {'🏠' * game.goals_hit}{'⬜' * (game.goals_needed - game.goals_hit)}  Difficulty: {game.difficulty}")
    print("=" * 52)

    for row in range(HEIGHT):
        lane = game.get_lane(row)
        line = ""

        if lane and lane.type == 'goal':
            goal_line = ""
            slot_w    = WIDTH // 5
            for s in range(5):
                center = s * slot_w + slot_w // 2
                if game.goals[s]:
                    goal_line += (GOAL + ' ' * (slot_w - 1))
                elif row == game.frog_row and abs(game.frog_col - center) <= slot_w//2:
                    goal_line += (FROG + ' ' * (slot_w - 1))
                else:
                    goal_line += (LILY + ' ' * (slot_w - 1))
            line = "  " + goal_line[:WIDTH*2]

        elif lane and lane.type == 'safe':
            row_chars = [SAFE] * WIDTH
            if row == game.frog_row:
                row_chars[min(game.frog_col, WIDTH-1)] = FROG
            line = "  " + ''.join(row_chars)

        elif lane and lane.type == 'water':
            cells     = lane.get_cells()
            row_chars = []
            for c in range(WIDTH):
                if c == game.frog_col and row == game.frog_row:
                    row_chars.append(FROG)
                elif c in cells:
                    row_chars.append(LOG)
                else:
                    row_chars.append(WATER)
            line = "  " + ''.join(row_chars)

        elif lane and lane.type == 'road':
            cells     = lane.get_cells()
            row_chars = []
            for c in range(WIDTH):
                if c == game.frog_col and row == game.frog_row:
                    row_chars.append(DEAD if game.dead else FROG)
                elif c in cells:
                    row_chars.append(cells[c])
                else:
                    row_chars.append(ROAD)
            line = "  " + ''.join(row_chars)

        else:
            row_chars = [ROAD] * WIDTH
            if row == game.frog_row:
                row_chars[min(game.frog_col, WIDTH-1)] = FROG
            line = "  " + ''.join(row_chars)

        print(line)

    print("=" * 52)
    now = time.time()
    if game.message and (now - game.msg_time) < 2.0:
        print(f"  {game.message}")
    else:
        print("  W=Up  S=Down  A=Left  D=Right  Q=Quit")
    print("=" * 52)

def get_key():
    if os.name == 'nt':
        if msvcrt.kbhit():
            ch = msvcrt.getch()
            try:    return ch.decode('utf-8').upper()
            except: return ''
        return None
    else:
        r, _, _ = select.select([sys.stdin], [], [], 0.05)
        if r:
            return sys.stdin.read(1).upper()
        return None

def play(difficulty):
    game        = Game(difficulty)
    old_settings= None

    if os.name != 'nt':
        fd           = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        tty.setcbreak(fd)

    try:
        last_update = time.time()
        last_draw   = time.time()

        while game.running:
            now = time.time()

            if game.time_remaining() <= 0:
                game.message = "⏰ Time's up!"
                game.running = False
                break

            if now - last_update >= 0.016:
                with game.lock:
                    if not game.dead:
                        game.update()
                last_update = now

            if now - last_draw >= 0.1:
                with game.lock:
                    render(game)
                last_draw = now

            ch = get_key()
            if ch:
                if ch == 'Q':
                    game.running = False
                    break
                with game.lock:
                    if game.dead:
                        game.reset_frog()
                    else:
                        if ch == 'W': game.move(-1,  0)
                        elif ch == 'S': game.move( 1,  0)
                        elif ch == 'A': game.move( 0, -1)
                        elif ch == 'D': game.move( 0,  1)

    finally:
        if os.name != 'nt' and old_settings:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    clear()
    print("=" * 50)
    if game.won:
        print("  🎉 YOU WIN! All frogs made it home!")
    elif game.lives <= 0:
        print("  💀 GAME OVER! No more lives!")
    else:
        print("  ⏰ TIME'S UP!")
    print("=" * 50)
    print(f"""
  Difficulty : {game.difficulty.upper()}
  Final Score: {game.score}
  Homes      : {game.goals_hit}/{game.goals_needed}
  Lives left : {game.lives}
""")
    if game.won:
        print("  🏆 AMAZING! You saved all the frogs!")
    elif game.score >= 500:
        print("  👍 Great effort!")
    else:
        print("  🐸 The road is dangerous. Try again!")
    print("=" * 50)
    input("\n  Press Enter to return to menu...")

def main():
    while True:
        clear()
        print("=" * 50)
        print("          🐸  F R O G G E R  🐸")
        print("=" * 50)
        print("""
  How to play:
  • Guide your frog from bottom to top
  • Avoid cars on the road — instant death!
  • Hop on logs to cross the river
  • Reach the homes at the top to score
  • Get all homes before time runs out!

  Controls: W=Up  S=Down  A=Left  D=Right
""")
        print("  Difficulty:")
        print("   1. Easy   (5 lives, slow traffic, 90s)")
        print("   2. Medium (3 lives, normal,       60s)")
        print("   3. Hard   (2 lives, fast traffic, 45s)")
        print("   Q. Quit")
        print()

        choice = input("  Choose: ").strip().upper()
        if choice == '1':    play('easy')
        elif choice == '2':  play('medium')
        elif choice == '3':  play('hard')
        elif choice == 'Q':
            print("\n  Thanks for playing Frogger! 🐸 Goodbye!")
            break
        else:
            print("  Invalid choice.")
            time.sleep(0.5)

if __name__ == "__main__":
    main()