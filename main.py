import random
import subprocess
import threading
import tkinter as tk

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

OP_SYMBOL = {"addition": "+", "subtraction": "−", "multiplication": "×", "division": "÷"}

DIFFICULTY_SETTINGS = {
    "Easy":   dict(add_sub=range(1, 10),  mul_div=range(1, 6),  questions=5),
    "Medium": dict(add_sub=range(1, 20),  mul_div=range(1, 10), questions=10),
    "Hard":   dict(add_sub=range(5, 30),  mul_div=range(1, 12), questions=15),
}

TRANSLATIONS = {
    "English": {
        "welcome_to":        "Welcome to the",
        "math_quiz":         "Math Quiz!",
        "start_quiz":        "Start Quiz",
        "select_language":   "Select Language",
        "language_subtitle": "Which language do you prefer?",
        "select_difficulty": "Select Difficulty",
        "how_challenging":   "How challenging do you want it?",
        "easy":              "Easy",
        "medium":            "Medium",
        "hard":              "Hard",
        "choose_operation":  "Choose an Operation",
        "addition":          "Addition",
        "subtraction":       "Subtraction",
        "multiplication":    "Multiplication",
        "division":          "Division",
        "difficulty_label":  "Difficulty",
        "submit":            "Submit",
        "correct":           "Correct!",
        "incorrect_msgs":    ["Incorrect!", "Try again!", "Not quite!", "Keep trying!", "Almost there!"],
        "enter_number":      "Please enter a whole number.",
        "question_of":       lambda n, t: f"Question {n} / {t}",
        "quiz_complete":     "Quiz Complete!",
        "correct_count":     lambda c, t: f"{c} / {t} correct",
        "wrong_count":       lambda w: f"{w} wrong answer{'s' if w != 1 else ''}",
        "play_again":        "Play Again",
        "change_difficulty": "Change Difficulty",
        "by_author":         "by: Mark Khomenko",
        "settings":          "Settings",
        "sound_effects":     "Sound Effects",
        "back_to_main":      "Back to Main Menu",
    },
    "Français": {
        "welcome_to":        "Bienvenue au",
        "math_quiz":         "Quiz de Maths!",
        "start_quiz":        "Commencer le Quiz",
        "select_language":   "Choisir la Langue",
        "language_subtitle": "Quelle langue préférez-vous?",
        "select_difficulty": "Choisir la Difficulté",
        "how_challenging":   "Quel niveau de difficulté?",
        "easy":              "Facile",
        "medium":            "Moyen",
        "hard":              "Difficile",
        "choose_operation":  "Choisir une Opération",
        "addition":          "Addition",
        "subtraction":       "Soustraction",
        "multiplication":    "Multiplication",
        "division":          "Division",
        "difficulty_label":  "Difficulté",
        "submit":            "Soumettre",
        "correct":           "Correct!",
        "incorrect_msgs":    ["Incorrect!", "Réessaie!", "Pas tout à fait!", "Continue!", "Presque!"],
        "enter_number":      "Veuillez entrer un nombre entier.",
        "question_of":       lambda n, t: f"Question {n} / {t}",
        "quiz_complete":     "Quiz Terminé!",
        "correct_count":     lambda c, t: f"{c} / {t} correct{'s' if c != 1 else ''}",
        "wrong_count":       lambda w: f"{w} mauvaise{'s' if w != 1 else ''} réponse{'s' if w != 1 else ''}",
        "play_again":        "Rejouer",
        "change_difficulty": "Changer de Difficulté",
        "by_author":         "par: Mark Khomenko",
        "settings":          "Paramètres",
        "sound_effects":     "Effets Sonores",
        "back_to_main":      "Retour au Menu Principal",
    },
}

# Colours
BG      = "#1e1e2e"
CARD    = "#313244"
SURFACE = "#45475a"
ACCENT  = "#89b4fa"
GREEN   = "#a6e3a1"
RED     = "#f38ba8"
ORANGE  = "#fab387"
TEXT    = "#cdd6f4"
SUBTEXT = "#a6adc8"

# ---------------------------------------------------------------------------
# Quiz state
# ---------------------------------------------------------------------------

state = {
    "language":      "English",
    "difficulty":    None,
    "operation":     None,
    "num_questions": 0,
    "current":       0,
    "wrong":         0,
    "num1":          0,
    "num2":          0,
    "add_sub_pool":  [],
    "mul_div_pool":  [],
    "sound_enabled": True,
}


def t(key):
    return TRANSLATIONS[state["language"]][key]

