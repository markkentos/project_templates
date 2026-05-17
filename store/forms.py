from django import forms

from .services.pricing import pricing_choices
from .services.shipping import shipping_choices


class CheckoutForm(forms.Form):
    name = forms.CharField(label="Имя", max_length=160)
    email = forms.EmailField(label="Email")
    phone = forms.CharField(label="Телефон", max_length=40, required=False)
    city = forms.CharField(label="Город", max_length=120, required=False)
    delivery_method = forms.ChoiceField(label="Доставка", choices=shipping_choices)
    pricing_strategy = forms.ChoiceField(label="Скидка", choices=pricing_choices)
    comment = forms.CharField(label="Комментарий", widget=forms.Textarea, required=False)


class ReviewForm(forms.Form):
    customer_name = forms.CharField(label="Имя", max_length=120)
    rating = forms.IntegerField(label="Оценка", min_value=1, max_value=5, initial=5)
    text = forms.CharField(label="Отзыв", widget=forms.Textarea)
