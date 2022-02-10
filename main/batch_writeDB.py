from botocore.exceptions import ClientError
from boto3.dynamodb.types import TypeSerializer
from boto3.dynamodb.conditions import Key
import asyncio
import boto3 

async def main():
    alluser = getAllUser()
    tasks = []
    
    for user in alluser:
        tasks.append(asyncio.create_task(writetoDB(user)))

    for task in tasks:
        await task
    

def getAllUser():
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
        print(_next,tmp)
        if tmp:
            items.append(tmp['content'])
            _next = tmp['next']
        else:
            break
    print(items)
    return items

async def writetoDB(user):
    items = await collectCache(user)

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('chat-message')
    try:
        for item in items:
            resource.batch_write_item(RequestItems={
                'chat-message': [{ 'PutRequest': { 'Item': item }}]
            })
            print(f'resource, specify none      : write succeeded.')
    except Exception as e:
        print(f'resource, specify none      : write failed: {e}')
    except ClientError as e:
        print(e)