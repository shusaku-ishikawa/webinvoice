from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import (AuthenticationForm, PasswordChangeForm,
                                       PasswordResetForm, SetPasswordForm,
                                       UserCreationForm)
from .models import *
from django.core.exceptions import ValidationError
from django.core.files.storage import default_storage
import pandas as pd

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
        exclude = ('id', 'registered_at', 'registered_by', 'updated_at', 'updated_by', 'deleted')
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control input-sm'

class InvoiceEntityForm(forms.ModelForm):
    """ 請求管理簿登録フォーム """   
    class Meta:
        model = InvoiceEntity
        exclude = ('id', 'registered_at', 'registered_by', 'updated_at', 'updated_by', 'deleted')
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control input-sm'

class InvoiceDetailForm(forms.ModelForm):
    """ 請求明細登録フォーム """   
    class Meta:
        model = InvoiceDetail
        exclude = ('id', 'registered_at', 'registered_by', 'updated_at', 'updated_by', 'deleted')
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control input-sm'

class CompanyExcelForm(forms.ModelForm):
    """ ファイルアップロードフォーム """   
    class Meta:
        model = UploadedFile
        exclude = ('id', 'type', 'processed_at', 'uploaded_by', 'record_count', 'error_count')
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control input-sm'
    
    def clean(self):
        cleaned_data = super(CompanyExcelForm, self).clean()
        d = pd.read_excel(self.files['file']) 
        df = d.where((pd.notnull(d)), None)
        # if len(df.columns) != UploadedFile.COLUMN_COUNT_COMPANY:
        #     print(len(df.columns))
        #     self.add_error('file', "列数が不正です")
        return cleaned_data

class InvoiceEntityExcelForm(forms.ModelForm):
    """ ファイルアップロードフォーム """   
    class Meta:
        model = UploadedFile
        exclude = ('pk', 'type', 'processed_at', 'uploaded_by', 'record_count', 'error_count')
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control input-sm'
    
    def clean(self):
        cleaned_data = super(InvoiceEntityExcelForm, self).clean()
        print(self.files['file'])
        return cleaned_data

class InvoiceDetailExcelForm(forms.ModelForm):
    """ ファイルアップロードフォーム """   
    class Meta:
        model = UploadedFile
        exclude = ('pk', 'type', 'processed_at', 'uploaded_by', 'record_count', 'error_count')
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control input-sm'
    
    def clean(self):
        cleaned_data = super(InvoiceDetailExcelForm, self).clean()
        print(self.files['file'])
        return cleaned_data
