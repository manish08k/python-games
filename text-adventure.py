import pygame
import sys
import random
import textwrap

pygame.init()
FPS = 60

W, H = 1100, 700
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Text Adventure RPG")
clock = pygame.time.Clock()

# Colors
BG       = (10, 12, 18)
PANEL    = (18, 22, 32)
BORDER   = (45, 55, 80)
WHITE    = (220, 225, 235)
GRAY     = (120, 130, 150)
YELLOW   = (255, 210, 60)
GREEN    = (80, 200, 120)
RED      = (220, 70, 70)
BLUE     = (80, 150, 255)
CYAN     = (60, 210, 220)
PURPLE   = (180, 100, 255)
ORANGE   = (255, 150, 60)
DARK_RED = (140, 30, 30)

F_MAIN  = pygame.font.SysFont("consolas", 15)
F_SMALL = pygame.font.SysFont("consolas", 13)
F_BIG   = pygame.font.SysFont("consolas", 18, bold=True)
F_TITLE = pygame.font.SysFont("consolas", 26, bold=True)
F_TINY  = pygame.font.SysFont("consolas", 11)

# ── World Data ─────────────────────────────────────────────────────────────
ROOMS = {
    'village': {
        'name': 'Ashveil Village',
        'desc': 'A small village shrouded in mist. Stone cottages line a muddy road. The villagers look frightened.',
        'exits': {'north': 'forest', 'east': 'blacksmith', 'south': 'tavern'},
        'enemies': [],
        'items': ['old_map'],
        'color': GREEN,
        'icon': '🏘'
    },
    'tavern': {
        'name': 'The Rusty Flagon',
        'desc': 'A dimly lit tavern. The barkeep polishes a mug and eyes you suspiciously. A wanted poster hangs on the wall.',
        'exits': {'north': 'village'},
        'enemies': [],
        'items': ['health_potion', 'ale'],
        'color': YELLOW,
        'icon': '🍺'
    },
    'blacksmith': {
        'name': "Gorran's Forge",
        'desc': 'The forge blazes with heat. Weapons and armor line the walls. The smith looks up from his work.',
        'exits': {'west': 'village'},
        'enemies': [],
        'items': ['iron_sword', 'leather_armor'],
        'color': ORANGE,
        'icon': '⚒'
    },
    'forest': {
        'name': 'Darkwood Forest',
        'desc': 'Ancient trees block the sky. Strange sounds echo. The path ahead is barely visible.',
        'exits': {'south': 'village', 'north': 'ruins', 'east': 'swamp'},
        'enemies': ['wolf', 'goblin'],
        'items': ['herbs'],
        'color': (60, 160, 80),
        'icon': '🌲'
    },
    'swamp': {
        'name': 'Murkmire Swamp',
        'desc': 'Putrid water surrounds rotting trees. Things move beneath the surface. The air is thick and foul.',
        'exits': {'west': 'forest', 'north': 'cave'},
        'enemies': ['swamp_troll', 'giant_frog'],
        'items': ['poison_vial'],
        'color': (80, 130, 60),
        'icon': '🌿'
    },
    'cave': {
        'name': 'Shadowmaw Cave',
        'desc': 'A yawning cave mouth drips with moisture. Glowing eyes peer from the darkness within.',
        'exits': {'south': 'swamp', 'deeper': 'lair'},
        'enemies': ['cave_bat', 'stone_golem'],
        'items': ['magic_crystal'],
        'color': GRAY,
        'icon': '🗻'
    },
    'ruins': {
        'name': 'Ancient Ruins',
        'desc': 'Crumbling towers of a lost civilization. Arcane runes pulse faintly. Magic hangs heavy in the air.',
        'exits': {'south': 'forest', 'west': 'cave', 'enter': 'lair'},
        'enemies': ['skeleton', 'dark_mage'],
        'items': ['spell_tome', 'gold_coins'],
        'color': PURPLE,
        'icon': '🏛'
    },
    'lair': {
        'name': "The Dragon's Lair",
        'desc': 'An enormous cavern lit by rivers of lava. Mountains of gold surround a massive sleeping dragon. This is the final challenge.',
        'exits': {'back': 'ruins'},
        'enemies': ['ancient_dragon'],
        'items': ['dragon_scale'],
        'color': RED,
        'icon': '🐉'
    }
}

