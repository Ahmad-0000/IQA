"""User view
"""
from flask import make_response, jsonify
from api.v1.views import app_views
from models import storage
from models.users import User


@app_views.route("/users", methods=['GET'], strict_slashes=False)
def show_all_users():
    """GET /users => Show all users accounts
    """
    users_accounts = storage.get_all(User)
    return make_response(
            jsonify([
                    user_account.to_dict() for user_account in users_accounts
                    ]), 200)
