from django.core.cache import cache
from .dynamodbchat import get_latest_messages
from .dynamodbauth import getRoominfo, updateRoomInfo
from django.http import Http404  

class CacheUser:
    
    def __init__(self, email, name=None, room=None):
        self.email = email
        self.name = None
        self.room = None
        self.desc = None

        if self.email is not None:
            if name is None and room is None:
                userinfo = cache.get(self.email)
                if userinfo is not None:
                    self.room = userinfo['room']
                    self.name = userinfo['name']
            else:
                self.room = room
                self.name = name

    def getCachedName(self):
        return self.name

    def getDescription(self):
        return self.desc
    
    def getCachedRoom(self):
        return self.room

    def cacheUser(self,name=None,desc=None):
        self.name = name or self.name 
        self.desc = desc or self.desc
        userinfo = {
            'name':self.name,
            'room':self.room,
            'desc':self.desc
        }
        cache.set(self.email,userinfo,timeout=None)
        

class CacheMessage:
    def __init__(self, mid, nextkey=None, content=None):
        self.mid = mid
        self.nextkey = None
        self.content = None

        if content is not None:
            self.nextkey = nextkey
            self.content = content
        else:
            node = cache.get(self.mid)
            if node is not None:
                self.nextkey = node['next']
                self.content = node['content']
    
    def cacheMessage(self):
        cache.set(self.mid, {'next':self.nextkey, 'content':self.content}, timeout=None)

    def deleteMessage(self):
        tmp = self.content
        tmp['content']['text'] = None
        tmp['content']['media'] = None

        cache.set(self.mid, {'next':self.nextkey, 'content':tmp}, timeout=None)

    def getMessage(self):
        return {'next':self.nextkey, 'content':self.content}
    
    def getNext(self):
        return self.nextkey

    def getContent(self):
        return self.content

def getCachedLatestKey(room):
    key = cache.get('%s:latest'%room)
    return key

def setLatestKey(room, mid):
    cache.set('%s:latest'%room, mid, timeout=None)

async def cacheNewDBMessage(room,startkey=None):
    items = await get_latest_messages(room=room,ExclusiveStartKey=startkey)
    if items is not None:
        return await cachingDBdata(items,room)
    return None
    
async def cachingDBdata(items,room):
    prev = None
    for item in reversed(items):
        mid = '_'.join([item['owner'],item['timestamp']])
        c_message = {
            'mid':mid,
            'content':item,
        }
        CacheMessage(mid=mid,nextkey=prev,content=c_message).cacheMessage()
        prev = mid
    # return latest among newdata
    return prev

def get_cached_data(room,resource=None,startkey=None):
    messages = []
    # cache empty
    # key = startkey
    # if startkey is None:
    #     # caching data
    #     key = await cacheNewDBMessage(room)
    #     # key == latestkey
    #     setLatestKey(room=room,mid=startkey)
    #     if key is None:
    #         return []
    
    # at least 1 cache data
    cnt = 8
    if startkey:
        key = startkey
        message = CacheMessage(key).getMessage()
        while cnt>0 and message['content'] is not None :
            messages.append(message['content'])
            # if message['next'] is None:
            #     # check if this is 'real end'
            #     ExclusiveStartKey = {
            #         'owner': message['content']['content']['owner'],
            #         'timestamp':message['content']['content']['timestamp'],
            #     }
            #     nextkey = await cacheNewDBMessage(room,ExclusiveStartKey)
            #     # connect to previous cache
            #     if nextkey is None: # real end
            #         return messages
            #     CacheMessage(key,nextkey=nextkey,content=message['content']).cacheMessage()
            #     message = CacheMessage(nextkey).getMessage()
            # else:
            message = CacheMessage(message['next']).getMessage()
            cnt -=1

    return messages

# class CacheRoom:
#     def __init__(self, roomid, name=None, bg=None):
#         self.room = roomid
#         self.roomname = name
#         if self.roomname is None:
#             roominfo = cache.get(roomid)
#             if roominfo is not None:
#                 self.roomname = roominfo['name']
#             else:
#                 roominfo = getRoominfo(self.room)
#                 if roominfo is not None:
#                     self.roomname = roominfo['rname']

#     def cacheRoom(self):
#         roominfo = {
#             'name':self.roomname
#         }
#         cache.set(self.room,roominfo,timeout=None)

#     def updateCacheRoom(self,name):
#         self.roomname= name
#         self.cacheRoom()
#         return updateRoomInfo(self.room, name)

#     def getName(self):
#         return self.roomname

        