ITEMS = {
    'old_map':       {'name': 'Old Map',        'type': 'misc',   'desc': 'A weathered map of the region.',    'value': 5},
    'health_potion': {'name': 'Health Potion',  'type': 'heal',   'desc': 'Restores 40 HP.',                   'heal': 40,  'value': 20},
    'ale':           {'name': 'Mug of Ale',     'type': 'heal',   'desc': 'Restores 10 HP.',                   'heal': 10,  'value': 5},
    'iron_sword':    {'name': 'Iron Sword',     'type': 'weapon', 'desc': 'A sturdy iron blade. +10 ATK.',     'atk': 10,   'value': 50},
    'leather_armor': {'name': 'Leather Armor',  'type': 'armor',  'desc': 'Basic protection. +8 DEF.',         'def': 8,    'value': 40},
    'herbs':         {'name': 'Healing Herbs',  'type': 'heal',   'desc': 'Restores 20 HP.',                   'heal': 20,  'value': 10},
    'poison_vial':   {'name': 'Poison Vial',    'type': 'weapon', 'desc': 'Coats weapon. +15 ATK.',            'atk': 15,   'value': 35},
    'magic_crystal': {'name': 'Magic Crystal',  'type': 'weapon', 'desc': 'Channels magic. +20 ATK.',          'atk': 20,   'value': 80},
    'spell_tome':    {'name': 'Spell Tome',     'type': 'weapon', 'desc': 'Ancient spells. +25 ATK.',          'atk': 25,   'value': 100},
    'gold_coins':    {'name': 'Gold Coins',     'type': 'misc',   'desc': 'A handful of gold.',                'value': 30},
    'dragon_scale':  {'name': 'Dragon Scale',   'type': 'armor',  'desc': 'Legendary armor. +40 DEF.',         'def': 40,   'value': 500},
}

ENEMIES = {
    'wolf':          {'name': 'Forest Wolf',     'hp': 30,  'atk': 8,  'def': 2,  'exp': 20,  'gold': 5,   'color': GRAY},
    'goblin':        {'name': 'Goblin Scout',    'hp': 25,  'atk': 6,  'def': 1,  'exp': 15,  'gold': 8,   'color': GREEN},
    'swamp_troll':   {'name': 'Swamp Troll',     'hp': 70,  'atk': 15, 'def': 5,  'exp': 50,  'gold': 20,  'color': (100,140,60)},
    'giant_frog':    {'name': 'Giant Frog',      'hp': 40,  'atk': 10, 'def': 3,  'exp': 30,  'gold': 10,  'color': GREEN},
    'cave_bat':      {'name': 'Giant Cave Bat',  'hp': 35,  'atk': 12, 'def': 2,  'exp': 25,  'gold': 8,   'color': PURPLE},
    'stone_golem':   {'name': 'Stone Golem',     'hp': 90,  'atk': 18, 'def': 10, 'exp': 70,  'gold': 30,  'color': GRAY},
    'skeleton':      {'name': 'Skeleton Warrior','hp': 55,  'atk': 14, 'def': 6,  'exp': 45,  'gold': 15,  'color': WHITE},
    'dark_mage':     {'name': 'Dark Mage',       'hp': 60,  'atk': 22, 'def': 4,  'exp': 60,  'gold': 40,  'color': PURPLE},
    'ancient_dragon':{'name': 'Ancient Dragon',  'hp': 250, 'atk': 40, 'def': 20, 'exp': 500, 'gold': 300, 'color': RED},
}

# ── Player ─────────────────────────────────────────────────────────────────
player = {
    'name': 'Hero',
    'hp': 100, 'max_hp': 100,
    'atk': 15, 'def': 5,
    'level': 1, 'exp': 0, 'exp_next': 100,
    'gold': 10,
    'location': 'village',
    'inventory': [],
    'weapon': None,
    'armor': None,
    'visited': {'village'},
    'kills': 0,
    'steps': 0,
}

