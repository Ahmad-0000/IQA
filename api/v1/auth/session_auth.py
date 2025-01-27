"""Session authentication mechanism implementation is here
"""
from os import getenv
from uuid import uuid4
from models import storage
from models.users import User
from models.sessions import Session

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
        """Returns the session cookie value if present, otherwise
        return <None>.
        """
        cookie_name = getenv("SESSION_COOKIE_NAME")
        if not cookie_name:
            return None
        return request.cookies.get(cookie_name)

    def current_user(self, request):
        """Get the user object based on the session id
        """
        session_id = self.session_cookie(request)
        if not session_id:
            return None
        session = storage.get(Session, session_id)
        if not session:
            return None
        return session.user

    def create_session(self, user_id):
        """Create a login session id for authenticating users
        """
        user = storage.get(User, user_id)
        if not user:
            return None
        session = Session(user_id=user.id)
        session.save()
        return session.id

    def destroy_session(self, request):
        """Destroys a session. Used in cases of logout and
        account deletion.
        """
        session_id = self.session_cookie(request)
        if not session_id:
            return False
        session = storage.get(Session, session_id)
        if session:
            session.delete()
            return True
        return False
