from django.core.cache import cache
from .dynamodbchat import get_latest_messages
from .dynamodbauth import getRoominfo
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
            self.next = nextkey
            self.content = content
        else:
            node = cache.get(self.mid)
            if node is not None:
                self.next = node['next']
                self.content = node['content']
    
    def cacheMessage(self):
        cache.set(self.mid, {'next':self.next, 'content':self.content}, timeout=None)

    def deleteMessage(self):
        tmp = self.content
        tmp['content']['text'] = None
        tmp['content']['media'] = None

        cache.set(self.mid, {'next':self.next, 'content':tmp}, timeout=None)

    def getMessage(self):
        return {'next':self.next, 'content':self.content}
    
    def getNext(self):
        return self.next

    def getContent(self):
        return self.content

async def getCachedLatestKey(room):
    key = cache.get('%s:latest'%room)
    
    if key is None:
        newkey = await caching_DBdata(room)
        if newkey is not None:
            cacheLatestKey(room,newkey)
    
    return cache.get('%s:latest'%room)

def cacheLatestKey(room, mid):
    cache.set('%s:latest'%room, mid, timeout=None)

async def getNewCacheMessage(room):
    key = await caching_DBdata(room)
    return key

async def caching_DBdata(room):
    # 데이터 db에서 가져와서 캐싱을 하고, 그중 가장 최신값의 mid 를 반환
    # startkey= request.session.get('startkey')
    items = await get_latest_messages(room=room,ExclusiveStartKey=None)
    # print("caching db data..")
    if items != []:
        # request.session.set('startkey', res['LastEvaluatedKey'])
        prev = None
        for item in reversed(items):
            mid = '_'.join([item['owner'],item['timestamp']])
            c_message = {
                'mid':mid,
                'content':item,
            }
            CacheMessage(mid=mid,nextkey=prev,content=c_message).cacheMessage()
            prev = mid
        
        return mid
    else:
        return None

async def get_cached_data(room,resource=None,latest_mid=None):
    messages = []
    # print("getting cached data..",room, latest_mid)
    
    if latest_mid is None:
        _mid = await getCachedLatestKey(room)
    else:
        _mid = latest_mid
    
    if _mid is not None:
        cnt = 15
        while cnt>0 and _mid is not None :
            message = CacheMessage(_mid).getMessage()
            messages.append(message['content'])
            
            if message['next'] is None:
                # check if this is 'real end'
                key = await getNewCacheMessage(room)
                # connect to previous cache
                if key is None: # real end
                    break
                CacheMessage(_mid,nextkey=key,content=message['content']).cacheMessage()
                _mid = key
            else:
                _mid = message['next']

            cnt -=1

    return messages

class CacheRoom:
    def __init__(self, roomid, name=None, bg=None):
        self.room = roomid
        self.roomname = name
        self.bg=bg
        if self.roomname is None:
            # roominfo = cache.get(roomid)
            # if roominfo is not None:
            #     self.roomname = roominfo['name']
            #     self.bg = roominfo['bg']
            # else:
            roominfo = getRoominfo(roomid)
            if roominfo is not None:
                self.roomname = roominfo['rname']
                self.bg = roominfo['bg']

    def cacheRoom(self):
        roominfo = {
            'name':self.roomname,
            'bg':self.bg
        }
        cache.set(self.room,roominfo,timeout=None)

    def getName(self):
        return self.roomname

    def getBg(self):
        return self.bg
        