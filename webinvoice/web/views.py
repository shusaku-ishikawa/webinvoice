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
import pandas as pd
import re

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
        key_invoice_code = "invoice_code"

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

class DeleteCompany(SuccessMessageMixin, LoginRequiredMixin, generic.TemplateView):
    template_name = 'delete_company.html'

    def get_success_url(self):
        return reverse('web:list_company')
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        selected_companies = self.request.GET.getlist('selected_companies')
        ctx['selected_companies'] = Company.objects.filter(pk__in = selected_companies)
        return ctx
    def post(self, request, *args, **kwargs):
        selected_companies = self.request.POST.getlist('selected_companies')
        companies_to_delete = Company.objects.filter(pk__in = selected_companies)
        for c in companies_to_delete:
            c.soft_delete()
        
        messages.success(
            self.request, '{} 件削除しました'.format(len(companies_to_delete)))
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
    paginate_by = 50  #and that's it !!
    def get_queryset(self):
        data = InvoiceEntity.objects.filter(deleted = False)
        key_corporate_number = "corporate_number"
        key_company_name = "company_name"
        key_phone_number = "phone_number"
        key_invoice_code = "invoice_code"

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

class DeleteInvoiceEntity(SuccessMessageMixin, LoginRequiredMixin, generic.TemplateView):
    template_name = 'delete_invoice_entity.html'

    def get_success_url(self):
        return reverse('web:list_invoice_entity')
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        selected_entities = self.request.GET.getlist('selected_entities')
        ctx['selected_entities'] = InvoiceEntity.objects.filter(pk__in = selected_entities)
        return ctx
    def post(self, request, *args, **kwargs):
        selected_entities = self.request.POST.getlist('selected_entities')
        entities_to_delete = InvoiceEntity.objects.filter(pk__in = selected_entities)
        for e in entities_to_delete:
            e.soft_delete()
        
        messages.success(
            self.request, '{} 件削除しました'.format(len(entities_to_delete)))
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
    paginate_by = 50  #and that's it !!
    def get_queryset(self):
        data = InvoiceDetail.objects.filter(deleted = False)

        key_corporate_number = "corporate_number"
        key_company_name = "company_name"
        key_phone_number = "phone_number"
        key_invoice_code = "invoice_code"
        key_is_invoiced = "is_invoiced"

        if key_corporate_number in self.request.GET and self.request.GET.get(key_corporate_number) != "":
            q = self.request.GET.get(key_corporate_number)
            data = data.filter(invoice_entity__company__corporate_number__icontains = q)
        
        if key_company_name in self.request.GET and self.request.GET.get(key_company_name) != "":
            q = self.request.GET.get(key_company_name)
            data = data.filter(Q(invoice_entity__invoice_company_name__icontains = q) | Q(invoice_entity__company__kanji_name__icontains = q))

        if key_phone_number in self.request.GET and self.request.GET.get(key_phone_number) != "":
            q = self.request.GET.get(key_phone_number)
            data = data.filter(Q(invoice_entity__company__telephone_1__icontains = q) | Q(invoice_entity__company__telephone_2__icontains = q))

        if key_invoice_code in self.request.GET and self.request.GET.get(key_invoice_code) != "":
            q = self.request.GET.get(key_invoice_code)
            data = data.filter(invoice_code__icontains = q)
        
        if key_is_invoiced in self.request.GET and self.request.GET.get(key_is_invoiced) != "":
            q = self.request.GET.get(key_is_invoiced)
            if q == 'y':
                data = data.filter(invoice__isnull = False)
            elif q == 'n':
                data = data.filter(invoice__isnull = True)
        
        
        return data

class UpdateInvoiceDetail(SuccessMessageMixin, LoginRequiredMixin, generic.UpdateView):
    model = InvoiceDetail
    form_class = InvoiceDetailForm
    template_name = 'update_invoice_detail.html'
    success_message = '登録情報を更新しました'

    def get_success_url(self):
        return reverse('web:list_invoice_detail')

