import random
import time

# ============================================================
#  DICE RPG - Terminal Adventure
# ============================================================

def roll(sides=6, count=1):
    return sum(random.randint(1, sides) for _ in range(count))

def slow_print(text, delay=0.03):
    for ch in text:
        print(ch, end='', flush=True)
        time.sleep(delay)
    print()

def show_bar(current, maximum, width=20, fill='█', empty='░'):
    filled = int((current / maximum) * width)
    bar = fill * filled + empty * (width - filled)
    return f"[{bar}] {current}/{maximum}"

# ============================================================
#  CHARACTER CLASSES
# ============================================================

CLASSES = {
    '1': {
        'name': 'Warrior',
        'emoji': '⚔️',
        'hp': 120, 'mp': 30,
        'atk': 15, 'def': 10, 'spd': 6,
        'skills': [
            {'name': 'Power Strike',  'mp': 5,  'dmg_dice': (2,8),  'bonus': 5,  'desc': 'A mighty blow'},
            {'name': 'Shield Bash',   'mp': 8,  'dmg_dice': (1,6),  'bonus': 3,  'desc': 'Stuns the enemy', 'stun': True},
            {'name': 'Whirlwind',     'mp': 15, 'dmg_dice': (3,6),  'bonus': 10, 'desc': 'Hits all around'},
        ]
    },
    '2': {
        'name': 'Mage',
        'emoji': '🔮',
        'hp': 70, 'mp': 120,
        'atk': 8, 'def': 4, 'spd': 8,
        'skills': [
            {'name': 'Fireball',      'mp': 15, 'dmg_dice': (3,8),  'bonus': 12, 'desc': 'Blazing explosion'},
            {'name': 'Ice Lance',     'mp': 12, 'dmg_dice': (2,10), 'bonus': 8,  'desc': 'Freezing spear', 'slow': True},
            {'name': 'Thunder Bolt',  'mp': 20, 'dmg_dice': (4,8),  'bonus': 15, 'desc': 'Divine lightning'},
        ]
    },
    '3': {
        'name': 'Rogue',
        'emoji': '🗡️',
        'hp': 90, 'mp': 60,
        'atk': 12, 'def': 6, 'spd': 14,
        'skills': [
            {'name': 'Backstab',      'mp': 10, 'dmg_dice': (3,6),  'bonus': 15, 'desc': 'Critical sneak attack', 'crit': True},
            {'name': 'Poison Blade',  'mp': 8,  'dmg_dice': (1,8),  'bonus': 5,  'desc': 'Poisons enemy', 'poison': True},
            {'name': 'Shadow Step',   'mp': 18, 'dmg_dice': (2,10), 'bonus': 10, 'desc': 'Teleport strike'},
        ]
    },
    '4': {
        'name': 'Paladin',
        'emoji': '🛡️',
        'hp': 110, 'mp': 80,
        'atk': 12, 'def': 14, 'spd': 5,
        'skills': [
            {'name': 'Holy Strike',   'mp': 12, 'dmg_dice': (2,8),  'bonus': 8,  'desc': 'Sacred damage'},
            {'name': 'Divine Heal',   'mp': 20, 'dmg_dice': (0,0),  'bonus': 0,  'desc': 'Restore HP', 'heal': True},
            {'name': 'Smite Evil',    'mp': 25, 'dmg_dice': (4,6),  'bonus': 20, 'desc': 'Massive holy burst'},
        ]
    },
}

# ============================================================
#  ENEMIES
# ============================================================