# ── Game State ──────────────────────────────────────────────────────────────
room_items   = {k: list(v['items']) for k, v in ROOMS.items()}
combat       = None   # current enemy in combat
log          = []
input_text   = ""
input_active = True
game_over    = False
game_won     = False

# ── Helpers ────────────────────────────────────────────────────────────────
def add_log(text, color=WHITE):
    lines = textwrap.wrap(text, 62)
    for l in lines:
        log.append((l, color))
    if len(log) > 200:
        log.pop(0)

def level_up():
    player['level'] += 1
    player['max_hp'] += 20
    player['hp'] = min(player['hp'] + 20, player['max_hp'])
    player['atk'] += 5
    player['def'] += 2
    add_log(f"★ LEVEL UP! You are now level {player['level']}!", YELLOW)
    add_log(f"  HP+20 ATK+5 DEF+2", YELLOW)

def gain_exp(amount):
    player['exp'] += amount
    while player['exp'] >= player['exp_next']:
        player['exp'] -= player['exp_next']
        player['exp_next'] = int(player['exp_next'] * 1.5)
        level_up()

def player_atk_total():
    base = player['atk']
    if player['weapon']:
        base += ITEMS[player['weapon']].get('atk', 0)
    return base

def player_def_total():
    base = player['def']
    if player['armor']:
        base += ITEMS[player['armor']].get('def', 0)
    return base

def spawn_enemy(room_id):
    pool = ROOMS[room_id]['enemies']
    if not pool: return None
    eid  = random.choice(pool)
    base = ENEMIES[eid]
    return {
        'id':   eid,
        'name': base['name'],
        'hp':   base['hp'],
        'max_hp': base['hp'],
        'atk': base['atk'],
        'def': base['def'],
        'exp': base['exp'],
        'gold':base['gold'],
        'color':base['color'],
    }

def enter_room(room_id):
    global combat
    player['location'] = room_id
    player['visited'].add(room_id)
    player['steps'] += 1
    room = ROOMS[room_id]
    add_log(f"\n[ {room['name']} ]", room['color'])
    add_log(room['desc'], GRAY)
    exits = ', '.join(f"{d}→{ROOMS[t]['name']}" for d, t in room['exits'].items())
    add_log(f"Exits: {exits}", CYAN)
    items = room_items.get(room_id, [])
    if items:
        names = ', '.join(ITEMS[i]['name'] for i in items)
        add_log(f"Items here: {names}", YELLOW)
    # Random encounter
    if room['enemies'] and random.random() < 0.6:
        enemy = spawn_enemy(room_id)
        if enemy:
            combat = enemy
            add_log(f"\n⚔  A {enemy['name']} appears!", RED)
            add_log("Commands: attack, flee, use <item>", ORANGE)

