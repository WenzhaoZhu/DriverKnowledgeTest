import tkinter as tk
import tkinter.font as tkf
import json
from PIL import ImageTk, Image
import random


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
        command=lambda: createQuestion(0, 0, 0, -1),
    )
    start_button.place(x=400, y=300, anchor="center")
    START_BUTTON = start_button


# Read JSON file
def read_JSON(num):
    with open("questions.json", "r") as f:
        data = json.load(f)
        return data[str(num)]["Q"], data[str(num)]["P"], data[str(num)]["O"], data[
            str(num)
        ]["A"]


# Clear all the components of main_windows
def clearFrame():
    for widget in main_windows.winfo_children():
        widget.destroy()


# show the final score
def showScore(score):
    scoreFont = tkf.Font(family="Comic Sans MS", size=24, weight="bold")
    score_str = "Your Score: " + str(score)
    score_label = tk.Label(main_windows, text=score_str, font=scoreFont)
    score_label.pack(anchor="center")


QUSET = [] # question set, maximum of length 30, storing all the previous shown questions
# create one questions
def createQuestion(index, score, var_int, prev_ref):
    # TEMP: destroy the 'start_button'
    clearFrame()

    # Initicalize the question number to bound it
    questionNum = -1
    while len(QUSET) != index + 1:
        questionNum = random.randint(0, NUM_OF_QUESTIONS - 1)
        if questionNum not in QUSET:
            QUSET.append(questionNum)

    # Read one question from the JSON file
    Q, P, Option, A = read_JSON(questionNum)

    # Font for all the following text
    questionFont = tkf.Font(family="Times New Roman", size=16, weight="bold")

    # score
    if prev_ref == var_int:
        score += 1
    score_str = "Score [%s/30]" % (str(score))
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
        global img  # This has to be global cuz it will be clear when it's just a local var
        img = ImageTk.PhotoImage(Image.open("pictures/Pic7.jpg"))

        # Create a Label Widget to display the text or Image
        label_img = tk.Label(main_windows, image=img)
        label_img.pack()

    var = tk.IntVar()  # the variable to store the value of myAnswer
    var.set(0)  # initialize var to 0

    # Content of the answer
    for ans in range(4):
        selectionLine = tk.Radiobutton(
            main_windows,
            text=Option[ans],
            variable=var,
            value=ans + 1,
            font=questionFont,
        )
        selectionLine.pack(anchor="w")

    if index < NUM_OF_QUESTION_PER_SET-1: # when it's not the last question
        next_button = tk.Button(
            main_windows,
            text="Next",
            font=questionFont,
            command=lambda: createQuestion(index + 1, score, var.get(), A),
        )

        next_button.pack(anchor="s")

    else: # When it's the last question
        finish_button = tk.Button(
            main_windows,
            text="Finish",
            font=questionFont,
            command=lambda: showScore(score),
        )

        finish_button.pack(anchor="s")


NUM_OF_QUESTIONS = 2
NUM_OF_QUESTION_PER_SET = 30
if __name__ == "__main__":
    main_windows = tk.Tk()

    main_windows.title("Alberta Driver's Knowledge Quiz")
    main_windows.geometry("800x600")

    startWidget()
    main_windows.mainloop()
