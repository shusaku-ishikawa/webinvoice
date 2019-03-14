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
    reg = re.compile('^[0-9]+$')
    if not reg.match(value):
        raise ValidationError(u'%s 電話番号のフォーマットが正しくありません' % value)

def validate_month(value):
    reg = re.compile('^20[0-9]{2}[0-1][0-9]$')
    if not reg.match(value):
        raise ValidationError(u'%s 年月のフォーマットが正しくありません' % value)


class Customer(models.Model):
    def __str__(self):
        return self.cumpany_name

    class Meta:
        verbose_name = '顧客'
        verbose_name_plural = '顧客'

    code = models.CharField(
        verbose_name = _('お客様No'), 
        max_length = 50,
        null = False,
        blank = False,
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
    phone = models.CharField(
        verbose_name = _('電話番号'), 
        max_length = 20,
        null = False,
        blank = False,
        validators = [
            validate_phonenumber,
        ]
    )

class Invoice(models.Model):
    def __str__(self):
        return self.code

    class Meta:
        verbose_name = '請求明細'
        verbose_name_plural = '請求明細'
    
    customer = models.ForeignKey(
        Customer,
        verbose_name = '顧客',
        on_delete = models.CASCADE
    )
    month_used = models.CharField(
        verbose_name = 'ご利用月',
        max_length = 6,
        validators = [
            validate_month,
        ]
    )