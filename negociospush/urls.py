from django.conf.urls import url
from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    url(r'^index.html$', views.index, name='index'),
    path('rest-auth/', include('rest_auth.urls')),
    url(r'^login', auth_views.LoginView.as_view(), name='login'),
    url(r'^logout', views.logout, name='logout'),
    url(r'^$', views.index, name='index'),
    url(r'^profiles', views.ListProfiles.as_view()),
    url(r'^products', views.ListProducts.as_view()),
    url(r'^processes', views.ListProcesses.as_view()),
    url(r'^dashboard',  views.dashboard, name='dashboard'),
    url(r'^register',  views.register, name='register'),
    url(r'^forgot-password',  views.forgot_password, name='forgotPassword'),
    url(r'^process', views.process, name='process'),
    url(r'^codigosUNSPSC', views.codigos_unspsc, name='codigosUNSPSC'),
    url(r'^FamiliesBySegment/(?P<segment_code>\d+)$', views.get_families, name='FamiliesBySegment'),
    url(r'^ClassesByFamily/(?P<family_code>\d+)$', views.get_classes, name='ClassesByFamily'),
    url(r'^ProductsByClass/(?P<class_code>\d+)$', views.get_products, name='ProductsByClass'),
    url(r'^notificationList/(?P<notification_code>\d+)$', views.notification_list, name='notificationList'),
    url(r'^detalleProcess/(?P<num_constancia>[\w.@+-]+)$', views.get_detalle_process, name='detalleProcess')
]
