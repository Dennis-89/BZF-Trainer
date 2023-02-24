from json import dumps, loads
from pathlib import Path
from random import choice, shuffle

from flask import Flask, render_template, request

FLIGHT_DIRECTION = list(range(10, 370, 10))
HEADING_ANGLE = {
    "Gegenanflug": -180,
    "Rechter Gegenanflug": -180,
    "Queranflug": 90,
    "Rechter Queranflug": -90,
}

QUESTIONS_PATH = Path(Path(__file__).parent.absolute() / "questions.json")
QUESTIONS = loads(QUESTIONS_PATH.read_bytes())
app = Flask(__name__)


def calculate_current_heading(flight_position, heading):
    return (heading + HEADING_ANGLE[flight_position]) % 360


def format_heading(heading):
    return f"{heading:03d}"


def question_ids():
    return [number for number, _ in enumerate(QUESTIONS, 1)]


def get_question(question_id):
    return QUESTIONS[question_id - 1]["question"]


def get_answers_in_random_order(question_id):
    answers = list(QUESTIONS[question_id - 1]["answers"])
    shuffle(answers)
    return answers


def check_right_answer(question_id, answer):
    return answer == QUESTIONS[question_id - 1]["answers"][0]


def render_question(question_id, rating=None, answers=None):
    if answers is None:
        answers = get_answers_in_random_order(question_id)
    return render_template(
        "question.html",
        question=get_question(question_id),
        id=question_id,
        answers=answers,
        answers_json=dumps(answers),
        rating=rating,
    )


@app.route("/question", methods=["GET", "POST"])
def chose_question():
    question_id = int(request.form["id"])
    return render_question(question_id)


@app.route("/answer", methods=["GET", "POST"])
def check_answer():
    question_id = int(request.form["id"])
    answer = request.form["answer"]
    answers = loads(request.form["answers_json"])
    rating = (
        f"Richtig!\n{answer}" if check_right_answer(question_id, answer) else "Falsch!"
    )
    return render_question(question_id, rating, answers)


@app.route("/next", methods=["GET", "POST"])
def next_question():
    question_id = int(request.form["id"]) + 1
    try:
        _ = get_question(question_id)
    except IndexError:
        return render_template("finish.html")
    return render_question(question_id)


@app.route("/back", methods=["GET", "POST"])
def previous_question():
    question_id = int(request.form["id"]) - 1
    if question_id < 1:
        return index()
    return render_question(question_id)


@app.route("/ask_for_heading", methods=["GET", "POST"])
def ask_for_heading():
    return render_template(
        "heading.html",
        flight_position=choice(list(HEADING_ANGLE.keys())),
        heading=choice(FLIGHT_DIRECTION),
    )


@app.route("/check_heading", methods=["GET", "POST"])
def check_heading():
    flight_position = request.form["flight_position"]
    heading = int(request.form["heading"])
    user_answer = request.form["answer"]
    correct_answer = format_heading(calculate_current_heading(flight_position, heading))
    if user_answer == correct_answer:
        return render_template(
            "heading.html",
            flight_position=flight_position,
            heading=heading,
            user_answer="D-EXYZ verstanden, Anflug fortsetzen!",
        )
    else:
        return render_template(
            "heading.html",
            flight_position=flight_position,
            heading=heading,
            user_answer=f"D-EXYZ bestätigen Sie Steuerkurs {user_answer}!",
        )


@app.route("/")
def index():
    return render_template("index.html", questions=question_ids())

