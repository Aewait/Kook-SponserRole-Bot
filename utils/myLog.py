import logging  # 采用logging来替换所有print
from logging.handlers import TimedRotatingFileHandler

from datetime import datetime, timezone, timedelta
from os import getpid

LOGGER_NAME = "botlog"
"""对象名字"""
LOGGER_FILE = "bot.log"
"""日志文件名字"""
LOGGER_ROLL_INTERVAL = 4
"""日志文件归档间隔（天）"""
BOT_PID = getpid()
"""机器人进程pid"""


def beijing_time(sec, what):
    """日志返回北京时间的处理"""
    utc_dt = datetime.now(timezone.utc)  # 获取当前时间
    beijing_time = utc_dt.astimezone(timezone(timedelta(hours=8)))  # 转换为北京时间
    return beijing_time.timetuple()


# 日志时间改为北京时间
logging.Formatter.converter = beijing_time  # type:ignore

# 只打印info以上的日志（debug低于info）
logging.basicConfig(
    level=logging.INFO,
    format=
    "[%(asctime)s] %(levelname)s:%(filename)s:%(funcName)s:%(lineno)d | %(message)s",
    datefmt="%y-%m-%d %H:%M:%S")  # 这里是全局的配置，不能添加上进程pid（或者说没找到办法）
# 获取一个logger对象
_log = logging.getLogger(LOGGER_NAME)
"""自定义的logger对象"""
# 1.实例化控制台handler和文件handler，同时输出到控制台和文件
file_handler = logging.FileHandler(LOGGER_FILE, mode="a", encoding="utf-8")
fmt = logging.Formatter(
    fmt=
    "[%(asctime)s] [%(bot_pid)d] %(levelname)s:%(filename)s:%(funcName)s:%(lineno)d | %(message)s",
    datefmt="%y-%m-%d %H:%M:%S")
file_handler.setFormatter(fmt)
# 2.按每天来自动生成日志文件的备份
log_handler = TimedRotatingFileHandler(LOGGER_FILE,
                                       when='D',
                                       interval=LOGGER_ROLL_INTERVAL)
log_handler.setFormatter(fmt)
# 3.添加个日志处理器
# _log.addHandler(file_handler) # 这个不用加，时间的日志处理器已经有这个功能了
_log.addHandler(log_handler)
_log = logging.LoggerAdapter(_log, {"bot_pid": BOT_PID})  # 添加机器人进程pid到文件日志中
