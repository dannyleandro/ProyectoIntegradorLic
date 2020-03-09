from django.conf.urls import url
from django.urls import path, include

from . import views

urlpatterns = [
    path('rest-auth/', include('rest_auth.urls')),
    url(r'^$', views.index, name='index'),
    url(r'^index.html$', views.index, name='index'),
    url(r'^profiles', views.ListProfiles.as_view()),
    url(r'^products', views.ListProducts.as_view()),
    url(r'^processes', views.ListProcesses.as_view()),
]
