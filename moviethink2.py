#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
todo list
基本:
OK  菜单排序功能(首列还不支持排序,需要修改.)
ing tkinter GUI 调整刚启动时各行列宽度,尤其是首行的宽度控制.
    portplayer 多项播放接口(估计要重装32bit的)
    电影后缀补完(过滤器完善)
ing 加载时间优化(没思路,不急,目前的多线程方式基本满足要求.)
ok  播放时间追踪功能(通过pid追踪来实现)(跨平台支持问题)

进阶:
ing GUI美化(直接更换GUI,或者考虑使用JAVA重构吧,不然也不知道封面怎么加,不过加封面可是个大工程...这个还得考虑)
    跨平台支持(播放器等等,暂时不考虑.)
'''
import sys
from pathlib import Path
import os
import PySimpleGUI as sg
from MvFile import MFile
from tqdm import tqdm
import threading
class AllMovie:
    def __init__(self):
        self.pp={}
        self.fpp={}
    def append(self,name,value,parent):
        self.pp[name]=[value,parent]
        if parent=="":
            self.fpp[name]=value
    def rootmv(self):
        return self.fpp
    def allmv(self):
        return self.pp

def inserttree(tree,pp):
    
    def insert2(tree,pn):
        mf=MFile(pn)
        if mf.mf:
            pp.append(mf.name,mf,"")
            nt=mf.name
            print(mf.name)
            tree.Insert("",nt,text=mf.name,values=mf.pshow())
            if(not mf.onefile):
                for i in mf.mf:
                    mykey=i.name
                    pp.append(mykey,i,nt)
                    #tree.place_forget()
                    tree.Insert(nt,mykey,text=mykey,values=i.pshow())
                    #tree.place()

    print("begin load")
    t=[]
    for pn in tqdm([x for x in Path(".").iterdir()]):
        #print(pn)
        ti=threading.Thread(target=insert2,args=(tree,pn))
        ti.start()
        t.append(ti)
    for i in t:
        i.join()

if __name__ == "__main__":
    pp=AllMovie()
    
    
    #threading.Thread(target=inserttree,args=(tree,pp)).start()
    treedata = sg.TreeData()
    inserttree(treedata,pp)
    col=("修改日期","OK","上次观看日期","观看次数","总观看时间","size")
    tree=sg.Tree(data=treedata,
                   headings=col,
                   auto_size_columns=True,
                   num_rows=20,
                   col0_width=40,
                   key='-TREE-',
                   show_expanded=False,
                   enable_events=True)
    layout = [  [tree],
                [sg.Button('Ok'), sg.Button('Cancel')]]
    window = sg.Window('Tree Element Test', layout)
    while True:     # Event Loop
        event, values = window.read()
        if event in (sg.WIN_CLOSED, 'Cancel'):
            break
        print(event, values)
    window.close()
#----------------------------------------------------------------------


def add_files_in_folder(parent, dirname):
    files = os.listdir(dirname)
    for f in files:
        fullname = os.path.join(dirname, f)
        if os.path.isdir(fullname):            # if it's a folder, add folder and recurse
            treedata.Insert(parent, fullname, f, values=[], icon=folder_icon)
            add_files_in_folder(fullname, fullname)
        else:

            treedata.Insert(parent, fullname, f, values=[
                            os.stat(fullname).st_size], icon=file_icon)


add_files_in_folder('', starting_path)


layout = [[sg.Text('File and folder browser Test')],
          [sg.Tree(data=treedata,
                   headings=['Size', ],
                   auto_size_columns=True,
                   num_rows=20,
                   col0_width=40,
                   key='-TREE-',
                   show_expanded=False,
                   enable_events=True),
           ],
          [sg.Button('Ok'), sg.Button('Cancel')]]

window = sg.Window('Tree Element Test', layout)


while True:     # Event Loop
    event, values = window.read()
    if event in (sg.WIN_CLOSED, 'Cancel'):
        break
    print(event, values)
window.close()
