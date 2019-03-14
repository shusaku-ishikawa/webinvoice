from django.urls import path
from . import views
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

app_name = 'web'
admin.site.site_title = 'web invoice' 
admin.site.site_header = 'web invoice' 
admin.site.index_title = 'メニュー'

urlpatterns = [
    path('', views.Login.as_view(), name=''),
    path('top/', views.TopPage.as_view(), name='top'),
    path('login/', views.Login.as_view(), name='login'),
    path('logout/', views.Logout.as_view(), name='logout'),
    path('create_customer/', views.CreateCustomer.as_view(), name='create_customer'),
    path('update_customer/<int:pk>', views.UpdateCustomer.as_view(), name='update_customer'),
    path('list_customer/', views.ListCustomer.as_view(), name='list_customer'),
    path('create_product/', views.CreateProduct.as_view(), name='create_product'),
    path('update_product/<int:pk>', views.UpdateProduct.as_view(), name='update_product'),
    path('list_product/', views.ListProduct.as_view(), name='list_product'),
    path('list_invoice/', views.ListInvoice.as_view(), name='list_invoice'),
    
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(settings.STATIC_URL,document_root=settings.STATIC_ROOT) 

