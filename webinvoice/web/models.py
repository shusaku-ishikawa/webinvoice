from django import forms
from django.contrib.auth.models import User,PermissionsMixin
from django.core.mail import send_mail
from django.core.validators import MaxValueValidator, MinValueValidator,  RegexValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError
from django.conf import settings
from datetime import datetime, date, timedelta
from django.db.models import Q, Sum
from django.core.validators import FileExtensionValidator
from datetime import datetime

import re

# Create your models here.

alphanumeric = RegexValidator(r'^[0-9a-zA-Z_]*$', 'IDは英数字もしくはアンダースコア(_)のみとしてください')
def validate_postcode(value):
    reg = re.compile('^[0-9]{3}-[0-9]{4}$')
    if not reg.match(value):
        raise ValidationError(u'%s 郵便番号のフォーマットが正しくありません' % value)

def validate_phonenumber(value):
    reg = re.compile('^[0-9]*$')
    if not reg.match(value):
        raise ValidationError(u'%s 電話番号のフォーマットが正しくありません' % value)

def validate_month(value):
    reg = re.compile('^20[0-9]{2}[0-1][0-9]$')
    if not reg.match(value):
        raise ValidationError(u'%s 年月のフォーマットが正しくありません' % value)

pref_options = (
    ('東京都', '東京都'),
    ('北海道', '北海道'),
    ('秋田県', '秋田県') 
)
class Company(models.Model):
    def __str__(self):
        return self.kanji_name

    class Meta:
        verbose_name = '会社'
        verbose_name_plural = '会社'
        ordering = ['pk']

    # 法人番号
    corporate_number = models.CharField(
        verbose_name = _('法人番号'),
        max_length = 50,
        null = False,
        blank = False,
        unique = True,
        validators = [
            alphanumeric
        ]
    )
    # 契約者名カナ
    kana_name = models.CharField(
        verbose_name = "契約者名カナ",
        max_length = 50,
        null = False,
        blank = False
    )
    # 契約者名漢字
    kanji_name = models.CharField(
        verbose_name = "契約者名漢字",
        max_length = 50,
        null = False,
        blank = False
    )
    # 郵便番号
    zip = models.CharField(
        verbose_name = _('契約者郵便番号'), 
        max_length = 10,
        null = False,
        blank = False,
        validators = [
            validate_postcode,
        ]
    )

    address_pref = models.CharField(
        verbose_name = "契約者都道府県",
        max_length = 10,
        null = False,
        blank = False,
        choices = pref_options
    )
    address_city = models.CharField(
        verbose_name = "契約者市区町村",
        max_length = 30,
        null = False,
        blank = False
    )
    address_street = models.CharField(
        verbose_name = "契約者住所番地以降",
        max_length = 50,
        null = False,
        blank = False
    )
    address_bld = models.CharField(
        verbose_name = "契約者住所建物名",
        max_length = 50,
        null = False,
        blank = False
    )

    telephone_1 = models.CharField(
        verbose_name = _('連絡先電話番号1'), 
        max_length = 20,
        null = True,
        blank = True,
        validators = [
            validate_phonenumber,
        ]
    )
    telephone_2 = models.CharField(
        verbose_name = _('連絡先電話番号2'), 
        max_length = 20,
        null = True,
        blank = True,
        validators = [
            validate_phonenumber,
        ]
    )
    fax = models.CharField(
        verbose_name = _('FAX番号'), 
        max_length = 20,
        null = True,
        blank = True,
        validators = [
            validate_phonenumber,
        ]
    )
    hp_url = models.CharField(
        verbose_name = _('URL'), 
        max_length = 20,
        null = True,
        blank = True
    )
    owner_name = models.CharField(
        verbose_name = "代表者名",
        max_length = 50,
        null = False,
        blank = False
    )
    representative_name = models.CharField(
        verbose_name = "担当者名",
        max_length = 50,
        null = False,
        blank = False
    )
    email = models.EmailField(
        verbose_name = _('メール'),
        blank = True,
        null = True
    )
    note = models.TextField(
        null = True,
        blank = True
    )
    registered_at = models.DateTimeField(
        verbose_name = '登録日',
        auto_now_add = True
    )
    registered_by = models.ForeignKey(
        to = User,
        null = True,
        verbose_name = '登録者',
        on_delete = models.SET_NULL,
        related_name = 'company_registered'
    )
    updated_at = models.DateTimeField(
        verbose_name = '更新日',
        auto_now = True
    )   
    updated_by = models.ForeignKey(
        to = User,
        null = True,
        verbose_name = '更新者',
        on_delete = models.SET_NULL,
        related_name = 'company_updated'
    )
    deleted = models.BooleanField(
        verbose_name = '削除フラグ',
        default = False
    )
    def soft_delete(self):
        self.deleted = True
        self.save()

