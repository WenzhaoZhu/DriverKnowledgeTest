import tkinter as tk
import tkinter.font as tkf
import json
from PIL import ImageTk, Image
import random


QUESTIONS_PATH = "./static/questions.json"


# create a start button
def startWidget():
    global START_BUTTON
    BUTTON_SIZE = [3, 14]
    buttonFont = tkf.Font(family="Comic Sans MS", size=20, weight="bold")
    start_button = tk.Button(
        main_windows,
        text="Start",
        font=buttonFont,
        height=BUTTON_SIZE[0],
        width=BUTTON_SIZE[1],
        command=lambda: createQuestion(0, 0, True, -1),
    )
    start_button.place(x=400, y=300, anchor="center")
    START_BUTTON = start_button


# Read JSON file
def read_JSON(num):
    with open(QUESTIONS_PATH, "r") as f:
        data = json.load(f)
        return (
            data[str(num)]["Q"],
            data[str(num)]["P"],
            data[str(num)]["O"],
            data[str(num)]["A"],
        )


# Clear all the components of main_windows
def clearFrame():
    for widget in main_windows.winfo_children():
        widget.destroy()


# show the final score
def showScore(score):
    clearFrame()
    scoreFont = tkf.Font(family="Comic Sans MS", size=24, weight="bold")
    score_str = "Your Score: " + str(score)
    score_label = tk.Label(main_windows, text=score_str, font=scoreFont)
    score_label.place(x=400, y=300, anchor="center")


QUSET = []  # question set, maximum of length 30


# create one questions
def createQuestion(index, score, flag, questionNum):
    # clear the frame
    clearFrame()

    # Initicalize the question number to bound it
    if flag:
        while len(QUSET) != index + 1:
            questionNum = random.randint(0, NUM_OF_QUESTIONS - 1)
            if questionNum not in QUSET:
                QUSET.append(questionNum)

    # Read one question from the JSON file
    Q, P, Option, A = read_JSON(questionNum)

    # Font for all the following text
    questionFont = tkf.Font(family="Times New Roman", size=16, weight="bold")

    # score
    score_str = "Score [%s/%s]" % (str(score), str(NUM_OF_QUESTION_PER_SET))
    score_label = tk.Label(main_windows, text=score_str, font=questionFont)
    score_label.pack(anchor="w")

    # NO. of a question
    qNum_str = "[%s]" % (str(index + 1))
    label = tk.Label(main_windows, text=qNum_str, font=questionFont)
    label.pack()

    # Content of a question
    label_q = tk.Label(main_windows, text=Q, font=questionFont)
    label_q.pack()

    # Picture if applicable
    if P != "None":
        # Create an object of tkinter ImageTk
        # This has to be global cuz it will be clear when it's just a local var
        global img
        img = ImageTk.PhotoImage(Image.open(P))

        # Create a Label Widget to display the text or Image
        label_img = tk.Label(main_windows, image=img)
        label_img.pack()

    var = tk.IntVar()  # the variable to store the value of myAnswer
    var.set(0)  # initialize var to 0

    # Content of the answer
    if flag:
        for ans in range(4):
            selectionLine = tk.Radiobutton(
                main_windows,
                text=Option[ans],
                variable=var,
                value=ans + 1,
                font=questionFont,
            )
            selectionLine.pack(anchor="w")
    else:
        for ans in range(4):
            if (ans + 1) != A:
                selectionLine = tk.Radiobutton(
                    main_windows,
                    text=Option[ans],
                    variable=var,
                    value=ans + 1,
                    font=questionFont,
                )
            else:
                selectionLine = tk.Radiobutton(
                    main_windows,
                    text=Option[ans],
                    variable=var,
                    value=ans + 1,
                    font=questionFont,
                    fg="green",
                )
            selectionLine.pack(anchor="w")

    if index < NUM_OF_QUESTION_PER_SET - 1:  # when it's not the last question
        if flag:
            next_button = tk.Button(
                main_windows,
                text="Next",
                font=questionFont,
                command=lambda: judge_right_or_wrong(
                    index, score, var.get(), A, questionNum
                ),  # determine whether the anser is right or wrong
            )
        else:
            next_button = tk.Button(
                main_windows,
                text="Next",
                font=questionFont,
                command=lambda: createQuestion(
                    index + 1, score, True, questionNum
                ),  # after showing the correct answer, go to the next question
            )

        next_button.pack(anchor="s")

    else:  # When it's the last question
        if flag:
            finish_button = tk.Button(
                main_windows,
                text="Finish",
                font=questionFont,
                command=lambda: judge_right_or_wrong(
                    index, score, var.get(), A, questionNum
                ),  # determine whether the anser is right or wrong
            )
        else:
            finish_button = tk.Button(
                main_windows,
                text="Finish",
                font=questionFont,
                command=lambda: showScore(
                    score
                ),  # after showing the correct answer, go to the next question
            )
        finish_button.pack(anchor="s")


def judge_right_or_wrong(index, score, var_int, prev_ref, qNum):
    if index == NUM_OF_QUESTION_PER_SET - 1:  # when it's the last question
        if prev_ref == var_int:  # if do it correct
            showScore(score + 1)  # show the final score directly
        else:  # if do it wrong
            createQuestion(
                index, score, False, qNum
            )  # show the same question with the right answer

    else:  # when it's not the last question
        if var_int == prev_ref:
            createQuestion(
                index + 1, score + 1, True, qNum
            )  # show the next question
        else:
            createQuestion(
                index, score, False, qNum
            )  # show the same question with the right answer


NUM_OF_QUESTIONS = 108
NUM_OF_QUESTION_PER_SET = 30

if __name__ == "__main__":
    main_windows = tk.Tk()
    main_windows.title("Alberta Driver's Knowledge Quiz")
    main_windows.geometry("800x600")
    startWidget()
    main_windows.mainloop()
