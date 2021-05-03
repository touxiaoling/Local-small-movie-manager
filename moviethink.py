#!/usr/bin/python
# -*- coding: UTF-8 -*-
'''
todo list
基本:
OK 菜单排序功能(首列还不支持排序,需要修改.)
    tkinter GUI 调整刚启动时各行列宽度,尤其是首行的宽度控制.
    portplayer 多项播放接口(估计要重装32bit的)
    电影后缀补完(过滤器完善)
    加载时间优化(没思路,不急,目前的多线程方式基本满足要求.)
ok  播放时间追踪功能(通过pid追踪来实现)(跨平台支持问题)
    增加删除功能
进阶:
    GUI美化(直接更换GUI,或者考虑使用JAVA重构吧,不然也不知道封面怎么加,不过加封面可是个大工程...这个还得考虑)(得用C#来实现)
    跨平台支持(播放器等等,暂时不考虑.)
'''
from tkinter import *           # 导入 Tkinter 库
from tkinter.ttk import *
import os
from pathlib import Path
from tqdm import tqdm
import pickle
import time
import threading
import subprocess
import shutil
player='PotPlayerMini64.exe'

class MvFile:
    '''
    电影文件类:代表单个电影文件,后续想要支持分段文件合为一个.(目前还不清楚细节,不知道能否在简单改变的条件下直接支持)
    因为MFile类和MvFile类内的方法并不相同--后面做到相同要(save方法怎么做就比较麻烦).
    目前的方法和成员:
        方法:
    '''
    def __init__(self,pn):
        self.pn=pn
        self.mf=[self]#反向适配,你就说骚不骚.
        self.name=pn.name
        
        stat=self.pn.stat()
        self.st_size=stat.st_size
        self.st_mtime=stat.st_mtime
        
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
        
        if hasattr(savep,"check_time"):
            self.check_time=savep.check_time
        else:
            self.check_time=0
        if hasattr(savep,"del_flag"):
            self.del_flag=savep.del_flag
        else:
            self.del_flag=False
    def pshow(self):

        if self.like:like="True"
        else:like=""
        check_time=time.strftime("%H:%M:%S",time.gmtime(self.check_time))
        return (time.strftime("%Y/%m/%d/%H:%M:%S",time.localtime(self.st_mtime)),
                like,
                self.ever_see_time(),
                self.all_see_times,
                check_time,
                "%.2fGB"%(self.st_size/(1024*1024*1024))
                )

    def ever_see_time(self):
        if not self.last_see_time:
            return "None"
        s= time.time()-self.last_see_time
        m=s//60%60
        h=s//3600%24
        d=s/3600//24
        if self.del_flag is True:
            return "%03dd%02dh%02dmD"%(d,h,m)
        else:    
            return "%03dd%02dh%02dm"%(d,h,m)
    def _init2(self):
        pass
    def gsave(self):
        with open(self._load_path,"wb+") as f:
            pickle.dump(self,f)
        #print("save ok")
    def play(self,waitcmd=None):
        print("%s '%s'"%(player,self.pn.resolve()))
        last_checktime=self.check_time
        #os.popen("%s %s"%(player,self.pn.resolve()))
        def thread_checkplay():
            begin_time=time.time()
            p = subprocess.Popen("%s %s"%(player,self.pn.resolve()))#异步
            i=0
            while p.poll() is None:
                i=(1+i)%10
                time.sleep(0.1)
                if (waitcmd is not None) and i==0:
                    waitcmd(time.time()-begin_time+self.check_time)

            self.check_time+=time.time()-begin_time
            waitcmd(self.check_time)
            self.gsave()
        threading.Thread(target=thread_checkplay).start()
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

        self.st_size=sum((x.st_size for x in self.mf))
        
        self.onefile=bool(len(self.mf)==1)
        if self.mf:
            self.pshow =self.mf[0].pshow
        if self.onefile:
            self.name=self.mf[0].name
        else:
            self.name=pn.name
        self.delfilecheck()

    def _mfilter(self,pn):
        if not pn.is_file():return False
        suffix=pn.suffix.strip(".")
        filter=["mp4","mkv","avi","flv","rmvb","wmv","iso","ISO","rm"]
        if suffix.lower() not in filter:return False

        filter=[".unwanted","#recycle",".moviedata"]
        for iterm in filter:
            if iterm in str(pn.resolve()):return False
        stat=pn.stat()
        if stat.st_size<100*1024*1024: return False#基本单位Bytes,判断小于20MB的就忽略
        
        return True
    def play(self,waitcmd=None):
        self.mf[0].play(waitcmd)
        #希望监听播放时长
    def delfilecheck(self):
        if self.mf:
            if self.mf[0].del_flag:
                if self.mf[0].last_see_time !=0:
                    if (time.time()-self.mf[0].last_see_time)//(3600*24) >=7:
                        print("delfile",self.pshow())
                        self.delfile(self.pn)
                        self.mf=[]
    def delfile(self,pn):
        if pn.is_file():
            pn.unlink()
        else:
            shutil.rmtree(pn)
        # for sub in pn.iterdir() :
        #     if sub.is_dir() :
        #         self.delfile(sub)
        #     else :
        #         sub.unlink()
        # pn.rmdir()
        

