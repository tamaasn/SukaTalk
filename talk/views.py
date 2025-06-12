from django.shortcuts import render, redirect
from django.http import HttpResponse
import sqlite3
import random
from django.db import connection
#from .auth_utils import create_account, login_user, get_chats, get_user_info, get_contacts, add_contact, check_valid_channel, insert_message, tz, now_utc, get_member_channels, get_member_event, tz, set_seen_message
from .auth_utils import *
import pusher
from datetime import datetime
from django.templatetags.static import static
import html
import re

pusher_client=#deklarasi variable pusher_client


# Create your views here.

def get_chat(request):
    channel = request.POST['channel']
    user_id=request.session['username']
    events = get_member_event([user_id])
    friend = get_friend_info(user_id,channel);
    friend_info=get_user_info(friend)
    print(friend_info['username'])
    for i in events:
        pusher_client.trigger("allevents",i,{'event':2,'username':friend_info['username'],'photo_profile':static(friend_info['photo_profile'])})


    data = get_chats(user_id,channel)

    return HttpResponse(data)

def delete_message(request):
    if request.method != "POST":
        response=HttpReponse("Method not allowed")
        response.status_code=403
        return response

    id_=request.POST['id']
    user_id=request.session['username']
    channel=request.POST['channel']
    request_delete_message(id_,user_id)

    user_info=get_user_info(user_id)
    user_event = user_info['event']
    members = get_member_channels(channel)
    events = get_member_event(members)

    for i in events:
        pusher_client.trigger("allevents",i,{'event':3})

    return HttpResponse("done")

def delete_chat(request):
    if request.method != "POST":
        response = HttpResponse("Method tidak diperbolehkan")
        response.status_code=403
        return response

    channel = request.POST['channel']
    request_delete_chat(channel,request.session['username'])
    events=get_member_event([request.session['username']])
    for i in events:
        pusher_client.trigger("allevents",i,{'event':1})
    return HttpResponse("done")


def handle_upload_file(file,file_dest):
    destination = open(file_dest,"wb+")
    for chunk in file.chunks():
        destination.write(chunk)
    destination.close()

def update_profile(request):
    if request.method != "POST":
        response = HttpResponse("method tidak diperbolehkan")
        response.status_code=403
        return response

    username = request.POST['username']
    avatar_file=""
    if "avatar" in request.FILES:    
        avatar = request.FILES['avatar']
        avatar_file="photo_profile/"+str(request.session['username'])+".jpg"
        handle_upload_file(avatar,"static/"+avatar_file)
    database_update_profile(username,avatar_file,request.session['username'])
    return redirect("/")

def seen_message(request):
    if request.method != "POST":
        response = HttpResponse("method dilarang!")
        response.status_code=403
        return response

    channel=request.POST['channel_id']
    user_id=request.session['username']
    set_seen_message(channel,user_id)
    members = get_member_channels(channel)
    events = get_member_event(members)

    for i in events:
        pusher_client.trigger("allevents",i,{'event':1})


    return HttpResponse("done")


def alert(message):
    return "<script> alert('{}'); </script>".format(message)

def href(url):
    return "<script> location.href='{}'; </script>".format(url)

def send_message(request):
    if request.method != "POST":
        response=HttpResponse("forbidden")
        response.status_code=403
        return response

    channel = request.POST['channel']
    message = html.escape(request.POST['message'])
#message=message.replace("\n","<hr>")

    time=datetime.now(tz).strftime("%Y-%m-%d %H:%M")
    user_info = get_user_info(request.session['username'])


    if check_valid_channel(channel,request.session['username']):
        user_event = user_info['event']
        members = get_member_channels(channel)
        events = get_member_event(members)

        new_id=insert_message(channel,request.session['username'],message)
        pusher_client.trigger(channel,'send',{'message':message,'time':time,'event':user_info['event'],'id':new_id,'username':user_info['username'],'pin':user_info['pin'],'photo_profile':static(user_info['photo_profile'])})


        for i in events:
            pusher_client.trigger("allevents",i,{'event':1})

        return HttpResponse("berhasil")
    else:
        response = HttpResponse("forbidden")
        response.status_code=403
        return response

def get_contact_lists(request):
    if request.method != 'GET':
        response = HttpResponse("method dilarang")
        response.status_code=403
        return response
    query=None
    sort=None
    if "query" in request.GET:
        print("search dimulai")
        query=request.GET["query"]
        sort=request.GET["sort"]
    contacts = get_contacts(request.session['username'],query,sort)
    result=""
    for i in contacts:
        base = f'<div class="chat-user"> <div onclick="change_channel(\'{i["channel_id"]}\')"><strong> {i["username"]} </strong> <br><span> {i["email"]} </span> <br>'
        if i['seen'] == 0:
            base += f"<i><b> {i['last_message']}  (New) </b></i>"
        else:
            base += f"<p> {i['last_message']} </p>"
        base += f"<span class='chat-time'>{i['last_timestamp']} </span> </div>"
        base += f"<br><button type='button' class='logout-button' onclick='delete_chat(\"{i['channel_id']}\")'><img src='https://img.icons8.com/?size=100&id=68064&format=png&color=000000' width='20' height='20'></button></div>"
        result += base

    return HttpResponse(result)



def login(request):
    if 'logged' in request.session:
        context=get_user_info(request.session['username'])
        contacts = get_contacts(request.session['username'])
        context['contacts'] = []
        for i in contacts:
            context['contacts'].append(i)
        print(context)
        return render(request,'main.html',context=context)
    return render(request,'index.html')

def send_contact(request):
    if request.method != "POST":
        return HttpResponse("method not allowed")

    friend = request.POST['name']
    pin = request.POST['pin']
    result = add_contact(request.session['username'],friend,pin)
    members = get_member_channels(result)
    events = get_member_event(members)
    for i in events:
        pusher_client.trigger("allevents",i,{'event':1})


    return HttpResponse("done")

def logout(request):
    if 'logged' in request.session:
        del request.session['logged']
        del request.session['username']
        return redirect("/")
    return HttpResponse("<h1> Logout gagal </h1>")

def account_handler(request):
    if (request.method != "POST"):
        response = HttpResponse()
        response.status_code=403
        return response

    if (request.POST['indicator'] == "signup"):
        email = html.escape(request.POST['email'])
        username = html.escape(request.POST['username'])
        if 'logged' in request.session:
            return redirect('/');
        if "uin-suka.ac.id" not in email.split("@")[1]:
            return HttpResponse("harap menggunakan email UIN")

        password = request.POST['password']

        valid = create_account(email,username,password)
        if valid['valid']:
            request.session['username']=valid['id']
            request.session['logged']=True

        return HttpResponse(alert(valid['message'])+href('/'));
    elif (request.POST['indicator'] == "signin"):
        valid = login_user(request.POST['email'],request.POST['password'])
        status="Login gagal"
        if valid > 0:
            request.session['username']=valid
            request.session['logged']=True
            status="Login berhasil"
        return HttpResponse(alert(status)+href("/"));
    else:
        return HttpResponse("INVALID!")
