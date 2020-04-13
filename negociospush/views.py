from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_protect
from rest_framework import generics
from .models import Profile, Product, Process, UserCode, Notification, NotificationProcesses
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
    context = {}
    codes = UserCode.objects.filter(User=request.user).count()
    processes = Process.objects.count()
    notifications = Notification.objects.filter(recipient=request.user)
    context['notifications'] = notifications
    context['codes'] = codes
    context['processes'] = processes
    return render(request, 'dashboard.html', context)


def codigos_unspsc(request):
    context = {}
    if request.method == 'POST':
        chosen_codes = [int(item[1:]) for item in request.POST.getlist('chosen_codes')]
        UserCode.objects.exclude(ProductCode_id__in=chosen_codes).delete()
        for chosen_code in chosen_codes:
            try:
                product = Product.objects.get(pk=chosen_code)
                if not UserCode.objects.filter(User=request.user, ProductCode_id=chosen_code).exists():
                    code = UserCode.objects.create(ProductCode=product, User=request.user)
                    code.save()
            except product.DoesNotExist:
                print('Product does not exist')
    segments = Product.objects.distinct('SegmentCode').values('SegmentCode', 'SegmentName')
    codes = UserCode.objects.filter(User=request.user)
    context['segments'] = segments
    code_template = []
    for code in codes:
        code_template.append(code.ProductCode.ProductCode)
    context['codes'] = codes
    context['code_template'] = code_template
    return render(request, 'codigosUNSPSC.html', context)


def get_families(request, segment_code):
    families = Product.objects.filter(SegmentCode=segment_code).distinct('FamilyCode').values('FamilyCode', 'FamilyName')
    result = []
    for family in families:
        result.append({
            "id": 'F' + str(family['FamilyCode']),
            "label": str(family['FamilyCode']) + ' - ' + family['FamilyName'],
            "items": [{"label": "Loading..."}]
        })
    return JsonResponse(result, safe=False)


def get_classes(request, family_code):
    classes = Product.objects.filter(FamilyCode=family_code).distinct('ClassCode').values('ClassCode', 'ClassName')
    result = []
    for classObject in classes:
        result.append({
            "id": 'C' + str(classObject['ClassCode']),
            "label": str(classObject['ClassCode']) + ' - ' + classObject['ClassName'],
            "items": [{"label": "Loading..."}]
        })
    return JsonResponse(result, safe=False)


def get_products(request, class_code):
    products = Product.objects.filter(ClassCode=class_code).values('ProductCode', 'ProductName')
    result = []
    for product in products:
        result.append({
            "id": 'P' + str(product['ProductCode']),
            "label": str(product['ProductCode']) + ' - ' + product['ProductName']
        })
    return JsonResponse(result, safe=False)


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
