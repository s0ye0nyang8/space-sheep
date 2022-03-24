from botocore.exceptions import ClientError
from boto3.dynamodb.types import TypeSerializer
from boto3.dynamodb.conditions import Key
import boto3 
from django.core.cache import cache
import asyncio
import os

def batch_write():
    alluser = getAllUser()
    
    if alluser:    
        for user in alluser:
            room = user['userinfo']['room']
            items=collectCache(user)
            writetoDB(room,items)
    

def getAllUser():
    dynamodb = boto3.resource('dynamodb')
    try:
        table = dynamodb.Table('user')
        response = table.scan(
            Select='SPECIFIC_ATTRIBUTES',
            AttributesToGet=[
                'userinfo',
            ],
        )
        items = response['Items']
        print(response)
        return items
    except ClientError as e:
        print(e)

def collectCache(room):
    _next = cache.get('%s:latest'%room)
    items =[]
    cnt = 0
    while cnt<50 and _next:
        cnt+=1
        tmp = cache.get(_next)
        if tmp:
            items.append(tmp['content'])
            _next = tmp['next']
        else:
            break            
    return items

def writetoDB(user,items):
    
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('messages-1')
    try:
        response = table.put_item(Item=items)
        # for item in items:
        #     dynamodb.batch_write_item(RequestItems={
        #         'messages-1': [{ 'PutRequest': { 'Item': [item] }}]
        #     })
        print(f'{user}     : write succeeded.')
    except Exception as e:
        print(f'{user}      : write failed: {e}')
    except ClientError as e:
        print(e)


if  __name__ == "__main__":
    batch_write()