from django import forms
from django.contrib.auth.forms import UserCreationForm


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(label="Электронная почта")

    class Meta(UserCreationForm.Meta):
        fields = ("username", "email")