def process_command(cmd):
    global combat, game_over, game_won
    cmd = cmd.strip().lower()
    if not cmd:
        return

    add_log(f"> {cmd}", CYAN)

    if game_over or game_won:
        add_log("The adventure is over. Close and restart to play again.", GRAY)
        return

    # ── Combat ──
    if combat:
        enemy = combat
        if cmd in ('a', 'attack'):
            # Player attacks
            dmg = max(1, player_atk_total() - enemy['def'] + random.randint(-3, 5))
            enemy['hp'] -= dmg
            add_log(f"You strike {enemy['name']} for {dmg} damage!", GREEN)
            if enemy['hp'] <= 0:
                add_log(f"You defeated {enemy['name']}!", YELLOW)
                add_log(f"  +{enemy['exp']} EXP  +{enemy['gold']} Gold", YELLOW)
                player['gold']  += enemy['gold']
                player['kills'] += 1
                gain_exp(enemy['exp'])
                if enemy['id'] == 'ancient_dragon':
                    game_won = True
                    add_log("\n🐉 THE DRAGON FALLS! YOU ARE VICTORIOUS! 🐉", YELLOW)
                    add_log("You have saved the realm of Ashveil!", YELLOW)
                combat = None
                return
            # Enemy attacks
            edef = player_def_total()
            edm  = max(1, enemy['atk'] - edef + random.randint(-2, 4))
            player['hp'] -= edm
            add_log(f"{enemy['name']} hits you for {edm} damage!", RED)
            if player['hp'] <= 0:
                player['hp'] = 0
                game_over = True
                add_log("\n☠  YOU HAVE DIED... Game Over.", RED)

        elif cmd in ('f', 'flee', 'run'):
            if random.random() < 0.5:
                add_log("You successfully flee!", GRAY)
                combat = None
                exits  = list(ROOMS[player['location']]['exits'].values())
                if exits:
                    enter_room(random.choice(exits))
            else:
                edm = max(1, enemy['atk'] - player_def_total())
                player['hp'] -= edm
                add_log(f"Failed to flee! {enemy['name']} hits you for {edm}!", RED)
                if player['hp'] <= 0:
                    game_over = True
                    add_log("☠  YOU HAVE DIED... Game Over.", RED)

        elif cmd.startswith('use '):
            item_name = cmd[4:].strip()
            use_item(item_name, in_combat=True)
        else:
            add_log("In combat: attack (a), flee (f), use <item>", ORANGE)
        return

    # ── Exploration ──
    tokens = cmd.split()
    verb   = tokens[0]
    args   = tokens[1:]

    if verb in ('go', 'move', 'travel') and args:
        direction = args[0]
        exits = ROOMS[player['location']]['exits']
        if direction in exits:
            enter_room(exits[direction])
        else:
            add_log(f"You can't go {direction} from here.", GRAY)

    elif verb in ROOMS[player['location']]['exits']:
        enter_room(ROOMS[player['location']]['exits'][verb])

    elif verb in ('n','north','s','south','e','east','w','west','up','down','deeper','back','enter'):
        dir_map = {'n':'north','s':'south','e':'east','w':'west'}
        d = dir_map.get(verb, verb)
        exits = ROOMS[player['location']]['exits']
        if d in exits:
            enter_room(exits[d])
        else:
            add_log(f"Can't go that way.", GRAY)

    elif verb in ('look', 'l', 'examine'):
        loc  = player['location']
        room = ROOMS[loc]
        add_log(f"\n[ {room['name']} ]", room['color'])
        add_log(room['desc'], GRAY)
        exits = ', '.join(f"{d}" for d in room['exits'])
        add_log(f"Exits: {exits}", CYAN)
        items = room_items.get(loc, [])
        if items:
            add_log("Items: " + ', '.join(ITEMS[i]['name'] for i in items), YELLOW)

    elif verb in ('get', 'take', 'pick') and args:
        item_name = ' '.join(args)
        items = room_items.get(player['location'], [])
        found = next((i for i in items if ITEMS[i]['name'].lower() == item_name or i == item_name), None)
        if found:
            player['inventory'].append(found)
            room_items[player['location']].remove(found)
            add_log(f"Picked up: {ITEMS[found]['name']}", YELLOW)
        else:
            add_log(f"No '{item_name}' here.", GRAY)

    elif verb in ('inventory', 'inv', 'i'):
        if not player['inventory']:
            add_log("Inventory is empty.", GRAY)
        else:
            add_log("Inventory:", CYAN)
            for item in player['inventory']:
                it = ITEMS[item]
                equipped = ""
                if player['weapon'] == item: equipped = " [WEAPON]"
                if player['armor']  == item: equipped = " [ARMOR]"
                add_log(f"  {it['name']}{equipped} - {it['desc']}", WHITE)

    elif verb == 'use' and args:
        use_item(' '.join(args))

    elif verb in ('equip', 'wield', 'wear') and args:
        item_name = ' '.join(args)
        found = next((i for i in player['inventory'] if ITEMS[i]['name'].lower() == item_name or i == item_name), None)
        if found:
            it = ITEMS[found]
            if it['type'] == 'weapon':
                player['weapon'] = found
                add_log(f"Equipped {it['name']} as weapon.", GREEN)
            elif it['type'] == 'armor':
                player['armor'] = found
                add_log(f"Equipped {it['name']} as armor.", GREEN)
            else:
                add_log("That item can't be equipped.", GRAY)
        else:
            add_log("Item not in inventory.", GRAY)

    elif verb in ('stats', 'status', 'char'):
        add_log(f"\n── {player['name']} ──", CYAN)
        add_log(f"Level {player['level']}  HP:{player['hp']}/{player['max_hp']}  Gold:{player['gold']}", WHITE)
        add_log(f"ATK:{player_atk_total()}  DEF:{player_def_total()}  EXP:{player['exp']}/{player['exp_next']}", WHITE)
        add_log(f"Kills:{player['kills']}  Steps:{player['steps']}", GRAY)
        if player['weapon']: add_log(f"Weapon: {ITEMS[player['weapon']]['name']}", YELLOW)
        if player['armor']:  add_log(f"Armor:  {ITEMS[player['armor']]['name']}", YELLOW)

    elif verb in ('help', '?'):
        add_log("── Commands ──", CYAN)
        add_log("go <dir> / north/south/east/west", WHITE)
        add_log("look  |  get <item>  |  inventory", WHITE)
        add_log("use <item>  |  equip <item>", WHITE)
        add_log("stats  |  help", WHITE)
        add_log("In combat: attack (a)  |  flee (f)  |  use <item>", ORANGE)

    else:
        add_log(f"Unknown command: '{cmd}'. Type 'help' for commands.", GRAY)


