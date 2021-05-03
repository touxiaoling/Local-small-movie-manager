from pathlib import Path
import pickle
import time
import threading
import subprocess
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
        return "%dd%dh%dm"%(d,h,m)
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
        
    def _mfilter(self,pn):
        if not pn.is_file():return False
        suffix=pn.suffix.strip(".")
        filter=["mp4","mkv","avi","flv","rmvb","wmv","iso","ISO"]
        if suffix not in filter:return False

        filter=[".unwanted","#recycle",".moviedata"]
        for iterm in filter:
            if iterm in str(pn.resolve()):return False
        stat=pn.stat()
        if stat.st_size<100*1024*1024: return False#基本单位Bytes,判断小于20MB的就忽略
        
        return True
    def play(self,waitcmd=None):
        self.mf[0].play(waitcmd)
        #希望监听播放时长