class InvoiceEntity(models.Model):
    def __str__(self):
        return self.invoice_company_name

    class Meta:
        verbose_name = '請求管理簿'
        verbose_name_plural = '請求管理簿'
        ordering = ['pk']
    company = models.ForeignKey(
        Company,
        verbose_name = '会社',
        on_delete = models.CASCADE
    )

    invoice_zip = models.CharField(
        verbose_name = _('請求郵便番号'), 
        max_length = 10,
        null = False,
        blank = False,
        validators = [
            validate_postcode,
        ]
    )

    invoice_address_pref = models.CharField(
        verbose_name = "請求都道府県",
        max_length = 10,
        null = False,
        blank = False,
        choices = pref_options
    )
    invoice_address_city = models.CharField(
        verbose_name = "請求市区町村",
        max_length = 30,
        null = False,
        blank = False
    )
    invoice_address_street = models.CharField(
        verbose_name = '請求住所番地以降',
        max_length = 50,
        null = False,
        blank = False
    )
    invoice_address_bld = models.CharField(
        verbose_name = "請求住所建物名",
        max_length = 50,
        null = False,
        blank = False
    )
    invoice_company_name = models.CharField(
        verbose_name = '請求会社名',
        max_length = 100,
        null = True,
        blank = True
    )
    inovoice_dept = models.CharField(
        verbose_name = '請求部署',
        max_length = 100,
        null = True,
        blank = True
    )
    invoice_person = models.CharField(
        verbose_name = '請求宛名',
        max_length = 50,
        null = True,
        blank = True
    )
    invoice_project_1 = models.CharField(
        verbose_name = '請求宛名1',
        max_length = 50,
        null = True,
        blank = True
    )
    invoice_project_2 = models.CharField(
        verbose_name = '請求宛名2',
        max_length = 50,
        null = True,
        blank = True
    )
    
    invoice_project_3 = models.CharField(
        verbose_name = '請求宛名3',
        max_length = 50,
        null = True,
        blank = True
    )
 
    payment_method = models.CharField(
        verbose_name = '支払い方法',
        max_length = 20,
        choices = (
            ('クレカ', 'クレカ'),
            ('引落', '引落'),
            ('振込', '振込')
        ),
        default = '振込'
    )

    invoice_closed_at = models.CharField(
        verbose_name = '締め日',
        max_length = 20,
        choices = (
            ('末日', '末日'),
            ('20日', '20日'),
        )
    )
    
    payment_due_to = models.CharField(
        verbose_name = '支払い期日',
        max_length = 20,
        choices = (
            ('末日', '末日'),
            ('20日', '20日'),
        )
    )
    
    invoice_sent_at = models.CharField(
        verbose_name = '請求書送付時期',
        max_length = 20,
        choices =  (
            ('末日', '末日'),
            ('20日', '20日'),
        )
    )
    invoice_timing = models.CharField(
        verbose_name = '請求タイミング',
        max_length = 20,
        choices = (
            ('売掛', '売掛'),
            ('前入金', '前入金'),
        )
    )
    invoice_period = models.CharField(
        verbose_name = '請求周期',
        max_length = 20,
        choices = (
            ('毎月', '毎月'),
            ('6ヶ月', '6ヶ月'),
        )
    )
    
    bank_name = models.CharField(
        verbose_name = '振込銀行名',
        max_length = 20
    )
    bank_branch_name = models.CharField(
        verbose_name = '振込支店名',
        max_length = 20
    )

    bank_account_type = models.CharField(
        verbose_name = '口座種類',
        max_length = 20,
        choices = (
            ('普通', '普通'),
            ('当座', '当座')
        )
    )

    bank_account_number = models.CharField(
        verbose_name = '口座番号',
        max_length = 20
    )
    credit_card_settlement_company = models.CharField(
        verbose_name = 'クレカ決済会社',
        max_length = 20
    )
    credit_card_code = models.CharField(
        verbose_name = 'クレカコード',
        max_length = 20
    )
    credit_card_id = models.CharField(
        verbose_name = 'クレカID',
        max_length = 20
    )
    settlement_company = models.CharField(
        verbose_name = '決済会社',
        max_length = 20
    )
    settlement_code = models.CharField(
        verbose_name = '決済コード',
        max_length = 20
    )
    settlement_id = models.CharField(
        verbose_name = '決済ID',
        max_length = 20
    )
  
    note = models.TextField(
        verbose_name = '特記事項',
        null = True,
        blank = True
    )
    registered_at = models.DateTimeField(
        verbose_name = '登録日',
        auto_now_add = True
    )
    registered_by = models.ForeignKey(
        User,
        null = True,
        verbose_name = '登録者',
        on_delete = models.SET_NULL,
        related_name = 'entity_registered'
    )
    updated_at = models.DateTimeField(
        verbose_name = '更新日',
        auto_now = True
    )   
    updated_by = models.ForeignKey(
        to = User,
        null = True,
        verbose_name = '更新者',
        on_delete = models.SET_NULL,
        related_name = 'entity_updated'
    )
    deleted = models.BooleanField(
        verbose_name = '削除フラグ',
        default = False
    )
    def soft_delete(self):
        self.deleted = True
        self.save()

