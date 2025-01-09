"""Quiz view
"""
from sqlalchemy.exc import DataError, IntegrityError
from flask import make_response, jsonify, abort, request
from api.v1.views import app_views
from models import storage
from models.users import User
from models.quizzes import Quiz
from models.questions import Question
from models.answers import Answer


@app_views.route("/quizzes", methods=['POST'], strict_slashes=False)
def create_quiz():
    """POST /api/v1/quizzes => Creates a quiz
    """
    if not request.is_json:
        abort(400, "Not JSON")
    user = request.current_user
    required_data = ["title", "description", "difficulty", "questions_collection"]
    for data in required_data:
        if data not in request.json:
            abort(400, f"Missing {data}")
    questions = request.json['questions_collection']
    if type(questions) is not list:
        abort(400, "Abide to data constraints")
    if not questions:
        abort(400, "At least one question is required")
    for question in questions:
        try:
            if "body" in question and "answers_collection" in question\
                and type(question['body']) is str and len(question['body']) > 0\
                and type(question['answers_collection']) is list and len(question['answers_collection']) > 1:
                break
        except TypeError:
            abort(400, "Abide to data constraints")
    else:
        abort(400, "Abide to data constraints")
    quiz = Quiz(user_id=user.id, **(request.json))
    try:
        quiz.save()
    except (DataError, IntegrityError):
        abort(400, "Abide to data constraints")
    added_questions = []
    for question in questions:
        try:
            new_question = Question(**question, quiz_id=quiz.id)
            new_question.save()
            saved_answers = []
            for answer in question['answers_collection']:
                if "body" not in answer or "is_true" not in answer:
                    pass
                else:
                    answer_object = Answer(**answer, question_id=new_question.id)
                    answer_object.save()
                    saved_answers.append(answer_object)
            if len(saved_answers) > 1:
                first_answer_state = saved_answers[0].is_true
                different_answers = list(filter(lambda x: x.is_true != first_answer_state, saved_answers))
                if different_answers:
                    new_question.answers.extend(saved_answers)
                    new_question.save()
                    added_questions.append(new_question)
                else:
                    new_question.delete()
        except (DataError, IntegrityError):
            storage.close()
            pass
    if not added_questions:
        quiz.delete()
        abort(400, "Abide to data constraints")
    quiz.questions.extend(added_questions)
    quiz.save()
    quiz_dict = quiz.to_dict()
    quiz_dict['questions'] = quiz_dict['questions_collection']
    quiz_dict.pop("questions_collection")
    return make_response(jsonify(quiz_dict), 201)

@app_views.route("/quizzes", methods=['GET'], strict_slashes=False)
def get_quizzes():
    """GET /api/v1/quizzes => Returns the quizzes
    """
    cats = request.args.get("cats")
    order_attribute = request.args.get("order_attribute")
    order_type = request.args.get("order_type")
    after = request.args.get("after")
    if cats:
        result = storage.get_quizzes_with_cats(cats.split(','), after, {"order_attribute": order_attribute, "order_type": order_type})
        if result is None:
            abort(400, "Abide to data constraints")
        return jsonify([r.to_dict() for r in result])
    if not order_attribute:
        return make_response(jsonify([quiz.to_dict() for quiz in storage.get_all(Quiz)]), 200)
    result = storage.get_paged(Quiz, order_attribute, order_type, after)
    if result is None:
        abort(400, "Abide to data constraints")
    if type(result) is Quiz:
        result = [result]
    return make_response(jsonify([r.to_dict() for r in result]), 200)

@app_views.route("/quizzes/<quiz_id>", methods=['GET'], strict_slashes=False)
def get_quiz(quiz_id):
    """GET /api/v1/quizzes/<quiz_id> => get the quiz with id "quiz_id"
    """
    quiz = storage.get(Quiz, quiz_id)
    if not quiz:
        abort(404)
    return make_response(jsonify(quiz.to_dict()), 200)

@app_views.route("/quizzes/<quiz_id>", methods=['PUT'], strict_slashes=False)
def update_a_quiz(quiz_id):
    """PUT /quizzes/<quiz_id> => Updates the quiz with id
                                                 "quiz_id" of user with id
                                                 "user_id"
    """
    if not request.is_json:
        abort(400, "Not JSON")
    user = request.current_user
    quiz = storage.get(Quiz, quiz_id)
    if not quiz:
        abort(404)
    if quiz.user_id != user.id:
        abort(401)
    allowed = ['title', 'description', 'duration', 'category_id', 'image_path', 'difficulty']
    updated = 0
    filtered_attributes = {}
    for k, v in request.json.items():
        if k in allowed:
            filtered_attributes[k] = v
    if not filtered_attributes:
        abort(400, "Provide at least one attribute to update")
    try:
        quiz.update(**filtered_attributes)
    except (DataError, IntegrityError):
        abort(400, "Abide to data constraints")
    return make_response(jsonify(quiz.to_dict()), 200)

@app_views.route("/quizzes/<quiz_id>", methods=['DELETE'], strict_slashes=False)
def delete_quiz(quiz_id):
    """DELETE /quizzes/<quiz_id> => deletes a quiz
    """
    quiz = storage.get(Quiz, quiz_id)
    if not quiz:
        abort(404)
    if quiz.user_id != request.current_user.id:
        abort(403)
    quiz.delete()
    return make_response(jsonify({}), 204)
