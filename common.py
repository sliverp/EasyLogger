import os
from enum import Enum
import datetime
import sys
import time


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR_NAME = '\\log'
INFO_DIR_NAME = '\\info\\'
WARN_DIR_NAME = '\\warn\\'
ERROR_DIR_NAME = '\\error\\'
NOTICE_DIR_NAME = '\\notice\\'

INFO = 'INFO'
WARN = 'WARN'
ERROR = 'ERROR'
NOTICE = 'NOTICE'

DEFUALT_TIME_STEP = 43200
DEFUALT_CAPCITY_STEP = 10
DEFUALT_EXECUTION_STEP = 1
DEFUALT_SERVER_MSG = '收到EasyLogger的Notice级别的消息'

LOG_FILE_NAME_TEMPLATE = '%Y年%m月%d日-%H时%M分%S秒'
ConfigConstruction = {
    'SaveLogFile': True,
    'FileSplit': {
        'type': '',
        'FileSplitTimeStep': '',
        'FileSplitCapacityStep': '',
        'FileSplitExecutionStep': '',
        'FileSplitNatureTimeStep': ''
    },
    'LogPath': {
        'InfoLogPath': '',
        'WarnLogPath': '',
        'ErrorLogPath': '',
        'NoticeLogPath': ''
    },
    'Handlers': {},
    'ServerKey': {
        'SendKey': '',
        'Title': ''
    },
    "Debug": True
}


class FileSplitType(Enum):
    TIME = 1
    CAPACITY = 2
    EXECUTION = 3
    NATURE_TIME = 4


class NatureTime(Enum):
    MIN = 1
    HOUR = 2
    DAY = 3
    WEEK = 4
    MONTH = 5
    QUARTER = 6
    HALF_YEAR = 7
    YEAR = 8


NatureTimeMap = {
    'MIN': NatureTime.MIN,
    'HOUR': NatureTime.HOUR,
    'DAY': NatureTime.DAY,
    'WEEK': NatureTime.WEEK,
    'MONTH': NatureTime.MONTH,
    'QUARTER': NatureTime.QUARTER,
    'HALF_YEAR': NatureTime.HALF_YEAR,
    'YEAR': NatureTime.YEAR,
}


class Utils():

    @staticmethod
    def getParsedTimeStep(unformattedTime) -> str:
        """
        将12:10:30这种每12小时零10分钟零30分钟的时间间隔类型变成秒
        """
        assert isinstance(unformattedTime, str)
        times = unformattedTime.split(":")
        if len(times) != 3:
            print("EasyLog 警告:按时间划分时间格式有误,划功能将以默认配置完成设置")
            times = ['12', '0', '0']
        try:
            seconds = int(times[0])*3600+int(times[1])*60+int(times[2])
        except Exception:
            import traceback
            traceback.print_exc()
        else:
            return seconds


