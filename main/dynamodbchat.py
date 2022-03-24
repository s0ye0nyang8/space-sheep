from botocore.exceptions import ClientError
from boto3.dynamodb.types import TypeSerializer
from boto3.dynamodb.conditions import Key
import boto3 
from django.http import Http404   
import base64

def delete_DBmessage(data):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('messages-1')
    # mid = data['mid'].split('_')
    try:
        response = table.delete_item(
            Key={
                'mid':mid,
            },
        )
        return response
    except ClientError as e:
        print(e)
    

async def get_latest_messages(room,ExclusiveStartKey=None):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('messages-1')
    # option = ExclusiveStartKey=ExclusiveStartKey
    try:
        if ExclusiveStartKey is not None:
            timestamp = int(ExclusiveStartKey.split('_')[1])
            response = table.query(
                KeyConditionExpression=Key('owner').eq(room)&Key('timestamp').lt(timestamp), 
                Limit=10,
                ScanIndexForward=False,
                ConsistentRead=True
            )
        else:
            response = table.query(
                KeyConditionExpression=Key('owner').eq(room),
                Limit=10,
                ScanIndexForward=False,
                ConsistentRead=True,
            )
        for i in response['Items']:
            i['timestamp']=str(i['timestamp'])
        return response['Items']

    except ClientError as e:
        print(e)
    

async def get_presigned_url(method,filename):
    url = await create_presigned_post(method=method,bucket_name='test-boo', object_name=filename)
    if url is not None:
        return url
    else:
        # print("fail to get url")
        return None

async def create_presigned_post(method, bucket_name, object_name):
    try:
        url = boto3.client('s3').generate_presigned_url(
            ClientMethod=method, 
            Params={'Bucket': bucket_name, 'Key': object_name},
            ExpiresIn=7*24*600)
        # encoded = base64.urlsafe_b64encode(bytes(url, 'UTF-8')).decode("UTF-8")#.rstrip("=")
        # print("encoded url:",encoded)
        
        return url
        # String policyEnc = EncodingUtil.base64Encode(Blob.valueOf(strpolicy));
        # policyEnc = policyEnc.replace('+','-').replace('=','_').replace('/','~');
    except ClientError as e:
        print(e)
        return None 

def uploadImageS3(file,owner):
    try:
        response = boto3.client('s3').put_object(
            ACL='public-read',
            Body=file,
            Bucket='sheep-1',
            Key=owner
        )
        print("upload",response)
        return response
    except ClientError as e:
        print(e)

# def getImageS3(filename):
#     try:
#         response = boto3.client('s3').get_object(
#             Bucket='sheep-1',
#             Key=filename
#         )
#         return response['Body']
#     except ClientError as e:
#         print(e)
#         return None 