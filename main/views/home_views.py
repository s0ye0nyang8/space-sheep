from django.shortcuts import render, redirect, get_object_or_404
from django.shortcuts import render
from django.utils.safestring import mark_safe
import json
from ..cache import *
from ..dynamodbauth import updateUserInfo


def home(request):
    if request.method == 'GET':
        user_id = request.session.get('user') #세션으로부터 유저 정보 가져오기
        if user_id is None:
            return redirect('login')
        else:
            # 캐시 유저 정보 안사라진다고 가정
            user = CacheUser(user_id)
            room = user.getCachedRoom()
            nickname = user.getCachedName()
            if room is None:
                try:
                    del request.session['user']
                except KeyError:
                    pass
                return redirect('login')
            else:
                return render(request, 'main/home.html',{"nickname":nickname,"room_name":room})
    
    if request.method == 'POST':
        user_id = request.session.get('user')
        user = CacheUser(user_id)
        
        room = user.getCachedRoom()
        nickname = request.POST.get('nickname')
        
        if nickname is not None:
            # cache update (room/user)
            # update userinfo
            updateUserInfo(request,user_id,nickname,None)
            CacheUser(email=user_id,name=nickname,room=room).cacheUser()

        return render(request, 'main/home.html',{"nickname":nickname,"room_name":room})


    
    
