from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_wtf.csrf import CSRFProtect
import json
import random
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Required for session and CSRF
csrf = CSRFProtect(app)

# Constants
NUM_OF_QUESTIONS = 108
NUM_OF_QUESTION_PER_SET = 30

def read_questions():
    """Read all questions from JSON file"""
    with open("questions.json", "r") as f:
        return json.load(f)

def get_random_questions(num_questions):
    """Get random questions without repetition"""
    all_questions = list(range(NUM_OF_QUESTIONS))
    return random.sample(all_questions, num_questions)

@app.route('/')
def home():
    """Render the home page"""
    session.clear()  # Clear any existing session data
    return render_template('index.html', 
                         NUM_OF_QUESTIONS=NUM_OF_QUESTIONS,
                         NUM_OF_QUESTION_PER_SET=NUM_OF_QUESTION_PER_SET)

@app.route('/start-quiz')
def start_quiz():
    """Initialize and start the quiz"""
    # Generate random questions for this session
    session['questions'] = get_random_questions(NUM_OF_QUESTION_PER_SET)
    session['current_question'] = 0
    session['score'] = 0
    session['start_time'] = datetime.now().isoformat()
    session['revealed_answers'] = []  # Track which questions had answers revealed
    session['user_answers'] = []  # Track user's answers for each question
    session['scored_questions'] = []  # Track which questions have been scored
    return redirect(url_for('show_question'))

@app.route('/question')
def show_question():
    """Show the current question"""
    if 'questions' not in session:
        return redirect(url_for('home'))
    
    current_index = session['current_question']
    if current_index >= NUM_OF_QUESTION_PER_SET:
        return redirect(url_for('show_score'))
    
    question_num = session['questions'][current_index]
    questions_data = read_questions()
    question_data = questions_data[str(question_num)]
    
    # Get user's previous answer for this question if it exists
    user_answer = None
    if 'user_answers' in session and current_index < len(session['user_answers']):
        user_answer = session['user_answers'][current_index]
    
    # Check if this question has already been scored
    is_scored = current_index in session.get('scored_questions', [])
    
    return render_template('question.html',
                         question=question_data['Q'],
                         options=question_data['O'],
                         image=question_data['P'],
                         correct_answer=question_data['A'],
                         question_num=current_index + 1,
                         total_questions=NUM_OF_QUESTION_PER_SET,
                         user_answer=user_answer,
                         is_scored=is_scored)

@app.route('/previous-question')
def previous_question():
    """Go back to the previous question"""
    if 'current_question' in session and session['current_question'] > 0:
        session['current_question'] -= 1
    return redirect(url_for('show_question'))

@app.route('/check_answer', methods=['POST'])
def check_answer():
    """Handle answer submission"""
    if 'questions' not in session:
        return redirect(url_for('home'))
    
    current_index = session['current_question']
    if current_index >= NUM_OF_QUESTION_PER_SET:
        return redirect(url_for('show_score'))
    
    # Get the user's answer
    user_answer = int(request.form.get('answer', 0))
    
    # Get the correct answer
    question_num = session['questions'][current_index]
    questions_data = read_questions()
    correct_answer = questions_data[str(question_num)]['A']
    
    # Store the answer
    if 'answers' not in session:
        session['answers'] = []
    while len(session['answers']) <= current_index:
        session['answers'].append({})
    session['answers'][current_index] = {
        'question': question_num,
        'user_answer': user_answer,
        'correct_answer': correct_answer,
        'is_correct': user_answer == correct_answer
    }
    
    # Store user's answer
    if 'user_answers' not in session:
        session['user_answers'] = []
    while len(session['user_answers']) <= current_index:
        session['user_answers'].append(None)
    session['user_answers'][current_index] = user_answer
    
    # Update score if answer is correct
    if user_answer == correct_answer:
        if 'score' not in session:
            session['score'] = 0
        if current_index not in session.get('scored_questions', []):
            session['score'] = session.get('score', 0) + 1
            if 'scored_questions' not in session:
                session['scored_questions'] = []
            session['scored_questions'].append(current_index)
    
    # Move to next question
    session['current_question'] = current_index + 1
    
    # If this was the last question, show the score
    if current_index + 1 >= NUM_OF_QUESTION_PER_SET:
        return redirect(url_for('show_score'))
    
    return redirect(url_for('show_question'))

@app.route('/show_score')
def show_score():
    """Show the final score and review all answers"""
    if 'questions' not in session:
        return redirect(url_for('home'))
    
    # Calculate final score
    final_score = session.get('score', 0)
    total_questions = NUM_OF_QUESTION_PER_SET
    
    # Get all questions and answers for review
    questions_data = read_questions()
    review_data = []
    
    for i, question_num in enumerate(session['questions']):
        question_data = questions_data[str(question_num)]
        answer_data = session['answers'][i] if i < len(session.get('answers', [])) else None
        
        review_data.append({
            'question_num': i + 1,
            'question': question_data['Q'],
            'image': question_data['P'],
            'options': question_data['O'],
            'correct_answer': question_data['A'],
            'user_answer': answer_data['user_answer'] if answer_data else None,
            'is_correct': answer_data['is_correct'] if answer_data else False
        })
    
    return render_template('score.html',
                         score=final_score,
                         total_questions=total_questions,
                         review_data=review_data)

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    app.run(debug=True) 