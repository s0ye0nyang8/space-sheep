from django.shortcuts import render, redirect, get_object_or_404
from ..cache import CacheUser
from django.utils.safestring import mark_safe
import json
from django.http import Http404
from urllib import parse
# for s3 presigned URL
import logging
import boto3

from ..dynamodbchat import uploadImageS3
from ..dynamodbauth import getRoominfo, updateRoomInfo
from botocore.exceptions import ClientError
import uuid
from ipware import get_client_ip


def ask(request,room_name):
    user_id = request.session.get('user') 
    myroom = CacheUser(user_id).getCachedRoom()
    # roominfo= {}
    # thisroom = CacheRoom(room_name)
    client_ip, is_routable = get_client_ip(request)
    print(client_ip,"entered room")
    if request.method == 'GET':
        # name = thisroom.getName()
        roominfo = getRoominfo(room_name)
        return render(request, 'main/ask.html', {
            'room_name':room_name,
            'name':roominfo['rname'],
            'user': myroom,
        })

    if request.method == 'POST':
        name =None
        bg=None
        if myroom==room_name:
            name = request.POST.get('rname')
            # thisroom = CacheRoom(room_name)
            if name is None:
                name=getRoominfo(room_name)
            # res = CacheRoom(room_name).updateCacheRoom(name)
            res = updateRoomInfo(room_name,name)
            try:
                bg = request.FILES['bg-file']
                res = uploadImageS3(bg,room_name)
            except:
                pass
            
            return render(request, 'main/ask.html', {
                    'room_name':room_name,
                    'name':name,
                    'user': myroom,
                })
        else:
            pass
            