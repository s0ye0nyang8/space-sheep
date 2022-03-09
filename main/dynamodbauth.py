from botocore.exceptions import ClientError
from django.contrib import messages
from django.http import Http404 
import hashlib
import uuid
import boto3


def updateUserInfo(request,email,name,desc):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('user')
    try:
        response = table.update_item(
            Key={'email': email},
            UpdateExpression="SET userinfo.uname=:n, userinfo.description=:d" ,
            ExpressionAttributeValues= {':n': name, ':d': desc}
        )
        return response
    except ClientError as e:
        print(e)
        # raise Http404("User does not exist")

def updateRoomInfo(request,roomid,name,bg):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('room')
    try:
        response = table.update_item(
            Key={'roomid': roomid},
            UpdateExpression="SET roominfo.rname=:n, roominfo.bg=:b" ,
            ExpressionAttributeValues= {':n': name, ':b':bg}
        )
        return response

    except ClientError as e:
        print(e)

        # raise Http404("Room does not exist")

def myauthenticate(request,email,password):
    try:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('user')
        response = table.get_item(
            Key={'email': email}
        )
        # print(response)
        if 'Item' in response.keys():
            encoded_pass = hashlib.sha256(str(password).encode('utf-8')).hexdigest()
            if encoded_pass == response['Item']['password']:
                # set cache and session 
                request.session['user']=email
                return response['Item']['userinfo']

        messages.add_message(request,messages.ERROR,"id or password not correct")
        return None
        
    except ClientError as e:
        messages.add_message(request,messages.ERROR,"id or password not correct")
        return None

        
def createUser(request,email,password):
    enc = hashlib.sha256(str(password).encode('utf-8')).hexdigest()
    
    try:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('user')
        name ='아무개'
        room = str(uuid.uuid4())
        
        response = table.put_item(
            # TableName='user',
            Item= {
                "email":email,
                "password": enc,
                "userinfo":{
                    'uname':name,
                    'room':room,
                }
            },
            ConditionExpression= 'attribute_not_exists(email)'
        )
        table = dynamodb.Table('room')
        response = table.put_item(
            # TableName='user',
            Item= {
                "roomid":room,
                "roominfo":{
                    'rname':name+'의 spacesheep',
                    'bg': None,
                }
            },
            ConditionExpression= 'attribute_not_exists(room)'
        )
        return room

    except ClientError as e:
        if e.response['Error']['Code'] == "ConditionalCheckFailedException":
            messages.error(request, '이미 존재하는 아이디입니다.') 
            return False
    
def removeUser(request,email,password):
    try:
        dynamodb = boto3.resource('dynamodb')
        userinfo = dynamodb.Table("userinfo")
        response = userinfo.delete_item(
            Key={
                'email': email,
            },
            ConditionExpression="password == :val",
            ExpressionAttributeValues={
                ":val": hashlib.sha256(str(password).encode('utf-8')).hexdigest()
            }
        )
    except ClientError as e:
        if e.response['Error']['Code'] == "ConditionalCheckFailedException":
            print(e.response['Error']['Message'],"이메일 또는 비밀번호가 일치하지 않음")
        else:
            raise
    else:
        return response

def getUserinfo(email):
    try:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('user')
        response = table.get_item(
            Key={'email': email},
        )
        if 'Item' in response.keys():
            return response['Item']['userinfo']
        else:
            return None
        
    except ClientError as e:
        print(e)

def getRoominfo(room):
    try:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('room')
        response = table.get_item(
            Key={'roomid':room},
        )
        if 'Item' in response.keys():
            return response['Item']['roominfo']
        else:
            return None
        
    except ClientError as e:
        print(e)



