"""Categories endpoints
"""
from api.v1.views import app_views
from flask import jsonify
from models import storage
from models.categories import Category


@app_views.route("/categories", methods=['GET'], strict_slashes=False)
def get_categories():
    """Return categories list
    """
    categories = storage.get_all(Category)
    return jsonify([cat.to_dict() for cat in categories])
