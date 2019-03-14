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
from django.views.generic import View
from django.utils import timezone
from .models import *
from .render import Render
from easy_pdf.views import PDFTemplateView


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
        return context

import xhtml2pdf.pisa as pisa
from django.http import HttpResponse
import io
class FooPDFView(generic.ListView):
    model = Invoice
    template_name = 'pdf/invoice.html'

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

    def render_to_response(self, context):
        html = get_template(self.template_name).render(self.get_context_data())
        result = io.BytesIO()
        pdf = pisa.pisaDocument(
            io.BytesIO(html.encode('utf-8')),
            result,
            link_callback=link_callback,
            encoding='utf-8',
        )

        if not pdf.err:
            return HttpResponse(
                result.getvalue(),
                content_type='application/pdf'
            )

        return HttpResponse('<pre>%s</pre>' % escape(html))

def link_callback(uri, rel):
    sUrl = settings.STATIC_URL
    sRoot = settings.STATIC_ROOT
    path = os.path.join(sRoot, uri.replace(sUrl, ""))

    if not os.path.isfile(path):
        raise Exception(
            '%s must start with %s' % \
            (uri, sUrl)
        )

    return path


class Pdf(View):
    def get(self, request):
        data = Invoice.objects.all()
        yearmonth = self.request.GET.get('yearmonth')
        customer_code = self.request.GET.get('customer')

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

        params = {
            'invoices': data,
            'ourinfo': ourinfo,
            'bank': bank_info,
            'customer': customer
        }

        return Render.render('pdf/invoice.html', params)

class InvoicePDFView(PDFTemplateView):
    template_name = 'pdf/invoice.html'
    def get_context_data(self, **kwargs):
        context = super(InvoicePDFView, self).get_context_data(**kwargs)

        data = Invoice.objects.all()
        yearmonth = self.request.GET.get('yearmonth')
        customer_code = self.request.GET.get('customer')

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

        context['invoices'] = data
        context['ourinfo'] = ourinfo
        context['bank'] = bank_info
        context['customer'] = customer
        return context