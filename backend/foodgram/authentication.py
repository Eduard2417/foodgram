from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.shortcuts import get_object_or_404

User = get_user_model()


class EmailBackend(ModelBackend):
    def authenticate(self, request, username, password, **kwargs):
        user = get_object_or_404(User, email=username)
        if user.check_password(password):
            return user
        return None
