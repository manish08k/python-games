#!/usr/bin/env python3
"""
Advanced Typing Speed Test – Improved UI
- Larger fonts and clearer buttons
- WPM graph moved to bottom (horizontal layout)
- Bot progress bar below typing area
- Dark mode toggle works globally
"""

import sys
import os

# Block dangerous filename
if os.path.basename(sys.argv[0]) == 'typing.py':
    print("\n❌ ERROR: Your script is named 'typing.py' which conflicts with Python's standard library.")
    print("   Please rename this file to something else (e.g., 'typing_advanced.py') and run again.\n")
    sys.exit(1)

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import random
import time
from collections import deque

# Optional imports
try:
    import matplotlib
    matplotlib.use('TkAgg')
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

try:
    import winsound
    SOUND_AVAILABLE = True
except ImportError:
    try:
        import beepy
        SOUND_AVAILABLE = True
    except ImportError:
        SOUND_AVAILABLE = False


# ======================== SENTENCE MANAGER ========================
class SentenceManager:
    def __init__(self):
        self.sentences = []
        self.recent = {'easy': deque(maxlen=8), 'medium': deque(maxlen=8), 'hard': deque(maxlen=8)}
        self._load_default_sentences()

    def _load_default_sentences(self):
        easy = [
            "The quick brown fox jumps over the lazy dog.",
            "Python is a powerful programming language.",
            "I love coding and building applications.",
            "Practice makes a man perfect.",
            "Keep your friends close but your enemies closer.",
            "The sun rises in the east and sets in the west.",
            "She sells sea shells on the sea shore.",
            "All that glitters is not gold.",
            "A journey of a thousand miles begins with a single step.",
            "Time flies when you are having fun.",
            "Coding is fun and creative.",
            "The cat sat on the mat.",
            "Hello world is the first program.",
            "Learning new things keeps the mind sharp.",
            "Coffee and code are a great combination."
        ]
        medium = [
            "Artificial intelligence is transforming the world as we know it, making tasks easier and faster.",
            "The development of renewable energy sources is crucial for a sustainable future on our planet.",
            "She decided to take a walk through the forest, enjoying the peaceful sounds of nature around her.",
            "The quick brown fox jumps over the lazy dog near the riverbank every morning at dawn.",
            "Python's simplicity and readability make it an excellent choice for both beginners and experts.",
            "Learning a new language opens up opportunities to connect with different cultures and people.",
            "The scientist carefully recorded the results of the experiment in her well-worn laboratory notebook.",
            "After the rain stopped, a beautiful rainbow appeared across the clear blue sky.",
            "He practiced the piano for hours each day, determined to master the difficult piece.",
            "The city library contains thousands of books, each holding stories and knowledge waiting to be discovered.",
            "Space exploration continues to reveal fascinating discoveries about our universe and its origins.",
            "Cooking a delicious meal requires patience, creativity, and the right ingredients.",
            "The team worked collaboratively to solve the complex problem before the deadline.",
            "Traveling to new places broadens your perspective and enriches your life experiences.",
            "Meditation and mindfulness can significantly improve mental health and overall well-being."
        ]
        hard = [
            "Quantum computing leverages the principles of superposition and entanglement to perform calculations that would be infeasible for classical computers, revolutionizing fields like cryptography and materials science.",
            "The philosopher argued that while free will appears to be an intrinsic aspect of human consciousness, it might ultimately be an emergent property of complex neural interactions rather than a fundamental metaphysical truth.",
            "Despite the initial skepticism from the scientific community, the researcher's groundbreaking work on epigenetics demonstrated that environmental factors could indeed trigger inheritable changes in gene expression without altering the DNA sequence itself.",
            "The intricate dance between supply and demand dynamics, coupled with unpredictable geopolitical events, creates a volatile landscape where even seasoned economists struggle to forecast market trends accurately.",
            "Through the use of advanced machine learning algorithms, the system can autonomously identify patterns in unstructured data, enabling predictive analytics that were previously impossible to achieve at scale."
        ]
        for s in easy: self.sentences.append((s, 'easy'))
        for s in medium: self.sentences.append((s, 'medium'))
        for s in hard: self.sentences.append((s, 'hard'))
        extra = [
            "The internet has changed how we communicate, access information, and conduct business globally.",
            "Regular exercise and a balanced diet are essential components of a healthy lifestyle.",
            "The museum's new exhibit features rare artifacts from ancient Egyptian tombs and temples.",
            "Writing clean, maintainable code is a skill that improves with practice and code reviews.",
            "Climate change poses significant challenges that require international cooperation and innovation."
        ]
        for s in extra: self.sentences.append((s, 'medium'))

    def get_random_sentence(self, difficulty):
        filtered = [s for s in self.sentences if s[1] == difficulty]
        if not filtered:
            return None, None
        recent_set = set(self.recent[difficulty])
        available = [s for s in filtered if s[0] not in recent_set]
        if not available:
            available = filtered
        selected = random.choice(available)
        self.recent[difficulty].append(selected[0])
        return selected[0], selected[1]

    def add_sentence(self, text, difficulty='medium'):
        if text and len(text) > 15:
            self.sentences.append((text, difficulty))
            return True
        return False


