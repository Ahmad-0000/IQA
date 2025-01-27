"""Quiz view to handle quizzes endpoints
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
    """POST /api/v1/quizzes

    AUTHENTICATION:
        Required

    DESCRIPTION:
        Create a new quiz.

    INPUT FORMAT:
        * A json body with the following fields is needed:
            {
                "title": <string, 100 chars maximumly>,
                "description": <string, 512 chars>,
                "duration": <intiger, 5 <= duration >= 30, in minutes>,
                "difficulty": <enum: Easy, Medium, or Difficult>,
                "category": <string, 20 chars maximumly>,
                "questions": [
                    {
                        "body": <string, no limit>
                        "answers": [
                            {"body": <string, 100 chars maximumly>, "status": bool},
                            {"body": <string, 100 chars maximumly>, "status": bool},
                            ...
                        ]
                    },
                    ...
                ]
            }
    NOTES:
        At least one question is required, and for each question, at least 2 answers
        are required, only one of them is true.

    RESPONSE:
        A JSON string representing basic quiz info (No questions and answers info).
    
    SUCCESS STATUS CODE: 201
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
    try:
        duration = int(duration)
    except (TypeError, ValueError):
        abort(400, "<duration> field is required to be an integer.") 
    if duration <= 0 or duration > 30:
        abort(400, "<duration> is required to be > 0 and <= 30")
    if not questions:
        abort(400, "At least one question is required")
    temp_questions = questions[:]
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
            elif len(list(filter(lambda answer: answer.get('status'), question['answers']))) != 1:
                questions.remove(question)
    if not questions:
        abort(400, "Provide at least one question with a valid answers collection")
    quiz = Quiz(
                title=title,
                description=description,
                duration=duration,
                difficulty=difficulty,
                category=category,
                user_id=request.current_user.id
    )
    quiz.save()
    for question in questions:
        q = Question(body=question['body'], quiz_id=quiz.id)
        q.save()
        for answer in question['answers']:
            a = Answer(body=answer['body'], status=answer['status'], question_id=q.id)
            a.save()
    return make_response(jsonify(quiz.to_dict()), 201)

