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
    print(request)
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
            CacheUser(email=email,room=uinfo['room'],name=uinfo['name']).cacheUser()
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
    
            response = createUser(request,email,pass1)
            
            if response:
                # korean -> unicode -> url format
                next_url = request.GET.get('next') or "home"
                return redirect(next_url)
        else:
            messages.error(request, '비밀번호가 일치하지 않습니다.')
        
        return redirect('login')

    if request.method == 'GET':
        return redirect('login')

# def create_bucket(bucket_name,region=None):
#     try:
#         s3_client = boto3.client('s3')
#         location = {'LocationConstraint':region}
#         s3_client.create_bucket(Bucket=bucket_name,CreateBucketConfiguration=location)
#     except ClientError as e:
#         logging.error(e)
#         return False
#     return True