"""User view to handle user's endpoints
"""
import bcrypt
from os import getenv
from datetime import datetime, date, timedelta
from sqlalchemy.exc import DataError
from flask import make_response, jsonify, abort, request
from api.v1.views import app_views
from models import storage
from models.users import User


@app_views.route("/users", methods=['GET'], strict_slashes=False)
def show_all_users():
    """GET /api/v1/users[?user_id=<user_id>]

    AUTHENTICATION:
        Not required

    DESCRIPTION:
        Get all the user's account info in JSON format.
    If the optional <user_id> parameter is present, 
    only the associated user's info will be returned if
    any.

    INPUT FORMAT:
        No input is needed.

    RESPONSE:
        A JSON representation of the user account.

    SUCCESS STATUS CODE: 200
    """
    user_id = request.args.get('user_id')
    if user_id:
        current_user = request.__dict__.get('current_user')
        if user_id == 'me' and current_user:
            return jsonify(current_user.to_dict())
        else:
            user = storage.get(User, user_id)
        if not user:
            abort(404)
        return jsonify(user.to_dict())
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


@app_views.route("/users", methods=['POST'], strict_slashes=False)
def new_account():
    """POST /api/v1/users

    AUTHENTICATION:
        Not required

    DESCRIPTION:
        Create a new user account and login session.

    INPUT FORMAT:
        * A json body with the following fields is needed:
            {
                "first_name": <first_name>,
                "middle_name": <middle_name>,
                "last_name": <last_name>,
                "email": <email>,
                "password": <password>,
                "dob": <date of birth, in ISO format "YYYY-MM-DD">
            }
        * Data constraints:
            first_name: A maximimuly 20 characters length string
            middle_name: A maximimuly 20 characters length string
            last_name: A maximimuly 20 characters length string
            email: A maximumly 50 characters length email
            password: A string.
        * Optional:
            You can also include the following field:
                "bio":  A maximimuly 300 characters length string

    RESPONSE:
        A JSON string representing the user's account info
    
    SUCCESS STATUS CODE: 201
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
        return make_response(jsonify({"error": f"User with email {request.json['email']} is present"}), 409)
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
    """PUT /api/v1/users?user_id=<user_id>

    DESCRIPTION:
        Update a user's account

    INPUT FORMAT:
        * A json body with at least one of the following fields:
            {
                "first_name": <first_name>,
                "password" : <password>,
                "bio": <bio>
            }

        * Data constraints:
            first_name: A maximimuly 20 characters length string
            password: A string.
            bio: A maximimuly 300 characters length string

    RESPONSE:
        A JSON string with the updated quiz info

    SUCCESS STATUS CODE: 200
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
    to_update_copy = to_update.copy()
    for k, v in to_update_copy.items():
        if type(to_update[k]) is not str or not to_update[k]:
            del to_update[k]
    if not to_update:
        abort(400, "Provide at least one value to update")
    same_data = 0
    for k, v in to_update.items():
        if k == 'password':
            if bcrypt.checkpw(bytes(v, "utf-8"), bytes(request.current_user.password, "utf-8")):
                same_data += 1
        elif request.current_user.__dict__[k] == v:
            same_data += 1
    if same_data == len(to_update):
        abort(400, "Provide at least one different value")
    try:
        request.current_user.update(**to_update)
    except DataError:
        storage.rollback()
        abort(400, "Abide to data constraints")
    return jsonify(request.current_user.to_dict())

@app_views.route("/users", methods=['DELETE'], strict_slashes=False)
def delete_account():
    """DELETE /api/v1/users

    AUTHENTICATION:
        Required.

    DESCRIPTION:
        Delete a user's account.

    INPUT FORMAT:
        * No input is needed, the user accound will be extracted
        with the login info
    
    RESPONSE:
        Empty

    SUCCESS STATUS CODE: 204
    """
    if not request.is_json:
        abort(400, "Not JSON")
    email = request.json.get("email")
    if not email:
        abort(400, "Missing email")
    password = request.json.get("password")
    if not password:
        abort(400, "Missing password")
    if request.current_user.email != email:
        abort(403)
    if not bcrypt.checkpw(bytes(password, "utf8"), bytes(request.current_user.password, "utf8")):
        abort(403)
    request.current_user.delete()
    from api.v1.app import auth
    auth.destroy_session(request)
    response = jsonify({})
    response.status_code = 204
    cookie_name = getenv("SESSION_COOKIE_NAME")
    response.set_cookie(cookie_name, "", expires=datetime.utcnow() - timedelta(1))
    return response