class Invoice(models.Model):
    def __str__(self):
        return str(self.pk)

    class Meta:
        verbose_name = '請求書'
        verbose_name_plural = '請求書'
        ordering = ['pk']
    
    invoice_id = models.CharField(
        verbose_name = '請求書ID',
        max_length = 50,
        primary_key = True
    )

    pdf = models.FileField(
        verbose_name = '出力PDF',
        null = True,
        upload_to = 'invoice_pdf',
    )

    invoice_printed_at = models.DateField(
        verbose_name = '発行日',
        auto_now_add = True
    )
    registered_at = models.DateTimeField(
        verbose_name = '登録日',
        auto_now_add = True
    )
    registered_by = models.ForeignKey(
        User,
        null = True,
        verbose_name = '登録者',
        on_delete = models.SET_NULL,
        related_name = 'invoice_registered'
    )
    updated_at = models.DateTimeField(
        verbose_name = '更新日',
        auto_now = True
    )   
    updated_by = models.ForeignKey(
        to = User,
        null = True,
        verbose_name = '更新者',
        on_delete = models.SET_NULL,
        related_name = 'invoice_updated'
    )
    deleted = models.BooleanField(
        verbose_name = '削除フラグ',
        default = False
    )
    def soft_delete(self):
        self.deleted = True
        self.save()

    @property
    def total_wo_tax(self):
        details = self.details.all()
        return details.aggregate(total = Sum('invoice_amount_wo_tax'))['total']

    @property
    def total_tax(self):
        details = self.details.all()
        return details.aggregate(total = Sum('tax_amount'))['total']

    @property
    def total_w_tax(self):
        details = self.details.all()
        return details.aggregate(total = Sum('invoice_amount_wo_tax'))['total']

    @property
    def details(self):
        details = InvoiceDetail.objects.filter(invoice_id = self.invoice_id)
        return details

    @property
    def invoice_entity(self):
        if len(self.details) > 0:
            return self.details[0].invoice_entity
        return None
    @property
    def yearmonth(self):
        if len(self.details) > 0:
            return self.details[0].yearmonth
        return None
        
