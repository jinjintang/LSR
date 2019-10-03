import socket
import threading
import time
import math
from collections import defaultdict
import sys



ch2port={}
port2ch={}

edgeList=defaultdict(list)

messageList=[]

activeTime={}

startTime=int(time.time()*1000)

ch=''

err=0

host=''
s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
s.setsockopt(socket.SOL_SOCKET,socket.SO_BROADCAST,1)

def addEdge(ch,n1,c,p):
    addPort(n1,p)
    edgeList[ch].append((n1,float(c)))

def addPort(ch,port):
    port=int(port)
    ch2port[ch]=port
    port2ch[port]=ch
    activeTime[port]=int(time.time()*1000)

def sameMessage(m1):
    if m1 in messageList:
        return True
    else:
        return False



def sendMessage(message,p):
    message=str(message)

    addr=('<broadcast>',p)
    s.sendto(message.encode('utf-8'),addr)
    
 

def sendLive():
    while(True):
        broadcast('hello',[])
        time.sleep(0.5)


def broadcast(message,ex_p):
    for p in port2ch:
        if p not in ex_p:
            sendMessage(message,p)
def checkDead():   
    if int(time.time()*1000)-startTime>10000:
        for p in port2ch:            
            if int(time.time()*1000)-activeTime[p]>=1500:
                n=port2ch[p]
                for e in edgeList[ch]:
                    if e[0]==n:
                        edgeList[ch].remove(e)
                        del port2ch[p]
                        del ch2port[n]
                        err=1
                        return True
        return False
    else:
        for p in port2ch:
            activeTime[p]=int(time.time()*1000)
     
def listening():
    while True:
        data,addr=s.recvfrom(65536)
        try:
            message=data.decode('utf-8')
                     
            if message=='hello':
                activeTime[addr[1]]=int(time.time()*1000)

            elif sameMessage(message):

                continue
            else:
                messageList.append(message)
                broadcast(message,[addr[1]])
                n,message=message.split(':')
                edge=eval(message)
                edgeList[n]=edge    
                            
            if checkDead():
                broadcast(edgeList[ch],[])
                            
            
        except:
            pass
            
def dij():
    while True:
        global err
        if err:
            time.sleep(60)
            err=0
        else:
            time.sleep(30)
        
        d=defaultdict(lambda:math.inf)
        d[ch]=0
        vis=defaultdict(int)
        path=defaultdict(int)
        for i in range(26):
            dist=math.inf
            u=-1
            for c in d:
                if dist>d[c] and vis[c]==0:
                    dist=d[c]
                    u=c
            if u==-1:
                break
       
            vis[u]=1
            for e in edgeList[u]:
                v,cost=e[0],e[1]
                if vis[v]==0 and d[v]>cost+d[u]:
                    d[v]=cost+d[u]
                    path[v]=u
        print('I am Router',ch)
        for i in d:
            if d[i]!=math.inf and i!=ch:
                l=[]
                p=i
                while(p!=0):
                    l.append(p)
                    p=path[p]
                
                print('Least cost path to router ',i,':',''.join(l[::-1]),' and the cost is ',round(d[i],1),sep='')   

        

if __name__=='__main__':
    filepath=sys.argv[1]
    with open(filepath,'r') as file:
        ch,port=file.readline().strip().split()
        s.bind((host,int(port)))
        h=int(file.readline())
        while(h):
            h-=1
            n,c,p=file.readline().split()
            addEdge(ch,n,c,p)
    t1=threading.Thread(target=listening,name='listening')
    t2=threading.Thread(target=sendLive,name='sendlive')
    t3=threading.Thread(target=dij,name='dij')
    t1.start()
    t2.start()
    t3.start()
    while(True):
        
        broadcast(str(ch)+':'+str(edgeList[ch]),[])
        time.sleep(1)
 




    