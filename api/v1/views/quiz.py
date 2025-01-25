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
    title = request.json.get('title')
    description = request.json.get('description')
    difficulty = request.json.get('difficulty')
    duration = request.json.get('duration')
    category = request.json.get('category')
    questions = request.json.get('questions')
    for dataname, datavalue in {
                                    "title": title,
                                    "description": description,
                                    "difficulty": difficulty,
                                    "category": category,
                                    "questions": questions
    }.items():
        if not datavalue:
            abort(400, f"Missing {dataname}")
    for data in [title, description, difficulty, category, questions]:
        if type(data) is not str and data != questions:
            abort(400, f"<{data}> field is required to be a string.")
        elif data == questions and type(data) is not list:
            abort(400, f"<questions> field is required to be a list.")
    if not questions:
        abort(400, "At least one question is required")
    temp_questions = question[:]
    for question in temp_questions:
        if type(question) is not dict:
            questions.remove(question)
    if not questions:
        abort(400, "Provide at least one question in a valid format")
    temp_questions = questions[:]
    for question in temp_questions:
        if "body" not in question or "answers" not in question:
            questions.remove(question)
    if not questions:
        abort(400, "Provide at least on question with complete data")
    temp_questions = questions[:]
    for question in temp_questions:
        if type(question.get("body")) is not str or len(question["body"]) <= 0:
            questions.remove(question)
    if not questions:
        abort(400, "Proivde at least one question with a valid body")
    temp_questions = questions[:]
    temp_questions = questions[:]
    for question in temp_questions:
        if type(question.get("answers")) is not list or len(question["answers"]) < 2:
            questions.remove(question)
        else:
            temp_answers = question["answers"][:]
            for answer in temp_answers:
                if type(answer) is not dict:
                    question['answers'].remove(answer)
                elif type(answer.get("body")) is not str or len(answer["body"]) == 0 or len(answer["body"]) > 100:
                    question['answers'].remove(answer)
                elif type(answer.get('status')) is not bool:
                    question['answers'].remove(answer)
            if len(question['answers']) < 2:
                questions.remove(question)
            elif len(list(filter(lambda answer: answer.status, question['answers']))) != 1:
                questions.remove(question)
    if not questions:
        abort(400, "Provide at least one question with a valid answers collection")
    quiz = Quiz(
                title=title,
                description=description,
                duration=duration,
                difficulty=difficult,
                category=category
    )
    for question in questions:
        q = Question(body=question['body'], quiz_id=quiz.id)
        for answer in question['answers']:
            a = Answer(body=answer['body'], status=answer['status'], question_id=q.id)
            q.answers.add(a)
    quiz.save()
    return make_response(jsonify(quiz_dict), 201)

@app_views.route("/quizzes", methods=['GET'], strict_slashes=False)
def get_quizzes():
    """GET /api/v1/quizzes => Returns the quizzes
    """
    categories = request.args.get("categories")
    attribute = request.args.get("attribute")
    _type = request.args.get("type")
    after = request.args.get("after")
    if not after:
        after = "initial"
    if not attribute or attribute not in ["added_at", "times_taken"]:
        order_attribute = "added_at"
    if not _type or _type not in ['asc', 'desc']:
        order_type = 'desc'
    if categories:
        result = storage.get_categorized_quizzes(
                                                    categories.split(','),
                                                    attribute,
                                                    _type,
                                                    after
        )
        return jsonify([r.to_dict() for r in result])
    result = storage.get_paged(Quiz, attribute, _type, after)
    return make_response(jsonify([r.to_dict() for r in result]), 200)

@app_views.route("/quizzes/<quiz_id>", methods=['GET'], strict_slashes=False)
def get_quiz(quiz_id):
    """GET /api/v1/quizzes/<quiz_id> => get the quiz with id "quiz_id"
    """
    quiz = storage.get(Quiz, quiz_id)
    if not quiz:
        abort(404)
    return jsonify(quiz.to_dict())


@app_views.route("/quizzes/<user_id>/liked", methods=['GET'], strict_slashes=False)
def get_users_liked_quizzes(user_id):
    """Get the user with id = user_id liked quizzes
    """
    if "user_id" == "me":
        if not request.current_user:
            abort(401)
        user_id = request.current_user.id
    user = storage.get(User, user_id)
    if not user:
        abort(404)
    return jsonify([quiz.to_dict() for quiz in user.liked_quizzes])

@app_views.route("/quizzes/<user_id>/taken", methods=['GET'], strict_slashes=False)
def get_users_taken_quizzes(user_id):
    """Get the user with id = id taken quizzes
    """
    if "user_id" == "me":
        if not request.current_user:
            abort(401)
        user_id = request.current_user.id
    user = storage.get(User, user_id)
    if not user:
        abort(404)
    taken_ids = [socre.quiz_id for score in user.scores]
    quizzes = [storage.get(Quiz, quiz_id) for quiz_id in taken_ids]
    return jsonify([quiz.to_dict() if quiz else "Deleted" for quiz in quizzes])
    

@app_views.route("/quizzes/<user_id>/uploaded", methods=['GET'], strict_slashes=False)
def get_users_uploaded_quizzes(user_id):
    """Get the user with id = id uploaded quizzes
    """
    if "user_id" == "me":
        if not request.current_user:
            abort(401)
        user_id = request.current_user.id
    user = storage.get(User, user_id)
    if not user:
        abort(404)
    return jsonify([quiz.to_dict() for quiz in user.quizzes])


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
        abort(403)
    allowed = ['title', 'description', 'category']
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
