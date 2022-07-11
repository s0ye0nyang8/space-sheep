from django.shortcuts import render, redirect, get_object_or_404

from django.utils.safestring import mark_safe
from django.contrib import messages
import json
from django.http import Http404

from ..dynamodbchat import get_latest_messages2
from ..dynamodbauth import getRoominfo, updateRoomInfo
from botocore.exceptions import ClientError
import uuid


def ask(request,room_name):
    uinfo = request.session.get('uinfo') 
    thisroom = getRoominfo(room=room_name)
    print(uinfo)
    print(thisroom)
    if request.method == 'GET':
        try:
            if thisroom['islocked']=='on':
                if uinfo is None:
                    messages.error(request, '로그인해야 이용 가능한 채널입니다.')
                    return redirect('home')
                    
                elif uinfo['room']==room_name:
                    return render(request, 'main/ask.html', {
                        'room_name':room_name,
                        'name': thisroom['rname'],
                        'user': uinfo['room'],
                    })
                else:
                    if uinfo['room'] in thisroom['blocklist']:
                        messages.error(request, '입장이 불가능한 채널입니다.')
                        return redirect('home')

            return render(request, 'main/ask.html', {
                'room_name':room_name,
                'name': thisroom['rname'],
                'user': uinfo['room'],
            })
        except:
            print("exception occured!")
            return render(request, 'main/ask.html', {
                    'room_name':room_name,
                    'name': thisroom['rname'],
                    'user': None,
                })

    if request.method == 'POST':
        raise Http404("올바른 접근이 아닙니다.")

    
def moment(request, room_name):
    messages = get_latest_messages2(room_name)
    # latestkey = getCachedLatestKey(room=room_name)
    # images = get_cached_data(room=room_name, startkey=latestkey)
    return render(request, 'main/moment.html', {"room_name":room_name,"messages":messages} )
