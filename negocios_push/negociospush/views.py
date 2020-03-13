from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_protect
from rest_framework import generics
from .models import Profile, Product, Process
from .serializers import ProfileSerializer, ProductSerializer, ProcessSerializer
from .forms import RegistrationForm
from django.contrib.auth import login, authenticate


def index(request):
    return render(request, 'index.html')


@csrf_protect
def register(request):
    context = {}
    print("register method")
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        print ("es met POST")
        print(form.errors)
        if form.is_valid():
            print ("el formulario es valido")
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('index')
    else:
        form = RegistrationForm()
    context['form'] = form
    return render(request, 'registration/register.html', context)


def logout(request):
    logout(request)
    return redirect('index')


def forgotPassword(request):
    return render(request, './frontend/pages/examples/forgot-password.html')


def process(request):
    return render(request, './frontend/pages/mailbox/mailbox.html')


def dashboard(request):
    return render(request, 'dashboard.html')


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