ENEMY_POOL = [
    {'name': 'Goblin',       'emoji': '👺', 'hp': 40,  'atk': 8,  'def': 3,  'xp': 30,  'gold': (5,15)},
    {'name': 'Skeleton',     'emoji': '💀', 'hp': 55,  'atk': 11, 'def': 5,  'xp': 45,  'gold': (8,20)},
    {'name': 'Orc Warrior',  'emoji': '👹', 'hp': 80,  'atk': 16, 'def': 8,  'xp': 70,  'gold': (15,30)},
    {'name': 'Dark Wizard',  'emoji': '🧙', 'hp': 60,  'atk': 20, 'def': 4,  'xp': 90,  'gold': (20,40)},
    {'name': 'Troll',        'emoji': '🏔️', 'hp': 120, 'atk': 22, 'def': 12, 'xp': 120, 'gold': (25,50)},
    {'name': 'Vampire',      'emoji': '🧛', 'hp': 90,  'atk': 25, 'def': 9,  'xp': 140, 'gold': (30,60)},
    {'name': 'Dragon',       'emoji': '🐉', 'hp': 200, 'atk': 35, 'def': 18, 'xp': 300, 'gold': (80,150)},
]

BOSS = {'name': 'Demon Lord', 'emoji': '😈', 'hp': 350, 'atk': 45, 'def': 20, 'xp': 999, 'gold': (200,300)}

ITEMS = [
    {'name': 'Health Potion',  'emoji': '🧪', 'cost': 50,  'effect': 'heal',   'value': 50},
    {'name': 'Mana Potion',    'emoji': '💧', 'cost': 40,  'effect': 'mana',   'value': 40},
    {'name': 'Elixir',         'emoji': '✨', 'cost': 120, 'effect': 'both',   'value': 60},
    {'name': 'Attack Scroll',  'emoji': '📜', 'cost': 80,  'effect': 'atk',    'value': 5},
    {'name': 'Shield Rune',    'emoji': '🔵', 'cost': 80,  'effect': 'def',    'value': 5},
]

# ============================================================
#  PLAYER & ENEMY CREATION
# ============================================================

def create_player(name, cls):
    c = CLASSES[cls].copy()
    return {
        'name': name,
        'class': c['name'],
        'emoji': c['emoji'],
        'hp': c['hp'], 'max_hp': c['hp'],
        'mp': c['mp'], 'max_mp': c['mp'],
        'atk': c['atk'], 'def': c['def'], 'spd': c['spd'],
        'skills': c['skills'],
        'level': 1, 'xp': 0, 'xp_next': 100,
        'gold': 100,
        'inventory': [ITEMS[0].copy(), ITEMS[1].copy()],
        'kills': 0,
        'status': None,
    }

def create_enemy(template):
    e = template.copy()
    e['max_hp'] = e['hp']
    e['status'] = None
    return e

# ============================================================
#  LEVEL UP
# ============================================================

def check_level_up(player):
    while player['xp'] >= player['xp_next']:
        player['xp'] -= player['xp_next']
        player['level'] += 1
        player['xp_next'] = int(player['xp_next'] * 1.4)
        player['max_hp'] += 15
        player['max_mp'] += 10
        player['hp'] = player['max_hp']
        player['mp'] = player['max_mp']
        player['atk'] += 3
        player['def'] += 2
        slow_print(f"\n🌟 LEVEL UP! You are now Level {player['level']}!")
        slow_print(f"   ❤️  HP: {player['max_hp']}  💙 MP: {player['max_mp']}")
        slow_print(f"   ⚔️  ATK: {player['atk']}  🛡️  DEF: {player['def']}")

# ============================================================
#  STATUS EFFECTS
# ============================================================

def apply_status(entity, status):
    entity['status'] = status
    slow_print(f"   ⚠️  {entity['name']} is {status}!")

def tick_status(entity):
    if entity['status'] == 'poisoned':
        dmg = roll(6)
        entity['hp'] = max(0, entity['hp'] - dmg)
        slow_print(f"   ☠️  {entity['name']} takes {dmg} poison damage!")
    elif entity['status'] == 'stunned':
        entity['status'] = None
        return True  # skip turn
    elif entity['status'] == 'slowed':
        entity['status'] = None
    return False

# ============================================================
#  COMBAT
# ============================================================

