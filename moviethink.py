#!/usr/bin/python
# -*- coding: UTF-8 -*-

from tkinter import *           # 导入 Tkinter 库
from tkinter.ttk import *
import hashlib
import os
from pathlib import Path
from tqdm import tqdm
import pickle
import math
import time
import datetime
import threading
player='PotPlayerMini64.exe'

class MvFile:
    def __init__(self,pn):
        self.pn=pn
        self.mf=[self]#反向适配,你就说骚不骚.
        self.name=pn.name

        self._load_path="./.moviedata/%s"%(self.name.replace(".","_"))
        self._gload(self._load_path)

        self._init2()

        #self.show=(time.strftime("%Y/%m/%d/%H:%M:%S",time.localtime(self.st_mtime)),self.like,self.ever_see_time(),self.all_see_times,"%.2fGB"%(self.st_size/(1024*1024*1024)))
        #self.gsave()

    def _gload(self,load_path):
        if(Path(load_path).exists()):
            with open(load_path,"rb") as f:
                savep=pickle.load(f)
        else:
            savep=None

        if hasattr(savep,"like"):
            self.like=savep.like
        else:
            self.like=False

        if hasattr(savep,"last_see_time"):
            self.last_see_time=savep.last_see_time
        else:
            self.last_see_time=0
        #print(self.last_see_time)
        if hasattr(savep,"all_see_times"):
            self.all_see_times=savep.all_see_times
        else:
            self.all_see_times=0
    def pshow(self):
        stat=self.pn.stat()
        self.st_size=stat.st_size
        self.st_mtime=stat.st_mtime
        return (time.strftime("%Y/%m/%d/%H:%M:%S",time.localtime(self.st_mtime)),self.like,self.ever_see_time(),self.all_see_times,"%.2fGB"%(self.st_size/(1024*1024*1024)))
    def ever_see_time(self):
        if not self.last_see_time:
            return "None"
        s= time.time()-self.last_see_time
        m=s//60%60
        h=s//3600%24
        d=s/3600//24
        return "%dd%dh%dm"%(d,h,m)
    def _init2(self):
        pass
    def gsave(self):
        with open(self._load_path,"wb+") as f:
            pickle.dump(self,f)
        #print("save ok")
    def play(self):
        print("%s '%s'"%(player,self.pn.resolve()))
        os.popen("%s %s"%(player,self.pn.resolve()))
        '''
        # 创建进程
        p = subprocess.Popen(cmd_, shell=True, cwd=, stdin=, stdout=, stderr=)
        # 获得 pid
        pid = p.pid
        # 监听
        glan = psutil.Process(pid)
        '''
class MFile:
    def __init__(self,pn):
        self.pn=pn
        self.is_file=pn.is_file

        if not pn.is_file():
            self.mf=[MvFile(x) for x in pn.glob("**/*") if self._mfilter(x)]
        else:
            if self._mfilter(pn):
                self.mf=[MvFile(pn)]
            else:
                self.mf=[]

        #self.st_size=sum((x.st_size for x in self.mf))
        
        self.onefile=bool(len(self.mf)==1)
        if self.mf:
            self.pshow =self.mf[0].pshow
        if self.onefile:
            self.name=self.mf[0].name
        else:
            self.name=pn.name
        
    def _mfilter(self,pn):
        if not pn.is_file():return False
        suffix=pn.suffix.strip(".")
        filter=["mp4","mkv","avi","flv","rmvb"]
        if suffix not in filter:return False

        filter=[".unwanted","#recycle",".moviedata"]
        for iterm in filter:
            if iterm in str(pn.resolve()):return False
        stat=pn.stat()
        if stat.st_size<100*1024*1024: return False#基本单位Bytes,判断小于20MB的就忽略
        
        return True
    def play(self):
        self.mf[0].play()
        #希望监听播放时长

def doubletree(event):
    items = tree.selection()
    item = tree.identify_row(event.y)
    iidy = int(item[1:],16)    #行号，也叫item， 以字母I开头，第一行是I001
    iidx = int(tree.identify_column(event.x)[1:]) #鼠标点击处的列号， 以#开头， 如#0
    selectkey=(tree.item(item, "text"))
    pp[selectkey].mf[0].all_see_times+=1
    pp[selectkey].mf[0].last_see_time=time.time()
    pp[selectkey].mf[0].gsave()
    tree.item(item,values=pp[selectkey].mf[0].pshow())
    pp[selectkey].mf[0].play()
    
    print("row = ", iidy)
    print("column = ", iidx)
    print("the items has been selected = ",tree.selection())              #取得被选中的行号
    
    print("item = ", item)
    print("%s "%(tree.item(item, "text")),tree.item(item, "values"))
    print("tree.get_children('') = ",tree.get_children(item))         #取得所有root下的item

def rightclicktree(event):
    items = tree.selection()
    item = tree.identify_row(event.y)
    iidy = int(item[1:],16)    #行号，也叫item， 以字母I开头，第一行是I001
    iidx = int(tree.identify_column(event.x)[1:]) #鼠标点击处的列号， 以#开头， 如#0
    selectkey=(tree.item(item, "text"))
    if iidx==2:
        pp[selectkey].mf[0].like = not pp[selectkey].mf[0].like
        tree.item(item,values=pp[selectkey].mf[0].pshow())
    pp[selectkey].mf[0].gsave()

def inserttree(tree,pp):
    
    def insert2(tree,pn):
        mf=MFile(pn)
        if mf.mf:
            pp[mf.name]=mf
            nt=tree.insert("",END,text=mf.name,values=mf.pshow())
            if(not mf.onefile):
                for i in mf.mf:
                    mykey=i.name
                    pp[mykey]=i
                    tree.insert(nt,END,text=mykey,values=i.pshow())
    print("begin load")
    for pn in tqdm([x for x in Path(".").iterdir()]):
        threading.Thread(target=insert2,args=(tree,pn)).start()

if __name__ == "__main__":
    pp={}
    root = Tk()                     # 创建窗口对象的背景色
    root.geometry("1500x1000")
    col=["1","2","3","4","5"]
    tree =Treeview(root,height=10,columns=col)
    # tree.column('1',width=50,anchor='center')
    tree.heading("1", text="修改日期")
    tree.heading("2", text="OK")
    tree.heading("3", text="上次观看日期")
    tree.heading("4", text="观看次数")
    tree.heading("5", text="size")


    sl=Scrollbar(root)
    sl.pack(side = RIGHT,fill=Y)
    #treeyview=lambda *args :threading.Thread(target=tree.yview,args=args)
    sl.configure(command=tree.yview)
    #slset=lambda *args :threading.Thread(target=sl.set,args=args)
    tree.configure(yscrollcommand=sl.set)
    tree.bind('<Double-Button-1>',doubletree)
    tree.bind('<ButtonRelease-3>',rightclicktree)

    
    t=threading.Thread(target=inserttree,args=(tree,pp))
    t.start()
    #inserttree(tree,pp)
    tree.pack(side=LEFT,fill=BOTH,ipadx=200)                    # 将小部件放置到主窗口中
    root.title("电影管理")
    
    root.mainloop()                 # 进入消息循环