class LoggerConfig:
    def __setupDefultFileSplitConfig(self):
        self.file_split_type = FileSplitType.TIME
        self.file_split_time_step = DEFUALT_TIME_STEP

    def __ckeckAndSetupFileSplitConfig(self, file_split_config):
        if not isinstance(file_split_config, dict):
            print("EasyLog 警告:日志文件划分配置信息类型错误,日志文件划功能将以默认配置完成设置")
            self.__setupDefultFileSplitConfig()
            return
        if 'type' not in file_split_config.keys():
            print("EasyLog 警告:配置信息中缺少日志文件划分类型,日志文件划功能将以默认配置完成设置")
            self.__setupDefultFileSplitConfig()
            return
        if 'time' == file_split_config['type']:
            self.file_split_type = FileSplitType.TIME
            if 'FileSplitTimeStep' not in file_split_config:
                print("EasyLog 警告:日志文件划分类型为时间,但未设置时间间隔,默认以12小时为间隔")
                self.file_split_time_step = DEFUALT_TIME_STEP
            else:
                self.file_split_time_step = Utils.getParsedTimeStep(
                    file_split_config['FileSplitTimeStep'])
        elif 'capacity' == file_split_config['type']:
            self.file_split_type = FileSplitType.CAPACITY
            if 'FileSplitCapacityStep' not in file_split_config:
                print("EasyLog 警告:日志文件划分类型为容量,但未设置容量间隔,默认以10MB为间隔")
                self.file_split_capacity_step = DEFUALT_CAPCITY_STEP
            else:
                exp = eval(file_split_config['FileSplitCapacityStep'])
                assert (isinstance(exp, int) or isinstance(
                    exp, float)) and exp > 0
                self.file_split_capacity_step = exp
        elif 'execution' == file_split_config['type']:
            self.file_split_type = FileSplitType.EXECUTION
            if 'FileSplitExecutionStep' not in file_split_config:
                print("EasyLog 警告:日志文件划分类型为执行次数,但未设置间隔,默认以一次为间隔")
                self.file_split_execution_step = DEFUALT_EXECUTION_STEP
            else:
                exp = eval(file_split_config['FileSplitExecutionStep'])
                assert isinstance(exp, int) and exp > 0
                self.file_split_execution_step = exp
        elif 'natureTime' == file_split_config['type']:
            self.file_split_type = FileSplitType.NATURE_TIME
            if 'FileSplitNatureTimeStep' not in file_split_config:
                print("EasyLog 警告:日志文件划分类型为自然时间,但未设置具体时长,默认以一天为间隔")
                self.file_split_nature_time_step = NatureTime.DAY
                return
            else:
                if file_split_config['file_split_config'].upper() not in [NatureTimeMap.keys()]:
                    print("EasyLog 警告:无法识别自然时间划分时长,默认以一天为间隔")
                    self.file_split_nature_time_step = NatureTime.DAY
                else:
                    self.file_split_nature_time_step = NatureTimeMap[file_split_config['file_split_config'].upper(
                    )]
        else:
            print("EasyLog 警告:配置信息中日志文件划分类型错误,日志文件划功能将以默认配置完成设置")
            self.__setupDefultFileSplitConfig()

    def __setupDefultPathConfig(self):
        for expectedKey in ConfigConstruction['LogPath']:
            self.__log_path[expectedKey] = '\\.'

    def __checkAndSetupPathConfig(self, path_config):
        if not isinstance(path_config, dict):
            self.__setupDefultPathConfig()
            print("EasyLog 警告:日志文件保存配置类型错误,日志保存能将以默认配置完成设置")
            return
        for expectedKey in ConfigConstruction['LogPath']:
            if expectedKey in path_config.keys():
                if path_config[expectedKey] == '':
                    path_config[expectedKey] = '\\.'
                self.__log_path[expectedKey] = path_config[expectedKey]

    def __checkAndSetupServerKey(self, serverKey_config):
        if not isinstance(serverKey_config, dict):
            print("EasyLog 警告:Server酱配置类型错误,暂时无法为您推送至微信")
            return
        if 'SendKey' not in serverKey_config.keys() \
                or not isinstance(serverKey_config['SendKey'], str)\
                or len(serverKey_config['SendKey']) == 0:
            print("EasyLog 警告:Server酱配未配置SendKey或SendKey类型错误,暂时无法为您推送至微信")
            return
        self.ServerSendKey = serverKey_config['SendKey']
        if 'Title' not in serverKey_config.keys():
            self.server_title = DEFUALT_SERVER_MSG
        else:
            self.server_title = serverKey_config['Title']

    def __setupAllDefultConfig(self):
        self.__setupDefultFileSplitConfig()
        self.__setupDefultPathConfig()
        self.isDebug = True

    def __checkAndSetupConfig(self, config_dict):
        if not isinstance(config_dict, dict):
            print("EasyLog 警告:配置信息类型错误,将以默认配置完成设置")
            self.__setupAllDefultConfig()
            return
        if 'SaveLogFile' in config_dict.keys() and config_dict['SaveLogFile']:
            self.is_save_log_file = True
            if 'FileSplit' not in config_dict.keys():
                print("EasyLog 警告:配置信息中缺少日志文件划分相关信息,日志文件划功能将以默认配置完成设置")
                self.__setupDefultFileSplitConfig()
            else:
                self.__ckeckAndSetupFileSplitConfig(config_dict['FileSplit'])
        else:
            self.is_save_log_file = False

        if 'LogPath' in config_dict.keys():
            self.__checkAndSetupPathConfig(config_dict['LogPath'])

        if 'ServerKey' in config_dict.keys():
            self.__checkAndSetupServerKey(config_dict['ServerKey'])

    def getINFOPath(self):
        return self.__log_path['InfoLogPath']

    def getWARNPath(self):
        return self.__log_path['WarnLogPath']

    def getERRORPath(self):
        return self.__log_path['ErrorLogPath']

    def getNOTICEPath(self):
        return self.__log_path['NoticeLogPath']

    def __init__(self, config_dict):
        self.__log_path = {}
        self.__checkAndSetupConfig(config_dict)

    def ableSendMsg(self):
        return True


class MsgSender(object):
    def __init__(self):
        pass

    def sendMessage(self, message):
        pass