def doubletree(event):
    items = tree.selection()
    item = tree.identify_row(event.y)
    iidy = int(item[1:],16)    #行号，也叫item， 以字母I开头，第一行是I001
    iidx = int(tree.identify_column(event.x)[1:]) #鼠标点击处的列号， 以#开头， 如#0
    selectkey=(tree.item(item, "text"))
    pp[selectkey].mf[0].all_see_times+=1
    pp[selectkey].mf[0].last_see_time=time.time()
    pp[selectkey].mf[0].gsave()

    showthing=pp[selectkey].mf[0].pshow

    tree.item(item,values=showthing())
    def mywaitcmd(all_check_time):
        newshowthing=[]
        for i in showthing():
            newshowthing.append(i)
        newshowthing[4]=time.strftime("%H:%M:%S",time.gmtime(all_check_time))
        tree.item(item,values=newshowthing)

    pp[selectkey].mf[0].play(mywaitcmd)
        
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
    selectkey=tree.item(item, "text")
    if iidx==2:
        pp[selectkey].mf[0].like = not pp[selectkey].mf[0].like
        tree.item(item,values=pp[selectkey].mf[0].pshow())
    if iidx==0:
        pp[selectkey].mf[0].del_flag = not pp[selectkey].mf[0].del_flag
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
                    #tree.place_forget()
                    tree.insert(nt,END,text=mykey,values=i.pshow())
                    #tree.place()

    print("begin load")
    for pn  in tqdm(Path(".").iterdir()):
        threading.Thread(target=insert2,args=(tree,pn)).start()

def treeview_sort_column(tv,col,reverse):
    print('sorting %s!' % col)
    l = [(tv.set(k, col), k) for k in tv.get_children('')]
    l.sort(reverse=reverse)

    # rearrange items in sorted positions
    for index, (val, k) in enumerate(l):
        print('Moving Index:%r, Value:%r, k:%r' % (index, val, k))
        tv.move(k, '', index)

    # reverse sort next time
    tv.heading(col, command=lambda: treeview_sort_column(tv, col, not reverse))
if __name__ == "__main__":
    pp={}
    root = Tk()                     # 创建窗口对象的背景色
    root.geometry("1500x1000")
    col=("修改日期","OK","上次观看日期","观看次数","总观看时间","size")
    tree =Treeview(root,height=10,columns=col)
    for each in col:
        tree.heading(each,text=each.capitalize(),command=lambda _each=each:treeview_sort_column(tree,_each, False) )
    # tree.column('1',width=50,anchor='center')

    sl=Scrollbar(root)
    sl.pack(side = RIGHT,fill=Y)
    #treeyview=lambda *args :threading.Thread(target=tree.yview,args=args)
    sl.configure(command=tree.yview)
    #slset=lambda *args :threading.Thread(target=sl.set,args=args)
    tree.configure(yscrollcommand=sl.set)
    tree.bind('<Double-Button-1>',doubletree)
    tree.bind('<ButtonRelease-3>',rightclicktree)

    
    #threading.Thread(target=inserttree,args=(tree,pp)).start()
    inserttree(tree,pp)

    tree.pack(side=LEFT,fill=BOTH,ipadx=200)                    # 将小部件放置到主窗口中
    root.title("电影管理")
    
    root.mainloop()                 # 进入消息循环
