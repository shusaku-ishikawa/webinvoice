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
from django.http import Http404, HttpResponseBadRequest, JsonResponse, HttpResponseRedirect
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
    def form_valid(self, form):
        instance = form.save()
        if instance.registered_by == None:
            instance.registered_by = self.request.user
        instance.updated_by = self.request.user 
        instance.save()
        self.object = instance

        # do somet  hing with self.object
        # remember the import: from django.http import HttpResponseRedirect
        return HttpResponseRedirect(self.get_success_url())

class ListCompany(SuccessMessageMixin, LoginRequiredMixin, generic.ListView):
    model = Company
    template_name = 'list_company.html'
    paginate_by = 10  #and that's it !!
    def get_queryset(self):
        data = Company.objects.filter(deleted = False)
        key_corporate_number = "corporate_number"
        key_company_name = "company_name"
        key_phone_number = "phone_number"
        key_invoice_id = "invoice_id"

        if key_corporate_number in self.request.GET and self.request.GET.get(key_corporate_number) != None:
            q = self.request.GET.get(key_corporate_number)
            data = data.filter(corporate_number__icontains = q)
        
        if key_company_name in self.request.GET and self.request.GET.get(key_company_name) != None:
            q = self.request.GET.get(key_company_name)
            data = data.filter(kanji_name__icontains = q)

        if key_phone_number in self.request.GET and self.request.GET.get(key_phone_number) != None:
            q = self.request.GET.get(key_phone_number)
            data = data.filter(Q(telephone_1__icontains = q) | Q(telephone_2__icontains = q))
    
        return data

class UpdateCompany(SuccessMessageMixin, LoginRequiredMixin, generic.UpdateView):
    model = Company
    form_class = CompanyForm
    template_name = 'update_company.html'
    success_message = '登録情報を更新しました'

    def get_success_url(self):
        return reverse('web:list_company')

class DeleteCompany(SuccessMessageMixin, LoginRequiredMixin, generic.DeleteView):
    model = Company
    form_class = CompanyForm
    template_name = 'delete_company.html'
    success_url = reverse_lazy('web:list_company')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.soft_delete()
        messages.success(
            self.request, '「{}」を削除しました'.format(self.object))
        return HttpResponseRedirect(self.get_success_url())

class CreateInvoiceEntity(SuccessMessageMixin, LoginRequiredMixin, generic.CreateView):
    template_name = "create_invoice_entity.html"
    form_class = InvoiceEntityForm
    success_message = '登録情報を更新しました'
    def get_success_url(self):
        return reverse('web:list_invoice_entity')
    def form_valid(self, form):
        instance = form.save()
        if instance.registered_by == None:
            instance.registered_by = self.request.user
        instance.updated_by = self.request.user 
        instance.save()
        self.object = instance

        # do somet  hing with self.object
        # remember the import: from django.http import HttpResponseRedirect
        return HttpResponseRedirect(self.get_success_url())

class ListInvoiceEntity(SuccessMessageMixin, LoginRequiredMixin, generic.ListView):
    model = InvoiceEntity
    template_name = 'list_invoice_entity.html'
    paginate_by = 10  #and that's it !!
    def get_queryset(self):
        data = InvoiceEntity.objects.filter(deleted = False)
        key_corporate_number = "corporate_number"
        key_company_name = "company_name"
        key_phone_number = "phone_number"
        key_invoice_id = "invoice_id"

        if key_corporate_number in self.request.GET and self.request.GET.get(key_corporate_number) != None:
            q = self.request.GET.get(key_corporate_number)
            data = data.filter(company__corporate_number__icontains = q)
        
        if key_company_name in self.request.GET and self.request.GET.get(key_company_name) != None:
            q = self.request.GET.get(key_company_name)
            data = data.filter(Q(invoice_company_name__icontains = q) | Q(company__kanji_name__icontains = q))

        if key_phone_number in self.request.GET and self.request.GET.get(key_phone_number) != None:
            q = self.request.GET.get(key_phone_number)
            data = data.filter(Q(company__telephone_1__icontains = q) | Q(company__telephone_2__icontains = q))
    
        return data

class UpdateInvoiceEntity(SuccessMessageMixin, LoginRequiredMixin, generic.UpdateView):
    model = InvoiceEntity
    form_class = InvoiceEntityForm
    template_name = 'update_invoice_entity.html'
    success_message = '登録情報を更新しました'

    def get_success_url(self):
        return reverse('web:list_invoice_entity')

class DeleteInvoiceEntity(SuccessMessageMixin, LoginRequiredMixin, generic.DeleteView):
    model = InvoiceEntity
    form_class = InvoiceEntityForm
    template_name = 'delete_invoice_entity.html'
    success_url = reverse_lazy('web:list_invoice_entity')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.soft_delete()
        messages.success(
            self.request, '「{}」を削除しました'.format(self.object))
        return HttpResponseRedirect(self.get_success_url())

class CreateInvoiceDetail(SuccessMessageMixin, LoginRequiredMixin, generic.CreateView):
    template_name = "create_invoice_detail.html"
    form_class = InvoiceDetailForm
    success_message = '登録情報を更新しました'
    def get_success_url(self):
        return reverse('web:list_invoice_detail')
    def form_valid(self, form):
        instance = form.save()
        if instance.registered_by == None:
            instance.registered_by = self.request.user
        instance.updated_by = self.request.user 
        instance.save()
        self.object = instance

        # do somet  hing with self.object
        # remember the import: from django.http import HttpResponseRedirect
        return HttpResponseRedirect(self.get_success_url())

