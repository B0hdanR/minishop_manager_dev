from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

from accounts.models import SupportRequest

User = get_user_model()

class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Username",
                "class": "form-control"
            }
        ))
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Password",
                "class": "form-control"
            }
        ))


class SignUpForm(UserCreationForm):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Username",
                "class": "form-control"
            }
        ))
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "placeholder": "Email",
                "class": "form-control"
            }
        ))
    password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Password",
                "class": "form-control"
            }
        ))
    password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Password check",
                "class": "form-control"
            }
        ))
    first_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            "placeholder": "First Name",
            "class": "form-control"
        })
    )

    last_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            "placeholder": "Last Name",
            "class": "form-control"
        })
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'first_name', 'last_name')


class SupportRequestForm(forms.ModelForm):
    class Meta:
        model = SupportRequest
        fields = ('title', 'content')
        widgets = {
            'title': forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Title",
            }),
            'content': forms.Textarea(attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "Content",
            }),
        }


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name')

        widgets = {
            'email': forms.EmailInput(attrs={
                "placeholder": "Email",
                "class": "form-control"
            }),
            'first_name': forms.TextInput(attrs={
                "placeholder": "First Name",
                "class": "form-control"
            }),
            'last_name': forms.TextInput(attrs={
                "placeholder": "Last Name",
                "class": "form-control"
            }),
        }