class DeleteInvoiceDetail(SuccessMessageMixin, LoginRequiredMixin, generic.TemplateView):
    template_name = 'delete_invoice_detail.html'

    def get_success_url(self):
        return reverse('web:list_invoice_detail')
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        selected_details = self.request.GET.getlist('selected_details')
        ctx['selected_details'] = InvoiceDetail.objects.filter(pk__in = selected_details)
        return ctx
    def post(self, request, *args, **kwargs):
        selected_details = self.request.POST.getlist('selected_details')
        details_to_delete = InvoiceDetail.objects.filter(pk__in = selected_details)
        for d in details_to_delete:
            d.soft_delete()
        
        messages.success(
            self.request, '{} 件削除しました'.format(len(details_to_delete)))
        return HttpResponseRedirect(self.get_success_url())  

class ListInvoice(SuccessMessageMixin, LoginRequiredMixin, generic.ListView):
    model = Invoice
    template_name = 'list_invoice.html'
    paginate_by = 10  #and that's it !!
    def get_queryset(self):
        data = Invoice.objects.all()
        key_corporate_number = "corporate_number"
        key_company_name = "company_name"
        key_phone_number = "phone_number"
        key_invoice_code = "invoice_code"
        key_invoice_pk = "invoice_pk"

        if key_corporate_number in self.request.GET and self.request.GET.get(key_corporate_number) != "":
            q = self.request.GET.get(key_corporate_number)
            data = data.filter(invoice_entity__company__corporate_number__icontains = q)
        
        if key_company_name in self.request.GET and self.request.GET.get(key_company_name) != "":
            q = self.request.GET.get(key_company_name)
            data = data.filter(Q(invoice_entity__invoice_company_name__icontains = q) | Q(invoice_entity__company__kanji_name__icontains = q))

        if key_phone_number in self.request.GET and self.request.GET.get(key_phone_number) != "":
            q = self.request.GET.get(key_phone_number)
            data = data.filter(Q(invoice_entity__company__telephone_1__icontains = q) | Q(invoice_entity__company__telephone_2__icontains = q))

        if key_invoice_code in self.request.GET and self.request.GET.get(key_invoice_code) != "":
            q = self.request.GET.get(key_invoice_code)
            data = data.filter(invoice_code__icontains = q)
           
        if key_invoice_pk in self.request.GET and self.request.GET.get(key_invoice_pk) != "":
            q = self.request.GET.get(key_invoice_pk)
            data = data.filter(invoice_pk = q)

        return data

class DeleteInvoice(SuccessMessageMixin, LoginRequiredMixin, generic.TemplateView):
    template_name = 'delete_invoice.html'

    def get_success_url(self):
        return reverse('web:list_invoice')
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        selected_invoices = self.request.GET.getlist('selected_invoices')
        ctx['selected_invoices'] = Invoice.objects.filter(pk__in = selected_invoices)
        return ctx
    def post(self, request, *args, **kwargs):
        selected_invoices = self.request.POST.getlist('selected_invoices')
        invoices_to_delete = Invoice.objects.filter(pk__in = selected_invoices)
        for i in invoices_to_delete:
            i.delete()
        
        messages.success(
            self.request, '{} 件削除しました'.format(len(invoices_to_delete)))
        return HttpResponseRedirect(self.get_success_url())  

def add_to_invoice(request):
    if request.method == 'POST':
        if 'pk' in request.POST and request.POST.get('pk') != None:
            
            detail = InvoiceDetail.objects.get(pk = request.POST.get('pk'))
            
            exist = Invoice.objects.filter(invoice_code = detail.invoice_code)
            if len(exist) == 0:
                new = Invoice(invoice_code = detail.invoice_code)
                new.registered_by = request.user
                new.updated_by = request.user
                new.save()
            return JsonResponse({'success': True})

            