# ======================== PROFILE MANAGER ========================
class ProfileManager:
    def __init__(self, data_dir="profiles"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        self.profiles = {}
        self.load_all()

    def load_all(self):
        for f in os.listdir(self.data_dir):
            if f.endswith('.json'):
                name = f[:-5]
                with open(os.path.join(self.data_dir, f), 'r') as file:
                    self.profiles[name] = json.load(file)

    def create_profile(self, name):
        if name in self.profiles:
            return False
        self.profiles[name] = {
            'name': name,
            'stats': {'easy': [], 'medium': [], 'hard': []},
            'best_wpm': {'easy': 0, 'medium': 0, 'hard': 0}
        }
        self._save_profile(name)
        return True

    def _save_profile(self, name):
        with open(os.path.join(self.data_dir, f"{name}.json"), 'w') as f:
            json.dump(self.profiles[name], f, indent=2)

    def add_score(self, name, difficulty, wpm, accuracy):
        if name not in self.profiles:
            return
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        self.profiles[name]['stats'][difficulty].append((wpm, accuracy, timestamp))
        if wpm > self.profiles[name]['best_wpm'][difficulty]:
            self.profiles[name]['best_wpm'][difficulty] = wpm
        self._save_profile(name)

    def get_best_wpm(self, name, difficulty):
        return self.profiles.get(name, {}).get('best_wpm', {}).get(difficulty, 0)


# ======================== GAME ENGINE ========================
class GameEngine:
    def __init__(self):
        self.reset()

    def reset(self):
        self.sentence = ""
        self.start_time = None
        self.end_time = None
        self.timer_running = False
        self.completed = False
        self.typed_text = ""
        self.correct_chars = 0
        self.wpm_history = []  # (time_elapsed, wpm)

    def start_timer(self):
        if not self.timer_running and not self.completed:
            self.start_time = time.time()
            self.timer_running = True
            self.wpm_history = [(0.0, 0.0)]

    def stop_timer(self):
        if self.timer_running:
            self.end_time = time.time()
            self.timer_running = False

    def get_elapsed(self):
        if self.start_time is None:
            return 0.0
        if self.end_time:
            return self.end_time - self.start_time
        return time.time() - self.start_time

    def update_typed(self, new_text):
        if self.completed:
            return
        self.typed_text = new_text
        self._recalc_stats()
        if self.typed_text == self.sentence:
            self.complete_game()

    def _recalc_stats(self):
        target = self.sentence
        typed = self.typed_text
        correct = sum(1 for i, ch in enumerate(typed) if i < len(target) and ch == target[i])
        self.correct_chars = correct
        elapsed = self.get_elapsed()
        if elapsed > 0 and correct > 0:
            wpm = (correct / 5) / (elapsed / 60)
            self.wpm_history.append((elapsed, wpm))
        if len(self.wpm_history) > 200:
            self.wpm_history = self.wpm_history[-200:]

    def complete_game(self):
        if self.completed:
            return
        self.completed = True
        self.stop_timer()
        final_correct = sum(1 for i, ch in enumerate(self.typed_text) if i < len(self.sentence) and ch == self.sentence[i])
        accuracy = (final_correct / len(self.sentence)) * 100 if self.sentence else 100
        elapsed = self.get_elapsed()
        final_wpm = (final_correct / 5) / (elapsed / 60) if elapsed > 0 else 0
        return final_wpm, accuracy

    def get_current_wpm(self):
        elapsed = self.get_elapsed()
        if elapsed > 0 and self.correct_chars > 0:
            return (self.correct_chars / 5) / (elapsed / 60)
        return 0.0

    def get_current_accuracy(self):
        if not self.typed_text:
            return 100.0
        correct = sum(1 for i, ch in enumerate(self.typed_text) if i < len(self.sentence) and ch == self.sentence[i])
        return (correct / len(self.typed_text)) * 100


# ======================== BOT OPPONENT ========================
class TypingBot:
    def __init__(self, difficulty='medium'):
        self.base_wpm = {'easy': 30, 'medium': 50, 'hard': 70}[difficulty]
        self.progress = 0
        self.finished = False
        self.finish_time = None
        self.sentence = ""

    def start(self, sentence, start_time):
        self.sentence = sentence
        self.start_time = start_time
        self.progress = 0
        self.finished = False
        actual_wpm = self.base_wpm * random.uniform(0.9, 1.1)
        total_chars = len(sentence)
        self.expected_duration = (total_chars / 5) / (actual_wpm / 60)
        self.finish_time = start_time + self.expected_duration

    def update(self, current_time):
        if self.finished:
            return 1.0
        if current_time >= self.finish_time:
            self.finished = True
            self.progress = len(self.sentence)
            return 1.0
        fraction = (current_time - self.start_time) / self.expected_duration
        fraction = min(1.0, max(0.0, fraction))
        self.progress = int(fraction * len(self.sentence))
        return fraction

    def get_progress(self):
        return self.progress


# ======================== MAIN APPLICATION (IMPROVED UI) ========================
class AdvancedTypingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🔥 Advanced Typing Speed Test | Race Against Bot")
        self.root.geometry("1200x800")
        self.root.resizable(True, True)

        # Core
        self.sentence_manager = SentenceManager()
        self.profile_manager = ProfileManager()
        self.game_engine = GameEngine()
        self.bot = None
        self.game_active = False
        self.bot_active = False
        self.update_loop_id = None

        # UI state
        self.current_difficulty = tk.StringVar(value="medium")
        self.current_profile = tk.StringVar()
        self.dark_mode = False
        self.themes = {
            'light': {'bg': '#f5f5f5', 'fg': '#2c3e50', 'entry': '#ffffff', 'button': '#ecf0f1',
                      'correct_bg': '#d4efdf', 'incorrect_bg': '#fadbd8'},
            'dark': {'bg': '#2c3e50', 'fg': '#ecf0f1', 'entry': '#34495e', 'button': '#3d566e',
                     'correct_bg': '#1e8449', 'incorrect_bg': '#b03a2e'}
        }
        self.current_theme = self.themes['light']

        self._build_ui()
        self._show_profile_selector()

    def _build_ui(self):
        # Main container with three vertical sections
        self.main_frame = tk.Frame(self.root, bg=self.current_theme['bg'])
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # --- Top panel: Profile, timer, sentence, input, buttons ---
        self.top_panel = tk.Frame(self.main_frame, bg=self.current_theme['bg'])
        self.top_panel.pack(fill=tk.X, pady=(0, 10))

        # Profile row
        profile_row = tk.Frame(self.top_panel, bg=self.current_theme['bg'])
        profile_row.pack(fill=tk.X, pady=5)
        tk.Label(profile_row, text="Profile:", font=('Arial', 12, 'bold'), bg=self.current_theme['bg'], fg=self.current_theme['fg']).pack(side=tk.LEFT, padx=5)
        self.profile_combo = ttk.Combobox(profile_row, textvariable=self.current_profile, state="readonly", width=15, font=('Arial', 12))
        self.profile_combo.pack(side=tk.LEFT, padx=5)
        self.profile_combo.bind('<<ComboboxSelected>>', lambda e: self._load_profile(self.current_profile.get()))
        tk.Button(profile_row, text="New Profile", command=self._new_profile, bg=self.current_theme['button'], fg=self.current_theme['fg'],
                  font=('Arial', 11), padx=10).pack(side=tk.LEFT, padx=5)

        tk.Label(profile_row, text="Difficulty:", font=('Arial', 12, 'bold'), bg=self.current_theme['bg'], fg=self.current_theme['fg']).pack(side=tk.LEFT, padx=(30,5))
        diff_combo = ttk.Combobox(profile_row, textvariable=self.current_difficulty, values=['easy','medium','hard'], state="readonly", width=8, font=('Arial', 12))
        diff_combo.pack(side=tk.LEFT, padx=5)

        tk.Button(profile_row, text="🌙 Dark Mode", command=self.toggle_dark_mode, bg=self.current_theme['button'], fg=self.current_theme['fg'],
                  font=('Arial', 11)).pack(side=tk.RIGHT, padx=10)

        # Timer and stats (larger fonts)
        stats_frame = tk.Frame(self.top_panel, bg=self.current_theme['bg'])
        stats_frame.pack(fill=tk.X, pady=5)
        self.timer_label = tk.Label(stats_frame, text="⏱️ Time: 0.0 s", font=('Arial', 16, 'bold'), bg=self.current_theme['bg'], fg=self.current_theme['fg'])
        self.timer_label.pack(side=tk.LEFT, padx=20)
        self.stats_label = tk.Label(stats_frame, text="📊 Accuracy: 100% | WPM: 0", font=('Arial', 14), bg=self.current_theme['bg'], fg=self.current_theme['fg'])
        self.stats_label.pack(side=tk.LEFT, padx=20)

        # Sentence display (bigger, more visible)
        self.sentence_text = tk.Text(self.top_panel, height=3, wrap=tk.WORD, font=('Courier', 16), relief=tk.SUNKEN, padx=15, pady=15,
                                     bg=self.current_theme['entry'], fg=self.current_theme['fg'])
        self.sentence_text.pack(fill=tk.X, padx=20, pady=15)
        self.sentence_text.config(state=tk.DISABLED)

        # Input entry (larger)
        self.input_entry = tk.Entry(self.top_panel, font=('Courier', 16), bg=self.current_theme['entry'], fg=self.current_theme['fg'],
                                    relief=tk.SUNKEN, bd=2)
        self.input_entry.pack(fill=tk.X, padx=20, pady=5)
        self.input_entry.bind('<KeyRelease>', self._on_typing)
        self.input_entry.bind('<KeyPress>', self._on_keypress)

        # Buttons row (larger padding)
        btn_frame = tk.Frame(self.top_panel, bg=self.current_theme['bg'])
        btn_frame.pack(pady=15)
        self.start_btn = tk.Button(btn_frame, text="▶ Start Race", command=self.start_race, bg="#27ae60", fg="white",
                                   font=('Arial', 13, 'bold'), padx=25, pady=5)
        self.start_btn.pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="🔄 Restart", command=self.restart_race, bg="#e67e22", fg="white",
                  font=('Arial', 13, 'bold'), padx=20, pady=5).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="🏠 Main Menu", command=self._show_profile_selector, bg="#95a5a6", fg="white",
                  font=('Arial', 13, 'bold'), padx=20, pady=5).pack(side=tk.LEFT, padx=5)

        # --- Middle panel: Bot progress ---
        self.mid_panel = tk.LabelFrame(self.main_frame, text="🤖 Bot Opponent", font=('Arial', 12, 'bold'),
                                       bg=self.current_theme['bg'], fg=self.current_theme['fg'], padx=10, pady=10)
        self.mid_panel.pack(fill=tk.X, pady=(0, 10))
        self.bot_bar = ttk.Progressbar(self.mid_panel, length=800, mode='determinate', style="TProgressbar")
        self.bot_bar.pack(pady=10, padx=20, fill=tk.X)
        self.bot_label = tk.Label(self.mid_panel, text="Waiting...", font=('Arial', 12), bg=self.current_theme['bg'], fg=self.current_theme['fg'])
        self.bot_label.pack()

        # --- Bottom panel: WPM Graph ---
        self.bottom_panel = tk.Frame(self.main_frame, bg=self.current_theme['bg'], height=250)
        self.bottom_panel.pack(fill=tk.BOTH, expand=True)
        if MATPLOTLIB_AVAILABLE:
            self.figure = Figure(figsize=(10, 3), dpi=90, facecolor=self.current_theme['bg'])
            self.ax = self.figure.add_subplot(111)
            self.ax.set_title("Live WPM Over Time", fontsize=12, color=self.current_theme['fg'])
            self.ax.set_xlabel("Time (seconds)", fontsize=10, color=self.current_theme['fg'])
            self.ax.set_ylabel("WPM", fontsize=10, color=self.current_theme['fg'])
            self.ax.tick_params(colors=self.current_theme['fg'], labelsize=9)
            self.ax.set_facecolor(self.current_theme['bg'])
            self.figure.tight_layout(pad=3.0)
            self.canvas = FigureCanvasTkAgg(self.figure, master=self.bottom_panel)
            self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        else:
            tk.Label(self.bottom_panel, text="Install matplotlib for live WPM graph", font=('Arial', 14),
                     bg=self.current_theme['bg'], fg='red').pack(expand=True)

    def _show_profile_selector(self):
        self.game_active = False
        if self.update_loop_id:
            self.root.after_cancel(self.update_loop_id)
            self.update_loop_id = None
        profiles = list(self.profile_manager.profiles.keys())
        if not profiles:
            name = simpledialog.askstring("First Time", "Enter your profile name:", parent=self.root)
            if name:
                self.profile_manager.create_profile(name)
                self.current_profile.set(name)
                self._load_profile(name)
            else:
                self.root.quit()
        else:
            self.profile_combo['values'] = profiles
            if self.current_profile.get() not in profiles:
                self.current_profile.set(profiles[0])
                self._load_profile(profiles[0])

    def _load_profile(self, name):
        best = self.profile_manager.get_best_wpm(name, self.current_difficulty.get())
        self.stats_label.config(text=f"🏆 Best WPM: {best}")

    def _new_profile(self):
        name = simpledialog.askstring("New Profile", "Enter profile name:", parent=self.root)
        if name and name not in self.profile_manager.profiles:
            self.profile_manager.create_profile(name)
            self.profile_combo['values'] = list(self.profile_manager.profiles.keys())
            self.current_profile.set(name)
            self._load_profile(name)

    def start_race(self):
        difficulty = self.current_difficulty.get()
        sentence, _ = self.sentence_manager.get_random_sentence(difficulty)
        if not sentence:
            messagebox.showerror("Error", "No sentences available")
            return

        self.game_engine.reset()
        self.game_engine.sentence = sentence
        self.input_entry.delete(0, tk.END)
        self.input_entry.config(state=tk.NORMAL)
        self._update_sentence_display()
        self.game_active = True
        self.bot_active = True
        self.bot = TypingBot(difficulty)
        self.bot.start(sentence, time.time())

        self.game_engine.start_timer()
        self._start_update_loop()
        self.input_entry.focus_set()

    def _update_sentence_display(self):
        self.sentence_text.config(state=tk.NORMAL)
        self.sentence_text.delete('1.0', tk.END)
        self.sentence_text.insert('1.0', self.game_engine.sentence)
        self.sentence_text.config(state=tk.DISABLED)
        self._apply_highlighting()

    def _apply_highlighting(self):
        self.sentence_text.config(state=tk.NORMAL)
        self.sentence_text.tag_delete('correct')
        self.sentence_text.tag_delete('incorrect')
        target = self.game_engine.sentence
        typed = self.game_engine.typed_text
        theme = self.current_theme
        self.sentence_text.tag_config('correct', background=theme['correct_bg'])
        self.sentence_text.tag_config('incorrect', background=theme['incorrect_bg'])
        for i, ch in enumerate(target):
            start = f'1.0 + {i}c'
            end = f'1.0 + {i+1}c'
            if i < len(typed):
                if typed[i] == ch:
                    self.sentence_text.tag_add('correct', start, end)
                else:
                    self.sentence_text.tag_add('incorrect', start, end)
        self.sentence_text.config(state=tk.DISABLED)

    def _on_typing(self, event):
        if not self.game_active or self.game_engine.completed:
            return
        typed = self.input_entry.get()
        if len(typed) > len(self.game_engine.sentence):
            self.input_entry.delete(len(self.game_engine.sentence), tk.END)
            typed = self.input_entry.get()
        self.game_engine.update_typed(typed)
        self._apply_highlighting()
        if self.game_engine.completed:
            self._end_race()

    def _on_keypress(self, event):
        if not self.game_active:
            return
        if not self.game_engine.timer_running:
            self.game_engine.start_timer()
        if SOUND_AVAILABLE and event.keysym not in ('BackSpace', 'Delete', 'Left', 'Right'):
            cursor = self.input_entry.index(tk.INSERT)
            if 0 < cursor <= len(self.game_engine.sentence):
                typed_so_far = self.input_entry.get()
                if cursor <= len(typed_so_far):
                    expected = self.game_engine.sentence[cursor-1]
                    if typed_so_far[cursor-1] != expected:
                        try:
                            winsound.Beep(1000, 50)
                        except:
                            pass

    def _start_update_loop(self):
        self._update_loop()

    def _update_loop(self):
        if not self.game_active:
            return
        elapsed = self.game_engine.get_elapsed()
        self.timer_label.config(text=f"⏱️ Time: {elapsed:.1f} s")
        acc = self.game_engine.get_current_accuracy()
        wpm = self.game_engine.get_current_wpm()
        self.stats_label.config(text=f"📊 Accuracy: {acc:.1f}% | WPM: {wpm:.0f}")

        # Update graph (now at bottom)
        if MATPLOTLIB_AVAILABLE and hasattr(self, 'ax'):
            self.ax.clear()
            times = [t for t, _ in self.game_engine.wpm_history]
            wpm_vals = [v for _, v in self.game_engine.wpm_history]
            if times:
                self.ax.plot(times, wpm_vals, 'g-', linewidth=2)
            self.ax.set_title("Live WPM Over Time", fontsize=12, color=self.current_theme['fg'])
            self.ax.set_xlabel("Time (seconds)", fontsize=10, color=self.current_theme['fg'])
            self.ax.set_ylabel("WPM", fontsize=10, color=self.current_theme['fg'])
            self.ax.tick_params(colors=self.current_theme['fg'], labelsize=9)
            self.ax.set_facecolor(self.current_theme['bg'])
            self.figure.tight_layout(pad=3.0)
            self.canvas.draw()

        # Update bot
        if self.bot_active and self.bot and not self.bot.finished:
            current_time = time.time()
            fraction = self.bot.update(current_time)
            self.bot_bar['value'] = fraction * 100
            self.bot_label.config(text=f"Bot progress: {int(fraction*100)}%  ({self.bot.get_progress()}/{len(self.game_engine.sentence)} chars)")
            if self.bot.finished and not self.game_engine.completed:
                self.bot_label.config(text="🤖 Bot finished! You lost.")
                self.game_active = False
                messagebox.showinfo("Race Over", "The bot completed first! Better luck next time.")
                self._end_race()
        elif self.bot_active and self.bot and self.bot.finished:
            pass

        if self.game_active and not self.game_engine.completed:
            self.update_loop_id = self.root.after(100, self._update_loop)
        else:
            self.update_loop_id = None

    def _end_race(self):
        if not self.game_active and self.game_engine.completed:
            return
        final_wpm, final_acc = self.game_engine.complete_game()
        self.game_active = False
        self.bot_active = False
        self.input_entry.config(state=tk.DISABLED)

        profile = self.current_profile.get()
        if profile:
            self.profile_manager.add_score(profile, self.current_difficulty.get(), final_wpm, final_acc)
            best = self.profile_manager.get_best_wpm(profile, self.current_difficulty.get())
            messagebox.showinfo("Race Finished", f"🎉 You completed the race!\n\nWPM: {final_wpm:.1f}\nAccuracy: {final_acc:.1f}%\n\n🏆 Best WPM: {best}")
        else:
            messagebox.showinfo("Race Finished", f"WPM: {final_wpm:.1f}\nAccuracy: {final_acc:.1f}%")

        if self.update_loop_id:
            self.root.after_cancel(self.update_loop_id)
            self.update_loop_id = None

    def restart_race(self):
        if self.update_loop_id:
            self.root.after_cancel(self.update_loop_id)
        self.start_race()

    def toggle_dark_mode(self):
        self.dark_mode = not self.dark_mode
        self.current_theme = self.themes['dark'] if self.dark_mode else self.themes['light']
        self._apply_theme_to_widgets(self.root)
        self._apply_highlighting()
        # Update graph colors
        if MATPLOTLIB_AVAILABLE and hasattr(self, 'ax'):
            self.ax.set_facecolor(self.current_theme['bg'])
            self.ax.set_title("Live WPM Over Time", color=self.current_theme['fg'])
            self.ax.set_xlabel("Time (seconds)", color=self.current_theme['fg'])
            self.ax.set_ylabel("WPM", color=self.current_theme['fg'])
            self.ax.tick_params(colors=self.current_theme['fg'])
            self.figure.set_facecolor(self.current_theme['bg'])
            self.canvas.draw()

    def _apply_theme_to_widgets(self, widget):
        try:
            if isinstance(widget, (tk.Label, tk.Button, tk.Frame, tk.LabelFrame, tk.Text)):
                widget.configure(bg=self.current_theme['bg'], fg=self.current_theme['fg'])
            elif isinstance(widget, tk.Entry):
                widget.configure(bg=self.current_theme['entry'], fg=self.current_theme['fg'])
        except:
            pass
        for child in widget.winfo_children():
            self._apply_theme_to_widgets(child)


# ======================== MAIN ========================
if __name__ == "__main__":
    root = tk.Tk()
    app = AdvancedTypingApp(root)
    root.mainloop()