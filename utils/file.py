import json
import os
from khl import Bot,Cert,Message, Event,PrivateMessage,Channel
from khl.card import Card, CardMessage, Element, Module, Types, Struct
from .myLog import _log
from .gtime import getTime

import asyncio
FlieSaveLock = asyncio.Lock()
"""日志文件写入锁"""

def open_file(path):
    """打开文件（json）"""
    with open(path, 'r', encoding='utf-8') as f:
        tmp = json.load(f)
    return tmp


def write_file(path: str, value):
    """写入文件,仅支持json格式的dict或者list"""
    with open(path, 'w+', encoding='utf-8') as fw2:
        json.dump(value, fw2, indent=2, sort_keys=True, ensure_ascii=False)


def logging(msg: Message) -> bool:
    """打印msg内容，用作日志
    - true: 公屏，允许运行
    - false：私聊，不给运行"""
    if isinstance(msg,PrivateMessage):
        _log.info(
            f"PmMsg - Au:{msg.author_id} {msg.author.username}#{msg.author.identify_num} = {msg.content}"
        )
        return False
    else:
        _log.info(
            f"G:{msg.ctx.guild.id} - C:{msg.ctx.channel.id} - Au:{msg.author_id} {msg.author.username}#{msg.author.identify_num} = {msg.content}"
        )
        return True


def loggingE(e: Event, func=" "):
    """打印event.body的日志"""
    _log.info(f"{func} | Event:{e.body}")

async def BaseException_Handler(def_name:str,excp,msg:Message,debug_ch=None,help=""):
    """基础的错误管理
    - debug_ch 不为none则发送错误日志
    """
    err_str = f"ERR! [{getTime()}] {def_name} Au:{msg.author_id}\n```\n{excp}\n```"
    _log.error(err_str)
    cm0 = CardMessage()
    c = Card()
    c.append(Module.Header(f"很抱歉，发生了一些错误"))
    c.append(Module.Divider())
    c.append(Module.Section(Element.Text(f"{err_str}\n\n{help}", Types.Text.KMD)))
    c.append(Module.Divider())
    c.append(
        Module.Section('有任何问题，请加入帮助服务器与我联系', Element.Button('帮助', 'https://kook.top/gpbTwZ', Types.Click.LINK)))
    cm0.append(c)
    await msg.reply(cm0)
    if debug_ch:
        await debug_ch.send(cm0)
        _log.info(f"debug_ch send")

def create_logFile(path: str, content={}):
    """创建根文件/文件夹

    Retrun value
    - False: path exist but keyerr / create false
    - True: path exist / path not exist, create success
    """
    try:
        # 如果文件路径存在
        if os.path.exists(path):
            tmp = open_file(path)  # 打开文件
            for key in content:  # 遍历默认的键值
                if key not in tmp:  # 判断是否存在
                    _log.critical(
                        f"[create_logFile] ERR! files exists, but key '{key}' not in {path} files!"
                    )
                    return False
            return True
        # 文件路径不存在，通过content写入path
        write_file(path, content)
        return True
    except Exception as result:
        _log.exception(f"create logFile ERR")
        return False



###############################################################################################

# 日志文件路径
ConfPath = './config/config.json'
"""配置文件路径"""
LogPath = './log'
"""根路径"""
GuildLogPath = './log/GuildLog.json'
"""服务器助力者日志文件路径"""
AfdPath = "./log/AfdWebhook.json"
"""爱发电的wh请求文件路径"""

config = open_file(ConfPath)
"""机器人配置文件"""
SponsorDict = {}
"""服务器助力者日志"""
AfdWebhook = {}
"""爱发电的wh请求"""
THX_TASK_INTERVEL=30
"""感谢助力者任务触发时间间隔（分钟）"""
start_time = getTime()
"""机器人启动时间"""
# 初始化机器人方便其他模组调用
bot = Bot(token=config['bot']['token'])  # websocket
"""main bot"""
if not config['bot']['ws']: # webhook
    _log.info(f"[BOT] using webhook at port {config['bot']['webhook_port']}")
    bot = Bot(cert=Cert(token=config['bot']['token'],
                        verify_token=config['bot']['verify_token'],
                        encrypt_key=config['bot']['encrypt']),
              port=config['bot']['webhook_port'])
# 所有文件如下
try:

    # 如果log路径不存在，创建log文件夹
    if (not os.path.exists(LogPath)):
        os.makedirs(LogPath)  # 文件夹不存在，创建
    # 自动创建日志文件
    if (not create_logFile(GuildLogPath , {
            "data": {},
            "del_guild": {},
            "err_guild": {},
            "guild":{}
    })):
        os.abort()  # err,退出进程
    if (not create_logFile(AfdPath , {
            "data": [],
            "guild":{},
            "plan":{},
            "user":{}
    })):
        os.abort()  # err,退出进程

    SponsorDict = open_file(GuildLogPath)
    AfdWebhook = open_file(AfdPath)

    _log.info(f"[BOT.START] open log.files success!")
except:
    _log.info(f"[BOT.START] open log.files ERR")
    os.abort()


async def save_all_files():
    """写入所有文件"""
    global FlieSaveLock
    async with FlieSaveLock:
        write_file(GuildLogPath, SponsorDict)
        write_file(AfdPath, AfdWebhook)

    _log.info(f"[save.file] save file success")