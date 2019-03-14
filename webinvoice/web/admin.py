from django.contrib import admin
from .models import Invoice, Product, Customer
from django.contrib.admin.views.main import ChangeList
from django.contrib.admin.utils import quote
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.utils.translation import ugettext_lazy as _


# Register your models here.
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('code', 'company_name', 'dept_name', 'representative', 'zip', 'address', 'email', 'phone')

class ProductAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'price', 'tax_type')

class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('code', 'customer', 'product', 'amount', 'month_used')


admin.site.register(Product, ProductAdmin)
admin.site.register(Customer, CustomerAdmin)
admin.site.register(Invoice, InvoiceAdmin)