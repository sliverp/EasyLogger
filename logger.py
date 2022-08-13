import threading
import time
from common import *
from typing import Iterable, Optional
from default_config import Config as default_config

LOG_TYPE = ['DEBUG', 'INFO', 'WARN', 'ERROR', 'NOTICE']
DEFAULT_LOG_LEVEL = 'INFO'
ColorDict = {
    # "BLACK":"\033[30m",
    "BLACK": "",
    "GREEN": "\033[32m",
    "YELLOW": "\033[33m",
    "RED": "\033[31m",
    "DEFAULT": "\033[40;37m",
}


def printWithNoEndl(color, value, end=None):
    print(color, value, end=end)
    print(ColorDict["DEFAULT"], end="")
    return value[1]

class Logger:


    __loggerInstance =None
    __multiTypeMsgHandler={
        "DEBUG":lambda msg,end:printWithNoEndl(ColorDict["BLACK"],msg,end),
        "INFO":lambda msg,end:printWithNoEndl(ColorDict["GREEN"],msg,end),
        "WARN":lambda msg,end:printWithNoEndl(ColorDict["YELLOW"],msg,end),
        "ERROR":lambda msg,end:printWithNoEndl(ColorDict["RED"],msg,end),
        "NOTICE":lambda msg,end:printWithNoEndl(ColorDict["RED"],msg,end),
    }


    @staticmethod
    def getInstance():
        if not Logger.__loggerInstance:
            Logger.__loggerInstance =Logger()
        return Logger.__loggerInstance

    def __init__(self,custom_config=None):
        if custom_config:
            self.loggerConfig=LoggerConfig(custom_config)
        else:
            self.loggerConfig = LoggerConfig(default_config)
        self.logfileWriter=LogFilerWriter(self.loggerConfig)
        self.msgSender=MsgSender()
        self.timer_dict=dict()
        self.default_start_time=None#计时器用
        #self.__infoWriter=open(self.loggerConfig.infoPath,"a")
    

    def __getTimeStamp(self,type):
        timeStamp=time.strftime("(%Y年%m月%d日|%H:%M:%S)",time.localtime())
        return "【%s】%s:"%(type,timeStamp)


    def __showMessage(self, message,type=None,end=None):
        if not type:
            type=DEFAULT_LOG_LEVEL
        return self.__multiTypeMsgHandler[type](self.__getTimeStamp(type)+message,end)
        
    def __showpProgressBarNotice(self,notice_type,check_info,current_progress):
        if not (notice_type and notice_type.upper() in LOG_TYPE):
            notice_type="NOTICE"
        print("")#进度汇报另起一行
        if  check_info and '{0}' in check_info:
            self.__showMessage(check_info.format(current_progress),notice_type.upper())
        elif check_info:
            self.__showMessage(check_info,notice_type.upper())
        else:
            self.__showMessage(f"当前进度:{current_progress}%",notice_type.upper())

    def setLoggerDirectory():
        pass

    def DEBUG(self,message,end=None):
        """
        仅在DEBUG=TRUE时显示
        显示颜色:黑色
        DEBUG信息不会保存至日志文件
        """
        if self.loggerConfig.isDebug:
            self.__showMessage(message,"DEBUG",end)

    def INFO(self,message,end=None):
        """
        一般信息,显示颜色:绿色
        """
        self.__showMessage(message,"INFO",end)
        self.logfileWriter.INFO(message)

    def WARN(self,message,end=None):
        """
        警告信息,显示颜色:黄色
        """
        self.__showMessage(message,"WARN",end)
        self.logfileWriter.WARN(message)

    def ERROR(self,message,end=None):
        """
        错误信息,显示颜色:红色
        """
        self.__showMessage(message,"ERROR",end)
        self.logfileWriter.ERROR(message)

    def NOTICE(self,message,end=None):
        """
        强提醒,显示颜色:红色
        配置NoticeKey后可发送提醒消息至微信
        """
        msg=self.__showMessage(message,"NOTICE",end)
        self.logfileWriter.NOTICE(message)
        if self.loggerConfig.ableSendMsg():
            self.msgSender.sendMessage(msg)
    def __INFO_PROGRESS_BAR(self,msg):
        info='\r'+ColorDict["GREEN"]+self.__getTimeStamp("INFO")+msg
        print(info,end="")


    def TIME_MONITOR(self,warn_timeline=None,notice_timeline=None):
        """
        warn_timeline: 警告时间线 单位:秒
        notice_timeline:强提醒时间线 单位:秒
        超出时间线则会触发响应的日志记录方式
        TODO
        """
        if warn_timeline and  notice_timeline and notice_timeline<warn_timeline:
            self.WARN("Loger.TIME_STAME中notice_timeline应大于warn_timeline,当前设置时间线无效")
            notice_timeline=warn_timeline=None
        def decorator(func):
            def wapper(*args, **kwargs):
                start_time = time.time()
                res = func(*args, **kwargs)
                end_time = time.time()
                duration_time=end_time - start_time
                log_info="函数{_funcname_}运行时长: {_time_}秒".format(_funcname_=func.__name__, _time_=duration_time)
                if not warn_timeline and  not notice_timeline:
                    self.INFO(log_info)
                elif not notice_timeline and warn_timeline:
                    if duration_time<warn_timeline:
                        self.INFO(log_info)
                    else:
                        self.WARN(log_info)
                elif not warn_timeline and notice_timeline:
                    if duration_time<notice_timeline:
                        self.INFO(log_info)
                    else:
                        self.NOTICE(log_info)
                elif notice_timeline and warn_timeline:
                    if duration_time<warn_timeline:
                        self.INFO(log_info)
                    elif warn_timeline<duration_time<notice_timeline:
                        self.WARN(log_info)
                    else:
                        self.NOTICE(log_info)
                return res
            return wapper
        return decorator


    
        
            


    def ProgressBar(self,it,check_points=None, notice_type=None, check_info=None):
        """
        check_points取0-100之间,经过检查点时会通知
        check_points:百分比,单个小数或list,30或[30,60,100]均可
        notice_type:经过检查点时通知类型,默认为NOTICE,会调用响应级别的handler
        """
        if not isinstance(it,Iterable):
            raise Exception("ProgressBar中应传入可迭代的对象")
        try:
            total=len(it)
        except:
            self.ERROR("ProgressBar中应传入可计算总长度的对象")
        last=0
        for i ,item in enumerate(it):
            current_progress=int((i/total)*100)
            log_info='当前进度：{0}   {1}%'.format('▉'*(current_progress//2),current_progress)
            if isinstance(check_points,(int,float)):
                if last<=check_points<current_progress:
                    self.__showpProgressBarNotice(notice_type,check_info,current_progress)
            if isinstance(check_points,list):
                for check_point in check_points:
                    if last<=check_point<current_progress:
                        self.__showpProgressBarNotice(notice_type,check_info,current_progress)
                        break
            self.__INFO_PROGRESS_BAR(log_info)
            last=current_progress
            yield item
            
    def TimerStart(self,name=None,notice_type=None):
        if not name and not self.default_start_time:
            self.default_start_time = time.time()
            self.__showMessage("默认计时器开始",notice_type)
        else:
            if name not in self.timer_dict.keys():
                self.timer_dict[name]=time.time()
                self.__showMessage(f"{name}计时器开始",notice_type)
            
    def TimerRefresh(self,name=None,notice_type=None):
        if not name and self.default_start_time:
            self.default_start_time = time.time()
            self.__showMessage("默认计时器刷新",notice_type)
        else:
            if name not in self.timer_dict.keys():
                self.timer_dict[name]=time.time()
                self.__showMessage(f"{name}计时器刷新",notice_type)

    def TimerEnd(self,name=None,notice_type=None):
        if not name and self.default_start_time:
            duration_time=time.time()-self.default_start_time
            self.__showMessage(f"默认计时器结束,时长{duration_time}秒",notice_type)
            self.default_start_time=None
        else:
            if name in self.timer_dict.keys():
                duration_time=time.time()-self.timer_dict[name]
                self.__showMessage(f"{name}计时器结束,时长{duration_time}秒",notice_type)
                del(self.timer_dict[name])
            else:
                self.WARN("未设定该计时器,已返回0值")
                return 0
        return duration_time

__logger_dict = {}
mutex = threading.Lock()


def get_logger(name: Optional[str] = "logger") -> Logger:
    """
    获取一个logger，未传入name时，默认名字为为logger
    """
    global __logger_dict
    if name not in __logger_dict.keys():
        mutex.acquire()
        if name not in __logger_dict.keys():
            __logger_dict[name] = Logger()
    return __logger_dict[name]
