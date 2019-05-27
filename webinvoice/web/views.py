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
    paginate_by = 10  #and that's it !!
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
        for c in entities_to_delete:
            c.soft_delete()
        
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
    paginate_by = 10  #and that's it !!
    def get_queryset(self):
        data = InvoiceDetail.objects.filter(deleted = False)

        key_corporate_number = "corporate_number"
        key_company_name = "company_name"
        key_phone_number = "phone_number"
        key_invoice_code = "invoice_code"

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
        ctx['selected_details'] = Company.objects.filter(pk__in = selected_details)
        return ctx
    def post(self, request, *args, **kwargs):
        selected_details = self.request.POST.getlist('selected_entities')
        details_to_delete = InvoiceDetail.objects.filter(pk__in = selected_details)
        for c in details_to_delete:
            c.soft_delete()
        
        messages.success(
            self.request, '{} 件削除しました'.format(len(details_to_delete)))
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
            try:
                id = row['企業ID']
                if id == '':
                    c = Company(registered_by = self.request.user, updated_by = self.request.user)
                else:
                    c = Company.objects.get(pk = id)
                    c.updated_by = self.request.user

                c.corporate_number = row['法人番号']
                c.kana_name = row['契約者名カナ']
                c.kanji_name = row['契約者名']
                c.zip = row['契約者郵便番号']
                c.address_pref = row['契約者都道府県']
                c.address_city = row['契約者市区町村']
                c.address_street = row['契約者住所番地以降']
                c.address_bld = row['契約者住所建物名']
                c.telephone_1 = row['連絡先電話番号1']
                c.telephone_2 = row['連絡先電話番号2']
                c.fax = row['FAX番号']
                c.hp_url = row['URL']
                c.owner_name = row['代表者名']
                c.representative_name = row['担当者名']
                c.email = row['メールアドレス']
                c.note = row['備考']
                c.save()
            except Exception as e:
                print(str(e.args))
                err = UploadedFileError()
                err.file = obj
                err.row_index = index + 1
                err.error = str(e.args)
                err.save()
        c.save()

        context = {
            'file': obj,
            'form': form, 
        }
        return self.render_to_response(context)
class UploadInvoiceEntityExcel(SuccessMessageMixin, LoginRequiredMixin, generic.FormView):
    form_class = InvoiceEntityExcelForm
    template_name = 'import_invoice_entity_excel.html'

    def form_valid(self, form):
        obj = form.save()
        obj.type = UploadedFile.TYPE_ENTITY

        d = pd.read_excel(obj.file.path, dtype=str) 
        df = d.fillna('')
        obj.record_count = len(df)
        obj.save()
        for index, row in df.iterrows():
            try:
                entity = InvoiceEntity()
                c = Company.objects.get(corporate_number = row['法人番号'])
                entity.company = c
                entity.invoice_zip = row['請求郵便番号']
                entity.invoice_address_pref = row['請求都道府県']
                entity.invoice_address_city = row['請求市区町村']
                entity.invoice_address_street = row['請求住所番地以降']
                entity.invoice_address_bld = row['請求住所建物名']
                entity.invoice_company_name = row['請求会社名']
                entity.invoice_dept = row['請求所属部署']
                entity.invoice_person = row['請求宛名']
                entity.invoice_project_1 = row['請求宛名1']
                entity.invoice_project_2 = row['請求宛名2']
                entity.invoice_project_3 = row['請求宛名3']
                entity.payment_method = row['支払方法']
                entity.invoice_closed_at = row['締日']
                entity.payment_due_to = row['支払期日']
                entity.invoice_sent_at = row['送付タイミング']
                entity.invoice_timing = row['請求タイミング']
                entity.invoice_period = row['請求周期']
                entity.bank_name = row['振込銀行名']
                entity.bank_banch_name = row['振込支店名']
                entity.bank_account_type = row['振込普通/当座']
                entity.bank_account_number = row['振込銀行口座番号']
                entity.credit_card_settlement_company = row['クレカ決済会社']
                entity.credit_card_code = row['クレカコード']
                entity.credit_card_id = row['クレカID']
                entity.settlement_company = row['決済会社']
                entity.settlement_code = row['決済コード']
                entity.settlement_id = row['決済ID']
                entity.note = row['備考']
                entity.registered_by = self.request.user
                entity.updated_by = self.request.user
                entity.save()
            except Exception as e:
                print(str(e.args))
                err = UploadedFileError()
                err.file = obj
                err.row_index = index + 1
                err.error = str(e.args)
                err.save()
        context = {
            'file': obj,
            'form': form,
            
        }
        return self.render_to_response(context)
