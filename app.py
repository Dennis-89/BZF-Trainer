from json import dumps, loads
from pathlib import Path
from random import choice, sample

from flask import Flask, render_template, request

FLIGHT_DIRECTION = list(range(10, 370, 10))
FLIGHT_POSITION = ["Gegenanflug", "Queranflug"]
STANDARD = [True, False]

QUESTIONS_PATH = Path(Path(__file__).parent.absolute() / "questions.json")
QUESTIONS = loads(QUESTIONS_PATH.read_bytes())
app = Flask(__name__)


def calculate_current_heading(flight_position, heading):
    if "Gegenanflug" in flight_position:
        return heading + 180 if heading < 181 else heading - 180
    elif "Rechter" in flight_position:
        return heading - 90 if heading > 90 else heading + 270
    else:
        return heading + 90 if heading < 271 else heading - 270


def check_for_three_values(current_heading):
    return f"0{current_heading}" if current_heading < 100 else str(current_heading)


def number_of_questions():
    return [number for number, _ in enumerate(QUESTIONS)]


def get_question(question_id):
    return QUESTIONS[question_id]["question"]


def get_answers_in_random_order(question_id):
    return sample(QUESTIONS[question_id]["answers"], 4)


def get_right_answer(question_id, answer):
    return answer == QUESTIONS[question_id]["answers"][0]


@app.route("/question", methods=["GET", "POST"])
def chose_question():
    question_id = int(request.form["answer"]) - 1
    answers = get_answers_in_random_order(question_id)
    return render_template(
        "question.html",
        question=get_question(question_id),
        id=question_id,
        answers=answers,
        answers_json=dumps(answers),
    )


@app.route("/answer", methods=["GET", "POST"])
def check_answer():
    question_id = int(request.form["id"])
    answer = str(request.form["answer"])
    answers_json = request.form["answers_json"]
    answers = loads(answers_json)
    rating = (
        f"Richtig!\n{answer}" if get_right_answer(question_id, answer) else "Falsch!"
    )
    return render_template(
        "question.html",
        question=get_question(question_id),
        id=question_id,
        answers=answers,
        answers_json=answers_json,
        rating=rating,
    )


@app.route("/next", methods=["GET", "POST"])
def next_question():
    try:
        question_id = int(request.form["id"])
        question = get_question(question_id)
        answers = get_answers_in_random_order(question_id)
        return render_template(
            "question.html",
            question=question,
            id=question_id,
            answers=answers,
            answers_json=dumps(answers),
        )
    except IndexError:
        return render_template("finish.html")


@app.route("/back", methods=["GET", "POST"])
def previous_question():
    question_id = int(request.form["id"])
    if question_id < 0:
        return index()
    question = get_question(question_id)
    answers = get_answers_in_random_order(question_id)
    return render_template(
        "question.html",
        question=question,
        id=question_id,
        answers=answers,
        answers_json=dumps(answers),
    )


@app.route("/ask_for_heading", methods=["GET", "POST"])
def ask_for_heading():
    heading, flight_position, standard = (
        choice(FLIGHT_DIRECTION),
        choice(FLIGHT_POSITION),
        choice(STANDARD),
    )
    if not standard:
        flight_position = f"Rechter {flight_position}"
    return render_template(
        "heading.html", flight_position=flight_position, heading=heading
    )


@app.route("/check_heading", methods=["GET", "POST"])
def check_heading():
    flight_position = request.form["flight_position"]
    heading = int(request.form["heading"])
    user_answer = request.form["answer"]
    correct_answer = check_for_three_values(
        calculate_current_heading(flight_position, heading)
    )
    if user_answer == correct_answer:
        return render_template(
            "heading.html",
            flight_position=flight_position,
            heading=heading,
            user_answer=f"D-EXYZ verstanden, Anflug fortsetzen!",
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
    return render_template("index.html", questions=number_of_questions())

