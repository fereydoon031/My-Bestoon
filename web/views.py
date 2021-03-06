# -*- coding: utf-8 -*-

import requests
from django.shortcuts import render
from django.http import JsonResponse
from json import JSONEncoder
from django.views.decorators.csrf import csrf_exempt
from web.models import User, Token, Expense, Income, Passwordresetcodes
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

from django.contrib.auth.hashers import make_password
from datetime import datetime
from django.conf import settings
import random
import string
import time
import os
from django.core.mail import EmailMessage
from django.core.mail import send_mail


random_str = lambda N: ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(N))

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def grecaptcha_verify(request):
    #logger.debug("def grecaptcha_verify: " + format(request.POST))
    data = request.POST
    captcha_rs = data.get('g-recaptcha-response')
    url = "https://www.google.com/recaptcha/api/siteverify"
    params = {
        'secret': settings.RECAPTCHA_SECRET_KEY,
        'response': captcha_rs,
        'remoteip': get_client_ip(request)
    }
    verify_rs = requests.get(url, params=params, verify=True)
    verify_rs = verify_rs.json()
    return verify_rs.get("success", False)

@csrf_exempt
def submit_income(request):
    """ user submit an expense"""
    #return HttpResponse("We are here")
    this_token =  request.POST.get('token','')
    if User.objects.filter(token__token = this_token).exists():
        this_user = User.objects.filter(token__token = this_token).get()

        if 'date' not in request.POST :
            date = datetime.now()
        Income.objects.create(user=this_user,amount= request.POST['amount'],
                    text = request.POST['text'], date = date)
        
        print (request.POST)

        return  JsonResponse({
            'status' : 'ok'
        }, encoder =JSONEncoder)
    else :
        return  JsonResponse({
            'status' : 'False'
        }, encoder =JSONEncoder) 


@csrf_exempt
def submit_expense(request):
    """ user submit an expense"""
    #return HttpResponse("We are here")
    this_token =  request.POST.get('token','')
    if User.objects.filter(token__token = this_token).exists():
        this_user = User.objects.filter(token__token = this_token).get()

        if 'date' not in request.POST :
            date = datetime.now()
        Expense.objects.create(user=this_user,amount= request.POST['amount'],
                    text = request.POST['text'], date = date)
        
        print (request.POST)

        return  JsonResponse({
            'status' : 'ok'
        }, encoder =JSONEncoder)
    else :
        return  JsonResponse({
            'status' : 'False'
        }, encoder =JSONEncoder) 

def index(request):
    context = {}
    return render(request,'index.html', context)

def user_login(request):

    if 'dologin' in request.POST: #form is filled. if not spam, generate code and save in db, wait for email confirmation, return message
        if not grecaptcha_verify(request): # captcha was not correct
            context = {'message': 'کپچای گوگل درست وارد نشده بود. شاید ربات هستید؟ کد یا کلیک یا تشخیص عکس زیر فرم را درست پر کنید.'} #TODO: forgot password
            return render(request, 'login.html', context)

        if User.objects.filter(username = request.POST['username']).exists(): # duplicate email
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    context = {'message': 'شما لاگین شدین'} #TODO: forgot password
                    return render(request, 'login.html', context)
                else:
                    return HttpResponse('your account is disabled')
            else:
                context = {'message': 'نام کاربری یا کلمه عبور اشتباه بود'}
                return render(request, 'login.html', context)
        else:
            context = {'message': 'شما حساب فعالی در بستون من ندارید لطفا ابتدا ثبت نام نمایید.'} #TODO: forgot password
            #TODO: keep the form data
            redirect('/web/accounts/login')
            return render(request, 'login.html', context)
            
    else:
        context = {'message': ''}
        return render(request, 'login.html', context)

def register(request):
    if 'requestcode' in request.POST: #form is filled. if not spam, generate code and save in db, wait for email confirmation, return message
        #is this spam? check reCaptcha
        if not grecaptcha_verify(request): # captcha was not correct
            context = {'message': 'کپچای گوگل درست وارد نشده بود. شاید ربات هستید؟ کد یا کلیک یا تشخیص عکس زیر فرم را درست پر کنید. ببخشید که فرم به شکل اولیه برنگشته!'} #TODO: forgot password
            return render(request, 'register.html', context)

        if User.objects.filter(email = request.POST['email']).exists(): # duplicate email
            context = {'message': 'متاسفانه این ایمیل قبلا استفاده شده است. در صورتی که این ایمیل شما است، از صفحه ورود گزینه فراموشی پسورد رو انتخاب کنین. ببخشید که فرم ذخیره نشده. درست می شه'} #TODO: forgot password
            #TODO: keep the form data
            return render(request, 'register.html', context)

        if not User.objects.filter(username = request.POST['username']).exists(): #if user does not exists
                code = random_str(28)
                now = datetime.now()
                email = request.POST['email']
                password = make_password(request.POST['password'])
                username = request.POST['username']
                temporarycode = Passwordresetcodes (email = email, time = now, code = code, username=username, password=password)
                temporarycode.save()

                message = "برای فعال سازی ایمیلی بستون من روی لینک روبرو کلیک کنید: {}?email={}&code={}".format(request.build_absolute_uri('/web/accounts/register/') ,email, code)
                mail_subject = "فعال سازی اکانت بستون من برای شما ارسال شد."
                email = EmailMessage( mail_subject, message,'ferydoon.jafari@gmail.com', [email]   )
                email.send()
                context = {'message': 'ایمیلی حاوی لینک فعال سازی اکانت به شما فرستاده شده، لطفا پس از چک کردن ایمیل، روی لینک کلیک کنید.'}
                return render(request, 'login.html', context)
        else:
            context = {'message': 'متاسفانه این نام کاربری قبلا استفاده شده است. از نام کاربری دیگری استفاده کنید. ببخشید که فرم ذخیره نشده. درست می شه'} #TODO: forgot password
            #TODO: keep the form data
            return render(request, 'register.html', context)
    elif  'code' in request.GET: # user clicked on code
        email = request.GET['email']
        code = request.GET['code']
        if Passwordresetcodes.objects.filter(code=code).exists(): #if code is in temporary db, read the data and create the user
            new_temp_user = Passwordresetcodes.objects.get(code=code)
            newuser = User.objects.create(username=new_temp_user.username, password=new_temp_user.password, email=email)
            this_token =  random_str(48)
            token = Token.objects.create(user=newuser,token=this_token)
            Passwordresetcodes.objects.filter(code=code).delete() #delete the temporary activation code from db
            context = {'message': 'اکانت شما فعال شد توکن شما {} است. آن را ذخیره کنید چون دیگر نمایش داده نمی شود.'.format(this_token)}
            return render(request, 'login.html', context)
        else:
            context = {'message': 'این کد فعال سازی معتبر نیست. در صورت نیاز دوباره تلاش کنید'}
            return render(request, 'login.html', context)
    else:
        context = {'message': ''}
        return render(request, 'register.html', context)

def user_logout(request):
    if not request.user.is_anonymous:
        logout(request)
    return redirect('/')