class Search(LoginRequiredMixin, generic.TemplateView):
    template_name = 'search_form.html'



class UploadCompanyExcel(SuccessMessageMixin, LoginRequiredMixin, generic.FormView):
    
    columns = [
        'id',
        'corporate_number',
        'kana_name',
        'kanji_name',
        'zip',
        'address_pref',
        'address_city',
        'address_street',
        'address_bld',
        'telephone_1',
        'telephone_2',
        'fax', 
        'hp_url',
        'owner_name',
        'representative_name',
        'email',
        # 'note', '備考')
    ]
    form_class = CompanyExcelForm
    template_name = 'import_company_excel.html'

    def form_valid(self, form):
        obj = form.save()
        obj.type = UploadedFile.TYPE_COMPANY

        d = pd.read_excel(obj.file.path, dtype=str) 
        df = d.fillna('')
        obj.record_count = len(df)
        obj.save()

        for index, row in df.iterrows():
            # 項目数チェック
            if len(row) != len(self.columns):
                err = UploadedFileError()
                err.file = obj
                err.row_index = index + 1
                err.error = '項目数が不正です'
                err.save()
                continue
            param_dict = {}
            for col_index in range(len(self.columns)):
                param_dict[self.columns[col_index]] = row[col_index]

            id = row[0]
            try:
                c = Company.objects.get(pk = id)
            except Company.DoesNotExist:
                f  = CompanyForm(param_dict)
            else:
                    f = CompanyForm(param_dict, instance = c)
            if f.is_valid():
                c = f.save()
                c.registered_by = self.request.user
                c.updated_by = self.request.user
                c.save()
            else:
                for key in f.errors.as_data():
                    print(key)
                    #print(f.errors[key].as_data())
                    for error in f.errors[key].as_data():
                        print(str(error))
                        err = UploadedFileError()
                        err.file = obj
                        err.row_index = index + 1
                        err.error = key + ': ' + str(error)
                        err.save()
                

        context = {
            'file': obj,
            'form': form, 
        }
        return self.render_to_response(context)
class UploadInvoiceEntityExcel(SuccessMessageMixin, LoginRequiredMixin, generic.FormView):
    columns = [
        'id',
        'company',
        'dammy',
        'dammy',
        'dammy',
        'dammy',
        'dammy',
        'dammy',
        'dammy',
        'invoice_zip',
        'invoice_address_pref',
        'invoice_address_city',
        'invoice_address_street',
        'invoice_address_bld',
        'invoice_company_name',
        'invoice_dept',
        'invoice_person',
        'invoice_project_1',
        'invoice_project_2',
        'invoice_project_3',
        'payment_method',
        'invoice_closed_at',
        'payment_due_to',
        'invoice_sent_at',
        'invoice_timing',
        'invoice_period',
        'bank_name',
        'bank_banch_name',
        'bank_account_type',
        'bank_account_number',
        'credit_card_settlement_company',
        'credit_card_code',
        'credit_card_id',
        'settlement_company',
        'settlement_code',
        'settlement_id',
    ]
    
    form_class = InvoiceEntityExcelForm
    template_name = 'import_invoice_entity_excel.html'

    def form_valid(self, form):
        obj = form.save()
        obj.type = UploadedFile.TYPE_ENTITY

        d = pd.read_excel(obj.file.path, dtype=str) 
        df = d.fillna('')
        obj.record_count = len(df)
        obj.save()
        print(len(df))
        for index, row in df.iterrows():
            # 項目数チェック
            if len(row) != len(self.columns):
                err = UploadedFileError()
                err.file = obj
                err.row_index = index + 1
                err.error = '項目数が不正です'
                err.save()
                continue
            param_dict = {}
            for col_index in range(len(self.columns)):
                key = self.columns[col_index]
                if key == 'payment_due_to':
                    param_dict[key] = row[col_index].split(' ')[0]
                    print(param_dict[key])
                else:
                    param_dict[key] = row[col_index]

            id = row[0]
           
            try:
                ie = InvoiceEntity.objects.get(pk = id)
            except InvoiceEntity.DoesNotExist:
                f = InvoiceEntityForm(param_dict)
            else:
                f = InvoiceEntityForm(param_dict, instance = ie)

            if f.is_valid():
                ie = f.save()
                ie.registered_by = self.request.user
                ie.updated_by = self.request.user
                ie.save()
            else:
                for key in f.errors.as_data():
                    for error in f.errors[key].as_data():
                        print(str(error))
                        err = UploadedFileError()
                        err.file = obj
                        err.row_index = index + 1
                        err.error = key + ': ' + str(error)
                        err.save()

        context = {
            'file': obj,
            'form': form,
            
        }
        return self.render_to_response(context)
