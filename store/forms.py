from django import forms
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


class RegistrationForm(forms.Form):
    username = forms.CharField(label="Имя пользователя (Логин)", max_length=150)
    email = forms.EmailField(label="Email")
    name = forms.CharField(label="Имя и фамилия", max_length=160)
    phone = forms.CharField(label="Телефон", max_length=40, required=False)
    city = forms.CharField(label="Город", max_length=120, required=False)
    password = forms.CharField(label="Пароль", widget=forms.PasswordInput)
    password_confirm = forms.CharField(label="Подтверждение пароля", widget=forms.PasswordInput)

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Пользователь с таким именем уже существует.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Пользователь с таким email уже существует.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")
        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError("Пароли не совпадают.")
        return cleaned_data

