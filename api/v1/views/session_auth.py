"""Handles authentication
"""
import bcrypt
from os import getenv
from datetime import datetime, timedelta
from flask import abort, jsonify, request
from api.v1.views import app_views
from models import storage
from models.users import User


@app_views.route("/login", methods=['POST'], strict_slashes=False)
def login():
    """Hanldes user login
    """
    if not request.json:
        abort(400, "Not JSON")
    email = request.json.get("email")
    password = request.json.get("password")
    if not email:
        abort(400, "Missing email")
    if type(email) is not str:
        abort(400, "Abide to data constraints")
    if not password:
        abort(400, "Missing password")
    if type(password) is not str:
        abort(400, "Abide to data constraints")
    user = storage.get_filtered(User, {"email": email})
    if len(user) == 0:
        abort(404)
    password = bytes(password, "utf-8")
    real_password = bytes(user[0].password, "utf-8")
    if not bcrypt.checkpw(password, real_password):
        abort(401)
    from api.v1.app import auth
    res = jsonify(user[0].to_dict())
    session_cookie = auth.create_session(user[0].id)
    cookie_name = getenv("SESSION_COOKIE_NAME")
    res.set_cookie(cookie_name, session_cookie, expires=datetime.utcnow() + timedelta(10))
    return res


@app_views.route("/logout", methods=['DELETE'], strict_slashes=False)
def logout():
    """Handles logout
    """
    from api.v1.app import auth
    status = auth.destroy_session(request)
    if not status:
        abort(400, "login first")
    res = jsonify({})
    cookie_name = getenv("SESSION_COOKIE_NAME")
    res.set_cookie(cookie_name, "session_cookie", expires=datetime.utcnow() - timedelta(1))
    return res 