# ---------------------------------------------------------------------------
# Quiz logic
# ---------------------------------------------------------------------------

def generate_question():
    op   = state["operation"]
    pool = state["add_sub_pool"] if op in ("addition", "subtraction") else state["mul_div_pool"]
    a = random.choice(pool)

    if op == "subtraction":
        a = random.choice([n for n in pool if n > min(pool)] or pool)
        candidates = [n for n in pool if n < a]
        b = random.choice(candidates)
    elif op == "division":
        candidates = [n for n in pool if n != 0 and a % n == 0]
        b = random.choice(candidates) if candidates else 1
    else:
        b = random.choice(pool)

    return a, b


def correct_answer(a, b, op):
    return {
        "addition":       a + b,
        "subtraction":    a - b,
        "multiplication": a * b,
        "division":       a // b,
    }[op]


def _play(path):
    subprocess.run(["afplay", path])


def play_correct_sound():
    if state["sound_enabled"]:
        threading.Thread(target=_play, args=("sound_effects/correct.mp3",), daemon=True).start()


def play_wrong_sound():
    if state["sound_enabled"]:
        threading.Thread(target=_play, args=("sound_effects/wrong_answer.mp3",), daemon=True).start()


def play_click_sound():
    if state["sound_enabled"]:
        threading.Thread(target=_play, args=("sound_effects/Click.mp3",), daemon=True).start()

# ---------------------------------------------------------------------------
# Shared widget helpers
# ---------------------------------------------------------------------------

def label(parent, text, size=14, bold=False, color=TEXT, bg=BG, **kw):
    return tk.Label(
        parent, text=text, fg=color, bg=bg,
        font=("Helvetica", size, "bold" if bold else "normal"),
        **kw,
    )


def button(parent, text, command, color=ACCENT, width=22):
    def _cmd():
        play_click_sound()
        command()
    return tk.Button(
        parent, text=text, command=_cmd,
        font=("Helvetica", 18, "bold"),
        fg=BG, bg=color, activebackground=color, activeforeground=BG,
        relief="flat", cursor="hand2", width=width,
        padx=14, pady=13,
    )


def divider(parent, padx=80, pady=24):
    tk.Frame(parent, bg=CARD, height=2).pack(fill="x", padx=padx, pady=pady)

# ---------------------------------------------------------------------------
# Screens
# ---------------------------------------------------------------------------

class WelcomeScreen(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg=BG)
        label(self, t("welcome_to"), size=20, color=SUBTEXT).pack(pady=(145, 0))
        label(self, t("math_quiz"), size=44, bold=True).pack(pady=(6, 90))
        button(self, t("start_quiz"), lambda: master.show(LanguageScreen)).pack()
        label(self, t("by_author"), size=12, color=SUBTEXT).place(x=14, y=670)


class LanguageScreen(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg=BG)
        label(self, t("select_language"), size=30, bold=True).pack(pady=(110, 8))
        label(self, t("language_subtitle"), size=16, color=SUBTEXT).pack(pady=(0, 55))

        button(self, "English",  lambda: self._select(master, "English"),  color=ACCENT).pack(pady=7)
        button(self, "Français", lambda: self._select(master, "Français"), color=ORANGE).pack(pady=7)

    def _select(self, master, lang):
        state["language"] = lang
        master.show(DifficultyScreen)


class DifficultyScreen(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg=BG)
        label(self, t("select_difficulty"), size=30, bold=True).pack(pady=(110, 8))
        label(self, t("how_challenging"), size=16, color=SUBTEXT).pack(pady=(0, 55))

        difficulty_keys = ["Easy", "Medium", "Hard"]
        display_keys    = ["easy", "medium", "hard"]
        colors          = [GREEN, ACCENT, RED]

        for key, dkey, color in zip(difficulty_keys, display_keys, colors):
            button(self, t(dkey), lambda k=key: self._select(master, k), color=color).pack(pady=7)

    def _select(self, master, name):
        cfg = DIFFICULTY_SETTINGS[name]
        state.update(
            difficulty=name,
            num_questions=cfg["questions"],
            add_sub_pool=list(cfg["add_sub"]),
            mul_div_pool=list(cfg["mul_div"]),
        )
        master.show(OperationScreen)


