from django.conf.urls import url
from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    url(r'^index.html$', views.index, name='index'),
    path('rest-auth/', include('rest_auth.urls')),
    url(r'^login', auth_views.LoginView.as_view(), name='login'),
    url(r'^logout', auth_views.LogoutView.as_view(), name='logout'),
    url(r'^$', views.index, name='index'),
    url(r'^profiles', views.ListProfiles.as_view()),
    url(r'^products', views.ListProducts.as_view()),
    url(r'^processes', views.ListProcesses.as_view()),
    url(r'^dashboard',  views.dashboard, name='dashboard'),
    url(r'^register',  views.register, name='register'),
    url(r'^forgot-password',  views.forgotPassword, name='forgotPassword'),
    url(r'^process', views.process, name='process'),


]
