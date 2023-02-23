from json import dumps, loads
from pathlib import Path
from random import choice, sample

from flask import Flask, render_template, request

CURSES = list(range(10, 370, 10))
APPROACH = ["Gegenanflug", "Queranflug"]
STANDARD = [True, False]

QUESTIONS_PATH = Path(Path(__file__).parent.absolute() / "questions.json")
QUESTIONS = loads(QUESTIONS_PATH.read_bytes())
app = Flask(__name__)


def calculate_current_curse(approach, curse):
    if "Gegenanflug" in approach:
        return curse + 180 if curse < 181 else curse - 180
    elif "Rechter" in approach:
        return curse - 90 if curse > 90 else curse + 270
    else:
        return curse + 90 if curse < 271 else curse - 270


def check_for_three_values(current_curse):
    return f"0{current_curse}" if current_curse < 100 else str(current_curse)


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


@app.route("/curses", methods=["GET", "POST"])
def ask_for_curse():
    curse, approach, standard = choice(CURSES), choice(APPROACH), choice(STANDARD)
    if not standard:
        approach = f"Rechter {approach}"
    return render_template("curses.html", approach=approach, curse=curse)


@app.route("/check_curse", methods=["GET", "POST"])
def check_curse():
    approach = request.form["approach"]
    curse = int(request.form["curse"])
    user_answer = request.form["answer"]
    correct_answer = check_for_three_values(calculate_current_curse(approach, curse))
    if user_answer == correct_answer:
        return render_template(
            "curses.html",
            approach=approach,
            curse=curse,
            user_answer=f"Richtig! {user_answer}",
        )
    else:
        return render_template(
            "curses.html", approach=approach, curse=curse, user_answer="Falsch!"
        )


@app.route("/")
def index():
    return render_template("index.html", questions=number_of_questions())