class InvoiceDetail(models.Model):
    def __str__(self):
        return self.order_number

    class Meta:
        verbose_name = '請求明細'
        verbose_name_plural = '請求明細'
        ordering = ['pk']

    invoice_entity = models.ForeignKey(
        to = InvoiceEntity,
        related_name = 'my_invoice_details',
        verbose_name = '請求管理簿',
        on_delete = models.CASCADE
    )
    product_category_1 = models.CharField(
        verbose_name = '商材大区分',
        max_length = 50
    )
    product_category_2 = models.CharField(
        verbose_name = '商材小区分',
        max_length = 50
    )
    yearmonth = models.CharField(
        verbose_name = '請求月',
        max_length = 6
    )
    seq_number = models.CharField(
        verbose_name = 'SEQNO',
        max_length = 50
    )
    order_number = models.CharField(
        verbose_name = '申込管理番号',
        max_length = 50
    )
    invoice_id = models.CharField(
        verbose_name = '請求書ID',
        max_length = 50
    )
    service_start_date = models.DateField(
        verbose_name = 'サービス開始日'
    )
    service_name = models.CharField(
        verbose_name = '請求明細内容',
        max_length = 50
    )
    invoice_amount_wo_tax = models.IntegerField(
        verbose_name = '請求金額(税抜)',
    )
    tax_type = models.CharField(
        verbose_name = '税区分',
        max_length = 10,
        choices = (
            ('課税','課税'),
            ('非課税', '非課税')
        )
    )
    tax_rate_perc = models.IntegerField(
        verbose_name = '税率'
    )
    tax_amount = models.IntegerField(
        verbose_name = '請求金額(税額)'
    )
 
    note = models.TextField(
        verbose_name = '備考',
        null = True,
        blank = True,
    )
    registered_at = models.DateTimeField(
        verbose_name = '登録日',
        auto_now_add = True
    )
    registered_by = models.ForeignKey(
        User,
        null = True,
        verbose_name = '登録者',
        on_delete = models.SET_NULL,
        related_name = 'detail_registered'
    )
    updated_at = models.DateTimeField(
        verbose_name = '更新日',
        auto_now = True
    )   
    updated_by = models.ForeignKey(
        to = User,
        null = True,
        verbose_name = '更新者',
        on_delete = models.SET_NULL,
        related_name = 'detail_updated'
    )
    deleted = models.BooleanField(
        verbose_name = '削除フラグ',
        default = False
    )
    def soft_delete(self):
        self.deleted = True
        self.save()
    @property
    def invoice_amount_w_tax(self):
        return int(self.invoice_amount_wo_tax) + int(self.tax_amount)
    @property
    def is_invoiced(self):
        return len(Invoice.objects.filter(invoice_id = self.invoice_id)) > 0
class UploadedFile(models.Model):
    def __str__(self):
        return self.order_number

    class Meta:
        verbose_name = 'アップロード'
        verbose_name_plural = 'アップロードファイル'
        ordering = ['pk']
    
    TYPE_COMPANY = 1
    TYPE_ENTITY = 2
    TYPE_DETAIL = 3

    type = models.CharField(
        verbose_name = 'ファイル種類',
        max_length = 10,
        choices = (
            (TYPE_COMPANY, '会社情報'),
            (TYPE_ENTITY, '請求管理簿'),
            (TYPE_DETAIL, '請求明細')
        )
    )
    csv_file = models.FileField(
        upload_to = 'company_csv',
        verbose_name = 'アップロードファイル',
        validators = [FileExtensionValidator(['csv', ])],
    )

    processed_at = models.DateTimeField(
        verbose_name = '処理日',
        auto_now_add = True
    )

    uploaded_by = models.ForeignKey(
        to = User,
        null = True,
        verbose_name = '実行ユーザ',
        on_delete = models.SET_NULL
    )

    record_count = models.IntegerField(
        verbose_name = '件数',
    )

    error_count = models.IntegerField(
        verbose_name = 'エラー件数'
    )

class BankInfo(models.Model):
    def __str__(self):
        return '口座情報'
    class Meta:
        verbose_name = "口座情報"
        verbose_name_plural = "口座情報"
    
    types = [
        ('普通', '普通'),
        ('当座', '当座')
    ]
    bank = models.CharField(
        verbose_name = '金融機関名',
        max_length = 20,
        default = 'xxx銀行',
        blank = False,
        null = False
    )
    branch = models.CharField(
        verbose_name = '支店名',
        max_length = 20,
        default = 'xxx支店',
        blank = False,
        null = False
    )
    type = models.CharField(
        verbose_name = '口座種別',
        max_length = 20,
        choices = types,
        default = '普通'
    )
    number = models.CharField(
        verbose_name = '口座番号',
        max_length = 20,
        default = '00000',
        null = False,
        blank = False
    )
    meigi= models.CharField(
        verbose_name = '名義',
        max_length = 50,
    )

    @staticmethod
    def get_bank_info():
        qs = BankInfo.objects.all()
        if len(qs) == 0:
            instance = BankInfo()
            instance.bank = 'no data'
            instance.branch = 'no data'
            instance.type = '普通'
            instance.number = 'no data'
            instance.meigi = 'no data'
            instance.save()
            return instance
        return qs[0]



    