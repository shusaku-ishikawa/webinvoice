from django.contrib import admin
from .models import *
from django.contrib.admin.views.main import ChangeList
from django.contrib.admin.utils import quote
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.utils.translation import ugettext_lazy as _


@admin.register(BankInfo)
class BankInfoAdmin(admin.ModelAdmin):
    list_display = [field.name for field in BankInfo._meta.get_fields()]
    fields = ['bank', 'branch', 'type', 'number', 'meigi']
    def has_add_permission(self, request):
        # 設定を1つだけしか登録できないようにする
        count = BankInfo.objects.all().count()
        if count == 0:
            return True
        return False

    def has_delete_permission(self, request, obj=None):
        # 設定を削除できないようにする
        return False

@admin.register(OurInfo)
class OurInfoAdmin(admin.ModelAdmin):
    list_display = [field.name for field in OurInfo._meta.get_fields()]
    fields = ['zip', 'address_1', 'address_2', 'phone']
    def has_add_permission(self, request):
        # 設定を1つだけしか登録できないようにする
        count = OurInfo.objects.all().count()
        if count == 0:
            return True
        return False

    def has_delete_permission(self, request, obj=None):
        # 設定を削除できないようにする
        return False