class OperationScreen(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg=BG)
        diff_display = t(state["difficulty"].lower())
        label(self, f"{t('difficulty_label')}: {diff_display}", size=16, color=SUBTEXT).pack(pady=(85, 0))
        label(self, t("choose_operation"), size=30, bold=True).pack(pady=(6, 48))

        ops = [
            ("addition",       GREEN),
            ("subtraction",    ACCENT),
            ("multiplication", ORANGE),
            ("division",       RED),
        ]
        for key, color in ops:
            text = f"{t(key)}  {OP_SYMBOL[key]}"
            button(self, text, lambda k=key: self._select(master, k), color=color).pack(pady=6)

    def _select(self, master, key):
        state.update(operation=key, current=0, wrong=0)
        master.show(QuizScreen)


class QuizScreen(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg=BG)
        self._master = master
        op = state["operation"]

        # ── Header ──────────────────────────────────────────────────────────
        header = tk.Frame(self, bg=CARD, pady=16)
        header.pack(fill="x")
        label(header, f"{t(op)}  {OP_SYMBOL[op]}", size=18, bold=True, bg=CARD).pack(side="left", padx=30)
        self._progress_lbl = label(header, "", size=16, color=SUBTEXT, bg=CARD)
        self._progress_lbl.pack(side="right", padx=(0, 85))

        # ── Progress bar ─────────────────────────────────────────────────────
        bar_bg = tk.Frame(self, bg=CARD, height=8)
        bar_bg.pack(fill="x", padx=0)
        bar_bg.pack_propagate(False)
        self._bar = tk.Frame(bar_bg, bg=ACCENT, height=8)
        self._bar.place(x=0, y=0, relheight=1, relwidth=0)

        # ── Question ─────────────────────────────────────────────────────────
        self._question_lbl = label(self, "", size=48, bold=True)
        self._question_lbl.pack(pady=(90, 40))

        # ── Answer entry ─────────────────────────────────────────────────────
        self._answer = tk.StringVar()
        self._entry = tk.Entry(
            self, textvariable=self._answer,
            font=("Helvetica", 30), width=6,
            justify="center", relief="flat",
            bg=CARD, fg=TEXT, insertbackground=TEXT,
        )
        self._entry.pack(ipady=14)
        self._entry.bind("<Return>", lambda _: self._submit())

        # ── Submit button ─────────────────────────────────────────────────────
        button(self, t("submit"), self._submit, color=ACCENT).pack(pady=20)

        # ── Feedback ─────────────────────────────────────────────────────────
        self._feedback_lbl = label(self, "", size=18)
        self._feedback_lbl.pack()

        self._load_question()

    def _load_question(self):
        n     = state["current"]
        total = state["num_questions"]
        self._progress_lbl.configure(text=t("question_of")(n + 1, total))
        self._bar.place(relwidth=n / total)
        self._answer.set("")
        self._feedback_lbl.configure(text="")
        a, b = generate_question()
        state["num1"], state["num2"] = a, b
        sym = OP_SYMBOL[state["operation"]]
        self._question_lbl.configure(text=f"{a}  {sym}  {b}  =  ?")
        self._entry.focus()

    def _submit(self):
        raw = self._answer.get().strip()
        if not raw:
            return
        try:
            answer = int(raw)
        except ValueError:
            self._feedback_lbl.configure(text=t("enter_number"), fg=RED)
            return

        expected = correct_answer(state["num1"], state["num2"], state["operation"])

        if answer == expected:
            play_correct_sound()
            self._feedback_lbl.configure(text=t("correct"), fg=GREEN)
            state["current"] += 1
            if state["current"] >= state["num_questions"]:
                self._bar.place(relwidth=1)
                self.after(700, lambda: self._master.show(ResultScreen))
            else:
                self.after(700, self._load_question)
        else:
            state["wrong"] += 1
            play_wrong_sound()
            self._feedback_lbl.configure(text=random.choice(t("incorrect_msgs")), fg=RED)
            self._answer.set("")
            self._entry.focus()


