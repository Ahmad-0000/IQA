"""Quiz view
"""
import json
from os import getenv
from uuid import uuid4
from cache import cache_client
from datetime import datetime
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
            abort(400, "<questions> field is required to be a list.")
    if duration and type(duration) != int:
        abort(400, "<duration> field is required to be an integer.")
    elif duration <= 0 or duration > 30:
        abort(400, "<duration> is required to be > 0 and <= 30")
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
        if type(question.get("body")) is not str or len(question["body"]) == 0:
            questions.remove(question)
    if not questions:
        abort(400, "Proivde at least one question with a valid body")
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
    quiz.save() # the cascade occurs
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
    if not attribute or attribute not in ["added_at", "repeats"]:
        attribute = "added_at"
    if not _type or _type not in ['asc', 'desc']:
        order_type = 'desc'
    if categories:
        result = storage.get_categorized_quizzes(
                                                    categories.split(','),
                                                    attribute,
                                                    _type,
                                                    after
        )
        return jsonify([quiz.to_dict() for quiz in result])
    if not cache_client.get_pool_size('newest'):
        cache_client.populate_quizzes_pool('newest')
        cache_client.populate_quizzes_pool('oldest')
        cache_client.populate_popular_pool()
    if attribute == 'added_at':
        if _type == 'desc':
            result = cache_client.get_paged_newest(after, 20)
        else:
            result = cache_client.get_paged_oldest(after, 20)
    else:
        result = cache_client.get_paged_popular(after, 20)
    docs = []
    for doc in result.docs:
        docs.append(json.loads(doc.json)['general_details'])
    if docs and len(docs) != 20:
        last_doc = docs[-1]
        if attribute == 'added_at':
            after = datetime.fromtimestamp(last_doc['added_at'])
        else:
            after = last_doc['repeats']
        rest_docs = storage.get_paged(Quiz, attribute, _type, after=after, limit=20 - len(docs))
        docs.extend(rest_docs)
    for doc in docs:
        if type(doc) is dict:
            doc['added_at'] = datetime.fromtimestamp(doc['added_at']).isoformat()
    return make_response(jsonify([quiz.to_dict() if type(quiz) is Quiz else quiz for quiz in docs]), 200)

@app_views.route("/quizzes/<quiz_id>", methods=['GET'], strict_slashes=False)
def get_quiz(quiz_id):
    """GET /api/v1/quizzes/<quiz_id> => get the quiz with id "quiz_id"
    """
    quiz = storage.get(Quiz, quiz_id)
    if not quiz:
        abort(404)
    return jsonify(quiz.to_dict())


@app_views.route("/favorite_quizzes", methods=['GET'], strict_slashes=False)
def get_users_liked_quizzes():
    """Get the user with id = user_id liked quizzes
    """
    user_id = request.args.get("user_id")
    if not user_id:
        abort(400, "Provide a user id as a query parameter")
    user = storage.get(User, user_id)
    if not user:
        abort(404)
    response = [quiz.to_dict() for quiz in user.liked_quizzes]
    return jsonify(response)

@app_views.route("/taken_quizzes", methods=['GET'], strict_slashes=False)
def get_users_taken_quizzes():
    """Get the user with id = id taken quizzes
    """
    user_id = request.args.get("user_id")
    if not user_id:
        abort(400, "Provide a user id as a query parameter")
    user = storage.get(User, user_id)
    if not user:
        abort(404)
    quizzes = {score.quiz for score in user.scores}
    response = [quiz.to_dict() for quiz in quizzes]
    return jsonify(response)


@app_views.route("/uploaded_quizzes", methods=['GET'], strict_slashes=False)
def get_users_uploaded_quizzes():
    """Get the user with id = id uploaded quizzes
    """
    user_id = request.args.get('user_id')
    if not user_id:
        abort(400, "Provide a user id as a query parameter")
    user = storage.get(User, user_id)
    if not user:
        abort(404)
    response = [quiz.to_dict() for quiz in user.quizzes]
    return jsonify(response)


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
    allowed = ['title', 'description']
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

@app_views.route("/quizzes/start/<quiz_id>", methods=['POST'], strict_slashes=False)
def start_a_quiz(quiz_id):
    """Start a quiz session
    """
    session_id = str(uuid4())
    result = cache_client.start_a_quiz(quiz_id, request.current_user.id, session_id)
    if result == 404:
        abort(404)
    res = jsonify({"status": "ok"})
    cookie_name = getenv('IQA_QUIZ_SESSION_COOKIE')
    res.set_cookie(cookie_name, result[0], expires=datetime.fromtimestamp(result[1]))
    return res

@app_views.route("/quizzes/next/<idx>", methods=['GET'], strict_slashes=False)
def get_next_question(idx):
    """Get the next question from the quiz session based on idx
    """
    cookie_name = getenv('IQA_QUIZ_SESSION_COOKIE')
    session_cookie = request.cookies.get(cookie_name)
    if type(idx) is not int:
        try:
            idx = int(idx)
        except (ValueError, TypeError):
            abort(400, "<index> is needed to be a number")
    result = cache_client.get_next_question(session_cookie, idx)
    if type(result) is tuple and result[0] == 404:
        abort(404)
    elif type(result) is tuple and result[0] == 201:
        return make_response(jsonify(result[1]), 201)
    return jsonify(result)

@app_views.route("/quizzes/answer/<question_id>", methods=['POST'], strict_slashes=False)
def answer_a_question(question_id):
    """Answer a question in a quiz session
    """
    if not request.is_json:
        abort(400, "Not JSON")
    cookie_name = getenv('IQA_QUIZ_SESSION_COOKIE')
    session_id = request.cookies.get(cookie_name)
    if not session_id:
        abort(404)
    answer_id = request.json.get('answer_id')
    if not answer_id:
        abort(404)
    result = cache_client.register_snapshots(session_id, question_id, answer_id) # cache_client.answer
    if type(result) is int:
        abort(result)
    if type(result) is tuple:
        abort(result[0], result[1])
    return make_response(jsonify({"status": "ok"}), 201)