class UploadInvoiceDetailExcel(SuccessMessageMixin, LoginRequiredMixin, generic.FormView):
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
            try:
                detail = InvoiceDetail()
                entity = InvoiceEntity.objects.get(pk = row['請求管理簿ID'])
                detail.invoice_entity = entity
                detail.product_category_1 = row['商品大区分']
                detail.product_category_2 = row['商品小区分']
                detail.yearmonth = row['請求月']
                detail.seq_number = row['SEQNO']
                detail.order_number = row['申込管理番号']
                detail.invoice_code = row['請求書ID']
                detail.service_start_date = row['サービス開始日']
                detail.service_name = row['サービス明細内容']
                detail.invoice_amount_wo_tax = row['請求金額（税抜）']
                detail.tax_type = row['税区分']
                detail.tax_rate_perc = row['税率'].replace('%', '')
                detail.tax_amount = row['請求金額（税額）']
                #detail.invoice_amount_w_tax = row['請求金額（税込合計）']
                detail.note = row['備考']
                detail.registered_by = self.request.user
                detail.updated_by = self.request.user
                detail.save()
            except Exception as e:
                print(str(e.args))
                err = UploadedFileError()
                err.file = obj
                err.row_index = index + 1
                err.error = str(e.args)
                err.save()
        context = {
            'file': obj,
            'form': form,
            
        }
        return self.render_to_response(context)



def pdf(request, pk):
    instance = Invoice.objects.get(pk = pk)
    bank = BankInfo.get_bank_info()
    ourinfo = OurInfo.get_ourinfo()

    ourinfo = {
        'zip': ourinfo.zip,
        'address_1': ourinfo.address_1,
        'address_2': ourinfo.address_2,
        'phone': ourinfo.phone
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
    paginate_by = 10  #and that's it !!
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

    def post(self, request, *args, **kwargs):
        obj_to_update = request.POST.get('obj_to_update')
        vision_phone = request.POST.get('phone')
        zip = request.POST.get('zip')
        address_1 = request.POST.get('address_1')
        address_2 = request.POST.get('address_2')
        company = request.POST.get('company')
        person = request.POST.get('person')
        dept = request.POST.get('dept')
        project = request.POST.get('project')
        date_created = request.POST.get('date_created')
        customerNo = InvoiceEntity.PREFIX + request.POST.get('customerNo')
        invoiceNo = Invoice.PREFIX + request.POST.get('invoiceNo')
        invoice_total = request.POST.get('total')
        
        dueDate = request.POST.get('due_date')

        total_wo_tax = request.POST.get('total_wo_tax')
        total_tax = request.POST.get('total_tax')
        total_w_tax = request.POST.get('total_w_tax')
        
        if obj_to_update != None and obj_to_update != "":
            new = HandWrittenInvoice.objects.get(pk = obj_to_update)
        else:
            new = HandWrittenInvoice()
        new.id = invoiceNo
        new.customer_id = customerNo
        new.vision_phone_number = vision_phone
        new.zip = zip
        new.address_1 = address_1
        new.address_2 = address_2
        new.company_name = company
        new.dept = dept
        new.person = person
        new.project = project
        new.date_created = date_created
        new.total = invoice_total
        new.total_wo_tax = total_wo_tax
        new.total_tax = total_tax
        new.total_w_tax = total_w_tax
        new.due_date = dueDate
        new.create_user = request.user
        new.save()        

        for i in range(1, 15):
            row = i
            yearmonth = request.POST.get("yearmonth_" + str(i))
            category = request.POST.get("category_" + str(i))
            service_name = request.POST.get("service_name_" + str(i))
            amount = request.POST.get("amount_" + str(i))
            unit_price = request.POST.get("unit_price_" + str(i))
            tax_type = request.POST.get("tax_type_" + str(i))
            invoice_amount_wo_tax = request.POST.get("invoice_amount_wo_tax_" + str(i))
            tax_amount = request.POST.get("tax_amount_" + str(i))
            invoice_amount_w_tax = request.POST.get("invoice_amount_w_tax_" + str(i))
            
            if obj_to_update != None and obj_to_update != "":
                new_detail = HandWrittenInvoiceDetail.objects.get(parent = new, row_no = row)
            else:
                new_detail = HandWrittenInvoiceDetail()
            new_detail.row_no = row
            new_detail.parent = new
            
            if yearmonth != None and yearmonth != '':    
                new_detail.yearmonth = yearmonth
                new_detail.product_category = category
                new_detail.product_name = service_name
                new_detail.amount = amount
                new_detail.unit_price = unit_price
                new_detail.tax_type = tax_type
                new_detail.total_wo_tax = invoice_amount_wo_tax
                new_detail.tax_price = tax_amount
                new_detail.total_w_tax = invoice_amount_w_tax
            new_detail.save()
        if obj_to_update != None and obj_to_update != "":
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


