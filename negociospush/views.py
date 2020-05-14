import datetime
from datetime import date

from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_protect
from rest_framework import generics
from .models import Profile, Product, Process, UserCode, Notification, NotificationProcesses, Events, EventTypes, User
from .serializers import ProfileSerializer, ProductSerializer, ProcessSerializer
from .forms import RegistrationForm
from django.contrib.auth import login, authenticate
from django.http import JsonResponse
from datetime import datetime, timedelta
from django.contrib import auth, messages
from enum import Enum


class EVENTS(Enum):
    LOGIN = 1
    QUICK_FILTER = 2
    PROCESS_FILTER = 3
    REGISTER = 4
    CUSTOM_FILTER = 5
    LOGOUT = 6
    FORGOT_PASSWD = 7
    LANDPAGE_VISIT = 8
    REGISTER_VISIT = 9
    NOTIFICATION_LIST = 10


def index(request):
    create_event(request, EVENTS.LANDPAGE_VISIT)
    return render(request, 'index.html')


@csrf_protect
def register(request):
    context = {}
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            create_event(request, EVENTS.REGISTER)
            print("el formulario es valido")
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('index')
    else:
        create_event(request, EVENTS.REGISTER_VISIT)
        form = RegistrationForm()
    context['form'] = form
    return render(request, 'registration/register.html', context)


def logout(request, *args, **kwars):
    create_event(request, EVENTS.LOGOUT)
    auth.logout(request)
    return redirect('index')


def forgot_password(request):
    create_event(request, EVENTS.FORGOT_PASSWD)
    return render(request, './frontend/pages/examples/forgot-password.html')


def process(request):
    global all_processes
    context = {}

    if request.method == "GET":
        quick_filter = request.GET.get('filter')
        print(quick_filter)
        if quick_filter is not None:
            create_event(request, EVENTS.QUICK_FILTER)
            if quick_filter == 'today':
                all_processes = Process.objects.filter(LoadDate=date.today())
            elif quick_filter == 'lastweek':
                start_date = date.today() - timedelta(days=7)
                end_date = date.today()
                all_processes = Process.objects.filter(LoadDate__range=(start_date, end_date))
            elif quick_filter == 'post':
                request_post = request.session['request_post']
                filter_words = request_post.get('words')
                filter_date = request_post.get('reservation')
                context['filter_words'] = filter_words
                context['filter_date'] = filter_date
                all_processes = get_post_query(filter_words, filter_date)
            else:
                all_processes = Process.objects.all()
            context['quick_filter'] = quick_filter
        else:
            all_processes = Process.objects.all()
    elif request.method == "POST":
        create_event(request, EVENTS.PROCESS_FILTER)
        filter_words = request.POST.get('words')
        filter_date = request.POST.get('reservation')
        context['filter_words'] = filter_words
        context['filter_date'] = filter_date
        all_processes = get_post_query(filter_words, filter_date)
        request.session['request_post'] = request.POST
        context['quick_filter'] = 'post'

    paginator = Paginator(all_processes, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context['page_obj'] = page_obj

    return render(request, './frontend/pages/business/process.html', context)


def get_post_query(filter_words, filter_date):
    if filter_words is not None and filter_date is not None:
        filter_date_split = filter_date.split('-')
        processes = Process.objects.filter(Description__contains=filter_words.upper(), LoadDate__range=(
            datetime.strptime(filter_date_split[0].strip(), "%m/%d/%Y").date(),
            datetime.strptime(filter_date_split[1].strip(), "%m/%d/%Y").date()))
    elif filter_words is not None and filter_date is None:
        processes = Process.objects.filter(Description__contains=filter_words.upper())
    elif filter_date is not None and filter_words is None:
        filter_date_split = filter_date.split('-')
        processes = Process.objects.filter(LoadDate__range=(
            datetime.strptime(filter_date_split[0].strip(), "%m/%d/%Y").date(),
            datetime.strptime(filter_date_split[1].strip(), "%m/%d/%Y").date()))
    else:
        processes = Process.objects.all()
    return processes


def dashboard(request):
    context = {}
    if not request.GET.get('menu'):
        create_event(request, EVENTS.LOGIN)
    codes = UserCode.objects.filter(User=request.user).count()
    processes = Process.objects.count()
    notifications = Notification.objects.filter(recipient=request.user)
    context['notifications'] = notifications
    context['unread_notifications'] = Notification.objects.filter(recipient=request.user, read=False)
    context['codes'] = codes
    context['processes'] = processes
    return render(request, 'dashboard.html', context)


def codigos_unspsc(request):
    context = {}
    if request.method == 'POST':
        create_event(request, EVENTS.CUSTOM_FILTER)
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
    families = Product.objects.filter(SegmentCode=segment_code).distinct('FamilyCode').values('FamilyCode',
                                                                                              'FamilyName')
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


# Create event for metrics
def create_event(request, idevtn):
    evt_type = EventTypes.objects.get(pk=idevtn.value)
    user_app = request.user
    if user_app is None or user_app.is_anonymous:
        users = User.objects.filter(username='anonimo')
        for anonimoUser in users:
            user_app = anonimoUser

    evt = Events(Data=request, User=user_app, EventType=evt_type, SessionKey=request.session.session_key)
    evt.save()


def notification_list(request, notification_code):
    Notification.objects.filter(id=notification_code).update(read=True)
    notification_processes_ids = NotificationProcesses.objects.filter(parent_id=notification_code).values('process_id')
    notification_processes = Process.objects.filter(IdProcess__in=notification_processes_ids)
    context = {}
    paginator = Paginator(notification_processes, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context['page_obj'] = page_obj
    create_event(request, EVENTS.NOTIFICATION_LIST)
    return render(request, 'notificationList.html', context)


class ListProfiles(generics.ListCreateAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer


class ListProducts(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class ListProcesses(generics.ListCreateAPIView):
    queryset = Process.objects.all()
    serializer_class = ProcessSerializer
