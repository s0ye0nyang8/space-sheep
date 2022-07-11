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
        raise Http404("User does not exist")

def updateRoomInfo(roomid,rinfo):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('room')
    print(rinfo)
    try:
        response = table.update_item(
            Key={'roomid': roomid},
            UpdateExpression="SET roominfo.rname=:n, roominfo.islocked=:op, roominfo.blocklist=:bl",
            ExpressionAttributeValues= {':n': rinfo['rname'], ':op': rinfo['islocked'], ':bl':rinfo['blocklist']}
        )
        return response

    except ClientError as e:
        print(e)
        raise Http404("channel does not exist")



def myauthenticate(request,email,password):
    try:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('user')
        response = table.get_item(
            Key={'email': email}
        )
        if 'Item' in response.keys():
            encoded_pass = hashlib.sha256(str(password).encode('utf-8')).hexdigest()
            if encoded_pass == response['Item']['password']:
                # set cache and session 
                request.session['user']=email
                return response['Item']['userinfo']

        messages.add_message(request,messages.ERROR,"계정 정보가 일치하지 않습니다.")
        return None
        
    except ClientError as e:
        messages.add_message(request,messages.ERROR,"계정 정보가 일치하지 않습니다.")
        return None

        
def createUser(email,password):
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
                    'islocked':'off',
                    'blocklist':[],
                }
            },
            ConditionExpression= 'attribute_not_exists(roomid)'
        )
        return room

    except ClientError as e:
        return False
    
def removeUser(request,email,room,password):
    dynamodb = boto3.resource('dynamodb')
    userinfo = dynamodb.Table("user")
    response = userinfo.delete_item(
        Key={
            'email': email,
        },
        ConditionExpression="attribute_exists(email)"
    )
    dynamodb = boto3.resource('dynamodb')
    userinfo = dynamodb.Table("room")
    response = userinfo.delete_item(
        Key={
            'roomid': room,
        },
        ConditionExpression="attribute_exists(roomid)"
    )
    print(response)

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

