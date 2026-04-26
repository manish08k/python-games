import turtle
import sys

# ========== SPEED MODES ==========
MODES = {
    "normal":   (2.0, 0.2, 6.0),   # (start_speed, increment, max_speed)
    "speed":    (3.5, 0.3, 8.0),
    "speeder":  (5.0, 0.4, 10.0),
    "fastest":  (7.0, 0.5, 14.0)
}
current_mode = "normal"

# ========== SETUP ==========
screen = turtle.Screen()
screen.title("PONG - Mouse Control + Speed Modes")
screen.bgcolor("black")
screen.setup(width=800, height=600)
screen.tracer(0, 0)          # maximum smoothness
try:
    screen.cv._rootwindow.attributes('-topmost', 1)  # keep on top (property, not method)
except:
    pass  # ignore if not supported

# ---------- Speed selector buttons (top) ----------
button_height = 30
button_y = 250
button_width = 80
buttons = {}

def create_button(x, label, mode):
    btn = turtle.Turtle()
    btn.speed(0)
    btn.penup()
    btn.hideturtle()
    btn.goto(x, button_y)
    btn.color("gray")
    btn.begin_fill()
    for _ in range(2):
        btn.forward(button_width)
        btn.left(90)
        btn.forward(button_height)
        btn.left(90)
    btn.end_fill()
    btn.goto(x + button_width//2, button_y - button_height//2 - 5)
    btn.color("black")
    btn.write(label, align="center", font=("Arial", 12, "bold"))
    buttons[(x, x + button_width)] = (btn, mode)

create_button(-150, "Normal", "normal")
create_button(-50,  "Speed",  "speed")
create_button(50,   "Speeder","speeder")
create_button(150,  "Fastest","fastest")

def highlight_mode(mode):
    for (x1, x2), (btn, m) in buttons.items():
        if m == mode:
            btn.color("lightgreen")
        else:
            btn.color("gray")
        btn.clear()
        btn.penup()
        btn.goto(x1, button_y)
        btn.begin_fill()
        for _ in range(2):
            btn.forward(button_width)
            btn.left(90)
            btn.forward(button_height)
            btn.left(90)
        btn.end_fill()
        btn.goto(x1 + button_width//2, button_y - button_height//2 - 5)
        btn.color("darkgreen" if m == mode else "black")
        btn.write(m.capitalize(), align="center", font=("Arial", 12, "bold"))

highlight_mode(current_mode)

# ---------- Game objects ----------
left_paddle = turtle.Turtle()
left_paddle.speed(0)
left_paddle.shape("square")
left_paddle.color("white")
left_paddle.shapesize(stretch_wid=5, stretch_len=1)
left_paddle.penup()
left_paddle.goto(-350, 0)

right_paddle = turtle.Turtle()
right_paddle.speed(0)
right_paddle.shape("square")
right_paddle.color("white")
right_paddle.shapesize(stretch_wid=5, stretch_len=1)
right_paddle.penup()
right_paddle.goto(350, 0)

ball = turtle.Turtle()
ball.speed(0)
ball.shape("square")
ball.color("white")
ball.penup()
ball.goto(0, 0)

# Score
score_left = 0
score_right = 0
score_display = turtle.Turtle()
score_display.speed(0)
score_display.color("white")
score_display.penup()
score_display.hideturtle()
score_display.goto(0, 210)
score_display.write(f"You: {score_left}   AI: {score_right}",
                    align="center", font=("Courier", 20, "normal"))

# ---------- Mouse control for left paddle ----------
def on_mouse_move(event):
    canvas = screen.getcanvas()
    win_y = event.y
    # Convert window y to turtle y (-300..300)
    turtle_y = 300 - (win_y * 600 / canvas.winfo_height())
    turtle_y = max(-240, min(240, turtle_y))
    left_paddle.sety(turtle_y)

canvas = screen.getcanvas()
canvas.bind('<Motion>', on_mouse_move)

# ---------- Computer AI (smooth) ----------
def computer_move():
    target = ball.ycor()
    current = right_paddle.ycor()
    diff = target - current
    right_paddle.sety(current + diff * 0.98)
    right_paddle.sety(max(-240, min(240, right_paddle.ycor())))

# ---------- Ball reset with current mode ----------
def reset_ball(serve_direction=None):
    ball.goto(0, 0)
    init_speed, _, _ = MODES[current_mode]
    if serve_direction is None:
        serve_direction = -1 if ball.dx > 0 else 1
    ball.dx = init_speed * serve_direction
    ball.dy = init_speed * (1 if ball.dy > 0 else -1)

# ---------- Speed button click (using turtle's onclick) ----------
def on_click(x, y):
    global current_mode
    if button_y - button_height < y < button_y + 20:
        for (x1, x2), (_, mode) in buttons.items():
            if x1 < x < x1 + button_width:
                current_mode = mode
                highlight_mode(current_mode)
                # Reset ball speed immediately
                init_speed, _, _ = MODES[current_mode]
                ball.dx = init_speed * (1 if ball.dx >= 0 else -1)
                ball.dy = init_speed * (1 if ball.dy >= 0 else -1)
                break

screen.onclick(on_click)

# ---------- Main game loop with error handling ----------
def start_game():
    global score_left, score_right, current_mode
    init_speed, speed_inc, max_speed = MODES[current_mode]
    ball.dx = init_speed
    ball.dy = init_speed

    while True:
        try:
            screen.update()
        except turtle.Terminator:
            # Window was closed – exit cleanly
            break

        # Move ball
        ball.setx(ball.xcor() + ball.dx)
        ball.sety(ball.ycor() + ball.dy)

        # Top/bottom bounce
        if abs(ball.ycor()) > 290:
            ball.dy *= -1

        computer_move()

        # Scoring
        if ball.xcor() > 390:
            score_left += 1
            score_display.clear()
            score_display.write(f"You: {score_left}   AI: {score_right}",
                                align="center", font=("Courier", 20, "normal"))
            reset_ball(serve_direction=-1)

        if ball.xcor() < -390:
            score_right += 1
            score_display.clear()
            score_display.write(f"You: {score_left}   AI: {score_right}",
                                align="center", font=("Courier", 20, "normal"))
            reset_ball(serve_direction=1)

        # Paddle collisions (with speed increase)
        left_collision = (ball.xcor() < -340 and ball.xcor() > -350 and
                          abs(ball.ycor() - left_paddle.ycor()) < 50)
        right_collision = (ball.xcor() > 340 and ball.xcor() < 350 and
                           abs(ball.ycor() - right_paddle.ycor()) < 50)

        if left_collision or right_collision:
            ball.dx *= -1
            # Increase speed (capped)
            new_speed = min(abs(ball.dx) + speed_inc, max_speed)
            ball.dx = new_speed * (1 if ball.dx > 0 else -1)
            ball.dy = new_speed * (1 if ball.dy > 0 else -1)

        # Re‑fetch current mode parameters (in case mode changed)
        _, speed_inc, max_speed = MODES[current_mode]

    print("Game closed. Thanks for playing!")

# Run
if __name__ == "__main__":
    try:
        start_game()
    except turtle.Terminator:
        pass  # normal exit
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        sys.exit(0)