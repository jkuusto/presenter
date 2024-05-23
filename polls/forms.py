from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

from .models import Choice, Question


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['question_text']


class ChoiceForm(forms.ModelForm):
    class Meta:
        model = Choice
        fields = ['choice_text']