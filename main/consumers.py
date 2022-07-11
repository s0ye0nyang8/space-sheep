from channels.generic.websocket import AsyncWebsocketConsumer
# from .models import Message
# from channels.db import database_sync_to_async
from datetime import datetime
from django.conf import settings
from .cache import *
from .dynamodbchat import *
from .batch_write_task import writetoDB, batch_write
import time, json
import base64, random
import requests 
import boto3
from urllib import parse


class AskConsumer(AsyncWebsocketConsumer):
    blocklist = []

    async def new_message(self,data):
        url = None
        # message caching --> removed temporarily
        try:
            if data['media'] is not None:
                print("there is media url")
                url = await get_presigned_url(method='get_object',filename=data['media'])
                # latestkey = getCachedLatestKey(room=self.room_name)
                # CacheMessage(mid=mid,nextkey=latestkey,content=url).cacheMessage()
                # setLatestKey(room=self.room_name, mid=mid)
        except:
            pass
        
        message = {
            'owner':self.room_name,
            'mid': '_'.join([self.room_name,data['timestamp']]),
            'content':{
                'user':data['user'],
                'text':data['text'],
                'media': url,# 수정된 값,
            },
            'timestamp':int(data['timestamp']),
        }
        await writetoDB(user=self.room_name,db='messages-1',items=message)
         
        # latestkey = await getCachedLatestKey(room=self.room_name)
        # CacheMessage(mid=mid,nextkey=latestkey,content=message).cacheMessage()
        # setLatestKey(room=self.room_name,mid=mid)

        await self.channel_layer.group_send(
            self.room_group_name, {
                'type':"chat.message",
                'command':"new_message",
                'message': [message]
            }
        )

    async def delete_message(self,data):
        response = delete_DBmessage(db='messages-1',data=data)
        mid = data['mid']
        if response['ResponseMetadata']['HTTPStatusCode']==200:
            # CacheMessage(mid).deleteMessage()
            content = {
                'type':"chat.message",
                'command':"delete_message",
                "message":{
                    'mid':mid,
                },
            }
            await self.channel_layer.group_send(
                self.room_group_name,
                content
            )
    
    async def presigned_url(self,data):
        url = await get_presigned_url(method=data['method'],filename=data['media'])
        if url is not None:
            encoded = parse.quote(url)
            await self.send(text_data=json.dumps({
               "command":"readyto_upload",
               "message":{
                    "url" : url,
                    "fileName":data['media']
               }
            }))

    async def fetch_message(self,data):
        top_message = data['top_message']
        if top_message is not None:
            messages = await get_latest_messages(room=self.room_name,db='messages-1',ExclusiveStartKey=top_message)
            # if messages:
            #     del messages[0]
        else:
            messages = await get_latest_messages(room=self.room_name,db='messages-1')
            # latest_mid = await getCachedLatestKey(self.room_name)
            # messages = await get_cached_data(room=self.room_name, startkey=latest_mid)
        
        await self.send(text_data=json.dumps({
            "command":"fetch_message",
            "message": messages,
            "top_message":top_message,
        },))

    async def keep_message(self,data):
        print('this is kept message')
        owner,timestamp=data['mid'].split('_')
        message = await getMessage(owner,'messages-1',timestamp)
        print(message)
        await writetoDB(user=self.room_name,db='message-2',items=message)

    
    async def block(self,data):
        print('user blocked')
        rinfo = getRoominfo(self.room_name)
        rinfo['blocklist'].append(data['user'])
        updateRoomInfo(self.room_name,rinfo)
    
    commands = {
        'fetch_message':fetch_message,
        'new_message':new_message,
        'delete_message':delete_message,
        'presigned_url':presigned_url,
        'addMoment':keep_message,
        'blockUser': block
    }

    async def connect(self):
        self.room_name = self.scope["url_route"]['kwargs']["room_name"]
        self.room_group_name = 'chat_%s' % self.room_name
        # print("channel name",self.channel_name)
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self,close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
    
    async def receive(self, text_data): 
        data = json.loads(text_data)
        await self.commands[data['command']](self,data['message'])
        
    async def chat_message(self, event):
        message = event['message']
        command = event['command']
        await self.send(text_data=json.dumps({
            'command':command,
            'message': message,
        }))
