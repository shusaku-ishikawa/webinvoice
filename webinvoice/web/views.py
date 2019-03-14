import json
import logging
import os

from django import forms, http
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import (LoginView, LogoutView,
                                       PasswordChangeDoneView,
                                       PasswordChangeView,
                                       PasswordResetCompleteView,
                                       PasswordResetConfirmView,
                                       PasswordResetDoneView,
                                       PasswordResetView)
from .forms import LoginForm, CustomerForm, ProductForm
from django.contrib.sites.shortcuts import get_current_site
from django.core import serializers
from django.core.signing import BadSignature, SignatureExpired, dumps, loads
from django.forms.utils import ErrorList
from django.shortcuts import redirect, resolve_url
from django.template.loader import get_template
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views import generic
from django.contrib.auth import authenticate
from django.conf import settings
from django.http import HttpResponseBadRequest,JsonResponse
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.views.generic.list import MultipleObjectMixin
from django.contrib.auth.hashers import check_password
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponseRedirect
from django.http import Http404, HttpResponseBadRequest, JsonResponse
from datetime import datetime, timedelta
from django.db import models
from .models import Customer, Product, Invoice

# Create your views here.
class TopPage(LoginRequiredMixin, generic.TemplateView):
    template_name = 'top.html'
    
class Login(LoginView):
    """ログインページ"""
    form_class = LoginForm
    template_name = 'login.html'

class Logout(LoginRequiredMixin, LogoutView):
    """ログアウトページ"""
    template_name = 'top.html'


class CreateCustomer(SuccessMessageMixin, LoginRequiredMixin, generic.CreateView):
    template_name = "create_customer.html"
    form_class = CustomerForm
    success_message = '登録情報を更新しました'
    def get_success_url(self):
        return reverse('web:list_customer')


class UpdateCustomer(SuccessMessageMixin, LoginRequiredMixin, generic.UpdateView):
    model = Customer
    form_class = CustomerForm
    template_name = 'update_customer.html'
    success_message = '登録情報を更新しました'

    def get_success_url(self):
        return reverse('web:list_customer')

class ListCustomer(SuccessMessageMixin, LoginRequiredMixin, generic.ListView):
    model = Customer
    template_name = 'list_customer.html'
    paginate_by = 10  #and that's it !!


class CreateProduct(SuccessMessageMixin, LoginRequiredMixin, generic.CreateView):
    template_name = "create_product.html"
    form_class = ProductForm
    success_message = '登録情報を更新しました'
    def get_success_url(self):
        return reverse('web:list_product')


class UpdateProduct(SuccessMessageMixin, LoginRequiredMixin, generic.UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'update_product.html'
    success_message = '登録情報を更新しました'

    def get_success_url(self):
        return reverse('web:list_product')

class ListProduct(SuccessMessageMixin, LoginRequiredMixin, generic.ListView):
    model = Product
    template_name = 'list_product.html'
    paginate_by = 10  #and that's it !!

class ListInvoice(SuccessMessageMixin, LoginRequiredMixin, generic.ListView):
    model = Invoice
    template_name = 'list_invoice.html'
    paginate_by = 100
