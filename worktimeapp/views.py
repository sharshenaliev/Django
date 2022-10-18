from django.shortcuts import render, redirect
from .models import *
from .forms import CustomUserCreationForm, CustomUserLoginForm
from django.contrib import messages, sessions
from django.contrib.auth import get_user_model, login, logout
from django.utils.timezone import now
from django.core.paginator import Paginator
from datetime import timedelta, datetime
from django.db.models import Q
from django.http import StreamingHttpResponse
import cv2
import threading
User = get_user_model()


def index(request):
    users = CustomUser.objects.all()
    companies = Organization.objects.all()
    paginator = Paginator(users, 10)
    page_num = request.GET.get('page', 1)
    page_objects = paginator.page(page_num)
    context = {
        'page_obj': page_objects,
        'companies': companies
    }
    return render(request, template_name='worktimeapp/index.html', context=context)


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            messages.success(request, 'Вы зарегистрировались!')
            form.save()
            return redirect('home')
        else:
            messages.error(request, 'Ошибка')
    else:
        form = CustomUserCreationForm()
    context = {
        'form': form
    }
    return render(request, template_name='worktimeapp/register.html', context=context)


def user_login(request):
    if request.method == 'POST':
        form = CustomUserLoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            start = Time.objects.create(user=CustomUser.objects.get(email=user))
            request.session['time_id'] = start.id
            request.session.modified = True
            start.save()
            org = Organization.objects.get(title=user.organization)
            if datetime.time(now()) > org.start_time:
                user.lateness += 1
                user.save()
            else:
                user.betimes += 1
                user.save()
            return redirect('scan')
    else:
        form = CustomUserLoginForm()
    context = {
        'form': form
    }
    return render(request, template_name='worktimeapp/register.html', context=context)


def user_logout(request):
    start = Time.objects.get(id=request.session.get('time_id'))
    d = now() - start.start_time
    Time.objects.filter(id=request.session.get('time_id')).update(end_time=now(), day=d)
    try:
        month_id = Profile.objects.get(user=CustomUser(email=str(request.user)))
        if month_id.month == int(datetime.today().strftime('%m')):
            month_id.hours += d
            month_id.save()
        else:
            month_id = Profile.objects.create(user=CustomUser.objects.get(email=str(request.user)),
                                              month=int(datetime.today().strftime('%m')), hours=d)
            month_id.save()
    except:
        month_id = Profile.objects.create(user=CustomUser.objects.get(email=str(request.user)),
                                          month=int(datetime.today().strftime('%m')), hours=d)
        month_id.save()
    del request.session['time_id']
    logout(request)
    return redirect('home')


def search(request):
    search_query = request.GET.get('search', '')
    if search_query:
        users = CustomUser.objects.filter(
            Q(email__iexact=search_query)|
            Q(first_name__icontains=search_query)|
            Q(last_name__icontains=search_query))
    else:
        users = CustomUser.objects.all()
    paginator = Paginator(users, 1)
    page_num = request.GET.get('page', 1)
    page_objects = paginator.page(page_num)
    context = {
        'page_obj': page_objects,
    }
    return render(request, template_name='worktimeapp/search.html', context=context)


def get_org(request, organization_id):
    users = CustomUser.objects.filter(organization=organization_id)
    companies = Organization.objects.all()
    company = Organization.objects.get(pk=organization_id)
    paginator = Paginator(users, 10)
    page_num = request.GET.get('page', 1)
    page_objects = paginator.page(page_num)
    context = {
        'page_obj': page_objects,
        'companies': companies,
        'company': company
    }
    return render(request, template_name='worktimeapp/org.html', context=context)


data = ''


def scan(request):
    if data == '':
        cam = VideoCamera()
        response = StreamingHttpResponse(gen(cam), content_type="multipart/x-mixed-replace;boundary=frame")
    else:
        response = redirect('logout')
    return response


class VideoCamera(object):
    def __init__(self):
        self.video = cv2.VideoCapture(0)
        (self.grabbed, self.frame) = self.video.read()
        threading.Thread(target=self.update, args=()).start()

    def __del__(self):
        self.video.release()
        cv2.destroyAllWindows()

    def get_frame(self):
        image = self.frame
        _, jpeg = cv2.imencode('.jpg', image)
        return jpeg.tobytes()

    def update(self):
        detector = cv2.QRCodeDetector()
        while True:
            (self.grabbed, self.frame) = self.video.read()
            clear_qrcode, img = self.video.read()
            global data
            data, bbox, clear_qrcode = detector.detectAndDecode(img)
            if data:
                print(data)
                break


def gen(camera):
    while data == '':
        frame = camera.get_frame()
        yield(b'--frame\r\n'
              b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
