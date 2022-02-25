from botocore.exceptions import ClientError
from boto3.dynamodb.types import TypeSerializer
from boto3.dynamodb.conditions import Key
from django.core.cache import cache

import asyncio
import boto3 

async def batch_write():
    alluser = await getAllUser()
    
    tasks = []
    
    if alluser:    
        for user in alluser:
            room = user['userinfo']['room']
            tasks.append(asyncio.create_task(writetoDB(room)))
        
        for task in tasks:
            await task
    

async def getAllUser():
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('chat-message')
    try:
        table = dynamodb.Table('user')
        response = table.scan(
            Select='SPECIFIC_ATTRIBUTES',
            AttributesToGet=[
                'userinfo',
            ],
        )
        items = response['Items']
        return items
    except ClientError as e:
        print(e)

async def collectCache(room):
    _next = cache.get('%s:latest'%room)
    items =[]

    while _next is not None:
        tmp = cache.get(_next)
        # print('tmp', tmp)
        if tmp:
            items.append(tmp['content'])
            _next = tmp['next']
        else:
            break
            
    return items

async def writetoDB(user):
    items = await collectCache(user)

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('chat-message')
    try:
        for item in items:
            dynamodb.batch_write_item(RequestItems={
                'chat-message': [{ 'PutRequest': { 'Item': item['content'] }}]
            })
            print(f'resource, specify none      : write succeeded.')
    except Exception as e:
        print(f'resource, specify none      : write failed: {e}')
    except ClientError as e:
        print(e)