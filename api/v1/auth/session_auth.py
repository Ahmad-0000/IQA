"""Session authentication
"""
from os import getenv
from uuid import uuid4
from models import storage
from models.users import User

class SessionAuth():
    """Handles session authentication
    """
    __user_id_by_session_id = {}

    def require_auth(
            self, method, path,
            included_methods: list, execluded_pathes) -> bool:
        """Determine if an authentication is required based on
        the HTTP method and the execluded pathes
        """
        if method in included_methods:
            if (method, path) not in execluded_pathes:
                return True
        if path.startswith('/api/v1/quzzies/next/'):
            return True
        return False

    def session_cookie(self, request):
        """Returns the session cookie if present
        """
        cookie_name = getenv("SESSION_COOKIE_NAME")
        if not cookie_name:
            return None
        return request.cookies.get(cookie_name)

    def current_user(self, request):
        """Get the account info based on the session id
        """
        session_id = self.session_cookie(request)
        if not session_id:
            return None
        user_id = SessionAuth.__user_id_by_session_id.get(session_id)
        if not user_id:
            return None
        return storage.get(User, user_id)

    def create_session(self, user_id):
        """Create a session
        """
        user = storage.get(User, user_id)
        if not user:
            return None
        session_id = str(uuid4())
        SessionAuth.__user_id_by_session_id[session_id] = user_id
        return session_id

    def destroy_session(self, request):
        """Destroys a session
        """
        session_id = self.session_cookie(request)
        if not session_id:
            return False
        if session_id in SessionAuth.__user_id_by_session_id:
            del SessionAuth.__user_id_by_session_id[session_id]
            return True
        return False