def use_item(item_name, in_combat=False):
    found = next((i for i in player['inventory'] if ITEMS[i]['name'].lower() == item_name or i == item_name), None)
    if not found:
        add_log(f"No '{item_name}' in inventory.", GRAY)
        return
    it = ITEMS[found]
    if it['type'] == 'heal':
        heal = it.get('heal', 0)
        player['hp'] = min(player['hp'] + heal, player['max_hp'])
        add_log(f"Used {it['name']}. Restored {heal} HP. ({player['hp']}/{player['max_hp']})", GREEN)
        player['inventory'].remove(found)
    elif it['type'] in ('weapon', 'armor'):
        if it['type'] == 'weapon':
            player['weapon'] = found
            add_log(f"Equipped {it['name']}. ATK now {player_atk_total()}.", GREEN)
        else:
            player['armor'] = found
            add_log(f"Equipped {it['name']}. DEF now {player_def_total()}.", GREEN)
    else:
        add_log(f"You examine the {it['name']}. {it['desc']}", GRAY)

# ── Drawing ────────────────────────────────────────────────────────────────
LOG_X, LOG_Y = 10, 10
LOG_W, LOG_H = 680, 460
INP_X, INP_Y = 10, 478
INP_W, INP_H = 680, 36
MAP_X, MAP_Y = 700, 10
MAP_W, MAP_H = 390, 320
STAT_X, STAT_Y = 700, 340
STAT_W, STAT_H = 390, 200
MINI_X, MINI_Y = 700, 548
MINI_W, MINI_H = 390, 140

scroll_offset = 0

def draw_panel(rect, title=None, border_color=BORDER):
    pygame.draw.rect(screen, PANEL, rect, border_radius=6)
    pygame.draw.rect(screen, border_color, rect, 1, border_radius=6)
    if title:
        ts = F_SMALL.render(title, True, GRAY)
        screen.blit(ts, (rect[0]+8, rect[1]+4))

def draw_bar(x, y, w, h, val, mx, col_full, col_empty=DARK_RED):
    pygame.draw.rect(screen, col_empty, (x, y, w, h), border_radius=3)
    fw = int(w * max(0, val) / max(1, mx))
    if fw > 0:
        pygame.draw.rect(screen, col_full, (x, y, fw, h), border_radius=3)

def draw_log():
    global scroll_offset
    pygame.draw.rect(screen, PANEL, (LOG_X, LOG_Y, LOG_W, LOG_H), border_radius=6)
    pygame.draw.rect(screen, BORDER, (LOG_X, LOG_Y, LOG_W, LOG_H), 1, border_radius=6)

    line_h   = 18
    visible  = (LOG_H - 16) // line_h
    total    = len(log)
    max_scroll = max(0, total - visible)
    if scroll_offset > max_scroll: scroll_offset = max_scroll

    start = max(0, total - visible - scroll_offset)
    end   = start + visible

    clip = pygame.Rect(LOG_X+4, LOG_Y+4, LOG_W-8, LOG_H-8)
    screen.set_clip(clip)
    for idx, (line, color) in enumerate(log[start:end]):
        ts = F_MAIN.render(line, True, color)
        screen.blit(ts, (LOG_X+8, LOG_Y+8 + idx*line_h))
    screen.set_clip(None)

    if scroll_offset > 0:
        hint = F_TINY.render(f"▲ scrolled ({scroll_offset} lines) ▲", True, GRAY)
        screen.blit(hint, (LOG_X+8, LOG_Y+LOG_H-16))

