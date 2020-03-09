from django.shortcuts import render
from rest_framework import generics
from .models import Profile, Product, Process
from .serializers import ProfileSerializer, ProductSerializer, ProcessSerializer

def index(request):
    return render(request, 'index.html')


def login(request):
    return render(request, './frontend/pages/examples/login.html')

def register(request):
    return render(request, './frontend/pages/examples/register.html')

def forgotPassword(request):
    return render(request, './frontend/pages/examples/forgot-password.html')

def process(request):
    return render(request, './frontend/pages/mailbox/mailbox.html')

def dashboard(request):
    return render(request, './frontend/index.html')




# Create your views here.
class ListProfiles(generics.ListCreateAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer


class ListProducts(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class ListProcesses(generics.ListCreateAPIView):
    queryset = Process.objects.all()
    serializer_class = ProcessSerializer
