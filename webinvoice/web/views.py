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
from .forms import LoginForm, CustomerForm, ProductForm, InvoiceForm
from django.contrib.sites.shortcuts import get_current_site
from django.core import serializers
from django.core.signing import BadSignature, SignatureExpired, dumps, loads
from django.forms.utils import ErrorList
from django.shortcuts import redirect, resolve_url
from django.template.loader import get_template, render_to_string
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views import generic
from django.contrib.auth import authenticate
from django.conf import settings
from django.http import HttpResponseBadRequest,JsonResponse, HttpResponse
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.views.generic.list import MultipleObjectMixin
from django.contrib.auth.hashers import check_password
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponseRedirect
from django.http import Http404, HttpResponseBadRequest, JsonResponse
from datetime import datetime, timedelta
from django.db import models
from django.views.generic import View
from django.utils import timezone
from .models import *
from .render import Render
from easy_pdf.views import PDFTemplateView
import pdfkit

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

class CreateInvoice(SuccessMessageMixin, LoginRequiredMixin, generic.CreateView):
    template_name = "create_invoice.html"
    form_class = InvoiceForm
    success_message = '登録情報を更新しました'
    def get_success_url(self):
        return reverse('web:list_invoice')


class UpdateInvoice(SuccessMessageMixin, LoginRequiredMixin, generic.UpdateView):
    model = Invoice
    form_class = InvoiceForm
    template_name = 'update_invoice.html'
    success_message = '登録情報を更新しました'

    def get_success_url(self):
        return reverse('web:list_invoice')
class ListInvoice(SuccessMessageMixin, LoginRequiredMixin, generic.ListView):
    model = Invoice
    template_name = 'list_invoice.html'
    paginate_by = 100

    def get_queryset(self):
        data = Invoice.objects.all()
        yearmonth = self.request.GET.get('yearmonth')
        customer_code = self.request.GET.get('customer')

        if yearmonth != None:
            data = data.filter(month_used = yearmonth)
        if customer_code != None:
            customer = Customer.objects.filter(code = customer_code)
            data = data.filter(customer = customer[0])
         
        return data

    def get_context_data(self, **kwargs):
        context = super(ListInvoice, self).get_context_data(**kwargs)
        customer_list = Customer.objects.all()
        context['customer_list'] = customer_list
        context['yearmonth'] = self.request.GET.get('yearmonth')
        context['customer'] = self.request.GET.get('customer')
        
        return context

def pdf(request):
    data = Invoice.objects.all()
    yearmonth = request.GET.get('yearmonth')
    total_wo_tax = data.aggregate(total_wo_tax = models.Sum('subtotal'))['total_wo_tax']
    total_tax = data.aggregate(total_tax = models.Sum('tax'))['total_tax']

    customer_code = request.GET.get('customer')

    ourinfo = {
        'zip': '111-1111',
        'address_1': 'xxxxx',
        'address_2': 'yyyyy',
        'phone': 'eeeeee'
    }
    bank_info = {
        'bank': '三井住友',
        'branch': '立川支店',
        'type': '普通',
        'number': '111111',
        'meigi': '株式会社ビジョン'
    }

    if yearmonth != None:
        data = data.filter(month_used = yearmonth)
    if customer_code != None:
        customer = Customer.objects.filter(code = customer_code)
        data = data.filter(customer = customer[0])

    context = {
        'data': data,
        'total_wo_tax': total_wo_tax,
        'total_tax': total_tax,
        'total': total_wo_tax + total_tax,
        'bank': bank_info,
        'ourinfo': ourinfo,
        'customer': customer[0],

    }
    html_template = render_to_string('pdf/invoice.html', context)

    options = {
        'page-size': 'Letter',
        'encoding': "UTF-8",
    }
    pdf = pdfkit.from_string(html_template, False, options)
    response = HttpResponse(pdf, content_type='application/pdf')
    return response

  