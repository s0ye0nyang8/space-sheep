from botocore.exceptions import ClientError
from boto3.dynamodb.types import TypeSerializer
from boto3.dynamodb.conditions import Key

import boto3 
from django.http import Http404   
import base64

def delete_DBmessage(data):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('chat-message')
    mid = data['mid'].split('_')
    try:
        response = table.delete_item(
            Key={
                'owner':mid[0],
                'timestamp':mid[1],
            },
        )
        return response
    except ClientError as e:
        print(e)
    


async def get_latest_messages(room,ExclusiveStartKey):
    print("get_latest_messages..")
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('chat-message')
    # option = ExclusiveStartKey=ExclusiveStartKey
    try:
        if ExclusiveStartKey is not None:
            response = table.query(
                KeyConditionExpression=Key('owner').eq(room),
                Limit=40,
                ScanIndexForward=False,
                ConsistentRead=True,
                ExclusiveStartKey=ExclusiveStartKey
            )
        else:
            response = table.query(
                KeyConditionExpression=Key('owner').eq(room),
                Limit=40,
                ScanIndexForward=False,
                ConsistentRead=True,
            )
            # print(response['Items'])
        return response['Items']

    except ClientError as e:
        print(e)
    

async def get_presigned_url(method,filename):
    url = await create_presigned_post(method=method,bucket_name='test-boo', object_name=filename)
    if url is not None:
        return url
    else:
        print("fail to get url")
        return None

async def create_presigned_post(method, bucket_name, object_name):
    try:
        url = boto3.client('s3').generate_presigned_url(
            ClientMethod=method, 
            Params={'Bucket': bucket_name, 'Key': object_name},
            ExpiresIn=72*600)
        # encoded = base64.urlsafe_b64encode(bytes(url, 'UTF-8')).decode("UTF-8")#.rstrip("=")
        # print("encoded url:",encoded)
        
        return url
        # String policyEnc = EncodingUtil.base64Encode(Blob.valueOf(strpolicy));
        # policyEnc = policyEnc.replace('+','-').replace('=','_').replace('/','~');
    except ClientError as e:
        print(e)
        return None 


    



