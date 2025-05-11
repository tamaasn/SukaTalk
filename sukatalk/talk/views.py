from django.shortcuts import render
from django.http import HttpResponse
import sqlite3
import random
from django.db import connection
from .auth_utils import create_account, login_user

# Create your views here.
conn = sqlite3.connect('db.sqlite3')
c = conn.cursor()

def login(request):
    return render(request,'index.html')

def randomize():
    result=""
    for i in range(15):
        result += str(random.randint(0,9))
    return result


def account_handler(request):
    if (request.method != "POST"):
        response = HttpResponse()
        response.status_code=403
        return response
    
    if (request.POST['indicator'] == "signup"):
        username = request.POST['username']
        email = request.POST['email']
        pin = randomize()
        password = request.POST['password']
        
        valid = create_account(email,username,password,pin)
        
        return HttpResponse(valid["message"]+"<br>"+str(valid["valid"]))
    elif (request.POST['indicator'] == "signin"):
        valid = login_user(request.POST['email'],request.POST['password'])
        status=""
        if valid:
            status="Login berhasil"
        else:
            status="Login gagal"
        return HttpResponse(status)
    else:
        return HttpResponse("INVALID!")
