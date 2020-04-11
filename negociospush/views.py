from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_protect
from rest_framework import generics
from .models import Profile, Product, Process
from .serializers import ProfileSerializer, ProductSerializer, ProcessSerializer
from .forms import RegistrationForm
from django.contrib.auth import login, authenticate
from django.http import JsonResponse


def index(request):
    return render(request, 'index.html')


@csrf_protect
def register(request):
    context = {}
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
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


def codigosUNSPSC(request):
    context = {}
    if request.method == 'POST':
        print('metodo post')
    else:
        segments = Product.objects.distinct('SegmentCode').values('SegmentCode', 'SegmentName')
        # print(segments)
        context['segments'] = segments
    return render(request, 'codigosUNSPSC.html', context)


def get_families(request, segment_code):
    families_list = list(Product.objects.filter(SegmentCode=segment_code).distinct('FamilyCode').values('FamilyCode', 'FamilyName'))
    return JsonResponse(families_list, safe=False)


def get_classes(request, family_code):
    classes_list = list(Product.objects.filter(FamilyCode=family_code).distinct('ClassCode').values('ClassCode', 'ClassName'))
    return JsonResponse(classes_list, safe=False)


def get_products(request, class_code):
    products_list = list(Product.objects.filter(ClassCode=class_code).values('ProductCode', 'ProductName'))
    return JsonResponse(products_list, safe=False)


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
