# Alberta Driver's Knowledge Quiz

A web-based quiz application for practicing Alberta's driver's knowledge test. This application helps users prepare for their driver's license exam by providing a modern, user-friendly interface to practice test questions.

## Features

### Web Version (Current)
- Modern web interface built with Flask and Bootstrap
- 30 questions per quiz session, randomly selected from a pool of questions
- Progress tracking with visual progress bar
- Real-time timer tracking quiz duration
- Support for questions with images
- Mobile-responsive design
- Flexible navigation between questions (Previous/Next)
- Dynamic scoring system that updates when answers are changed
- Comprehensive final review showing:
  - Final score with percentage
  - Total time taken to complete the quiz
  - Detailed review of all questions with correct/incorrect answers highlighted
- Session-based state management with CSRF protection

### Legacy Version (Tkinter)
- Desktop application with Tkinter GUI
- Simple and straightforward interface
- 30 questions per quiz session (configurable)
- Basic score tracking
- Support for questions with images

## Requirements

### Web Version
- Python 3.8 or higher
- Flask 3.0.0
- Flask-WTF 1.2.1
- Other dependencies listed in `requirements.txt`

### Legacy Version
- Python 3.9 or higher
- Pillow (PIL) for image handling
- Tkinter (usually comes with Python)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/DriverKnowledgeTest.git
cd DriverKnowledgeTest
```

2. Create and activate a virtual environment (recommended):
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Unix or MacOS:
source venv/bin/activate
```

3. Install dependencies:
```bash
# For web version:
pip install -r requirements.txt

# For legacy version:
pip install pillow
```

## Usage

### Web Version
1. Start the application:
```bash
python dotest-new.py
```

2. Open your web browser and navigate to:
```
http://localhost:5000
```

3. Click "Start Quiz" to begin a new quiz session
4. Answer each question by selecting one of the options
5. Use the Previous/Next buttons to navigate between questions
6. After completing all questions, review your answers and score

### Legacy Version
1. Run the application:
```bash
python doTest.py
```

2. Click "Start" to begin a new quiz session
3. Answer each question by selecting one of the options
4. Use the "Next" button to proceed
5. View your final score at the end

Note: You can adjust the number of questions by changing `NUM_OF_QUESTION_PER_SET` in the application files (default: 30, maximum: 108)

## Project Structure

- `dotest-new.py` - Main Flask application (web version)
- `doTest.py` - Legacy Tkinter application
- `templates/` - HTML templates (web version)
  - `base.html` - Base template with common elements
  - `question.html` - Quiz question template
  - `score.html` - Final score and review template
- `static/` - Static files (web version)
  - `pictures/` - Question images
- `questions.json` - Question database
- `requirements.txt` - Python dependencies for web version

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
