from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import (AuthenticationForm, PasswordChangeForm,
                                       PasswordResetForm, SetPasswordForm,
                                       UserCreationForm)
from .models import *
from django.core.exceptions import ValidationError
from django.core.files.storage import default_storage


class LoginForm(AuthenticationForm):
    """ログインフォーム"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control input-sm'
            field.widget.attrs['placeholder'] = field.label  # placeholderにフィールドのラベルを入れる

class CompanyForm(forms.ModelForm):
    """ 会社登録フォーム """   
    class Meta:
        model = Company
        exclude = ('pk', 'registered_at', 'registered_by', 'updated_at', 'updated_by', 'deleted')
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control input-sm'

class InvoiceEntityForm(forms.ModelForm):
    """ 請求管理簿登録フォーム """   
    class Meta:
        model = InvoiceEntity
        exclude = ('pk', 'registered_at', 'registered_by', 'updated_at', 'updated_by', 'deleted')
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control input-sm'

class InvoiceDetailForm(forms.ModelForm):
    """ 請求明細登録フォーム """   
    class Meta:
        model = InvoiceDetail
        exclude = ('pk', 'registered_at', 'registered_by', 'updated_at', 'updated_by', 'deleted')
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control input-sm'

class FileUploadForm(forms.ModelForm):
    """ ファイルアップロードフォーム """   
    class Meta:
        model = UploadedFile
        exclude = ('pk', 'processed_at', 'uploaded_by', 'record_count', 'error_count')
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control input-sm'

