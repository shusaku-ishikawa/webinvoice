from django import forms
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.core.mail import send_mail
from django.core.validators import MaxValueValidator, MinValueValidator,  RegexValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError

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

class Product(models.Model):
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '商材'
        verbose_name_plural = '商材'
    
    tax_type_choice = (
        ('課税', '課税'),
        ('非課税', '非課税')
    )
    code = models.CharField(
        verbose_name = '商品コード',
        null = False,
        blank = False,
        unique = True,
        max_length = 50,
        validators = [
            alphanumeric
        ]
    )
    name = models.CharField(
        verbose_name = '商品・サービス名',
        max_length = 100,
        blank = False,
        null = False
    )
    price = models.IntegerField(
        verbose_name='単価',
        null = False,
        blank = False
    )
    tax_type = models.CharField(
        verbose_name = '税区分',
        max_length = 10,
        null = False,
        blank = False,
        choices = tax_type_choice
    )

class Customer(models.Model):
    def __str__(self):
        return self.company_name

    class Meta:
        verbose_name = '顧客'
        verbose_name_plural = '顧客'

    code = models.CharField(
        verbose_name = _('お客様No'), 
        max_length = 50,
        null = False,
        blank = False,
        unique = True,
        validators = [
            alphanumeric
        ]
    )
    company_name = models.CharField(
        verbose_name = "会社名",
        max_length = 50,
        null = False,
        blank = False
    )
    dept_name = models.CharField(
        verbose_name = "部署名",
        max_length = 50,
        null = False,
        blank = False
    )
    representative = models.CharField(
        verbose_name = "担当者名",
        max_length = 50,
        null = False,
        blank = False
    )
    zip = models.CharField(
        verbose_name = _('送付先郵便番号'), 
        max_length = 10,
        null = False,
        blank = False,
        validators = [
            validate_postcode,
        ]
    )
    address = models.CharField(
        verbose_name = "請求書送付先住所",
        max_length = 100,
        null = False,
        blank = False
    )
    email = models.EmailField(
        verbose_name = 'メールアドレス',
        null = True,
        blank = True,
    )
    phone = models.CharField(
        verbose_name = _('電話番号'), 
        max_length = 20,
        null = True,
        blank = True,
        validators = [
            validate_phonenumber,
        ]
    )

class Invoice(models.Model):
    def __str__(self):
        if self.code:
            return self.code
        else:
            return '未請求'

    class Meta:
        verbose_name = '請求明細'
        verbose_name_plural = '請求明細'
    
    code = models.CharField(
        verbose_name = '請求番号',
        null = True,
        blank = True,
        max_length = 100
    )
    customer = models.ForeignKey(
        Customer,
        verbose_name = '顧客',
        on_delete = models.CASCADE
    )
    product = models.ForeignKey(
        Product,
        verbose_name = '商品',
        on_delete = models.CASCADE
    )
    amount = models.IntegerField(
        verbose_name='数量',
        null = False,
        blank=False
    )
    month_used = models.CharField(
        verbose_name = 'ご利用月',
        max_length = 6,
        validators = [
            validate_month,
        ]
    )