class ListInvoiceDetail(SuccessMessageMixin, LoginRequiredMixin, generic.ListView):
    model = InvoiceDetail
    template_name = 'list_invoice_detail.html'
    paginate_by = 10  #and that's it !!
    def get_queryset(self):
        data = InvoiceDetail.objects.filter(deleted = False)

        key_corporate_number = "corporate_number"
        key_company_name = "company_name"
        key_phone_number = "phone_number"
        key_invoice_id = "invoice_id"

        if key_corporate_number in self.request.GET and self.request.GET.get(key_corporate_number) != "":
            q = self.request.GET.get(key_corporate_number)
            data = data.filter(invoice_entity__company__corporate_number__icontains = q)
        
        if key_company_name in self.request.GET and self.request.GET.get(key_company_name) != "":
            q = self.request.GET.get(key_company_name)
            data = data.filter(Q(invoice_entity__invoice_company_name__icontains = q) | Q(invoice_entity__company__kanji_name__icontains = q))

        if key_phone_number in self.request.GET and self.request.GET.get(key_phone_number) != "":
            q = self.request.GET.get(key_phone_number)
            data = data.filter(Q(invoice_entity__company__telephone_1__icontains = q) | Q(invoice_entity__company__telephone_2__icontains = q))

        if key_invoice_id in self.request.GET and self.request.GET.get(key_invoice_id) != "":
            q = self.request.GET.get(key_invoice_id)
            data = data.filter(invoice_id__icontains = q)

        
        return data

class UpdateInvoiceDetail(SuccessMessageMixin, LoginRequiredMixin, generic.UpdateView):
    model = InvoiceDetail
    form_class = InvoiceDetailForm
    template_name = 'update_invoice_detail.html'
    success_message = '登録情報を更新しました'

    def get_success_url(self):
        return reverse('web:list_invoice_detail')

class DeleteInvoiceDetail(SuccessMessageMixin, LoginRequiredMixin, generic.DeleteView):
    model = InvoiceDetail
    form_class = InvoiceDetailForm
    template_name = 'delete_invoice_detail.html'
    success_url = reverse_lazy('web:list_invoice_detail')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.soft_delete()
        messages.success(
            self.request, '「{}」を削除しました'.format(self.object))
        return HttpResponseRedirect(self.get_success_url())

class ListInvoice(SuccessMessageMixin, LoginRequiredMixin, generic.ListView):
    model = Invoice
    template_name = 'list_invoice.html'
    paginate_by = 10  #and that's it !!
    def get_queryset(self):
        data = Invoice.objects.filter(deleted = False)
        key_corporate_number = "corporate_number"
        key_company_name = "company_name"
        key_phone_number = "phone_number"
        key_invoice_id = "invoice_id"

        if key_corporate_number in self.request.GET and self.request.GET.get(key_corporate_number) != "":
            q = self.request.GET.get(key_corporate_number)
            data = data.filter(invoice_entity__company__corporate_number__icontains = q)
        
        if key_company_name in self.request.GET and self.request.GET.get(key_company_name) != "":
            q = self.request.GET.get(key_company_name)
            data = data.filter(Q(invoice_entity__invoice_company_name__icontains = q) | Q(invoice_entity__company__kanji_name__icontains = q))

        if key_phone_number in self.request.GET and self.request.GET.get(key_phone_number) != "":
            q = self.request.GET.get(key_phone_number)
            data = data.filter(Q(invoice_entity__company__telephone_1__icontains = q) | Q(invoice_entity__company__telephone_2__icontains = q))

        if key_invoice_id in self.request.GET and self.request.GET.get(key_invoice_id) != "":
            q = self.request.GET.get(key_invoice_id)
            data = data.filter(invoice_id__icontains = q)

        return data

def add_to_invoice(request):
    if request.method == 'POST':
        if 'pk' in request.POST and request.POST.get('pk') != None:
            
            detail = InvoiceDetail.objects.get(pk = request.POST.get('pk'))
            
            exist = Invoice.objects.filter(invoice_id = detail.invoice_id)
            if len(exist) == 0:
                new = Invoice(invoice_id = detail.invoice_id)
                new.registered_by = request.user
                new.updated_by = request.user
                new.save()
            return JsonResponse({'success': True})

            

class Search(LoginRequiredMixin, generic.TemplateView):
    template_name = 'search_form.html'

class UploadFile(SuccessMessageMixin, LoginRequiredMixin, generic.FormView):
    form_class = FileUploadForm
    template_name = 'import_csv.html'

    def form_valid(self, form):
        file_name = form.save()

        with open('media/' + file_name, 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                print(len(row))
                print(row[1])
                print(row[2])
                print(row[3])
                
        
        context = {
            'file_name': file_name,
            'form': form,
            
        }
        return self.render_to_response(context)



def pdf(request, pk):
    instance = Invoice.objects.get(pk = pk)
    bank = BankInfo.get_bank_info()

    ourinfo = {
        'zip': '111-1111',
        'address_1': 'xxxxx',
        'address_2': 'yyyyy',
        'phone': 'eeeeee'
    }

    bank_info = {
        'bank': bank.bank,
        'branch': bank.branch,
        'type': bank.type,
        'number': bank.number,
        'meigi': bank.meigi
    }

    context = {
        'object': instance,
        'bank': bank_info,
        'ourinfo': ourinfo,
        'pad_range': range(14 - len(instance.details.all())),
        'details_count': len(instance.details.all())
    }
    html_template = render_to_string('pdf/invoice.html', context)

    options = {
        'page-size': 'Letter',
        'encoding': "UTF-8",
        'javascript-delay':'1000'
    }

    pdf = pdfkit.from_string(html_template, False, options)

    instance.pdf.save(str(instance.pk) + '.pdf', ContentFile(pdf))
    instance.save()
    
    response = HttpResponse(pdf, content_type='application/pdf')
    return response

  