@app_views.route("/quizzes", methods=['GET'], strict_slashes=False)
def get_quizzes():
    """GET /api/v1/quizzes

    AUTHENTICATION:
        Not required

    DESCRIPTION:
        Get quizzes with filters and paginations
    
    URL paramters:
        type: "asc" or "desc"
        attribute: "added_at" or "repeats"
        after: "added_at" value or "repeats" value or "initial"
        categoires: category1,category2,...

    INPUT FORMAT:
        Not needed

    RESPONSE:
        A JSON structure representing basic quizzes info (No questions and answers info).
    
    SUCCESS STATUS CODE: 200
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
    if attribute == "added_at":
        try:
            datetime.fromisoformat(after)
        except:
            abort(400, "<after> is needed to be in a valid iso format")
    else:
        try:
            after = int(after)
        except:
            abort(400, "<after> is needed to be a number")
    if categories:
        result = storage.get_categorized_quizzes(
                                                    categories.split(','),
                                                    attribute,
                                                    _type,
                                                    (datetime.fromisoformat(after) if attribute == "added_at" else after)
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
    """GET /api/v1/quizzes/<quiz_id>

    AUTHENTICATION:
        Not required

    DESCRIPTION:
        Get a quiz info

    RESPONSE:
        A JSON structure representing basic quiz info (No questions and answers info).
    
    SUCCESS STATUS CODE: 200

    """
    quiz = storage.get(Quiz, quiz_id)
    if not quiz:
        aboruser_id=<user_id>]
    (404)
    return jsonify(quiz.to_dict())


@app_views.route("/favorite_quizzes", methods=['GET'], strict_slashes=False)
def get_users_liked_quizzes():
    """GET /api/v1/favorite_quizzes?user_id=<user_id>

    AUTHENTICATION:
        Not required

    DESCRIPTION:
        GET a specific user's favorite quizzes info
    
    URL paramters:
        user_id: a user's id

    INPUT FORMAT:
        Not needed

    RESPONSE:
        A JSON structure representing basic quizzes info (No questions and answers info).
    
    SUCCESS STATUS CODE: 200
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
    """GET /api/v1/taken_quizzes?user_id=<user_id>

    AUTHENTICATION:
        Not required

    DESCRIPTION:
        GET a specific user's taken quizzes info
    
    URL paramters:
        user_id: a user's id

    INPUT FORMAT:
        Not needed

    RESPONSE:
        A JSON structure representing basic quizzes info (No questions and answers info).
    
    SUCCESS STATUS CODE: 200
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
    """GET /api/v1/uploaded_quizzes?user_id=<user_id>

    AUTHENTICATION:
        Not required

    DESCRIPTION:
        GET a specific user's uploaded quizzes info
    
    URL paramters:
        user_id: a user's id

    INPUT FORMAT:
        Not needed

    RESPONSE:
        A JSON structure representing basic quizzes info (No questions and answers info).
    
    SUCCESS STATUS CODE: 200
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
    """PUT /api/v1/quizzes/<quiz_id>

    AUTHENTICATION:
        Required

    DESCRIPTION:
        Update a quiz
    
    URL paramters:
        user_id: a user's id

    INPUT FORMAT:
        At least one field is required:
        {
            'title': <same as in POST>,
            'description': <same in POST>
        }

    RESPONSE:
        A JSON structure representing basic quizzes info (No questions and answers info).
    
    SUCCESS STATUS CODE: 200
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
    """DELETE /api/v1/quizzes/<quiz_id>

    AUTHENTICATION 
        Required

    DESCRIPTION:
        Delete a quiz

    INPUT FORMAT:
        Not needed

    RESPONSE:
        Empty
    
    SUCCESS STATUS CODE: 204
    """
    quiz = storage.get(Quiz, quiz_id)
    if not quiz:
        abort(404)
    if quiz.user_id != request.current_user.id:
        abort(403)
    quiz.delete()
    return make_response(jsonify({}), 204)

@app_views.route("/start_quiz", methods=['POST'], strict_slashes=False)
def start_a_quiz():
    """POST /api/v1/start_quiz?quiz_id=<quiz_id>

    AUTHENTICATION 
        Required

    DESCRIPTION:
        Start a quiz session

    RESPONSE:
        A json represents the first question
    
    SUCCESS STATUS CODE: 200  
    """
    quiz_id = request.args.get("quiz_id")
    if not quiz_id:
        abort(404)
    session_id = str(uuid4())
    result = cache_client.start_a_quiz(quiz_id, request.current_user.id, session_id)
    if result == 404:
        abort(404)
    first_question = cache_client.get_next_question(f"{session_id}:{quiz_id}", 0)
    res = jsonify({"status": "ok", "first_question": first_question})
    cookie_name = getenv('IQA_QUIZ_SESSION_COOKIE')
    res.set_cookie(cookie_name, result[0], expires=datetime.fromtimestamp(result[1]))
    return res

@app_views.route("/quizzes/next/<idx>", methods=['GET'], strict_slashes=False)
def get_next_question(idx):
    """GET /api/v1/quizzes/next/<idx>

    AUTHENTICATION 
        Required

    DESCRIPTION:
        Gets the next's quizzes question

    INPUT FORMAT:
        Not needed

    RESPONSE:
        A json represents the next question
    
    SUCCESS STATUS CODE: 200

    NOTE: to finish, send -1 as <idx>
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
    """POST /api/quizzes/answer/<question_id>

    AUTHENTICATION 
        Required

    DESCRIPTION:
        Answer the question with id <question_id>

    INPUT FORMAT:
        Not needed

    RESPONSE:
        A json represents the status
    
    SUCCESS STATUS CODE: 200

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
