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
from ..cache import CacheRoom
from botocore.exceptions import ClientError
import uuid

def ask(request,room_name):
    user_id = request.session.get('user') 
    myroom = CacheUser(user_id).getCachedRoom()
    roominfo= {}
    thisroom = CacheRoom(room_name)

    if request.method == 'GET':
        name = thisroom.getName()
        
        return render(request, 'main/ask.html', {
            'room_name':room_name,
            'name':name,
            'user': myroom,
        })

    if request.method == 'POST':
        name =None
        bg=None
        if myroom==room_name:
            name = request.POST.get('rname')
            thisroom = CacheRoom(room_name)
            if name is None:
                name=thisroom.getName()
            res = CacheRoom(room_name).updateCacheRoom(name)
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
            