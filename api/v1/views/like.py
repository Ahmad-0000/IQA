"""Hanlde likes endpoint
"""
from flask import jsonify, make_response, abort, request
from api.v1.views import app_views
from models import storage
from models.quizzes import Quiz

@app_views.route("/like", methods=['POST'], strict_slashes=False)
def make_like():
    """POST /api/v1/like?quiz_id=<quiz_id>

    AUTHENTICATION 
        Required

    DESCRIPTION:
        Like a quiz with id <quiz_id>

    INPUT FORMAT:
        Not needed

    RESPONSE:
        A json represents the liked quiz
    
    SUCCESS STATUS CODE: 201
    """
    quiz_id = request.args.get("quiz_id")
    if not quiz_id or type(quiz_id) is not str:
        abort(400, "Abide to data constraints")
    quiz = storage.get(Quiz, quiz_id)
    if not quiz:
        abort(404)
    if quiz.user_id == request.current_user.id:
        abort(400, "You can't make a like to your own quiz")
    if request.current_user in quiz.fans_users:
        abort(400, "You've already made a like for this quiz")
    taken = False
    for score in request.current_user.scores:
        if score.quiz == quiz:
            taken = True
            break
    if not taken:
        abort(400, "You didn't take this quiz")
    quiz.fans_users.append(request.current_user)
    quiz.likes_num += 1
    quiz.save()
    return make_response(jsonify(quiz.to_dict()), 201)

@app_views.route("/remove_like", methods=['DELETE'], strict_slashes=False)
def remove_like():
    """DELETE /api/v1/remove_like?quiz_id=<quiz_id>

    AUTHENTICATION 
        Required

    DESCRIPTION:
        Remove a like from the quiz with id <quiz_id>

    INPUT FORMAT:
        Not needed

    RESPONSE:
        A json represents the quizzes
    
    SUCCESS STATUS CODE: 200
    """
    quiz_id = request.args.get("quiz_id")
    if not quiz_id or type(quiz_id) is not str:
        abort(400, "Abide to data constraints")
    quiz = storage.get(Quiz, quiz_id)
    if not quiz:
        abort(404)
    if request.current_user in quiz.fans_users:
        quiz.fans_users.remove(request.current_user)
        quiz.likes_num -= 1
        quiz.save()
        result = quiz.to_dict()
        return make_response(jsonify(result), 200)
    abort(400, "You didn't like this quiz")
