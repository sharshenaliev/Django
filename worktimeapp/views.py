from django.shortcuts import render, redirect
from .models import *
from .forms import CustomUserCreationForm, CustomUserLoginForm
from django.contrib import messages
from django.contrib.auth import get_user_model, login, logout
from django.utils.timezone import now
from django.core.paginator import Paginator
from datetime import timedelta, time, datetime
from django.db.models import Q
User = get_user_model()
userid = 0


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
            return redirect('login')
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
            start = Time.objects.create(user=CustomUser.objects.get(email=user))
            global userid
            userid = start.id
            start.save()
            org = Organization.objects.get(title=user.organization)
            if datetime.time(now()) > org.start_time:
                user.lateness += 1
                user.save()
            else:
                user.betimes += 1
                user.save()
            login(request, user)
            return redirect('home')
    else:
        form = CustomUserLoginForm()
    context = {
        'form': form
    }
    return render(request, template_name='worktimeapp/register.html', context=context)


def user_logout(request):
    logout(request)
    start = Time.objects.get(id=userid)
    d = now() - start.start_time
    Time.objects.filter(id=userid).update(end_time=now(), day=d)
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
