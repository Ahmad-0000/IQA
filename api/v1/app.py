"""API app
"""
from os import getenv
from flask import Flask, make_response, jsonify
from flask_cors import CORS
from models import storage


app = Flask(__name__)
CORS(app, origins=["http://localhost:8080"], supportes_credentials=True)

@app.teardown_appcontext
def refresh(exception):
    """Refresh database connection after each
    """
    storage.close()

@app.errorhandler(404)
def error404(error):
    """Hanlde status code 404
    """
    return make_response(jsonify({"error" : "Not found"}), 404)

if __name__ == "__main__":
    host = getenv("IQA_API_HOST")
    port = getenv("IQA_API_PORT")
    if not (host and port):
        host = "0.0.0.0"
        port = "5000"
    app.run(host=host, port=port, threaded=True)
