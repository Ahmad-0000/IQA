"""Initialize main blueprint
"""
from flask import Blueprint


app_views = Blueprint('app_views', __name__)
from api.v1.views.user import *
from api.v1.views.quiz import *
from api.v1.views.feedback import *
from api.v1.views.like import *
from api.v1.views.session_auth import *