def player_attack(player, enemy):
    hit_roll = roll(20)
    if hit_roll == 1:
        slow_print("   💨 MISS! Attack failed!")
        return
    dmg = max(1, player['atk'] + roll(8) - enemy['def'])
    if hit_roll == 20:
        dmg *= 2
        slow_print(f"   💥 CRITICAL HIT! {enemy['emoji']} {enemy['name']} takes {dmg} damage!")
    else:
        slow_print(f"   ⚔️  You deal {dmg} damage to {enemy['emoji']} {enemy['name']}!")
    enemy['hp'] = max(0, enemy['hp'] - dmg)

def player_skill(player, enemy, skill):
    if player['mp'] < skill['mp']:
        slow_print(f"   ❌ Not enough MP! Need {skill['mp']} MP.")
        return False
    player['mp'] -= skill['mp']

    if skill.get('heal'):
        heal = roll(8, 3) + 20
        player['hp'] = min(player['max_hp'], player['hp'] + heal)
        slow_print(f"   💚 {skill['name']}! Restored {heal} HP!")
        return True

    d_count, d_sides = skill['dmg_dice']
    raw = roll(d_sides, d_count) if d_count > 0 else 0
    dmg = max(1, raw + skill['bonus'] + player['atk'] - enemy['def'])

    if skill.get('crit') and roll(6) >= 5:
        dmg = int(dmg * 1.8)
        slow_print(f"   ⚡ CRITICAL {skill['name']}! {dmg} damage!")
    else:
        slow_print(f"   ✨ {skill['name']}! {dmg} damage to {enemy['emoji']} {enemy['name']}!")

    enemy['hp'] = max(0, enemy['hp'] - dmg)
    if skill.get('poison') and roll(6) >= 4:
        apply_status(enemy, 'poisoned')
    if skill.get('stun') and roll(6) >= 4:
        apply_status(enemy, 'stunned')
    if skill.get('slow') and roll(6) >= 4:
        apply_status(enemy, 'slowed')
    return True

def enemy_attack(enemy, player):
    skip = tick_status(enemy)
    if skip:
        slow_print(f"   😵 {enemy['name']} is stunned and loses their turn!")
        return
    hit = roll(20)
    if hit == 1:
        slow_print(f"   💨 {enemy['name']} misses!")
        return
    dmg = max(1, enemy['atk'] + roll(6) - player['def'])
    if hit == 20:
        dmg *= 2
        slow_print(f"   💥 {enemy['emoji']} CRITICAL! You take {dmg} damage!")
    else:
        slow_print(f"   🔴 {enemy['emoji']} {enemy['name']} deals {dmg} damage!")
    player['hp'] = max(0, player['hp'] - dmg)

def show_combat_status(player, enemy):
    print(f"\n  {'─'*45}")
    print(f"  {player['emoji']} {player['name']} (Lv.{player['level']})")
    print(f"  ❤️  HP  {show_bar(player['hp'], player['max_hp'])}")
    print(f"  💙 MP  {show_bar(player['mp'], player['max_mp'])}")
    print(f"  {'─'*45}")
    print(f"  {enemy['emoji']} {enemy['name']}")
    print(f"  ❤️  HP  {show_bar(enemy['hp'], enemy['max_hp'])}")
    if enemy.get('status'):
        print(f"  ⚠️  Status: {enemy['status']}")
    print(f"  {'─'*45}")

def use_item(player):
    if not player['inventory']:
        slow_print("   🎒 Inventory is empty!")
        return False
    print("\n  🎒 Inventory:")
    for i, item in enumerate(player['inventory']):
        print(f"   {i+1}. {item['emoji']} {item['name']}")
    print("   0. Cancel")
    try:
        choice = int(input("  Use item: "))
        if choice == 0:
            return False
        item = player['inventory'].pop(choice - 1)
        if item['effect'] == 'heal':
            player['hp'] = min(player['max_hp'], player['hp'] + item['value'])
            slow_print(f"   💚 Used {item['name']}! +{item['value']} HP")
        elif item['effect'] == 'mana':
            player['mp'] = min(player['max_mp'], player['mp'] + item['value'])
            slow_print(f"   💙 Used {item['name']}! +{item['value']} MP")
        elif item['effect'] == 'both':
            player['hp'] = min(player['max_hp'], player['hp'] + item['value'])
            player['mp'] = min(player['max_mp'], player['mp'] + item['value'])
            slow_print(f"   ✨ Used {item['name']}! +{item['value']} HP & MP")
        elif item['effect'] == 'atk':
            player['atk'] += item['value']
            slow_print(f"   ⚔️  Used {item['name']}! +{item['value']} ATK")
        elif item['effect'] == 'def':
            player['def'] += item['value']
            slow_print(f"   🛡️  Used {item['name']}! +{item['value']} DEF")
        return True
    except (ValueError, IndexError):
        slow_print("   ❌ Invalid choice.")
        return False

