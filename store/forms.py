from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .services.pricing import pricing_choices
from .services.shipping import shipping_choices


class CheckoutForm(forms.Form):
    name = forms.CharField(label="Имя", max_length=160)
    email = forms.EmailField(label="Email")
    phone = forms.CharField(label="Телефон", max_length=40, required=False)
    city = forms.CharField(label="Город", max_length=120, required=False)
    delivery_method = forms.ChoiceField(label="Доставка", choices=shipping_choices, widget=forms.HiddenInput)
    pricing_strategy = forms.ChoiceField(label="Скидка", choices=pricing_choices, widget=forms.HiddenInput)
    comment = forms.CharField(label="Комментарий", widget=forms.Textarea, required=False)



class ReviewForm(forms.Form):
    customer_name = forms.CharField(label="Имя", max_length=120)
    rating = forms.IntegerField(label="Оценка", min_value=1, max_value=5, initial=5)
    text = forms.CharField(label="Отзыв", widget=forms.Textarea, required=False)


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Логин",
        widget=forms.TextInput(attrs={"placeholder": "Введите логин", "autofocus": True}),
    )
    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(attrs={"placeholder": "Введите пароль"}),
    )


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={"placeholder": "you@example.com"}),
    )
    first_name = forms.CharField(
        label="Имя",
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Ваше имя"}),
    )
    last_name = forms.CharField(
        label="Фамилия",
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Ваша фамилия"}),
    )
    username = forms.CharField(
        label="Логин",
        max_length=150,
        widget=forms.TextInput(attrs={"placeholder": "Придумайте логин"}),
    )
    password1 = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(attrs={"placeholder": "Не менее 8 символов"}),
    )
    password2 = forms.CharField(
        label="Подтверждение пароля",
        widget=forms.PasswordInput(attrs={"placeholder": "Повторите пароль"}),
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "first_name", "last_name", "password1", "password2")

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Пользователь с таким email уже существует.")
        return email
