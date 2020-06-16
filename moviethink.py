#!/usr/bin/python
# -*- coding: UTF-8 -*-
 
# Python2.x 导入方法
from tkinter import *           # 导入 Tkinter 库
import hashlib
import os
from pathlib import Path
from tqdm import tqdm
# Python3.x 导入方法
#from tkinter import * 
player='PotPlayerMini64.exe'
class MvFile:
    def __init__(self,pn):
        self.pn=pn
        self.name=pn.name
    def play(self):
        print("%s '%s'"%(player,self.pn.resolve()))
        os.popen("%s %s"%(player,self.pn.resolve()))

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

        self.onefile=bool(len(self.mf)==1)

        if self.onefile:
            self.name=self.mf[0].name
        else:
            self.name=pn.name
        
    def _mfilter(self,pn):
        if not pn.is_file():return False
        suffix=pn.suffix.strip(".")
        filter=[".unwanted","#recycle"]
        for iterm in filter:
            if iterm in str(pn.resolve()):return False
        filter=["mp4","mkv","avi","flv","rmvb"]
        if suffix not in filter:return False
        stat=pn.stat()
        if stat.st_size<100*1024*1024: return False#基本单位Bytes,判断小于20MB的就忽略
        
        return True
    def play(self):
        self.mf[0].play()
def listselect(event):
    playname=listb.get(listb.curselection())
    print(listb.get(listb.curselection()))
    pp[playname].play()
    #print(dir(pp[playname].pn))
if __name__ == "__main__":
    p=[]
    pp={}
    for pn in tqdm(Path(".").iterdir()):
        mf=MFile(pn)
        if mf.mf:
            p.append(mf)
    # for i in p:
    #     print(i.name)



    root = Tk()                     # 创建窗口对象的背景色
    root.geometry("500x600")
    listb  = Listbox(root,selectmode = BROWSE)          #  创建一个列表组件
    sl=Scrollbar(root)
    sl.pack(side = RIGHT,fill=Y)
    sl['command'] = listb.yview
    listb['yscrollcommand'] = sl.set
    listb.bind('<Double-Button-1>',listselect)
    for item in tqdm(p):                 # 插入数据
        mykey=item.name
        pp[mykey]=item
        listb.insert(END,item.name)
        if(not item.onefile):
            for i in item.mf:
                mykey="|_\\"+i.name
                pp[mykey]=i
                listb.insert(END,mykey) 
    listb.pack(side=LEFT,fill=BOTH,ipadx=200)                    # 将小部件放置到主窗口中
    root.title("电影管理")
    root.mainloop()                 # 进入消息循环