def battle(player, enemy_template, is_boss=False):
    enemy = create_enemy(enemy_template)
    slow_print(f"\n⚔️  A wild {enemy['emoji']} {enemy['name']} appears!")
    time.sleep(0.5)

    while player['hp'] > 0 and enemy['hp'] > 0:
        show_combat_status(player, enemy)
        tick_status(player)
        if player['hp'] <= 0:
            break

        print("\n  Actions:")
        print("   1. ⚔️  Attack")
        print("   2. ✨ Skills")
        print("   3. 🎒 Use Item")
        print("   4. 🏃 Flee")

        choice = input("  Your action: ").strip()

        if choice == '1':
            player_attack(player, enemy)
        elif choice == '2':
            print("\n  Skills:")
            for i, sk in enumerate(player['skills']):
                print(f"   {i+1}. {sk['name']} (MP:{sk['mp']}) - {sk['desc']}")
            print("   0. Back")
            sc = input("  Choose skill: ").strip()
            if sc in [str(i+1) for i in range(len(player['skills']))]:
                player_skill(player, enemy, player['skills'][int(sc)-1])
            else:
                continue
        elif choice == '3':
            used = use_item(player)
            if not used:
                continue
        elif choice == '4':
            if roll(6) >= 4:
                slow_print("   🏃 You fled successfully!")
                return 'fled'
            else:
                slow_print("   ❌ Couldn't escape!")
        else:
            slow_print("   ❌ Invalid action.")
            continue

        if enemy['hp'] <= 0:
            break

        time.sleep(0.4)
        enemy_attack(enemy, player)

    if player['hp'] <= 0:
        return 'dead'

    # Victory
    xp_gain = enemy['xp']
    gold_gain = random.randint(*enemy['gold'])
    player['xp'] += xp_gain
    player['gold'] += gold_gain
    player['kills'] += 1
    slow_print(f"\n🏆 Victory! +{xp_gain} XP | +{gold_gain} Gold")
    check_level_up(player)
    return 'won'

# ============================================================
#  SHOP
# ============================================================

def visit_shop(player):
    slow_print("\n🏪 Welcome to the Shop!")
    while True:
        print(f"\n  💰 Gold: {player['gold']}")
        print("  Items for sale:")
        for i, item in enumerate(ITEMS):
            print(f"   {i+1}. {item['emoji']} {item['name']:15} - {item['cost']} gold")
        print("   0. Leave shop")
        choice = input("  Buy: ").strip()
        if choice == '0':
            break
        try:
            item = ITEMS[int(choice)-1]
            if player['gold'] >= item['cost']:
                player['gold'] -= item['cost']
                player['inventory'].append(item.copy())
                slow_print(f"   ✅ Bought {item['name']}!")
            else:
                slow_print("   ❌ Not enough gold!")
        except (ValueError, IndexError):
            slow_print("   ❌ Invalid choice.")

# ============================================================
#  SHOW STATS
# ============================================================

