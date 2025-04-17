from django import forms
from django.contrib.auth.forms import AuthenticationForm


class AdminAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(label='Почта пользователя')
