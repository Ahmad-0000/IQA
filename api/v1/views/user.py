"""User view
"""
from os import getenv
from datetime import datetime, date, timedelta
from sqlalchemy.exc import DataError
from flask import make_response, jsonify, abort, request
from api.v1.views import app_views
from models import storage
from models.users import User


@app_views.route("/users", methods=['GET'], strict_slashes=False)
def show_all_users():
    """GET /users => Shows all users accounts
    """
    _type = request.args.get('type')
    after = request.args.get('after')
    if not _type or _type not in ['asc', 'desc']:
        _type = 'desc'
    try:
        after = datetime.fromisoformat(after)
    except (TypeError, ValueError):
        after = 'initial'
    users = storage.get_paged(User, 'added_at', _type, after)
    return jsonify([user.to_dict() for user in users])

@app_views.route("/users/<user_id>", methods=['GET'], strict_slashes=False)
def show_user(user_id):
    """GET /users/<user_id> => Shows user account of 
                               user with id equal to
                               "user_id"
    """
    current_user = request.__dict__.get('current_user')
    if user_id == 'me' and current_user:
        return jsonify(current_user.to_dict())
    else:
        user = storage.get(User, user_id)
    if not user:
        abort(404)
    return jsonify(user.to_dict())


@app_views.route("/users", methods=['POST'], strict_slashes=False)
def new_account():
    """POST /users => Creates a new user account
    """
    if not request.is_json:
        abort(400, "Not a JSON")
    first_name = request.json.get('first_name')
    middle_name = request.json.get('middle_name')
    last_name = request.json.get('last_name')
    dob = request.json.get('dob')
    email = request.json.get('email')
    password = request.json.get('password')
    if not first_name or not middle_name or not last_name or not dob or not email or not password:
        abort(400, "Missing data")
    try:
        dob = date.fromisoformat(dob)
    except ValueError:
        abort(400, "Use YYYY-MM-DD format for date of birth")
    if (date.today() - dob).days < 3650:
        abort(400, "You need to be at least 10 years old")
    if storage.get_filtered(User, {"email": email}):
        abort(409, f"User with email {request.json['email']} is present")
    new_user = User(
                    first_name=first_name,
                    middle_name=middle_name,
                    last_name=last_name,
                    dob=dob,
                    email=email,
                    password=password
    )
    try:
        new_user.save()
    except DataError:
        storage.rollback()
        abort(400, "Abide to data constraints")
    from api.v1.app import auth
    res = make_response(jsonify(new_user.to_dict()), 201)
    session_id = auth.create_session(new_user.id)
    cookie_name = getenv("SESSION_COOKIE_NAME")
    res.set_cookie(cookie_name, session_id, expires=datetime.utcnow() + timedelta(10)) # Change it to None
    return res


@app_views.route("/users", methods=["PUT"], strict_slashes=False)
def update_account():
    """PUT /users => update the current user's account
    """
    if not request.is_json:
        abort(400, "Not JSON")
    allowed = ["first_name", "bio", "password"]
    to_update = {}
    for k, v in request.json.items():
        if k not in allowed:
            pass
        else:
            to_update[k] = v
    if not to_update:
        abort(400, "Provide at least one value to update")
    same_data = 0
    for k, v in to_update.items():
        if request.current_user.__dict__[k] == v:
            same_data += 1
    if same_data == len(to_update):
        abort(400, "Provide at least one different value")
    try:
        request.current_user.update(**to_update)
    except DataError:
        abort(400, "Abide to data constraints")
    return jsonify(request.current_user.to_dict())

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