def show_stats(player):
    print(f"\n{'='*45}")
    print(f"  {player['emoji']} {player['name']} - {player['class']}")
    print(f"  Level: {player['level']}  XP: {player['xp']}/{player['xp_next']}")
    print(f"  ❤️  HP:  {show_bar(player['hp'], player['max_hp'])}")
    print(f"  💙 MP:  {show_bar(player['mp'], player['max_mp'])}")
    print(f"  ⚔️  ATK: {player['atk']}   🛡️  DEF: {player['def']}   💨 SPD: {player['spd']}")
    print(f"  💰 Gold: {player['gold']}   💀 Kills: {player['kills']}")
    print(f"  🎒 Items: {len(player['inventory'])}")
    print(f"{'='*45}")

# ============================================================
#  MAIN GAME LOOP
# ============================================================

def main():
    print("=" * 50)
    print("       🎲 DICE RPG - TERMINAL ADVENTURE 🎲")
    print("=" * 50)
    slow_print("A land plagued by darkness awaits a hero...")
    time.sleep(0.5)

    name = input("\n⚔️  Enter your hero's name: ").strip() or "Hero"

    print("\n🧙 Choose your class:")
    for key, cls in CLASSES.items():
        c = cls
        print(f"  {key}. {c['emoji']} {c['name']:10} HP:{c['hp']}  MP:{c['mp']}  ATK:{c['atk']}  DEF:{c['def']}")

    cls_choice = input("Your choice (1-4): ").strip()
    if cls_choice not in CLASSES:
        cls_choice = '1'

    player = create_player(name, cls_choice)
    slow_print(f"\n🌟 {player['emoji']} {name} the {player['class']} begins their journey!")
    time.sleep(0.5)

    floor = 1
    enemies_per_floor = 3
    boss_floor = 5

    while True:
        print(f"\n{'='*50}")
        slow_print(f"  🗺️  Floor {floor} - The dungeon grows darker...")
        print(f"{'='*50}")
        print("\n  What do you do?")
        print("   1. ⚔️  Explore (fight enemy)")
        print("   2. 🏪 Visit Shop")
        print("   3. 📊 View Stats")
        print("   4. 😴 Rest (+20 HP/MP, costs 30 gold)")
        if floor >= boss_floor:
            print("   5. 😈 Challenge Boss!")
        print("   0. 🚪 Quit")

        action = input("\n  Action: ").strip()

        if action == '0':
            slow_print(f"\n👋 {name} retreats from the dungeon. Farewell!")
            show_stats(player)
            break

        elif action == '1':
            # Pick enemy based on floor
            max_idx = min(floor + 1, len(ENEMY_POOL) - 1)
            pool = ENEMY_POOL[:max_idx+1]
            template = random.choice(pool)
            result = battle(player, template)
            if result == 'dead':
                slow_print(f"\n💀 {name} has fallen in battle!")
                slow_print("   GAME OVER")
                show_stats(player)
                break
            elif result == 'won':
                enemies_per_floor -= 1
                if enemies_per_floor <= 0:
                    floor += 1
                    enemies_per_floor = 3 + floor
                    slow_print(f"\n🗺️  You advance to Floor {floor}!")

        elif action == '2':
            visit_shop(player)

        elif action == '3':
            show_stats(player)

        elif action == '4':
            if player['gold'] >= 30:
                player['gold'] -= 30
                player['hp'] = min(player['max_hp'], player['hp'] + 20)
                player['mp'] = min(player['max_mp'], player['mp'] + 20)
                slow_print("   😴 You rest... HP and MP restored by 20.")
            else:
                slow_print("   ❌ Need 30 gold to rest!")

        elif action == '5' and floor >= boss_floor:
            slow_print("\n😈 THE DEMON LORD AWAITS...")
            time.sleep(1)
            result = battle(player, BOSS, is_boss=True)
            if result == 'dead':
                slow_print(f"\n💀 The Demon Lord has defeated {name}!")
                slow_print("   GAME OVER")
                show_stats(player)
                break
            elif result == 'won':
                slow_print("\n🎉 YOU DEFEATED THE DEMON LORD!")
                slow_print("🏆 THE REALM IS SAVED! YOU WIN!")
                show_stats(player)
                break
        else:
            slow_print("   ❌ Invalid choice.")

if __name__ == "__main__":
    main()