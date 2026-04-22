import sys
import math
import pygame
import pymunk

# ----------------------------------------------------------------------
# Constants
# ----------------------------------------------------------------------
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 700
GROUND_Y = SCREEN_HEIGHT - 80

SLINGSHOT_X = 250
SLINGSHOT_Y = GROUND_Y - 20
BIRD_RADIUS = 14

GRAVITY = (0, 800)
PHYSICS_STEP = 1 / 60.0

MAX_DRAG_DISTANCE = 120
POWER_FACTOR = 23

TARGET_POINTS = 100
BONUS_PER_REMAINING_BIRD = 150
COLLISION_SPEED_THRESHOLD = 350  # pixels/sec (impact speed to kill pig)

INITIAL_BIRDS = 3
FRAME_RATE = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 80, 80)
BROWN = (139, 69, 19)
LIGHT_BROWN = (200, 140, 70)
YELLOW = (255, 220, 80)
PINK = (255, 150, 150)

# Collision types (for static walls)
COLLTYPE_BIRD = 1
COLLTYPE_BLOCK = 2
COLLTYPE_TARGET = 3
COLLTYPE_GROUND = 4


# ----------------------------------------------------------------------
# Helper drawing
# ----------------------------------------------------------------------
def draw_slingshot(screen):
    x, y = SLINGSHOT_X, SLINGSHOT_Y
    pygame.draw.rect(screen, BROWN, (x - 15, y - 10, 30, 40))
    pygame.draw.rect(screen, LIGHT_BROWN, (x - 8, y - 15, 16, 20))
    pygame.draw.line(screen, BLACK, (x, y), (x - 20, y - 30), 4)
    pygame.draw.line(screen, BLACK, (x, y), (x + 20, y - 30), 4)
    pygame.draw.circle(screen, (180, 100, 40), (x, y), 8)


def draw_drag_line(screen, start_pos, current_pos, max_dist):
    dx = current_pos[0] - start_pos[0]
    dy = current_pos[1] - start_pos[1]
    distance = min(math.hypot(dx, dy), max_dist)
    if distance > 5:
        angle = math.atan2(dy, dx)
        end_x = start_pos[0] + math.cos(angle) * distance
        end_y = start_pos[1] + math.sin(angle) * distance
        pygame.draw.line(screen, (255, 255, 200), start_pos, (end_x, end_y), 5)
        power_ratio = distance / max_dist
        num_dots = int(power_ratio * 15) + 1
        for i in range(1, num_dots):
            t = i / num_dots
            dot_x = start_pos[0] + (end_x - start_pos[0]) * t
            dot_y = start_pos[1] + (end_y - start_pos[1]) * t
            pygame.draw.circle(screen, YELLOW, (int(dot_x), int(dot_y)), 3)


# ----------------------------------------------------------------------
# Game Objects
# ----------------------------------------------------------------------
class Bird:
    def __init__(self, space, pos):
        self.space = space
        self.body = pymunk.Body(1.0, pymunk.moment_for_circle(1.0, 0, BIRD_RADIUS))
        self.body.position = pos
        self.shape = pymunk.Circle(self.body, BIRD_RADIUS)
        self.shape.elasticity = 0.55
        self.shape.friction = 0.8
        self.shape.collision_type = COLLTYPE_BIRD
        self.space.add(self.body, self.shape)
        self.joint = None

    def attach_to_slingshot(self, anchor_pos):
        static_body = self.space.static_body
        self.joint = pymunk.PivotJoint(static_body, self.body, anchor_pos, (0, 0))
        self.joint.max_bias = 0
        self.joint.collide_bodies = False
        self.space.add(self.joint)

    def detach_and_launch(self, impulse):
        if self.joint:
            self.space.remove(self.joint)
            self.joint = None
        self.body.apply_impulse_at_local_point(impulse, (0, 0))

    def remove_from_space(self):
        if self.joint:
            self.space.remove(self.joint)
        self.space.remove(self.shape, self.body)

    @property
    def is_moving(self):
        vel = self.body.velocity
        return math.hypot(vel.x, vel.y) > 15

    @property
    def is_out_of_bounds(self):
        x, y = self.body.position
        return x < -100 or x > SCREEN_WIDTH + 100 or y > SCREEN_HEIGHT + 150