class UploadInvoiceDetailExcel(SuccessMessageMixin, LoginRequiredMixin, generic.FormView):
    
    columns = [
        'id',
        'invoice_entity',
        'product_category_1',
        'product_category_2',
        'yearmonth',
        'seq_number',
        'order_number',
        'invoice_code',
        'service_start_date',
        'service_name',
        'invoice_amount_wo_tax',
        'tax_type',
        'tax_rate_perc',
        'tax_amount',
    ]

    form_class = InvoiceDetailExcelForm
    template_name = 'import_invoice_detail_excel.html'

    def form_valid(self, form):
        obj = form.save()
        obj.type = UploadedFile.TYPE_DETAIL

        d = pd.read_excel(obj.file.path, dtype=str) 
        df = d.fillna('')
        obj.record_count = len(df)
        obj.save()
        for index, row in df.iterrows():
            # 項目数チェック
            if len(row) != len(self.columns):
                err = UploadedFileError()
                err.file = obj
                err.row_index = index + 1
                err.error = '項目数が不正です'
                err.save()
                continue
            param_dict = {}
            for col_index in range(len(self.columns)):
                key = self.columns[col_index]
                if key == 'tax_rate_perc':
                    param_dict[key] = float(row[col_index]) * 100
                    print(row[col_index] * 100)
                elif key == 'service_start_date':
                    
                    if len(row[col_index].split(' ')) > 1:
                        param_dict[key] = row[col_index].split(' ')[0]
                    else:
                        param_dict[key] = row[col_index].replace('/', '-')
                else:
                    param_dict[key] = row[col_index]

            try:
                ide = InvoiceDetail.objects.get(pk = id)
            except InvoiceDetail.DoesNotExist:
                f = InvoiceDetailForm(param_dict)
            else:
                f = InvoiceDetailForm(param_dict, instance = ide)
            if f.is_valid():
                ide = f.save()
                ide.registered_by = self.request.user
                ide.updated_by = self.request.user
                ide.save()
              
            else:
                
                for key in f.errors.as_data():
                    for error in f.errors[key].as_data():
                        print(str(error))
                        err = UploadedFileError()
                        err.file = obj
                        err.row_index = index + 1
                        err.error = key + ': ' + str(error)
                        err.save()
                        print('after err save')
        context = {
            'file': obj,
            'form': form,
            
        }
        return self.render_to_response(context)



def pdf(request):
    selected_invoices = request.GET.getlist('selected_invoices')

    instances = Invoice.objects.filter(id__in = selected_invoices)
    print(instances)
    bank_info = BankInfo.get_bank_info()
    our_info = OurInfo.get_ourinfo()


    context = {
        'object_list': instances,
        'bank': bank_info,
        'ourinfo': our_info,
    }
    html_template = render_to_string('pdf/invoice.html', context)

    options = {
        'page-size': 'Letter',
        'encoding': "UTF-8",
    }

    pdf = pdfkit.from_string(html_template, False, options)

    response = HttpResponse(pdf, content_type='application/pdf')
    return response

