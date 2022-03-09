from django.shortcuts import render
from django.http import JsonResponse
from json import JSONEncoder
from django.views.decorators.csrf import csrf_exempt
from web.models import User, Token, Expense, Income
from datetime import datetime

# Create your views here.
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



