"""Answer view
"""
from sqlalchemy.exc import DataError, IntegrityError
from flask import make_response, jsonify, abort, request
from api.v1.views import app_views
from models import storage
from models.quizzes import Quiz
from models.questions import Question
from models.answers import Answer


@app_views.route("/questions/<question_id>/answers", methods=['POST'], strict_slashes=False)
def add_answer(question_id):
    """Add a new answer
    """
    if not request.json:
        abort(400, "Not JSON")
    body = request.json.get("body")
    is_true = request.json.get("is_true")
    if not body:
        abort(400, "Missing body")
    if type(body) is not str:
        abort(400, "Abide to data constraints")
    if is_true is None:
        abort(400, "Missing answer status")
    if type(is_true) is not bool:
        abort(400, "Abide to data constraints")
    question = storage.get(Question, question_id)
    if not question:
        print("Here")
        abort(404)
    quiz = storage.get(Quiz, question.quiz_id)
    if quiz.user_id != request.current_user.id:
        abort(401)
    answer = Answer(body=body, is_true=is_true, question_id=question_id)
    try:
        answer.save()
    except (DataError, IntegrityError):
        abort(400, "Abide to data constraints")
    return make_response(jsonify(answer.to_dict()), 201)

@app_views.route("/answers/<answer_id>", methods=['PUT'], strict_slashes=False)
def update_answer(answer_id):
    """Update an answer
    """
    if not request.is_json:
        abort(400, "Not JSON")
    allowed = ["body", "is_true"]
    values_to_update = {}
    body = request.json.get("body")
    is_true = request.json.get("is_true")
    if not body and not is_true:
        abort(400, "Provide attributes to update")
    if body and type(body) is str:
        values_to_update["body"] = body
    if is_true and type(is_true) is str:
        values_to_update["is_true"] = is_true
    if not values_to_update:
        abort(400, "Abide to data constraints")
    answer = storage.get(Answer, answer_id)
    if not answer:
        abort(404)
    question = storage.get(Question, answer.question_id)
    quiz_id = question.quiz_id
    user_id = storage.get(Quiz, quiz_id).user_id
    if user_id != request.current_user.id:
        abort(401)
    new_is_true = values_to_update.get("is_true")
    if new_is_true == False and answer.is_true:
        only_true = list(filter(lambda answer: answer.is_true, question.answers)).__len__() == 1
        if only_true:
            alternate_id = request.json.get("alternate_id")
            if not alternate_id:
                abort(400, "Abide to data constraints")
            else:
                alternate_answer = storage.get(Answer, alternate_id)
                if not alternate_answer:
                    abort(404)
                if alternate_answer.question_id != answer.question_id:
                    abort(409)
                try:
                    answer.update(**values_to_update)
                except DataError:
                    abort(400, "Abide to data constraints")
                alternate_answer.update(is_true=True)
    else:
        try:
            answer.update(**values_to_update)
        except DataError:
            abort(400, "Abide to data constraints")
    return jsonify(answer.to_dict())

@app_views.route("/answers/<answer_id>", methods=['DELETE'], strict_slashes=False)
def delete_answer(answer_id):
    """Delete an answer
    """
    answer = storage.get(Answer, answer_id)
    if not answer:
        abort(404)
    if answer.is_true:
        abort(400, "Can't delete the true answer")
    question = storage.get(Question, answer.question_id)
    if len(question.answers) == 2:
        abort(400, "Can't keep a question with one answer")
    quiz_id = question.quiz_id
    user_id = storage.get(Quiz, quiz_id).user_id
    if user_id != request.current_user.user_id:
        abort(401)
    answer.delete()
    return make_response(jsonify({}), 204)
