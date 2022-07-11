from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils.safestring import mark_safe
import json
from ..cache import *
from ..dynamodbauth import updateUserInfo, updateRoomInfo, removeUser, myauthenticate, getRoominfo
from ..dynamodbchat import uploadImageS3

def home(request):
    if request.method == 'GET':
        uinfo = request.session.get('uinfo') #세션으로부터 유저 정보 가져오기
        rinfo = None
        if uinfo is not None:
            rinfo = getRoominfo(uinfo['room'])
        return render(request, 'main/home.html',{"user": uinfo,"rinfo":rinfo,"popup":None})

    if request.method == 'POST':
        pass

def deregister(request):
    try:
        email = request.POST['email']
        password = request.POST['password']
        uinfo = request.session['uinfo']

        room = uinfo['room']
        res = myauthenticate(request,email,password)
        if res is not None:
            removeUser(request,email=email,room=room,password=password)
            messages.success(request,'계정이 삭제되었습니다.')
            del request.session['uinfo']
            
        return redirect('home')

    except:
        messages.error(request, '인증에 실패했습니다.')
        return redirect('home')

def setting(request):
    
    if request.method == 'POST':
        uinfo = request.session.get('uinfo')
        rinfo = getRoominfo(uinfo['room'])
        blocklist = []

        if 'blocklist' in rinfo.keys():
            blocklist = rinfo['blocklist']

        try:
            rinfo = {
                'rname' : request.POST.get('rname'),
                'islocked' : request.POST.get('memberonly'),
                'blocklist': blocklist,
            }
            res = updateRoomInfo(roomid=uinfo['room'], rinfo=rinfo)
        except:
            raise Http404("권한이 없습니다.")

        try:
            bg = request.FILES.get('bg-file')
            if bg is not None:
                res = uploadImageS3(bg,uinfo['room'])
        except:
            raise Http404("User does not exist")
        
        messages.error(request, '설정이 변경되었습니다.')
           
        return redirect('home') #/home/ask/{room_name}