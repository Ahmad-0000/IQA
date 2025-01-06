"""Question view
"""
from sqlalchemy.exc import DataError, IntegrityError
from flask import make_response, jsonify, abort, request
from api.v1.views import app_views
from models import storage
from models.quizzes import Quiz
from models.questions import Question
from models.answers import Answer


@app_views.route("/quizzes/<quiz_id>/questions", methods=['POST'], strict_slashes=False)
def create_question(quiz_id):
    """Create a quiz question
    """
    if not request.is_json:
        abort(400, "Not JSON")
    quiz = storage.get(Quiz, quiz_id)
    if not quiz:
        abort(404)
    if quiz.user_id != request.current_user.id:
        abort(403)
    body = request.json.get("body")
    answers_collection = request.json.get("answers_collection")
    if not body or body == '':
        abort(400, "Missing body")
    if not answers_collection:
        abort(400, "Missing answers collection")
    if type(answers_collection) is not list:
        abort(400, "Abide to data constraints")
    for answer in answers_collection:
        if type(answer) is not dict:
            abort(400, "Abide to data constraints")
    def _pre_filter(answer):
        """Filter correct answers
        """
        if "is_true" not in answer and "body" not in answer:
            return False
        is_true = answer["is_true"]
        body = answer["body"]
        if type(is_true) is not bool and type(body) is not str and len(body) == 0:
            return False
        return True
    pre_valid_collection = list(filter(_pre_filter, answers_collection))
    if not pre_valid_collection or len(pre_valid_collection) < 2:
        abort(400, "Abide to data constraints")
    first_status = pre_valid_collection[0]['is_true']
    valid_answers_collection = list(filter(lambda first_status: answer['is_true'] != first_status, pre_valid_collection))
    if not valid_answers_collection:
        abort(400, "Abide to data constraints")
    question = Question(body=body, quiz_id=quiz.id)
    try:
        question.save()
    except (DataError, IntegrityError):
        abort(400, "Abide to data constraints")
    saved_answers = []
    for answer in valid_answers_collection:
        try:
            answer = Answer(body=answer['body'], question_id=question.id, is_true=answer['is_true'])
            answer.save()
            saved_answers.append(answer)
        except (DataError, IntegrityError):
            pass
    if len(saved_answers) < 2:
        abort(400, "Abide to data constraints")
    first_status = saved_answers[0].is_true
    valid_question = list(filter(lambda answer: answer.is_true != first_status, saved_answers))
    if not valid_question:
        question.delete()
        abort(400, "Abide to data constraints")
    res = {
        "question": question.to_dict(),
        "answers": [answer.to_dict() for answer in saved_answers]
    }
    return make_response(jsonify(res), 201)


@app_views.route("/questions/<question_id>", methods=["PUT"], strict_slashes=False)
def update_question(question_id):
    """Update a question
    """
    if not request.is_json:
        abort(400, "Not JSON")
    question = storage.get(Question, question_id)
    if not question:
        abort(404)
    quiz = storage.get(Quiz, question.quiz_id)
    if quiz.user_id != request.current_user.id:
        abort(401)
    body = request.json.get("body")
    if not body:
        abort(400, "Missing body")
    if type(body) is not str or len(body) == 0:
        abort(400, "Abide to data constraints")
    try:
        question.update(body=body)
    except DataError:
        abort(400, "Abide to data constraints")
    return jsonify(question.to_dict())

@app_views.route("/questions/<question_id>", methods=['DELETE'], strict_slashes=False)
def delete_question(question_id):
    """Delete a question
    """
    question = storage.get(Question, question_id)
    if not question:
        abort(404)
    quiz = storage.get(Quiz, question.quiz_id)
    if quiz.user_id != request.current_user.id:
        abort(401)
    if len(quiz.questions) == 1:
        quiz.delete()
    else:
        question.delete()
    return make_response(jsonify({}), 204)
