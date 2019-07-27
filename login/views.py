from .models import ip_class
from django.contrib.auth import login as dj_login
from django.contrib.auth import logout as dj_logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.utils import timezone
from django.contrib.auth.models import User

from .forms import *

# functions
def calculate_difference(x,y):
    hour = y.hour-x.hour
    minute = y.minute-x.minute
    return hour*60+minute

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    if ip_class.objects.filter(ip = str(ip)):
        x = ip_class.objects.get(ip = str(ip))
    else:
        x = ip_class(ip=str(ip),tresh_time=None)
        x.save()
    return x



def show(request):
    time = 'time'
    if request.user.is_authenticated:
        condition = True
    else:
        ip = get_client_ip(request)
        if ip.tresh_time is not None:
            time = 60-calculate_difference(ip.tresh_time,timezone.now())
            if time <= 0:
                condition = True
                ip.tresh_time = None
                ip.save()
            else:
                condition = False
        else:
            condition = True
    return render(request,"first_page.html",{
        'condition':condition,
        'time':time,
    })

def logout(request):
    dj_logout(request)
    return redirect('show')

            
def login(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('show'))
    else:
        ip = get_client_ip(request)
        time = ""
        condition = True
        form = None
        if ip.tresh_time is not None:
            time = 60-calculate_difference(ip.tresh_time,timezone.now())
            if time <= 0:
                condition = True
                ip.tresh_time = None
                ip.trials=0
                ip.save()
            else:
                condition = False
        else:
            if request.method == 'POST':
                form = LoginForm(request.POST)
                if form.is_valid():
                    user = form.user
                    dj_login(request, user)
                    ip.trials = 0
                    ip.save()
                    return HttpResponseRedirect(reverse('show'))
                else:
                    ip.trials = ip.trials+1
                    if ip.trials >= 3:
                        ip.tresh_time = timezone.now()
                        condition = False
                        time = 60
                        ip.trials = 0
                    ip.save()     
            else:
                form = LoginForm()
        return render(request, 'login.html', {
            'form': form,
            'condition':condition,
            'time':time,
        })

def register(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('show'))
    else:
        ip = get_client_ip(request)
        time = ""
        state = 0
        condition = True
        if ip.tresh_time is not None:
            time = 60-calculate_difference(ip.tresh_time,timezone.now())
            if time <= 0:
                condition = True
                ip.tresh_time = None
                ip.trials=0
                ip.save()
            else:
                condition = False
        else:
            if ip.trials >= 3:
                ip.tresh_time = timezone.now()
                condition = False
                time = 60
                ip.trials = 0
                ip.save()     

        return render(request, 'register.html',
        {
            'condition':condition,
            'state':state,
            'time':time,
        })

def verify(request):
    if request.method == 'GET':
        return HttpResponseRedirect(reverse('register'))
    else:
        ip = get_client_ip(request)
        ip.trials = ip.trials+1
        ip.save()
        phone = request.POST.get('username')
        return render(request, 'verify.html',{'p':phone})

def signUp(request, user):
    if request.method == 'GET':
        return HttpResponseRedirect(reverse('register'))
    else:
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()              
            ip = get_client_ip(request)
            ip.trials = 0
            ip.save()
            authenticate(username=user.username, password=user.password)
            return HttpResponseRedirect(reverse('show'))
    return render(request, 'signup.html',{
        'form':form,
        'user':user,
    })
