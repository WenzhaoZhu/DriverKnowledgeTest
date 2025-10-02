from flask import (
    Flask,
    render_template,
    request,
    session,
    redirect,
    url_for,
)
from flask_wtf.csrf import CSRFProtect
import json
import random
from datetime import datetime
import os
from functools import wraps

app = Flask(__name__)
app.secret_key = "your-secret-key-here"  # Required for session and CSRF
csrf = CSRFProtect(app)

# Constants
NUM_OF_QUESTIONS = 108
NUM_OF_QUESTION_PER_SET = 30


def read_questions():
    """Read all questions from JSON file"""
    with open("./static/questions.json", "r") as f:
        return json.load(f)


def get_random_questions(num_questions):
    """Get random questions without repetition"""
    all_questions = list(range(NUM_OF_QUESTIONS))
    return random.sample(all_questions, num_questions)


def init_session():
    """Initialize or reset session variables"""
    # Store only question numbers in session, not the full question data
    session["questions"] = get_random_questions(NUM_OF_QUESTION_PER_SET)
    session["current_question"] = 0
    session["score"] = 0
    session["start_time"] = datetime.now().isoformat()
    session["answers"] = []  # Store only essential answer data
    session["scored_questions"] = []  # Track which questions have been scored
    # Remove questions_data from session as it's too large
    if "questions_data" in session:
        del session["questions_data"]


def get_question_data(question_num):
    """Get question data from JSON file"""
    # Read from file each time instead of storing in session
    questions_data = read_questions()
    return questions_data[str(question_num)]


def requires_quiz_session(f):
    """Decorator to ensure quiz session is active"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "questions" not in session:
            return redirect(url_for("home"))
        return f(*args, **kwargs)

    return decorated_function


@app.route("/")
def home():
    """Render the home page"""
    session.clear()  # Clear any existing session data
    return render_template(
        "index.html",
        NUM_OF_QUESTIONS=NUM_OF_QUESTIONS,
        NUM_OF_QUESTION_PER_SET=NUM_OF_QUESTION_PER_SET,
    )


@app.route("/start-quiz")
def start_quiz():
    """Initialize and start the quiz"""
    init_session()
    return redirect(url_for("show_question"))


@app.route("/question")
@requires_quiz_session
def show_question():
    """Show the current question"""
    current_index = session["current_question"]
    if current_index >= NUM_OF_QUESTION_PER_SET:
        return redirect(url_for("show_score"))

    question_num = session["questions"][current_index]
    question_data = get_question_data(question_num)

    # Get user's previous answer for this question if it exists
    answer_data = (
        session["answers"][current_index]
        if current_index < len(session["answers"])
        else None
    )
    user_answer = answer_data["user_answer"] if answer_data else None

    # A question is only scored if it has been answered
    is_scored = answer_data is not None

    return render_template(
        "question.html",
        question=question_data["Q"],
        options=question_data["O"],
        image=question_data["P"],
        correct_answer=question_data["A"],
        question_num=current_index + 1,
        total_questions=NUM_OF_QUESTION_PER_SET,
        user_answer=user_answer,
        is_scored=is_scored,
    )


@app.route("/previous-question")
@requires_quiz_session
def previous_question():
    """Go back to the previous question"""
    if session["current_question"] > 0:
        session["current_question"] -= 1
    return redirect(url_for("show_question"))


@app.route("/check_answer", methods=["POST"])
@requires_quiz_session
def check_answer():
    """Handle answer submission"""
    try:
        current_index = session["current_question"]
        if current_index >= NUM_OF_QUESTION_PER_SET:
            return redirect(url_for("show_score"))

        # Get the user's answer with better error handling
        answer = request.form.get("answer")
        if answer is None:
            app.logger.error("No answer submitted in form data")
            return "No answer submitted", 400

        try:
            user_answer = int(answer)
        except ValueError:
            app.logger.error(f"Invalid answer value submitted: {answer}")
            return "Invalid answer value", 400

        if user_answer not in [1, 2, 3, 4]:
            app.logger.error(f"Answer out of valid range: {user_answer}")
            return "Answer must be between 1 and 4", 400

        question_num = session["questions"][current_index]
        question_data = get_question_data(question_num)
        correct_answer = question_data["A"]

        # Store only essential answer data
        while len(session["answers"]) <= current_index:
            session["answers"].append({})

        # Get previous answer data if it exists
        previous_answer = session["answers"][current_index]
        was_correct = (
            previous_answer.get("is_correct", False)
            if previous_answer
            else False
        )

        is_correct = user_answer == correct_answer
        session["answers"][current_index] = {
            "question_num": question_num,  # Store only the question number
            "user_answer": user_answer,
            "is_correct": is_correct,
        }

        # Update score based on whether the answer changed
        # from correct to incorrect or vice versa
        if was_correct and not is_correct:
            session["score"] = max(
                0, session.get("score", 0) - 1
            )  # Decrement score if changing from correct to incorrect
        elif not was_correct and is_correct:
            session["score"] = (
                session.get("score", 0) + 1
            )  # Increment score if changing from incorrect to correct

        # Move to next question
        session["current_question"] = current_index + 1

        # If this was the last question, show the score
        if current_index + 1 >= NUM_OF_QUESTION_PER_SET:
            return redirect(url_for("show_score"))

        return redirect(url_for("show_question"))

    except Exception as e:
        app.logger.error(f"Error processing answer: {str(e)}")
        return "An error occurred while processing your answer", 400


@app.route("/show_score")
@requires_quiz_session
def show_score():
    """Show the final score and review all answers"""
    # Record end time
    session["end_time"] = datetime.now().isoformat()

    # Calculate duration
    start_time = datetime.fromisoformat(session["start_time"])
    end_time = datetime.fromisoformat(session["end_time"])
    duration = end_time - start_time
    minutes = duration.seconds // 60
    seconds = duration.seconds % 60

    # Recalculate final score by counting all correct answers
    final_score = sum(
        1 for answer in session["answers"] if answer.get("is_correct", False)
    )
    total_questions = NUM_OF_QUESTION_PER_SET

    # Update the session score to match the actual count
    session["score"] = final_score

    # Get all questions and answers for review
    review_data = []
    for i, question_num in enumerate(session["questions"]):
        question_data = get_question_data(question_num)
        answer_data = (
            session["answers"][i] if i < len(session["answers"]) else None
        )

        review_data.append(
            {
                "question_num": i + 1,
                "question": question_data["Q"],
                "image": question_data["P"],
                "options": question_data["O"],
                "correct_answer": question_data["A"],
                "user_answer": answer_data["user_answer"]
                if answer_data
                else None,
                "is_correct": answer_data["is_correct"]
                if answer_data
                else False,
            }
        )

    return render_template(
        "score.html",
        score=final_score,
        total_questions=total_questions,
        review_data=review_data,
        duration_minutes=minutes,
        duration_seconds=seconds,
    )


if __name__ == "__main__":
    # Create templates directory if it doesn't exist
    os.makedirs("templates", exist_ok=True)
    app.run(debug=True)