def draw_input():
    col = BLUE if input_active else BORDER
    pygame.draw.rect(screen, (20, 25, 38), (INP_X, INP_Y, INP_W, INP_H), border_radius=5)
    pygame.draw.rect(screen, col, (INP_X, INP_Y, INP_W, INP_H), 1, border_radius=5)
    prompt = F_MAIN.render("> " + input_text + ("█" if pygame.time.get_ticks()//500 % 2 == 0 else " "), True, WHITE)
    screen.blit(prompt, (INP_X+8, INP_Y+9))

def draw_map():
    draw_panel((MAP_X, MAP_Y, MAP_W, MAP_H), "  ◈ WORLD MAP")
    # Simple node map
    positions = {
        'village':    (195, 180),
        'tavern':     (195, 240),
        'blacksmith': (300, 180),
        'forest':     (195, 110),
        'swamp':      (310, 110),
        'cave':       (310, 55),
        'ruins':      (120, 55),
        'lair':       (215, 30),
    }
    # Draw connections
    for room_id, room in ROOMS.items():
        if room_id not in positions: continue
        rx, ry = MAP_X + positions[room_id][0], MAP_Y + positions[room_id][1]
        for d, target in room['exits'].items():
            if target in positions:
                tx, ty = MAP_X + positions[target][0], MAP_Y + positions[target][1]
                col = (40, 50, 70)
                pygame.draw.line(screen, col, (rx, ry), (tx, ty), 1)

    for room_id, (rx, ry) in positions.items():
        ax, ay = MAP_X + rx, MAP_Y + ry
        visited = room_id in player['visited']
        current = room_id == player['location']
        room    = ROOMS[room_id]
        r = 14 if current else 10
        col = room['color'] if visited else (40, 50, 70)
        pygame.draw.circle(screen, col, (ax, ay), r)
        pygame.draw.circle(screen, WHITE if current else BORDER, (ax, ay), r, 1 if not current else 2)
        if visited:
            nm = F_TINY.render(room['name'].split()[0], True, WHITE if current else GRAY)
            screen.blit(nm, (ax - nm.get_width()//2, ay + r + 2))
        if current:
            you = F_TINY.render("YOU", True, YELLOW)
            screen.blit(you, (ax - you.get_width()//2, ay - r - 12))

def draw_stats():
    draw_panel((STAT_X, STAT_Y, STAT_W, STAT_H), "  ◈ CHARACTER")
    x, y = STAT_X+10, STAT_Y+22

    loc_name = ROOMS[player['location']]['name']
    ts = F_BIG.render(player['name'], True, YELLOW)
    screen.blit(ts, (x, y)); y += 24

    lv = F_SMALL.render(f"Level {player['level']}   Location: {loc_name}", True, GRAY)
    screen.blit(lv, (x, y)); y += 20

    # HP bar
    screen.blit(F_SMALL.render(f"HP  {player['hp']}/{player['max_hp']}", True, GREEN), (x, y))
    draw_bar(x+120, y+3, 240, 11, player['hp'], player['max_hp'], GREEN)
    y += 20

    # EXP bar
    screen.blit(F_SMALL.render(f"EXP {player['exp']}/{player['exp_next']}", True, BLUE), (x, y))
    draw_bar(x+120, y+3, 240, 11, player['exp'], player['exp_next'], BLUE)
    y += 22

    row = [
        (f"ATK  {player_atk_total()}", ORANGE),
        (f"DEF  {player_def_total()}", CYAN),
        (f"GOLD {player['gold']}", YELLOW),
    ]
    for label, col in row:
        ts = F_SMALL.render(label, True, col)
        screen.blit(ts, (x, y)); y += 18

    if player['weapon']:
        ts = F_SMALL.render(f"Wpn: {ITEMS[player['weapon']]['name']}", True, ORANGE)
        screen.blit(ts, (x, y)); y += 18
    if player['armor']:
        ts = F_SMALL.render(f"Arm: {ITEMS[player['armor']]['name']}", True, CYAN)
        screen.blit(ts, (x, y)); y += 18

def draw_combat():
    if not combat: return
    draw_panel((MINI_X, MINI_Y, MINI_W, MINI_H), "  ⚔  COMBAT", RED)
    x, y = MINI_X+10, MINI_Y+22
    en = combat
    ts = F_BIG.render(en['name'], True, en['color'])
    screen.blit(ts, (x, y)); y += 26
    screen.blit(F_SMALL.render(f"HP  {en['hp']}/{en['max_hp']}", True, RED), (x, y))
    draw_bar(x+110, y+3, 250, 11, en['hp'], en['max_hp'], RED)
    y += 20
    screen.blit(F_SMALL.render(f"ATK {en['atk']}   DEF {en['def']}", True, ORANGE), (x, y)); y += 20
    hint = F_SMALL.render("attack (a)  |  flee (f)  |  use <item>", True, GRAY)
    screen.blit(hint, (x, y))

def draw_inventory_mini():
    if combat: return
    draw_panel((MINI_X, MINI_Y, MINI_W, MINI_H), "  ◈ INVENTORY")
    x, y = MINI_X+10, MINI_Y+22
    if not player['inventory']:
        screen.blit(F_SMALL.render("Empty", True, GRAY), (x, y))
        return
    for item in player['inventory'][:6]:
        it = ITEMS[item]
        eq = " ●" if (player['weapon']==item or player['armor']==item) else ""
        ts = F_SMALL.render(f"{it['name']}{eq}", True, YELLOW if eq else WHITE)
        screen.blit(ts, (x, y)); y += 19
    if len(player['inventory']) > 6:
        screen.blit(F_TINY.render(f"+{len(player['inventory'])-6} more...", True, GRAY), (x, y))

def draw_overlay():
    if game_won:
        ov = pygame.Surface((W, H), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 160))
        screen.blit(ov, (0, 0))
        t1 = F_TITLE.render("VICTORY!", True, YELLOW)
        t2 = F_BIG.render("You have slain the Ancient Dragon!", True, WHITE)
        t3 = F_BIG.render("The realm of Ashveil is saved!", True, GREEN)
        screen.blit(t1, t1.get_rect(center=(W//2, H//2-50)))
        screen.blit(t2, t2.get_rect(center=(W//2, H//2)))
        screen.blit(t3, t3.get_rect(center=(W//2, H//2+40)))
    elif game_over:
        ov = pygame.Surface((W, H), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 180))
        screen.blit(ov, (0, 0))
        t1 = F_TITLE.render("YOU DIED", True, RED)
        t2 = F_BIG.render(f"Reached level {player['level']} with {player['kills']} kills", True, GRAY)
        screen.blit(t1, t1.get_rect(center=(W//2, H//2-30)))
        screen.blit(t2, t2.get_rect(center=(W//2, H//2+20)))

# ── Init ───────────────────────────────────────────────────────────────────
add_log("╔══════════════════════════════════════════╗", YELLOW)
add_log("║     ASHVEIL - Text Adventure RPG         ║", YELLOW)
add_log("╚══════════════════════════════════════════╝", YELLOW)
add_log("Type 'help' for commands.", GRAY)
enter_room('village')

# ── Main Loop ──────────────────────────────────────────────────────────────
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit(); sys.exit()

        if event.type == pygame.MOUSEWHEEL:
            scroll_offset = max(0, scroll_offset - event.y * 2)

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                cmd = input_text.strip()
                input_text = ""
                scroll_offset = 0
                if cmd:
                    process_command(cmd)
            elif event.key == pygame.K_BACKSPACE:
                input_text = input_text[:-1]
            else:
                if len(input_text) < 60:
                    input_text += event.unicode

    screen.fill(BG)
    draw_log()
    draw_input()
    draw_map()
    draw_stats()
    if combat:
        draw_combat()
    else:
        draw_inventory_mini()
    draw_overlay()

    pygame.display.flip()
    clock.tick(FPS)