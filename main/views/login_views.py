from django.shortcuts import render, redirect
from django.views.generic import View
from django.contrib import messages
from ..cache import *
from urllib import parse
import sys
import logging
import boto3
from botocore.exceptions import ClientError
from ..dynamodbauth import *

def login(request):
    if request.method == 'GET':
        uid = request.session.get('user')

        if uid is not None :
            response = CacheUser(uid).cacheUser()
            next_url = request.GET.get('next') or "home"
            return redirect(next_url)
        
        return render(request,'main/login.html')

    if request.method == 'POST':
        email = request.POST.get('userid')
        pass1 = request.POST.get('userpw')
        
        uinfo = myauthenticate(request, email=email, password=pass1)

        if uinfo:
            CacheUser(email=email,room=uinfo['room'],name=uinfo['uname']).cacheUser()
            CacheRoom(roomid=uinfo['room']).cacheRoom()
            next_url = request.POST.get('next') or "home" 
            # enc = parse.quote(self.user.getCachedRoom().encode('utf-8'))
            return redirect(next_url)

        return render(request,'main/login.html')
    

def logout(request):
    try:
        del request.session['user']
    except KeyError:
        pass
    return redirect('login')

def signup(request):
    if request.method == 'POST':
        email = request.POST['userid']
        pass1 = request.POST['password1']
        pass2 = request.POST['password2']
        
        if pass1 == pass2:
            roomid = createUser(request,email,pass1)
            if roomid:
                request.session['user']=email
                CacheUser(email=email,name='아무개',room=roomid).cacheUser()
                CacheRoom(roomid=roomid).cacheRoom()
                next_url = request.GET.get('next') or "home"
                return redirect(next_url)
        else:
            messages.error(request, '입력한 두 비밀번호가 일치하지 않습니다.')
        
        return redirect('login')

    if request.method == 'GET':
        return redirect('login')
