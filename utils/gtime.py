from datetime import datetime,timezone,timedelta

def getTime(format_str='%y-%m-%d %H:%M:%S'):
    """获取当前时间，格式为 `23-01-01 00:00:00`"""    
    utc_dt = datetime.now(timezone.utc) # 获取当前时间
    bj_dt = utc_dt.astimezone(timezone(timedelta(hours=8))) # 转换为北京时间
    return bj_dt.strftime(format_str)
    # use time.loacltime if you aren't using BeiJing Time
    # return time.strftime("%y-%m-%d %H:%M:%S", time.localtime())


def getTimeFromStamp(timestamp:float|int,format_str="%y-%m-%d %H:%M:%S"):
    """通过时间戳获取当前的本地时间，格式 23-01-01 00:00:00"""
    utc_dt = datetime.fromtimestamp(timestamp,tz=timezone.utc)
    bj_dt = utc_dt.astimezone(timezone(timedelta(hours=8))) # 转换为北京时间
    return bj_dt.strftime(format_str)