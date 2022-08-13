# 直接修改配置信息或根据该格式
# 缺少字段或会有提示信息,然后以下表中的默认配置完成配置
# 工程中只需配置一次,多次配置以第一次为准
Config={
    
    # 是否保存日志文件
    # False或None或不设置均视为关闭
    # 关闭时FileSplit和LogPath中的配置将会失效
    'SaveLogFile':True,

    # 日志文件划分相关
    # 只要使用同一日志路径,就会持续生效,与程序启动次数无关
    'FileSplit':{
        #time:按时间划分日志文件,capacity:按文件大小划分,execution:按每次执行,natureTime:按自然时间划分
        'type':'time',
        # 仅当划分类型是time时生效,划分日志文件时按照时间粒度大小进行划分
        # 按照每(小时:分钟:秒)排列,示例中为每12小时划分一个,此为默认值
        # 格式【时:分:秒】
        'FileSplitTimeStep':'12:0:0',
        # 仅当划分类型是capacity时生效,划分日志文件时按照文件大小进行划分
        # 单位MB,示例中为10MB,此为默认值
        'FileSplitCapacityStep':'10',
        # 仅当划分类型是execution时生效,每n次执行程序使用同一日志文件
        # 单位:词,示例中为1,即每次执行生成新的日志文件
        'FileSplitExecutionStep':'1',
        # 仅当划分类型是natureTime时生效,按照自然日,自然小时划分
        # 示例中为每日划分一次,此为默认值
        # 此外可选值有:HOUR:每小时,MIN:每分钟,WEEK:每周,MONTH:每月,QUARTER:每季度,HALF_YEAR:每半年,YEAR:每年
        # 当尺度过大超过文件系统允许的单个文件大小时,会自动切分
        'FileSplitNatureTimeStep':'DAY'
    },
    # 日志存储位置
    'LogPath':{
        # 日志存储位置,以当前执行目录或文件位置为基准
        # 设置为None即为不保存该类型日志
        # 后续日志存储位置配置意义相同
        'InfoLogPath':'',
        'WarnLogPath':'',
        'ErrorLogPath':'',
        'NoticeLogPath':''
    },
    # 不同级别日志自定义处理方法
    'Handlers':{

    },
    # Server酱配置,用于使用微信接受Notice级别的日志
    # 详见https://sct.ftqq.com/

    'ServerKey':{
        # 您的SendKey
        # 未填写即表示不使用微信推送
        'SendKey':'',
        # 推送标题
        'Title':'收到EasyLogger的Notice级别的消息'
    },
    # Debug级别的日志仅在Debug为True时打印
    # 且Debug信息不会保存至日志文件
    "Debug":True
    
}



        








