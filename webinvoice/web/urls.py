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
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(settings.STATIC_URL,document_root=settings.STATIC_ROOT) 

