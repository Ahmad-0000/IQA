"""User view
"""
from os import getenv
from datetime import datetime, date, timedelta
from sqlalchemy.exc import DataError
from flask import make_response, jsonify, abort, request
from api.v1.views import app_views
from models import storage
from models.users import User
from models.exc import DOBError


@app_views.route("/users", methods=['GET'], strict_slashes=False)
def show_all_users():
    """GET /users => Shows all users accounts
    """
    users = storage.get_all(User)
    return jsonify([user.to_dict() for user in users]),

@app_views.route("/users/<user_id>", methods=['GET'], strict_slashes=False)
def show_user(user_id):
    """GET /users/<user_id> => Shows user account of 
                               user with id equal to
                               "user_id"
    """
    current_user = request.__dict__.get('current_user')
    if user_id == 'me' and current_user:
        user_account = storage.get(User, current_user.id)
    else:
        user_account = storage.get(User, user_id)
    if not user_account:
        abort(404)
    return jsonify(user_account.to_dict())


@app_views.route("/users", methods=['POST'], strict_slashes=False)
def new_account():
    """POST /users => Creates a new user account
    """
    if not request.is_json:
        abort(400, "Not a JSON")
    required_data = [
                "first_name", "middle_name", "last_name",
                "dob", "email", "password"
            ]
    for data in required_data:
        if data not in request.json:
            abort(400, f"Missing {data}")
    user_attributes = {k: v for k, v in request.json.items() if k in required_data}
    if len(storage.get_filtered(User, {"email": request.json['email']})) > 0:
        abort(409, f"User with email {request.json['email']} is present")
    try:
        user_attributes['dob'] = date.fromisoformat(user_attributes['dob'])
    except ValueError:
        abort(400, "Use YYYY-MM-DD format for date of birth")
    new_user = User(**user_attributes)
    try:
        new_user.save()
    except DataError:
        abort(400, "Abide to data constraints")
    except DOBError:
        abort(400, "Users with age less than 10 years are not allowed")
    from api.v1.app import auth
    session_id = auth.create_session(new_user.id)
    res = make_response(jsonify(new_user.to_dict()), 201)
    cookie_name = getenv("SESSION_COOKIE_NAME")
    res.set_cookie(cookie_name, session_id, expires=datetime.utcnow() + timedelta(10))
    return res


@app_views.route("/users", methods=["PUT"], strict_slashes=False)
def update_account():
    """PUT /users => update the current user's account
    """
    if not request.is_json:
        abort(400, "Not JSON")
    user = request.current_user
    allowed = ["first_name", "bio", "image", "password"]
    to_update = {}
    for k, v in request.json.items():
        if k not in allowed:
            pass
        else:
            to_update.update({k: v})
    if not to_update:
        abort(400, "Provide attribute names to update")
    try:
        user.update(**to_update)
    except DataError:
        abort(400, "Abide to data constraints")
    return jsonify(user.to_dict())

@app_views.route("/users", methods=['DELETE'], strict_slashes=False)
def delete_account():
    """DELETE /users => Deletes the current user's account
    """
    request.current_user.delete()
    response = jsonify({})
    response.status_code = 204
    cookie_name = getenv("SESSION_COOKIE_NAME")
    response.set_cookie(cookie_name, "", expires=datetime.utcnow() - timedelta(1))
    return response