class LogFilerWriter(object):

    def getAllLogfileNamesInADir(self, dir_name):
        names = []
        for root, dirs, files in os.walk(BASE_DIR+LOG_DIR_NAME+dir_name):
            for f in files:
                names.append(f)
        return names

    def getAllLogfileNames(self):
        names = {
            INFO: self.getAllLogfileNamesInADir(INFO_DIR_NAME),
            WARN: self.getAllLogfileNamesInADir(WARN_DIR_NAME),
            ERROR: self.getAllLogfileNamesInADir(ERROR_DIR_NAME),
            NOTICE: self.getAllLogfileNamesInADir(NOTICE_DIR_NAME),
        }
        return names

    def getCurrentFilenameInTIME(self, filenames):
        times = []
        for filename in filenames:
            try:
                start_time, end_time = filename.split("--")
                times.append([
                    datetime.datetime.strptime(
                        start_time, LOG_FILE_NAME_TEMPLATE),
                    datetime.datetime.strptime(
                        end_time, LOG_FILE_NAME_TEMPLATE)
                ])
            except:
                continue
        times.sort(key=lambda x: x[1])
        if len(times) == 0 or (datetime.datetime.now()-times[-1][0]).seconds > self.config.file_split_time_step:
            #之前没有文件或现有的日志文件太旧了
            new_start_time = datetime.datetime.now()
            new_end_time = new_start_time + \
                datetime.timedelta(seconds=self.config.file_split_time_step)
            filename = datetime.datetime.strftime(
                new_start_time, LOG_FILE_NAME_TEMPLATE)+'--'+datetime.datetime.strftime(new_end_time, LOG_FILE_NAME_TEMPLATE)
        else:
            filename = datetime.datetime.strftime(
                times[-1][0], LOG_FILE_NAME_TEMPLATE)+'--'+datetime.datetime.strftime(times[-1][1], LOG_FILE_NAME_TEMPLATE)
        return filename

    def caculateFilenameByType(self, type: FileSplitType):
        filenames_dir = self.getAllLogfileNames()
        if type == FileSplitType.TIME:
            return {
                INFO: self.getCurrentFilenameInTIME(filenames_dir[INFO]),
                WARN: self.getCurrentFilenameInTIME(filenames_dir[WARN]),
                ERROR: self.getCurrentFilenameInTIME(filenames_dir[ERROR]),
                NOTICE: self.getCurrentFilenameInTIME(filenames_dir[NOTICE]),
            }
        elif type == FileSplitType.NATURE_TIME:
            pass
        elif type == FileSplitType.CAPACITY:
            pass
        elif type == FileSplitType.EXECUTION:
            pass

    def initDirectory(self):
        if not os.path.exists(BASE_DIR+LOG_DIR_NAME):
            os.makedirs(BASE_DIR+LOG_DIR_NAME)
        if not os.path.exists(BASE_DIR+LOG_DIR_NAME+INFO_DIR_NAME):
            os.makedirs(BASE_DIR+LOG_DIR_NAME+INFO_DIR_NAME)
        if not os.path.exists(BASE_DIR+LOG_DIR_NAME+WARN_DIR_NAME):
            os.makedirs(BASE_DIR+LOG_DIR_NAME+WARN_DIR_NAME)
        if not os.path.exists(BASE_DIR+LOG_DIR_NAME+ERROR_DIR_NAME):
            os.makedirs(BASE_DIR+LOG_DIR_NAME+ERROR_DIR_NAME)
        if not os.path.exists(BASE_DIR+LOG_DIR_NAME+NOTICE_DIR_NAME):
            os.makedirs(BASE_DIR+LOG_DIR_NAME+NOTICE_DIR_NAME)

    def initLogfilePointer(self):
        if not self.config.is_save_log_file:
            return
        self.initDirectory()
        filenames_dir = self.caculateFilenameByType(
            self.config.file_split_type)
        if self.config.getINFOPath():
            self.__info_writer = open(BASE_DIR+self.config.getINFOPath(
            )+LOG_DIR_NAME+INFO_DIR_NAME+filenames_dir[INFO], 'a', encoding='utf-8')
        if self.config.getWARNPath():
            self.__warn_writer = open(
                BASE_DIR+LOG_DIR_NAME+WARN_DIR_NAME+filenames_dir[WARN], 'a', encoding='utf-8')
        if self.config.getERRORPath():
            self.__error_writer = open(
                BASE_DIR+LOG_DIR_NAME+ERROR_DIR_NAME+filenames_dir[ERROR], 'a', encoding='utf-8')
        if self.config.getNOTICEPath():
            self.__notice_writer = open(
                BASE_DIR+LOG_DIR_NAME+NOTICE_DIR_NAME+filenames_dir[INFO], 'a', encoding='utf-8')

    def __getTimeStamp(self, type):
        timeStamp = time.strftime("(%Y年%m月%d日|%H:%M:%S)", time.localtime())
        return "【%s】%s:" % (type, timeStamp)

    def __init__(self, config: LoggerConfig):
        self.config = config
        self.__info_writer = self.__warn_writer = self.__error_writer = self.__notice_writer = None
        self.initLogfilePointer()

    def INFO(self, message):
        if self.__info_writer:
            self.__info_writer.write(self.__getTimeStamp("INFO")+message+'\n')

    def WARN(self, message):
        if self.__warn_writer:
            self.__warn_writer.write(self.__getTimeStamp("WARN")+message+'\n')

    def ERROR(self, message):
        if self.__error_writer:
            self.__error_writer.write(
                self.__getTimeStamp("ERROR")+message+'\n')

    def NOTICE(self, message):
        if self.__notice_writer:
            self.__notice_writer.write(
                self.__getTimeStamp("NOTICE")+message+'\n')


if __name__ == "__main__":
    print(LogFilerWriter.getCurrentFilenameInTIME([
        "2023:07:01-00:00:01--2024:07:02-00:00:01",
        "2021:07:02-00:00:01--2021:07:03-00:00:01",
        "2021:07:03-00:00:01--2021:07:04-00:00:01",
        "2021:07:04-00:00:01--2021:07:05-00:00:01",
        "2021:07:05-00:00:01--2021:07:06-00:00:01",
    ]))
