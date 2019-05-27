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

import re, base64

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
    PREFIX = "C"
    
    def __str__(self):
        return self.kanji_name

    class Meta:
        verbose_name = '会社'
        verbose_name_plural = '会社'
        ordering = ['pk']

    id = models.CharField(
        verbose_name = '会社ID',
        max_length = 50,
        primary_key = True,
        unique = True
    )
    def make_id(self):
        qs = Company.objects.all().order_by('-id')
        if len(qs) == 0:
            return 1
        return int(qs[0].id.replace(self.PREFIX, '')) + 1
    def save(self, *args, **kwargs):
        if not self.id:
            custom_id = self.PREFIX + ('000000000000' + str(self.make_id()))[-10:]
            self.id = custom_id
        super(Company, self).save(*args, **kwargs)

    # 法人番号
    corporate_number = models.CharField(
        verbose_name = _('法人番号'),
        max_length = 50,
        null = False,
        blank = False,
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
        null = True,
        blank = True
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
        null = True,
        blank = True
    )
    representative_name = models.CharField(
        verbose_name = "担当者名",
        max_length = 50,
        null = True,
        blank = True
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
    PREFIX = "B"
    def __str__(self):
        return self.invoice_company_name
    def make_id(self):
        qs = InvoiceEntity.objects.all().order_by('-id')
        if len(qs) == 0:
            return 1
        return int(qs[0].id.replace(self.PREFIX, '')) + 1
    def save(self, *args, **kwargs):
        if not self.id:
            custom_id = self.PREFIX + ('000000000000' + str(self.make_id())) [-10:]
            self.id = custom_id
        super(InvoiceEntity, self).save(*args, **kwargs)
        
    class Meta:
        verbose_name = '請求管理簿'
        verbose_name_plural = '請求管理簿'
        ordering = ['pk']
    id = models.CharField(
        verbose_name = '会社ID',
        max_length = 50,
        primary_key = True,
        unique = True
    )

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
        null = True,
        blank = True
    )
    invoice_company_name = models.CharField(
        verbose_name = '請求会社名',
        max_length = 100,
        null = True,
        blank = True
    )
    invoice_dept = models.CharField(
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
        null = True,
        blank = True,
        choices = (
            ('末日', '末日'),
            ('20日', '20日'),
        )
    )
    
    payment_due_to = models.CharField(
        verbose_name = '支払い期日',
        max_length = 20,
        null = True,
        blank = True,
        choices = (
            ('末日', '末日'),
            ('20日', '20日'),
        )
    )
    
    invoice_sent_at = models.CharField(
        verbose_name = '請求書送付時期',
        max_length = 20,
        null = True,
        blank = True,
        choices =  (
            ('末日', '末日'),
            ('20日', '20日'),
        )
    )
    invoice_timing = models.CharField(
        verbose_name = '請求タイミング',
        max_length = 20,
        null = True,
        blank = True,
        choices = (
            ('売掛', '売掛'),
            ('前入金', '前入金'),
        )
    )
    invoice_period = models.CharField(
        verbose_name = '請求周期',
        max_length = 20,
        null = True,
        blank = True,
        choices = (
            ('毎月', '毎月'),
            ('6ヶ月', '6ヶ月'),
        )
    )
    
    bank_name = models.CharField(
        verbose_name = '振込銀行名',
        max_length = 20,
        blank = True,
        null = True
    )
    bank_branch_name = models.CharField(
        verbose_name = '振込支店名',
        max_length = 20,
        blank = True,
        null = True
    )

    bank_account_type = models.CharField(
        verbose_name = '口座種類',
        max_length = 20,
        blank = True,
        null = True,
        choices = (
            ('普通', '普通'),
            ('当座', '当座')
        )
    )

    bank_account_number = models.CharField(
        verbose_name = '口座番号',
        max_length = 20,
        blank = True,
        null = True
    )
    credit_card_settlement_company = models.CharField(
        verbose_name = 'クレカ決済会社',
        max_length = 20,
        blank = True,
        null = True
    )
    credit_card_code = models.CharField(
        verbose_name = 'クレカコード',
        max_length = 20,
        blank = True,
        null = True
    )
    credit_card_id = models.CharField(
        verbose_name = 'クレカID',
        max_length = 20,
        blank = True,
        null = True
    )
    settlement_company = models.CharField(
        verbose_name = '決済会社',
        max_length = 20,
        blank = True,
        null = True
    )
    settlement_code = models.CharField(
        verbose_name = '決済コード',
        max_length = 20,
        blank = True,
        null = True
    )
    settlement_id = models.CharField(
        verbose_name = '決済ID',
        max_length = 20,
        blank = True,
        null = True
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
    PREFIX = "IV"
    def __str__(self):
        return str(self.pk)
    def make_id(self):
        qs = Invoice.objects.all().order_by('-id')
        if len(qs) == 0:
            return 1
        return int(qs[0].id.replace(self.PREFIX, '')) + 1

    def save(self, *args, **kwargs):
        if not self.id:
            custom_id = self.PREFIX + ('000000000000' + str(self.make_id()))[-10:]
            self.id = custom_id
        super(Invoice, self).save(*args, **kwargs)
    class Meta:
        verbose_name = '請求書'
        verbose_name_plural = '請求書'
        ordering = ['pk']

    id = models.CharField(
        verbose_name = '会社ID',
        max_length = 50,
        primary_key = True,
        unique = True
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
    PREFIX = "S"
    def __str__(self):
        return self.order_number
    def make_id(self):
        qs = InvoiceDetail.objects.all().order_by('-id')
        if len(qs) == 0:
            return 1
        return int(qs[0].id.replace(self.PREFIX, '')) + 1
    def save(self, *args, **kwargs):
        if not self.id:
            custom_id = self.PREFIX + ('000000000000' + str(self.make_id()))[-10:]
            self.id = custom_id
        super(InvoiceDetail, self).save(*args, **kwargs)
    class Meta:
        verbose_name = '請求明細'
        verbose_name_plural = '請求明細'
        ordering = ['pk']

    id = models.CharField(
        verbose_name = '会社ID',
        max_length = 50,
        primary_key = True,
        unique = True
    )

    invoice = models.ForeignKey(
        to = Invoice,
        verbose_name = '請求書',
        on_delete = models.CASCADE,
        related_name = 'details',
        null = True,
        blank = True
    )
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
    invoice_code = models.CharField(
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

    COLUMN_COUNT_COMPANY = 17
    COLUMN_COUNT_ENTITY = 17
    COLUMN_COUNT_DETAIL = 17
    

    type = models.CharField(
        verbose_name = 'ファイル種類',
        max_length = 10,
        choices = (
            (TYPE_COMPANY, '会社情報'),
            (TYPE_ENTITY, '請求管理簿'),
            (TYPE_DETAIL, '請求明細')
        )
    )
    file = models.FileField(
        upload_to = 'company_csv',
        verbose_name = 'アップロードファイル',
        validators = [FileExtensionValidator(['xlsx', ])],
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
        default = 0
    )
    @property
    def error_count(self):
        return len(self.errors.all())
class UploadedFileError(models.Model):
    
    file = models.ForeignKey(
        to = UploadedFile,
        on_delete = models.CASCADE,
        related_name = 'errors'
    )
    row_index = models.IntegerField(
        verbose_name = '行番号',
    )
    error = models.CharField(
        verbose_name = 'エラー',
        null = True,
        blank = True,
        max_length = 255
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

class OurInfo(models.Model):
    class Meta:
        verbose_name = "Vision基本情報"
        verbose_name_plural = "Vision基本情報"

    zip = models.CharField(
        verbose_name = '郵便番号',
        max_length = 100,
    )
    address_1 = models.CharField(
        verbose_name = '住所1',
        max_length = 100
    )
    address_2 = models.CharField(
        verbose_name = '住所2',
        max_length = 100
    )
    phone = models.CharField(
        verbose_name = '電話番号',
        max_length = 100
    )
    @staticmethod
    def get_ourinfo():
        qs = OurInfo.objects.all()
        if len(qs) == 0:
            new = OurInfo()
            new.zip = 'no data',
            new.address_1 = 'no data'
            new.address_2 = 'no data'
            new.phone = 'no data'
            new.save()
            return new
        return qs[0]
    
class HandWrittenInvoice(models.Model):

    id = models.CharField(
        verbose_name = 'id',
        primary_key = True,
        unique = True,
        max_length = 50
    )
    customer_id = models.CharField(
        verbose_name = 'お客様番号',
        max_length = 50
    )
    vision_phone_number = models.CharField(
        verbose_name = '連絡先電話番号',
        max_length = 50
    )

    zip = models.CharField(
        verbose_name = _('請求郵便番号'), 
        max_length = 10,
        null = False,
        blank = False,
        validators = [
            validate_postcode,
        ]
    )

    address_1 = models.CharField(
        verbose_name = "住所1",
        max_length = 10,
        null = False,
        blank = False,
        choices = pref_options
    )
    address_2 = models.CharField(
        verbose_name = "住所2",
        max_length = 30,
        null = False,
        blank = False
    )
    company_name = models.CharField(
        verbose_name = '請求会社名',
        max_length = 100,
    )
    dept = models.CharField(
        verbose_name = '請求部署',
        max_length = 100,
    )
    person = models.CharField(
        verbose_name = '請求宛名',
        max_length = 50,
    )
    project_1 = models.CharField(
        verbose_name = '請求宛名1',
        max_length = 50,
        null = True,
        blank = True
    )
    date_created = models.DateField(
        verbose_name = '作成日',
        default = timezone.now()
    )
    total = models.IntegerField(
        verbose_name = '請求金額'
    )

    due_date = models.DateField(
        verbose_name = '支払期日',
    )
    total_wo_tax = models.IntegerField(
        verbose_name  = '税抜合計'
    )
    total_tax = models.IntegerField(
        verbose_name  = '税額合計'
    )
    total_w_tax = models.IntegerField(
        verbose_name  = '税込合計'
    )
    create_user = models.ForeignKey(
        to = User,
        related_name = 'create_user',
        on_delete = models.CASCADE
    )
    
    
class HandWrittenInvoiceDetail(models.Model):
    parent = models.ForeignKey(
        to = HandWrittenInvoice,
        on_delete = models.CASCADE,
        related_name = 'details'
    )
    row_no = models.IntegerField(
        verbose_name = '行番号'
    )
    yearmonth = models.CharField(
        max_length = 6,
        null = True,
        blank = True,
    )
    product_category = models.CharField(
        max_length = 100,
        null = True,
        blank = True,
    )
    product_name = models.CharField(
        max_length = 100,
        null = True,
        blank = True,
    )
    amount = models.IntegerField(
        null = True,
        blank = True,
    )
    unit_price = models.IntegerField(
        null = True,
        blank = True,
    )
    tax_type = models.CharField(
        max_length = 10,
        choices = (
            ('1', '課税'),
            ('2', '非課税')
        ),
        null = True,
        blank = True,
    )
    total_wo_tax = models.IntegerField(
        null = True,
        blank = True,
    )
    tax_price = models.IntegerField(
        null = True,
        blank = True,
    )
    total_w_tax = models.IntegerField(
        null = True,
        blank = True,
    )