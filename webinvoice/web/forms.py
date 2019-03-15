from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import (AuthenticationForm, PasswordChangeForm,
                                       PasswordResetForm, SetPasswordForm,
                                       UserCreationForm)
from .models import Customer, Product, Invoice
from django.core.exceptions import ValidationError
Clinic = get_user_model()

class LoginForm(AuthenticationForm):
    """ログインフォーム"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = field.label  # placeholderにフィールドのラベルを入れる

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ('code', 'company_name', 'dept_name', 'representative', 'zip', 'address','email' ,'phone')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
        self.fields['zip'].widget.attrs['placeholder'] = '例：111-1111'  # placeholderにフィールドのラベルを入れる
        self.fields['phone'].widget.attrs['placeholder'] = '例：08012345678'  # placeholderにフィールドのラベルを入れる
        self.fields['email'].widget.attrs['placeholder'] = '例：example@hoge.com'  # placeholderにフィールドのラベルを入れる

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ('code', 'name', 'price', 'tax_type')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ('code', 'customer', 'product', 'amount', 'subtotal', 'tax', 'month_used')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'