def pdf_handwritten(request, pk):
    instance = HandWrittenInvoice.objects.get(pk = pk)
    bank = BankInfo.get_bank_info()
    ourinfo = OurInfo.get_ourinfo()

    ourinfo = {
        'zip': ourinfo.zip,
        'address_1': ourinfo.address_1,
        'address_2': ourinfo.address_2,
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
    }
    html_template = render_to_string('pdf/invoice-handwritten.html', context)

    options = {
        'page-size': 'Letter',
        'encoding': "UTF-8",
        
    }

    pdf = pdfkit.from_string(html_template, False, options)
    
    response = HttpResponse(pdf, content_type='application/pdf')
    return response

class CompanyExcelUploadHistor(SuccessMessageMixin, LoginRequiredMixin, generic.ListView):
    model = UploadedFile
    template_name = 'list_upload_company.html'
    paginate_by = 50  #and that's it !!
    def get_queryset(self):
        data = UploadedFile.objects.filter(type = UploadedFile.TYPE_COMPANY)
        return data

class EntityExcelUploadHistor(SuccessMessageMixin, LoginRequiredMixin, generic.ListView):
    model = UploadedFile
    template_name = 'list_upload_entity.html'
    paginate_by = 10  #and that's it !!
    def get_queryset(self):
        data = UploadedFile.objects.filter(type = UploadedFile.TYPE_ENTITY)
        return data

class DetailExcelUploadHistor(SuccessMessageMixin, LoginRequiredMixin, generic.ListView):
    model = UploadedFile
    template_name = 'list_upload_detail.html'
    paginate_by = 10  #and that's it !!
    def get_queryset(self):
        data = UploadedFile.objects.filter(type = UploadedFile.TYPE_DETAIL)
        return data

def create_invoice_bulk(request):
    not_yet_invoiced = InvoiceDetail.objects.filter(invoice__isnull = True)
    add_count = 0
    modify_count= 0

    for d in not_yet_invoiced:
        try:
            invoice = Invoice.objects.get(id = d.invoice_code)
            invoice.updated_by = request.user
            invoice.save()
            modify_count = modify_count + 1
        except Exception:
            invoice = Invoice(id = d.invoice_code, registered_by = request.user)
            invoice.save()
            add_count = add_count + 1

        d.invoice = invoice
        d.updated_by = request.user
        d.save()

    messages.success(request, "{} 件 新規作成 {} 件 修正しました".format(add_count, modify_count))
    return HttpResponseRedirect(reverse_lazy('web:list_invoice'))

        


