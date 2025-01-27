"""Feedback endpoint
"""
from flask import make_response, jsonify, abort, request
from sqlalchemy.exc import DataError
from api.v1.views import app_views
from models import storage
from models.feedbacks import FeedBack
from models.quizzes import Quiz


@app_views.route("/quizzes/<quiz_id>/feedbacks", methods=['GET'], strict_slashes=False)
def get_quiz_feedbacks(quiz_id):
    """GET /api/v1AUTHENTICATION 

    AUTHENTICATION
        Not required

    DESCRIPTION:
        Gets the quizzes feedbacks

    INPUT FORMAT:
        Not needed

    RESPONSE:
        A json represents the feedback
    
    SUCCESS STATUS CODE: 200


    """
    quiz = storage.get(Quiz, quiz_id)
    if not quiz:
        abort(404)
    feedbacks = quiz.feedbacks
    return make_response(jsonify([feedback.to_dict() for feedback in feedbacks]))

@app_views.route("/feedbacks/<feedback_id>", methods=['GET'], strict_slashes=False)
def get_feedback(feedback_id):
    """GET /api/v1/feedbacks/<feedback_id>

    AUTHENTICATION 
        Not required

    DESCRIPTION:
        Get a specific feedback

    INPUT FORMAT:
        Not needed

    RESPONSE:
        A json represents the feedback
    
    SUCCESS STATUS CODE: 200
    """
    feedback = storage.get(FeedBack, feedback_id)
    if not feedback:
        abort(404)
    return jsonify(feedback.to_dict())

@app_views.route("/quizzes/<quiz_id>/feedbacks", methods=['POST'], strict_slashes=False)
def create_feedback(quiz_id):
    """POST /api/v1/quizzes/<quiz_id>/feedbacks

    AUTHENTICATION 
        Required

    DESCRIPTION:
        Create a feedback for a quiz with id <quiz_id>

    INPUT FORMAT:
        {
            'body': <string, 512 chars maximumly>
        }

    RESPONSE:
        A json represents the feedback
    
    SUCCESS STATUS CODE: 201
    """
    if not request.is_json:
        abort(400, "Not JSON")
    quiz = storage.get(Quiz, quiz_id)
    if not quiz:
        abort(404)
    body = request.json.get("body")
    if not body:
        abort(400, "Missing body")
    if type(body) is not str:
        abort(400, "Abide to data constraints")
    feedback = FeedBack(body=body, user_id=request.current_user.id, quiz_id=quiz_id)
    try:
        feedback.save()
    except DataError:
        storage.rollback()
        abort(400, "Abide to data constraints")
    return make_response(jsonify(feedback.to_dict()), 201)

@app_views.route("/feedbacks/<feedback_id>", methods=['PUT'], strict_slashes=False)
def update_feedback(feedback_id):
    """PUT /api/v1/feedbacks/<feedback_id>

    AUTHENTICATION
        Required

    DESCRIPTION:
        Update the feedback with id <feedback_id>

    INPUT FORMAT:
        {
            'body': <string, 512 chars maximumly>
        }

    RESPONSE:
        A json represents the feedback
    
    SUCCESS STATUS CODE: 200  
    """
    if not request.is_json:
        abort(400, "Not JSON")
    feedback = storage.get(FeedBack, feedback_id)
    if not feedback:
        abort(404)
    if feedback.user_id != request.current_user.id:
        abort(403)
    body = request.json.get("body")
    if not body:
        abort(400, "Provide a body")
    if type(body) is not str:
        abort(400, "Abide to data constraints")
    if body == feedback.body:
        abort(400, "Provide a different body")
    try:
        feedback.update(body=body)
    except DataError:
        abort(400, "Abide to data constraints")
    return make_response(jsonify(feedback.to_dict()), 200)

@app_views.route("/feedbacks/<feedback_id>", methods=['DELETE'], strict_slashes=False)
def delete_feedback(feedback_id):
    """DELETE /api/v1/feedbacks/<feedback_id>

    AUTHENTICATION 
        Required

    DESCRIPTION:
        Delete a feedback with id <feedback_id>

    INPUT FORMAT:
        Not needed

    RESPONSE:
        Empty
    
    SUCCESS STATUS CODE: 204
    """
    feedback = storage.get(FeedBack, feedback_id)
    if not feedback:
        abort(404)
    if feedback.user_id != request.current_user.id:
        abort(403)
    feedback.delete()
    return make_response(jsonify({}), 204)
