import random
from tkinter import *

WORD_BANKS = {
    "Normal": [
        "apple",
        "banana",
        "keyboard",
        "result",
        "time",
        "Hippopotomonstrosesquipedaliophobia",
    ],
    "Hard": [
        "binary search",
        "linked list",
        "cloud storage",
        "get question",
        "total rounds",
    ],
    "Nightmare": ["Practice makes perfect.", "Accuracy is more important than speed."],
}

total_rounds = 0
current_round = 0
score = 0
current_answer = ""
time_left = 0
time_left_ms = 0
timer_job = None
elapsed_seconds = 0
wpm_list = []


def get_question(diff):
    return random.choice(WORD_BANKS[diff])


def get_time(diff):
    return 15 if diff == "Nightmare" else 10


def start_game():
    global total_rounds, current_round, score, wpm_list
    wpm_list = []

    diff = diff_var.get()
    rounds_str = round_entry.get()

    if not rounds_str.isdigit():
        result_label.config(text="請輸入有效回合數", fg="red")
        return

    total_rounds = int(rounds_str)
    current_round = 0
    score = 0

    result_label.config(text="")
    answer_entry.config(state="normal")
    next_question()


def next_question():
    global current_round, total_rounds, current_answer
    global time_left, elapsed_seconds

    if current_round >= total_rounds:
        show_result()
        return

    diff = diff_var.get()
    current_answer = get_question(diff)

    show_question(current_answer)

    answer_entry.delete(0, END)
    answer_entry.config(state="normal")

    time_left = get_time(diff)
    current_round += 1

    elapsed_seconds = 0
    start_timer()


# ===== 顯示題目 (動畫) =====
def show_question(text):
    question_text.config(state="normal")
    question_text.delete("1.0", END)

    for i, char in enumerate(text):
        question_text.insert(END, char)
        question_text.tag_add("normal", f"1.{i}", f"1.{i + 1}")

    question_text.tag_config("normal", foreground="black")
    question_text.config(state="disabled")


# ===== 即時顏色回饋 =====
def update_typing_feedback(event=None):

    user = answer_entry.get()

    question_text.config(state="normal")
    question_text.tag_remove("correct", "1.0", END)
    question_text.tag_remove("wrong", "1.0", END)

    for i, char in enumerate(user):
        if i >= len(current_answer):
            break

        if char == current_answer[i]:
            question_text.tag_add("correct", f"1.{i}", f"1.{i + 1}")
        else:
            question_text.tag_add("wrong", f"1.{i}", f"1.{i + 1}")

    question_text.tag_config("correct", foreground="green")
    question_text.tag_config("wrong", foreground="red")

    question_text.config(state="disabled")

    update_live_wpm()


# ===== 即時 WPM =====
def update_live_wpm():
    text = answer_entry.get()
    wpm = calculate_wpm(text, elapsed_seconds)
    wpm_label.config(text=f"WPM: {wpm:.1f}")


def check_answer(event=None):
    global score, timer_job

    if timer_job is not None:
        root.after_cancel(timer_job)

    user_ans = answer_entry.get().strip()
    wpm = calculate_wpm(user_ans, elapsed_seconds)
    wpm_list.append(wpm)

    if user_ans == current_answer:
        result_label.config(text="正確！", fg="green")
        score += 1
    else:
        result_label.config(text=f"錯誤！正確：{current_answer}", fg="red")

    next_question()


def show_result():
    answer_entry.config(state="disabled")

    accuracy = (score / total_rounds) * 100
    avg_wpm = sum(wpm_list) / len(wpm_list) if wpm_list else 0

    result_label.config(
        text=f"成績：{score}/{total_rounds}（{accuracy:.1f}%），平均 WPM：{avg_wpm:.1f}",
        fg="blue",
    )


def start_timer():
    global time_left_ms
    time_left_ms = int(time_left * 1000)
    update_timer()


# ===== Timer + UI動畫 =====
def update_timer():
    global time_left_ms, timer_job, elapsed_seconds

    if time_left_ms <= 0:
        timer_label.config(text="0.0", fg="red")
        result_label.config(text=f"時間到！正確：{current_answer}", fg="red")
        answer_entry.config(state="disabled")
        wpm_list.append(0)

        timer_job = root.after(
            1000, lambda: (answer_entry.config(state="normal"), next_question())
        )
        return

    seconds = time_left_ms / 1000
    timer_label.config(text=f"{seconds:.1f}")

    if seconds < 3:
        timer_label.config(fg="red")
    else:
        timer_label.config(fg="black")

    time_left_ms -= 100
    elapsed_seconds += 0.1
    timer_job = root.after(100, update_timer)


def calculate_wpm(user_input, elapsed_seconds):
    words = len(user_input.split())
    minutes = elapsed_seconds / 60
    if minutes == 0:
        return 0
    return words / minutes


def create_main_window():
    root = Tk()
    root.title("Speed Typing Challenge")
    root.geometry("450x350")
    return root


def create_widgets(root):
    global question_text, timer_label
    global diff_var, round_entry
    global answer_entry, result_label
    global wpm_label

    question_text = Text(
        root, height=2, width=35, font=("Arial", 16), bg="#e0ffff", relief="flat"
    )
    question_text.pack(pady=10)

    timer_label = Label(
        root, text="準備開始", font=("Arial", 18), bg="#ccffcc", width=10
    )
    timer_label.pack(pady=5)

    wpm_label = Label(root, text="WPM: 0", font=("Arial", 14))
    wpm_label.pack()

    diff_var = StringVar(value="Normal")
    OptionMenu(root, diff_var, "Normal", "Hard", "Nightmare").pack(pady=5)

    round_entry = Entry(root, width=10, font=("Arial", 12))
    round_entry.pack(pady=5)
    round_entry.insert(0, "5")

    answer_entry = Entry(root, width=25, font=("Arial", 14))
    answer_entry.pack(pady=10)
    answer_entry.bind("<Return>", check_answer)
    answer_entry.bind("<KeyRelease>", update_typing_feedback)

    result_label = Label(root, text="", font=("Arial", 12))
    result_label.pack()

    Button(
        root,
        text="開始遊戲",
        width=12,
        height=2,
        bg="#ffcc99",
        font=("Arial", 12, "bold"),
        command=start_game,
    ).pack(pady=10)


root = create_main_window()
create_widgets(root)
root.mainloop()