class CreateHandwrittenInvoice(LoginRequiredMixin, generic.TemplateView):
    template_name = 'create_handwritten_invoice.html'
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        bank = BankInfo.get_bank_info()
        ourinfo = OurInfo.get_ourinfo()
        ctx['bank'] = bank
        ctx['ourinfo'] = ourinfo
        ctx['rec_per_page'] = range(14)
        return ctx

    def get_success_url(self):
        return reverse_lazy('web:list_handwritten_invoice')
    def get_update_error_url(self, pk):
        return reverse_lazy('web:update_handwritten_invoice', kwargs={'pk': pk},)
    def get_create_error_url(self):
        return reverse_lazy('web:create_handwritten_invoice')

    def post(self, request, *args, **kwargs):
        f = HandWrittenInvoiceForm()
        params = {}

        for field in f.fields:
            if field == 'id':
                params[field] = Invoice.PREFIX + request.POST.get(field)
                print(params[field])
            elif field == 'customer_id':
                params[field] = InvoiceEntity.PREFIX + request.POST.get(field)
            else:
                params[field] = request.POST.get(field)
        params['create_user'] = request.user.id

        obj_id = request.POST.get('obj_to_update')
        print(obj_id)

        is_update_mode = False
        if obj_id == None:
            f = HandWrittenInvoiceForm(params) 
        else:
            is_update_mode = True
            #del params['id']
            obj = HandWrittenInvoice(pk = obj_id)
            f = HandWrittenInvoiceUpdateForm(params, instance = obj)
           
        if f.is_valid():
            parent = f.save()
        else:
            for key in f.errors.as_data():
                print(key)
                for error in f.errors[key].as_data():
                    messages.error(
                        self.request, '項目に不備がありました。' + str(error))
            if is_update_mode:
                return HttpResponseRedirect(self.get_update_error_url(obj_id))  
            else:  
                return HttpResponseRedirect(self.get_create_error_url())  
        errlist = []
        for i in range(1, 15):
            params = {}
            f = HandWrittenInvoiceDetailForm()

            for field in f.fields:
                print(field)
                print(request.POST)
                print(request.POST.get(field + '_' + str(i)))
                params[field] = request.POST.get(field + '_' + str(i))
            params['row_no'] = i
            params['parent'] = parent.pk
            
            print('parent id = ' + str(parent))

            if is_update_mode:
                obj = HandWrittenInvoiceDetail.objects.get(parent = parent, row_no = i)
                f = HandWrittenInvoiceDetailForm(params, instance = obj)
            else:
                f = HandWrittenInvoiceDetailForm(params)
            
            if f.is_valid():
                f.save()
            else:
                for key in f.errors.as_data():
                    print(key)
                    for error in f.errors[key].as_data():
                        print(str(error))
                        errlist.append(str(i) + '行目:' + str(error))
        
        if len(errlist) > 0:
            for e in errlist:
                messages.error(self.request, e)
                print(e)
            if is_update_mode:
                return HttpResponseRedirect(self.get_update_error_url(parent.pk))  
            else:  
                return HttpResponseRedirect(self.get_create_error_url())  
        else:
            if is_update_mode:
                messages.success(
                    self.request, '更新が完了しました')
            else:
                messages.success(
                    self.request, '登録が完了しました')
            return HttpResponseRedirect(self.get_success_url())  

class UpdateHandwrittenInvoice(SuccessMessageMixin, LoginRequiredMixin, generic.TemplateView):
    template_name = 'create_handwritten_invoice.html'
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        bank = BankInfo.get_bank_info()
        ourinfo = OurInfo.get_ourinfo()
        ctx['bank'] = bank
        ctx['ourinfo'] = ourinfo
        ctx['rec_per_page'] = range(14)
        ctx['obj_to_update'] = HandWrittenInvoice.objects.get(pk = self.kwargs['pk'])
        
        return ctx
    
class ListHandwrittenInvoice(SuccessMessageMixin, LoginRequiredMixin, generic.ListView):
    model = HandWrittenInvoice
    template_name = 'list_handwritten_invoice.html'
    paginate_by = 10  #and that's it !!
    def get_queryset(self):
        data = HandWrittenInvoice.objects.all()
        key_customer_id = "q_costomer_id"
        key_company_name = "q_company_name"
        key_create_user = "q_create_user"
        key_date_created = "q_date_created"
        key_address = "q_address"

        if key_customer_id in self.request.GET and self.request.GET.get(key_customer_id) != "":
            q = self.request.GET.get(key_customer_id)
            data = data.filter(customer_id__icontains = q)
        
        if key_company_name in self.request.GET and self.request.GET.get(key_company_name) != "":
            q = self.request.GET.get(key_company_name)
            data = data.filter(company_name__icontains = q)

        if key_create_user in self.request.GET and self.request.GET.get(key_create_user) != "":
            q = self.request.GET.get(key_create_user)
            data = data.filter(create_user__name__icontains = q)
           
        if key_date_created in self.request.GET and self.request.GET.get(key_date_created) != "":
            q = self.request.GET.get(key_date_created)
            data = data.filter(date_created = q)

        if key_address in self.request.GET and self.request.GET.get(key_address) != "":
            q = self.request.GET.get(key_address)
            data = data.filter(Q(address_1__icontains = q) | Q(address_2__icontains = q) )
        
        return data