class Block:
    def __init__(self, space, pos, width=40, height=25):
        self.space = space
        mass = 1.2
        moment = pymunk.moment_for_box(mass, (width, height))
        self.body = pymunk.Body(mass, moment)
        self.body.position = pos
        self.shape = pymunk.Poly.create_box(self.body, (width, height))
        self.shape.elasticity = 0.4
        self.shape.friction = 0.7
        self.shape.collision_type = COLLTYPE_BLOCK
        self.space.add(self.body, self.shape)

    def remove_from_space(self):
        self.space.remove(self.shape, self.body)


class Target:
    def __init__(self, space, pos, radius=16):
        self.space = space
        self.radius = radius
        self.body = pymunk.Body(1.5, pymunk.moment_for_circle(1.5, 0, radius))
        self.body.position = pos
        self.shape = pymunk.Circle(self.body, radius)
        self.shape.elasticity = 0.5
        self.shape.friction = 0.6
        self.shape.collision_type = COLLTYPE_TARGET
        self.space.add(self.body, self.shape)
        self.destroyed = False

    def remove_from_space(self):
        if not self.destroyed:
            self.destroyed = True
            self.space.remove(self.shape, self.body)


# ----------------------------------------------------------------------
# Main Game Class
# ----------------------------------------------------------------------
class AngryBirdsGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Angry Birds - Pymunk")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 28, bold=True)
        self.small_font = pygame.font.SysFont("Arial", 22)

        self.space = pymunk.Space()
        self.space.gravity = GRAVITY
        self.space.damping = 0.98

        self.score = 0
        self.birds_remaining = INITIAL_BIRDS
        self.game_state = "playing"
        self.current_bird = None
        self.bird_launched = False
        self.aiming_active = False
        self.drag_start_pos = None
        self.drag_current_pos = None

        self.blocks = []
        self.targets = []

        self._create_static_world()
        self._create_level()
        self._spawn_new_bird()

    def _create_static_world(self):
        static_body = self.space.static_body
        ground_seg = pymunk.Segment(static_body, (0, GROUND_Y), (SCREEN_WIDTH, GROUND_Y), 5)
        ground_seg.elasticity = 0.6
        ground_seg.friction = 0.9
        ground_seg.collision_type = COLLTYPE_GROUND
        self.space.add(ground_seg)

        left_wall = pymunk.Segment(static_body, (0, 0), (0, SCREEN_HEIGHT), 5)
        right_wall = pymunk.Segment(static_body, (SCREEN_WIDTH, 0), (SCREEN_WIDTH, SCREEN_HEIGHT), 5)
        ceiling = pymunk.Segment(static_body, (0, 0), (SCREEN_WIDTH, 0), 5)
        for wall in (left_wall, right_wall, ceiling):
            wall.elasticity = 0.7
            wall.collision_type = COLLTYPE_GROUND
        self.space.add(left_wall, right_wall, ceiling)

    def _create_level(self):
        for block in self.blocks:
            block.remove_from_space()
        for target in self.targets:
            target.remove_from_space()
        self.blocks.clear()
        self.targets.clear()

        base_x = SCREEN_WIDTH // 2 + 80
        base_y = GROUND_Y - 15

        # Left pillar
        for i in range(4):
            block = Block(self.space, (base_x - 35, base_y - i * 28), 40, 25)
            self.blocks.append(block)
        # Right pillar
        for i in range(4):
            block = Block(self.space, (base_x + 15, base_y - i * 28), 40, 25)
            self.blocks.append(block)
        # Top plank
        plank = Block(self.space, (base_x - 10, base_y - 115), 100, 20)
        self.blocks.append(plank)

        # Pig on top
        pig = Target(self.space, (base_x - 8, base_y - 135), 16)
        self.targets.append(pig)
        # Extra pig
        pig2 = Target(self.space, (base_x + 120, GROUND_Y - 18), 16)
        self.targets.append(pig2)
        # Scattered block
        extra = Block(self.space, (base_x + 80, GROUND_Y - 45), 35, 25)
        self.blocks.append(extra)

    def _spawn_new_bird(self):
        if self.current_bird:
            self.current_bird.remove_from_space()
        self.current_bird = Bird(self.space, (SLINGSHOT_X, SLINGSHOT_Y))
        self.current_bird.attach_to_slingshot((SLINGSHOT_X, SLINGSHOT_Y))
        self.bird_launched = False

    def _end_turn(self):
        if self.game_state != "playing":
            return
        if self.current_bird:
            self.current_bird.remove_from_space()
            self.current_bird = None

        if len(self.targets) == 0:
            self.score += self.birds_remaining * BONUS_PER_REMAINING_BIRD
            self.game_state = "win"
            return

        self.birds_remaining -= 1
        if self.birds_remaining <= 0:
            self.game_state = "game_over"
            return
        self._spawn_new_bird()

    def _handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    self._reset_game()
                if event.key == pygame.K_ESCAPE:
                    return False

            if self.game_state == "playing" and not self.bird_launched and self.current_bird:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mx, my = pygame.mouse.get_pos()
                    if math.hypot(mx - SLINGSHOT_X, my - SLINGSHOT_Y) < 30:
                        self.aiming_active = True
                        self.drag_start_pos = (SLINGSHOT_X, SLINGSHOT_Y)
                        self.drag_current_pos = (mx, my)

                elif event.type == pygame.MOUSEMOTION and self.aiming_active:
                    mx, my = pygame.mouse.get_pos()
                    dx = mx - SLINGSHOT_X
                    dy = my - SLINGSHOT_Y
                    dist = math.hypot(dx, dy)
                    if dist > MAX_DRAG_DISTANCE:
                        dx = dx / dist * MAX_DRAG_DISTANCE
                        dy = dy / dist * MAX_DRAG_DISTANCE
                        mx, my = SLINGSHOT_X + dx, SLINGSHOT_Y + dy
                    self.drag_current_pos = (mx, my)

                elif event.type == pygame.MOUSEBUTTONUP and event.button == 1 and self.aiming_active:
                    dx = self.drag_start_pos[0] - self.drag_current_pos[0]
                    dy = self.drag_start_pos[1] - self.drag_current_pos[1]
                    dist = min(math.hypot(dx, dy), MAX_DRAG_DISTANCE)
                    if dist > 5:
                        norm_x = dx / dist
                        norm_y = dy / dist
                        impulse = (norm_x * dist * POWER_FACTOR, norm_y * dist * POWER_FACTOR)
                        self.current_bird.detach_and_launch(impulse)
                        self.bird_launched = True
                    self.aiming_active = False
        return True

    def _manual_collision_detection(self):
        """Check bird-target collisions by distance and relative velocity."""
        if not self.current_bird or self.bird_launched is False:
            return

        bird_pos = self.current_bird.body.position
        bird_vel = self.current_bird.body.velocity
        for target in self.targets[:]:  # iterate over copy
            if target.destroyed:
                continue
            target_pos = target.body.position
            dx = bird_pos.x - target_pos.x
            dy = bird_pos.y - target_pos.y
            distance = math.hypot(dx, dy)
            if distance < BIRD_RADIUS + target.radius:
                # Collision! Compute impact speed
                rel_vel_x = bird_vel.x - target.body.velocity.x
                rel_vel_y = bird_vel.y - target.body.velocity.y
                impact_speed = math.hypot(rel_vel_x, rel_vel_y)
                if impact_speed > COLLISION_SPEED_THRESHOLD:
                    target.remove_from_space()
                    self.targets.remove(target)
                    self.score += TARGET_POINTS

    def _update_physics(self):
        self.space.step(PHYSICS_STEP)

        # Manual bird–target collision
        self._manual_collision_detection()

        if self.bird_launched and self.current_bird:
            if (not self.current_bird.is_moving) or self.current_bird.is_out_of_bounds:
                self._end_turn()
        elif self.bird_launched and not self.current_bird:
            self._end_turn()

    def _draw(self):
        self.screen.fill((135, 206, 235))
        pygame.draw.rect(self.screen, (80, 120, 40), (0, GROUND_Y, SCREEN_WIDTH, SCREEN_HEIGHT - GROUND_Y))
        pygame.draw.line(self.screen, (50, 70, 20), (0, GROUND_Y), (SCREEN_WIDTH, GROUND_Y), 5)

        draw_slingshot(self.screen)

        for block in self.blocks:
            verts = block.shape.get_vertices()
            if len(verts) == 4:
                points = [(v.x, v.y) for v in verts]
                pygame.draw.polygon(self.screen, BROWN, points)
                pygame.draw.polygon(self.screen, BLACK, points, 2)

        for target in self.targets:
            x, y = target.body.position
            pygame.draw.circle(self.screen, PINK, (int(x), int(y)), target.radius)
            pygame.draw.circle(self.screen, BLACK, (int(x), int(y)), target.radius, 2)
            pygame.draw.circle(self.screen, BLACK, (int(x) - 5, int(y) - 4), 2)
            pygame.draw.circle(self.screen, BLACK, (int(x) + 5, int(y) - 4), 2)
            pygame.draw.circle(self.screen, BLACK, (int(x), int(y) + 2), 3, 1)

        if self.current_bird:
            x, y = self.current_bird.body.position
            pygame.draw.circle(self.screen, RED, (int(x), int(y)), BIRD_RADIUS)
            pygame.draw.circle(self.screen, BLACK, (int(x), int(y)), BIRD_RADIUS, 2)
            pygame.draw.circle(self.screen, WHITE, (int(x) - 4, int(y) - 4), 3)
            pygame.draw.circle(self.screen, BLACK, (int(x) - 4, int(y) - 4), 1)

        if self.aiming_active and self.drag_current_pos:
            draw_drag_line(self.screen, self.drag_start_pos, self.drag_current_pos, MAX_DRAG_DISTANCE)

        score_text = self.font.render(f"Score: {self.score}", True, BLACK)
        self.screen.blit(score_text, (20, 20))
        birds_text = self.font.render(f"Birds: {self.birds_remaining}", True, BLACK)
        self.screen.blit(birds_text, (20, 60))

        if self.game_state == "win":
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))
            win_text = self.font.render("VICTORY! All pigs destroyed.", True, (255, 255, 100))
            restart_text = self.small_font.render("Press R to restart", True, WHITE)
            self.screen.blit(win_text, (SCREEN_WIDTH//2 - win_text.get_width()//2, SCREEN_HEIGHT//2 - 40))
            self.screen.blit(restart_text, (SCREEN_WIDTH//2 - restart_text.get_width()//2, SCREEN_HEIGHT//2 + 20))

        elif self.game_state == "game_over":
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))
            over_text = self.font.render("GAME OVER - No birds left.", True, (255, 120, 120))
            restart_text = self.small_font.render("Press R to restart", True, WHITE)
            self.screen.blit(over_text, (SCREEN_WIDTH//2 - over_text.get_width()//2, SCREEN_HEIGHT//2 - 40))
            self.screen.blit(restart_text, (SCREEN_WIDTH//2 - restart_text.get_width()//2, SCREEN_HEIGHT//2 + 20))

        pygame.display.flip()

    def _reset_game(self):
        if self.current_bird:
            self.current_bird.remove_from_space()
        for block in self.blocks:
            block.remove_from_space()
        for target in self.targets:
            target.remove_from_space()
        self.blocks.clear()
        self.targets.clear()

        self.score = 0
        self.birds_remaining = INITIAL_BIRDS
        self.game_state = "playing"
        self.bird_launched = False
        self.aiming_active = False

        self._create_level()
        self._spawn_new_bird()

    def run(self):
        running = True
        while running:
            running = self._handle_input()
            if self.game_state == "playing":
                self._update_physics()
            self._draw()
            self.clock.tick(FRAME_RATE)
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = AngryBirdsGame()
    game.run()