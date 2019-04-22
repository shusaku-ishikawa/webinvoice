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
from .forms import *
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
import pdfkit
from django.core.files.base import ContentFile
import csv
from io import TextIOWrapper, StringIO
from django.db.models import *

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


class CreateCompany(SuccessMessageMixin, LoginRequiredMixin, generic.CreateView):
    template_name = "create_company.html"
    form_class = CompanyForm
    success_message = '登録情報を更新しました'
    def get_success_url(self):
        return reverse('web:list_company')

class ListCompany(SuccessMessageMixin, LoginRequiredMixin, generic.ListView):
    model = Company
    template_name = 'list_company.html'
    paginate_by = 10  #and that's it !!


# class UpdateCustomer(SuccessMessageMixin, LoginRequiredMixin, generic.UpdateView):
#     model = Customer
#     form_class = CustomerForm
#     template_name = 'update_customer.html'
#     success_message = '登録情報を更新しました'

#     def get_success_url(self):
#         return reverse('web:list_customer')



# class CreateProduct(SuccessMessageMixin, LoginRequiredMixin, generic.CreateView):
#     template_name = "create_product.html"
#     form_class = ProductForm
#     success_message = '登録情報を更新しました'
#     def get_success_url(self):
#         return reverse('web:list_product')


# class UpdateProduct(SuccessMessageMixin, LoginRequiredMixin, generic.UpdateView):
#     model = Product
#     form_class = ProductForm
#     template_name = 'update_product.html'
#     success_message = '登録情報を更新しました'

#     def get_success_url(self):
#         return reverse('web:list_product')

# class ListProduct(SuccessMessageMixin, LoginRequiredMixin, generic.ListView):
#     model = Product
#     template_name = 'list_product.html'
#     paginate_by = 10  #and that's it !!

# class CreateOrder(SuccessMessageMixin, LoginRequiredMixin, generic.CreateView):
#     template_name = "create_order.html"
#     form_class = OrderForm
#     success_message = '登録情報を更新しました'
#     def get_success_url(self):
#         return reverse('web:list_order')


# class UpdateOrder(SuccessMessageMixin, LoginRequiredMixin, generic.UpdateView):
#     model = Order
#     form_class = OrderForm
#     template_name = 'update_order.html'
#     success_message = '登録情報を更新しました'

#     def get_success_url(self):
#         return reverse('web:list_order')

# class ListOrder(SuccessMessageMixin, LoginRequiredMixin, generic.ListView):
#     model = Order
#     template_name = 'list_order.html'
#     paginate_by = 100

#     def get_queryset(self):
#         data = Order.objects.all()
#         yearmonth = self.request.GET.get('yearmonth')
#         customer_code = self.request.GET.get('customer')

#         if yearmonth != None:
#             data = data.filter(month_used = yearmonth)
#         if customer_code != None:
#             customer = Customer.objects.filter(code = customer_code)
#             data = data.filter(customer = customer[0])
         
#         return data

#     def get_context_data(self, **kwargs):
#         context = super(ListOrder, self).get_context_data(**kwargs)
#         customer_list = Customer.objects.all()
#         context['customer_list'] = customer_list
#         context['yearmonth'] = self.request.GET.get('yearmonth')
#         context['customer'] = self.request.GET.get('customer')
        
#         return context

# class UploadOrderCsv(SuccessMessageMixin, LoginRequiredMixin, generic.FormView):
#     form_class = UploadCsvForm
#     template_name = 'import_order_csv.html'

#     def form_valid(self, form):
#         file_name = form.save()

#         with open('media/' + file_name, 'r') as f:
#             reader = csv.reader(f)
#             for row in reader:
#                 print(len(row))
#                 print(row[1])
#                 print(row[2])
#                 print(row[3])
                
        
#         context = {
#             'file_name': file_name,
#             'form': form,
            
#         }
#         return self.render_to_response(context)

# class ListInvoice(SuccessMessageMixin, LoginRequiredMixin, generic.ListView):
#     model = Invoice
#     template_name = 'list_invoice.html'
#     paginate_by = 10


# def pdf(request):
#     data = Order.objects.all()
#     customer_code = request.GET.get('customer')
#     yearmonth = request.GET.get('yearmonth')
#     total_wo_tax = 0
#     total_tax = 0

#     for order in data:
#         total_wo_tax += order.product.price * order.amount
#         if order.product.tax_type == '課税':
#             total_tax += order.product.price * settings.TAX_RATE * order.amount
    
    
#     ourinfo = {
#         'zip': '111-1111',
#         'address_1': 'xxxxx',
#         'address_2': 'yyyyy',
#         'phone': 'eeeeee'
#     }
#     bank_info = {
#         'bank': '三井住友',
#         'branch': '立川支店',
#         'type': '普通',
#         'number': '111111',
#         'meigi': '株式会社ビジョン'
#     }

#     if yearmonth != None:
#         data = data.filter(month_used = yearmonth)
#     if customer_code != None:
#         customer = Customer.objects.filter(code = customer_code)[0]
#         data = data.filter(customer = customer)

#     total_per_product = data.values('product', 'month_used').annotate(count_per_product = Sum('amount'), total_per_product = Sum(F('product__price') * F('amount'), output_field=models.FloatField()))
#     tax_per_product = data.filter(product__tax_type = '課税').values('product', 'month_used').annotate(tax_per_product = Sum(F('tax_rate__rate') * F('product__price') * F('amount'), output_field=models.FloatField()))
#     for obj in total_per_product:
#         obj['product_info'] = Product.objects.get(pk = obj['product'])
#         for tax_obj in tax_per_product:
#             if tax_obj['product'] == obj['product']:
#                 obj['tax'] = tax_obj['tax_per_product']
#         if not 'tax' in obj.keys():
#             obj['tax'] = 0
        

#     print(total_per_product)
#     context = {
#         'data': total_per_product,
#         'total_wo_tax': total_wo_tax,
#         'total_tax': int(total_tax),
#         'total': total_wo_tax + int(total_tax),
#         'bank': bank_info,
#         'ourinfo': ourinfo,
#         'customer': customer,
#     }
#     html_template = render_to_string('pdf/invoice.html', context)

#     options = {
#         'page-size': 'Letter',
#         'encoding': "UTF-8",
#     }

#     pdf = pdfkit.from_string(html_template, False, options)

#     invoice_code = customer.code + '_' + datetime.today().strftime('%Y%m%d%H%M')
#     invoice = Invoice()
#     invoice.customer = customer
#     invoice.code = invoice_code
#     invoice.file.save(invoice_code + '.pdf', ContentFile(pdf))
#     invoice.save()
#     data.update(invoice = invoice)

#     response = HttpResponse(pdf, content_type='application/pdf')
#     return response

  