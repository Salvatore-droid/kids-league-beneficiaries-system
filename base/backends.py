from django.contrib.auth import get_user_model
from .models import User

class EmailOrUsernameAuthBackend:
    """
    Custom authentication backend that allows login with email for Members
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # Try email first
            user = User.objects.get(email=username, is_active=True)
            if user.check_password(password):
                return user
        except Members.DoesNotExist:
            try:
                # Fall back to username
                user = User.objects.get(username=username, is_active=True)
                if user.check_password(password):
                    return user
            except Members.DoesNotExist:
                return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id, is_active=True)
        except User.DoesNotExist:
            return None