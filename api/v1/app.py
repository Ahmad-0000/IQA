"""API app
"""
from os import getenv
from flask import (
        Flask,
        make_response,
        jsonify,
        request,
        abort
)
from flask_cors import CORS
from api.v1.views import app_views
from models import storage
from api.v1.auth.session_auth import SessionAuth


app = Flask(__name__)
app.register_blueprint(app_views, url_prefix="/api/v1")
# Create the authentication object for managing authentication
auth = SessionAuth()
# Handle CORS policies for Front-End side
CORS(app, supports_credentials=True, origins="http://localhost:8080")

@app.before_request
def handle_credentials():
    """Handle authentication
    """
    if auth.require_auth(
            request.method,
            request.path,
            included_methods=["POST", "PUT", "DELETE"],
            execluded_pathes=[("POST", "/api/v1/login"), ("POST", "/api/v1/users")]
    ):
        if not auth.session_cookie(request):
            abort(401)
        request.current_user = auth.current_user(request)
        if not request.current_user:
            abort(403)

@app.teardown_appcontext
def refresh(exception):
    """Refresh database connection after each so-called "request"
    """
    storage.close()

@app.errorhandler(404)
def error404(error):
    """Hanlde "Not Found" error
    """
    return make_response(jsonify({"error" : "Not found"}), 404)

@app.errorhandler(400)
def error400(error):
    """Handle "Bad Request" error
    """
    return make_response(jsonify({"error": error.description}), 400)

@app.errorhandler(401)
def error401(error):
    """Handles "unauthorized" error
    """
    return make_response(jsonify({"error": "unauthorized"}), 401)


@app.errorhandler(403)
def error403(error):
    """Handles "Forbidden" error
    """
    return make_response(jsonify({"error": "forbidden"}), 403)
