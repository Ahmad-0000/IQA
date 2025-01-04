"""User view
"""
from datetime import date
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
    users_accounts = storage.get_all(User)
    return make_response(jsonify(
            [user_account.to_dict() for user_account in users_accounts]),
            200)

@app_views.route("/users/<user_id>", methods=['GET'], strict_slashes=False)
def show_user(user_id):
    """GET /users/<user_id> => Shows user account of 
                               user with id equal to
                               "user_id"
    """
    user_account = storage.get(User, user_id)
    if not user_account:
        abort(404)
    return make_response(jsonify(user_account.to_dict()), 200)


@app_views.route("/users", methods=['POST'], strict_slashes=False)
def new_account():
    """POST /users => Creates a new user account
    """
    if not request.json:
        abort(404, "Not a JSON")
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
    return make_response(jsonify(new_user.to_dict()), 201)


@app_views.route("/users/<user_id>", methods=["PUT"], strict_slashes=False)
def update_account(user_id):
    """PUT /users/<user_id> => update a user account
    """
    user = storage.get(User, user_id)
    if not user:
        abourt(404)
    if not request.json:
        abort(400, "Not JSON")
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
    return make_response(jsonify(user.to_dict()), 200)

@app_views.route("/users/<user_id>", methods=['DELETE'], strict_slashes=False)
def delete_account(user_id):
    """DELETE /users/<user_id> => Deletes a user account
    """
    user = storage.get(User, user_id)
    if not user:
        abort(404)
    user.delete()
    return make_response(jsonify({}), 204)
