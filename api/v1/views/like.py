"""Hanlde likes endpoint
"""
from flask import jsonify, make_response, abort, request
from api.v1.views import app_views
from models import storage
from models.quizzes import Quiz

@app_views.route("/quizzes/<quiz_id>/like", methods=['POST'], strict_slashes=False)
def make_like(quiz_id):
    """Increases quizzes likes
    """
    if not quiz_id or type(quiz_id) is not str:
        abort(400, "Abide to data constraints")
    quiz = storage.get(Quiz, quiz_id)
    if not quiz:
        abort(404)
    if quiz.user_id == request.current_user.id:
        abort(400, "You can't assign a like to your own quiz")
    quiz.fans_users.append(request.current_user)
    quiz.likes_num += 1
    quiz.save()
    return make_response(jsonify(quiz.to_dict()), 201)

@app_views.route("/quizzes/<quiz_id>/remove_like", methods=['DELETE'], strict_slashes=False)
def remove_like(quiz_id):
    """Remove a like from a quiz
    """
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
