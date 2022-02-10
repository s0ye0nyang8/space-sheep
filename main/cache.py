from django.core.cache import cache
from .dynamodbauth import getUserinfo, updateUsername
from .dynamodbchat import get_latest_messages
from django.http import Http404  

class CacheUser:
    
    def __init__(self, email, name=None, room=None):
        self.email = email
        self.name = None
        self.room = None

        if self.email is not None:
            if name is None and room is None:
                userinfo = cache.get(self.email)
                if userinfo is not None:
                    self.room = userinfo['room']
                    self.name = userinfo['name']
            else:
                self.room = room
                self.name = name
                
    # def getUser(self,id):
    #     self.email = id
    #     if name is None:
    #         userinfo = cache.get(self.email)
    #         if userinfo is None:
    #             raise Http404("user does not exist")

    #         self.room = userinfo['room']
    #         self.name = userinfo['name']

    def getCachedName(self):
        return self.name

    def getCachedRoom(self):
        return self.room

    def updateCacheName(self,name):
        self.name = name
        response = updateUsername(self.name)
        print(response)
        userinfo = {
            'name':self.name,
            'room':self.room
        }
        cache.set(self.email,userinfo,timeout=None)
        
    
    def cacheUser(self):
        userinfo = {
            'name':self.name,
            'room':self.room
        }
        cache.set(self.email,userinfo,timeout=None)
        # cache.set(self.room,self.name,timeout=None)


class CacheMessage:
    def __init__(self, mid, nextkey=None, content=None):
        if content is not None:
            self.mid = mid
            self.next = nextkey
            self.content = content
        else:
            self.mid = mid
            node = cache.get(mid)
            if node is None:
                raise Http404("message does not exist")
            self.next = node['next']
            self.content = node['content']
    
    def cacheMessage(self):
        cache.set(self.mid, {'next':self.next, 'content':self.content}, timeout=None)

    def deleteMessage(self):
        self.content = None
        cache.set(self.mid, {'next':self.next, 'content':self.content}, timeout=None)

    def getMessage(self):
        print('next',self.next, 'content',"blabla")
        return {'next':self.next, 'content':self.content}
    
    def getNext(self):
        return self.next

    def getContent(self):
        return self.content
        
def getOwner(room_name):
    return cache.get(room_name)

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
    res = await get_latest_messages(room=room,ExclusiveStartKey=None)
    print("caching db data..")
    if res != []:
        # request.session.set('startkey', res['LastEvaluatedKey'])
        prev = None
        for i in reversed(res['Items']):
            CacheMessage(mid=i['mid'],nextkey=prev,content=i['content']).cacheMessage()
            prev = i['mid']
        
        return i['mid']
    else:
        return None

async def get_cached_data(room,resource=None,latest_mid=None):
    messages = []
    print("getting cached data..",room, latest_mid)
    
    if latest_mid is None:
        _mid = await getCachedLatestKey(room)
    else:
        _mid = latest_mid
    
    if _mid is not None:
        cnt = 7
        while cnt>0 and _mid is not None :
            message = CacheMessage(_mid).getMessage()
            messages.append(message['content'])
            
            if message['next'] is None:
                # check if this is 'real end'
                key = await getNewCacheMessage(room)
                # connect to previous cache
                if key is None: # real end
                    print("key is None")
                    break
                CacheMessage(_mid,nextkey=key,content=message['content']).cacheMessage()
                _mid = key
            else:
                _mid = message['next']

            cnt -=1

    return {'messages':messages}

