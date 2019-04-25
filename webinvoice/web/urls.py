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
    # path('logout/', views.Logout.as_view(), name='logout'),
    path('c_new/', views.CreateCompany.as_view(), name='create_company'),
    path('c_edit/<int:pk>', views.UpdateCompany.as_view(), name='update_company'),
    path('c_del/<int:pk>', views.DeleteCompany.as_view(), name='delete_company'),
    path('c_li/', views.ListCompany.as_view(), name='list_company'),
    path('entity_new/', views.CreateInvoiceEntity.as_view(), name='create_invoice_entity'),
    path('entity_edit/<int:pk>', views.UpdateInvoiceEntity.as_view(), name='update_invoice_entity'),
    path('entity_del/<int:pk>', views.DeleteInvoiceEntity.as_view(), name='delete_invoice_entity'),
    path('entity_li/', views.ListInvoiceEntity.as_view(), name='list_invoice_entity'),
    path('detail_new/', views.CreateInvoiceDetail.as_view(), name='create_invoice_detail'),
    path('detail_edit/<int:pk>', views.UpdateInvoiceDetail.as_view(), name='update_invoice_detail'),
    path('detail_del/<int:pk>', views.DeleteInvoiceDetail.as_view(), name='delete_invoice_detail'),
    path('detail_li/', views.ListInvoiceDetail.as_view(), name='list_invoice_detail'),
    path('search/', views.Search.as_view(), name='search'),
    path('upload_csv/', views.UploadFile.as_view(), name='file_upload'),
    path('invoice_li/', views.ListInvoice.as_view(), name='list_invoice'),
    path('add_to_invoice/', views.add_to_invoice, name='add_to_invoice'),
    path('pdf/<int:pk>', views.pdf, name='pdf_invoice'),
    
    
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(settings.STATIC_URL,document_root=settings.STATIC_ROOT) 

