from botocore.exceptions import ClientError
from boto3.dynamodb.types import TypeSerializer
from boto3.dynamodb.conditions import Key
import boto3 
from django.core.cache import cache
import asyncio
import os

async def batch_write():
    alluser = await getAllUser()
    if alluser:    
        for user in alluser[:100]:
            room = user['userinfo']['room']
            items = await collectCache(user)
            await bwritetoDB(room,items)
    
async def getAllUser():
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

async def collectCache(room):
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

# async def writetoSecondDB(user,items):
    
#     dynamodb = boto3.resource('dynamodb')
#     table = dynamodb.Table('messages-2')
#     try:
#         response = table.put_item(Item=items)
#     except Exception as e:
#         print(f'{user}      : write failed: {e}')


async def writetoDB(user,db,items):
    
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(db)
    try:
        response = table.put_item(Item=items)
    except Exception as e:
        print(f'{user}      : write failed: {e}')


async def bwritetoDB(user,db,items):  
    print(items)
    
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(db)
    try:
        for i in items:
            response = await table.put_item(Item=i)
        
        print(f'{user}     : write succeeded.')
    except Exception as e:
        print(f'{user}      : write failed: {e}')
    except ClientError as e:
        print(e)


if  __name__ == "__main__":
    batch_write()