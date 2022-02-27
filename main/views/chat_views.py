from django.shortcuts import render, redirect, get_object_or_404
from ..cache import CacheUser
from django.utils.safestring import mark_safe
import json
from django.http import Http404
from urllib import parse
# for s3 presigned URL
import logging
import boto3
from ..dynamodbauth import getRoominfo, updateRoomInfo

from botocore.exceptions import ClientError
import uuid

def ask(request,room_name):
    if request.method == 'GET':
        user_id = request.session.get('user') # 세션으로부터 유저 정보 가져오기
        myroom = CacheUser(user_id).getCachedRoom()
        
        # room info 는 cache 굳이?
        # thisroom = CacheRoom(room_name)
        # name = thisroom.getName()
        # bg = thisroom.getBg()

        rinfo = getRoominfo(room_name)
        return render(request, 'main/ask.html', {
            'room_name':room_name,
            'roominfo': {
                'name':rinfo['rname'],
                'bg':rinfo['bg']
            },
            'user': myroom,
        })

    if request.method == 'POST':
        user_id = request.session.get('user') 
        myroom = CacheUser(user_id).getCachedRoom()
        
        if myroom==room_name:
            name = request.POST.get('rname')

            updateRoomInfo(request,room_name,name,None)
            # CacheRoom(room_name,name,None).cacheRoom()
            
            return render(request, 'main/ask.html', {
                'room_name':room_name,
                'roominfo': {
                    'name':name,
                    # 'bg':bg
                },
                'user': myroom,
            })