class ResultScreen(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg=BG)
        total   = state["num_questions"]
        wrong   = state["wrong"]
        correct = total - wrong
        op      = t(state["operation"])
        diff    = t(state["difficulty"].lower())

        label(self, t("quiz_complete"), size=36, bold=True).pack(pady=(110, 6))
        label(self, f"{op}  ·  {diff}", size=18, color=SUBTEXT).pack()

        divider(self, padx=90, pady=32)

        score_color = GREEN if wrong == 0 else (ORANGE if wrong <= total // 2 else RED)
        label(self, t("correct_count")(correct, total), size=28, bold=True, color=score_color).pack(pady=6)
        label(self, t("wrong_count")(wrong), size=18, color=SUBTEXT).pack(pady=6)

        divider(self, padx=90, pady=32)

        btn_row = tk.Frame(self, bg=BG)
        btn_row.pack()
        button(btn_row, t("play_again"),        lambda: master.show(OperationScreen),  color=GREEN,  width=18).pack(side="left", padx=14)
        button(btn_row, t("change_difficulty"), lambda: master.show(DifficultyScreen), color=ACCENT, width=20).pack(side="left", padx=14)

class ToggleSwitch(tk.Canvas):
    """Pill-shaped toggle switch."""
    W, H = 64, 32

    def __init__(self, parent, initial, on_change, **kw):
        super().__init__(
            parent, width=self.W, height=self.H,
            bg=CARD, highlightthickness=0, cursor="hand2", **kw,
        )
        self._on = initial
        self._on_change = on_change
        self._draw()
        self.bind("<Button-1>", self._click)

    def _draw(self):
        self.delete("all")
        w, h, r = self.W, self.H, self.H // 2
        track = GREEN if self._on else SURFACE
        # Track
        self.create_oval(0, 0, h - 1, h - 1, fill=track, outline="")
        self.create_oval(w - h, 0, w - 1, h - 1, fill=track, outline="")
        self.create_rectangle(r, 0, w - r, h, fill=track, outline="")
        # Knob
        pad = 4
        cx = w - r if self._on else r
        self.create_oval(cx - r + pad, pad, cx + r - pad, h - pad, fill=BG, outline="")

    def _click(self, _):
        play_click_sound()
        self._on = not self._on
        self._on_change(self._on)
        self._draw()


class SettingsScreen(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg=BG)

        # ── Close button (top-left) ─────────────────────────────────────────
        close_btn = tk.Button(
            self, text="✕", command=lambda: master.show(master._prev_frame_class),
            font=("Helvetica", 18), fg=SUBTEXT, bg=BG,
            activebackground=BG, activeforeground=TEXT,
            relief="flat", cursor="hand2", bd=0,
            padx=12, pady=8,
        )
        close_btn.place(x=8, y=8)
        close_btn.bind("<Enter>", lambda _: close_btn.configure(fg=TEXT))
        close_btn.bind("<Leave>", lambda _: close_btn.configure(fg=SUBTEXT))

        # ── Title ──────────────────────────────────────────────────────────
        label(self, t("settings"), size=32, bold=True).pack(pady=(100, 48))

        # ── Settings card ──────────────────────────────────────────────────
        card = tk.Frame(self, bg=CARD)
        card.pack(padx=220, fill="x")

        row = tk.Frame(card, bg=CARD)
        row.pack(fill="x", padx=32, pady=26)
        label(row, t("sound_effects"), size=16, bg=CARD).pack(side="left")
        ToggleSwitch(row, state["sound_enabled"],
                     lambda v: state.update(sound_enabled=v)).pack(side="right")

        # ── Back button ────────────────────────────────────────────────────
        divider(self, padx=220, pady=40)
        button(self, t("back_to_main"), lambda: master.show(WelcomeScreen), color=ACCENT).pack()

# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

class QuizApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Math Quiz")
        self.geometry("1000x700")
        self.resizable(False, False)
        self.configure(bg=BG)
        self._frame = None
        self._prev_frame_class = WelcomeScreen

        self._settings_btn = tk.Button(
            self, text="⚙", command=self._open_settings,
            font=("Helvetica", 26), fg=SUBTEXT, bg=BG,
            activebackground=BG, activeforeground=TEXT,
            relief="flat", cursor="hand2", bd=0,
            padx=12, pady=8,
        )
        self._settings_btn.place(relx=1.0, x=-8, y=8, anchor="ne")
        self._settings_btn.bind("<Enter>", lambda _: self._settings_btn.configure(fg=TEXT))
        self._settings_btn.bind("<Leave>", lambda _: self._settings_btn.configure(fg=SUBTEXT))

        self.show(WelcomeScreen)

    def _open_settings(self):
        play_click_sound()
        self._prev_frame_class = self._frame.__class__
        self.show(SettingsScreen)

    def show(self, FrameClass):
        if self._frame:
            self._frame.destroy()
        self._frame = FrameClass(self)
        self._frame.pack(expand=True, fill="both")
        btn_bg = CARD if FrameClass == QuizScreen else BG
        self._settings_btn.configure(bg=btn_bg, activebackground=btn_bg)
        self._settings_btn.lift()


if __name__ == "__main__":
    QuizApp().mainloop()
