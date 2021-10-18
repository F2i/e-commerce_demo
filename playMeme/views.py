from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.
# procedure a request return a response

def cal():
    x = 1
    y = 2
    return x + y

def say_hello(request):
    # pull data from database
    # send email
    # return HttpResponse("dit me may")
    x = cal()
    return render(request, 'index.html', {'cac': 'wtf'})