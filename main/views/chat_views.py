from django.shortcuts import render, redirect, get_object_or_404
from ..cache import CacheUser, getOwner
from django.utils.safestring import mark_safe
import json
from django.http import Http404
from urllib import parse
# for s3 presigned URL
import logging
import boto3
from botocore.exceptions import ClientError
import uuid

def ask(request,room_name):
    user_id = request.session.get('user') # 세션으로부터 유저 정보 가져오기
    myroom = CacheUser(user_id).getCachedRoom()
    owner = getOwner(room_name)
    
    if owner is None:
        return redirect('login')
    
    return render(request, 'main/ask.html', {
        'room_name':room_name,
        'owner':owner,
        'user': myroom,
    })
