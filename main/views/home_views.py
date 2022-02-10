from django.shortcuts import render, redirect, get_object_or_404
from django.shortcuts import render
from django.utils.safestring import mark_safe
import json
from ..cache import *


def home(request):
    user_id = request.session.get('user') #세션으로부터 유저 정보 가져오기
    if user_id is None:
        return redirect('login')
    else:
        # 캐시 유저 정보 안사라진다고 가정
        user = CacheUser(user_id)
        room = user.getCachedRoom()
        owner = user.getCachedName()
        print(room,owner)
        if room is None:
            try:
                del request.session['user']
            except KeyError:
                pass
            return redirect('login')
        else:  
            return render(request, 'main/home.html',{"owner":owner,"room_name":room})
    
# def mypage(request,pk):

#     user_id = request.session.get('user') #세션으로부터 유저 정보 가져오기
#     user = CacheUser(user_id)

#     if user_id and name==pk:
#         if request.method == 'GET':
#             return render(request,'main/mypage.html',{"ask_name":user.getCachedName(),"room_name":user.getCachedRoom()})
#     else:
#         return redirect('login')
