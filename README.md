# 🎮 Python Games Collection

A collection of classic and modern games implemented in Python, ranging from simple terminal games to fully-featured graphical experiences using Pygame. This repository serves as a fun, educational resource for learning Python and game development concepts.

## ✨ Features

- **11+ Playable Games**: A diverse set of games covering puzzles, arcade classics, and board games.
- **Multiple Libraries**: Games built using the standard library (terminal-based), Pygame for graphics, and Tkinter for the typing test GUI.
- **AI Opponents**: Includes an AI opponent in Connect 4 powered by the Minimax algorithm.
- **Persistent High Scores**: Games like 2048 and Flappy Bird save your best scores locally.
- **Modern Codebase**: Clean, well-structured code with proper OOP principles, making it easy to read and extend.

## 🎲 Games Included

| Game | Description | Type | Dependencies |
|------|-------------|------|--------------|
| **2048** | The classic tile-merging puzzle. Play in your terminal with ANSI colors. | Puzzle | None (Standard Lib) |
| **Angry Bird** | A physics-based slingshot game inspired by the popular mobile hit. | Arcade | `pygame`, `pymunk` |
| **Connect 4** | Drop discs and connect four. Play against a friend or a challenging AI. | Board | None (Standard Lib) |
| **Dragon Runner** | A flappy-bird style game with a dragon. Dodge trees and collect points. | Arcade | `pygame` |
| **Flappy Bird** | The beloved one-tap flyer. Navigate through pipes and beat your high score. | Arcade | `pygame` |
| **N-Queen** | Solve the classic N-Queens puzzle in this interactive visualizer. | Puzzle | `pygame` |
| **Snake** | The timeless snake game. Eat apples, grow, and avoid walls and yourself. | Arcade | `pygame` |
| **Sudoku** | Generate and play Sudoku puzzles right in your terminal. | Puzzle | None (Standard Lib) |
| **Tetris** | A faithful recreation of the iconic block-stacking game. | Arcade | `pygame` |
| **Tic Tac Toe** | The classic X and O game for two players in the terminal. | Board | None (Standard Lib) |
| **Typing Advanced** | A fully-featured typing speed test with WPM graphs and difficulty levels. | Educational | `tkinter`, `matplotlib` (optional) |

## 🚀 Getting Started

### Prerequisites

- **Python 3.6+** (Tested with Python 3.9+)
- **pip** (Python package installer)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/manish08k/python-games.git
   cd python-games
Install dependencies:

bash
pip install pygame pymunk matplotlib
pygame: Required for all graphical games.
pymunk: Required for Angry Bird's physics engine.
matplotlib: Optional for the Typing Advanced game's WPM graph.
Running a Game

Navigate to the project directory and run the desired game using Python:

bash
# Terminal-based games
python 2048.py
python connect4.py
python tictactoe.py
python suduko.py

# Pygame graphical games
python snake.py
python angrybird.py
python flipybird.py
python dragon.py
python tertis.py
python n-queen.py

# Tkinter GUI game
python typing_advanced.py
📁 Project Structure

text
python-games/
├── .gitignore            # Specifies intentionally untracked files
├── 2048.py               # 2048 puzzle (terminal)
├── angrybird.py          # Angry Bird (pygame + pymunk)
├── connect4.py           # Connect 4 with AI (terminal)
├── dragon.py             # Dragon Runner (pygame)
├── flipybird.py          # Flappy Bird (pygame)
├── n-queen.py            # N-Queens solver & visualizer (pygame)
├── snake.py              # Snake game (pygame)
├── suduko.py             # Sudoku generator/solver (terminal)
├── tertis.py             # Tetris (pygame)
├── tictactoe.py          # Tic Tac Toe (terminal)
└── typing_advanced.py    # Typing speed test (tkinter)
🤝 Contributing

Contributions are welcome! If you'd like to add a new game, fix a bug, or improve an existing game:

Fork the repository.
Create a new branch (git checkout -b feature/your-feature).
Make your changes and commit (git commit -m 'Add some feature').
Push to the branch (git push origin feature/your-feature).
Open a Pull Request.
Please ensure your code follows the existing style and includes appropriate comments.

📜 License

This project is open-source and available under the MIT License. Feel free to use, modify, and distribute the code for personal or educational purposes.

🙏 Acknowledgements

The Pygame community for the excellent library.
The Pymunk library for bringing Chipmunk2D physics to Python.
All the classic games that inspired this collection.
text
