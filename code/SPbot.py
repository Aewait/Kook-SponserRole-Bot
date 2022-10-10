# encoding: utf-8:
import json
import time
import os
import aiohttp
import traceback
from khl import Message, PrivateMessage, Bot
from khl.card import Card, CardMessage, Element, Module, Types, Struct

# 初始化bot
with open('./config/config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)
# 用读取来的 config 初始化 bot，字段对应即可
bot = Bot(token=config['token'])
# 初始化bot header 来调用api
kook_base_url = "https://www.kookapp.cn"
kook_headers = {f'Authorization': f"Bot {config['token']}"}
debug_ch = None

# 向botmarket通信
@bot.task.add_interval(minutes=30)
async def botmarket():
    api ="http://bot.gekj.net/api/v1/online.bot"
    headers = {'uuid':'8b3b4c14-d20c-4a23-9c71-da4643b50262'}
    async with aiohttp.ClientSession() as session:
        await session.post(api, headers=headers)

# 加载文件
with open('./log/GuildLog.json', 'r', encoding='utf-8') as f:
    SponsorDict = json.load(f)

######################################################################################

#将获取当前时间封装成函数方便使用
def GetTime():  
    return time.strftime("%y-%m-%d %H:%M:%S", time.localtime())

# 在控制台打印msg内容，用作日志
def logging(msg: Message):
    now_time = GetTime()
    if isinstance(msg, PrivateMessage):
        print(f"[{now_time}] PrivateMessage - Au:{msg.author_id}_{msg.author.username}#{msg.author.identify_num} = {msg.content}")
        return False
    else:
        print(f"[{now_time}] G:{msg.ctx.guild.id} - C:{msg.ctx.channel.id} - Au:{msg.author_id}_{msg.author.username}#{msg.author.identify_num} = {msg.content}")
        return True

# 基础的错误管理
async def BaseException_Handler(def_name:str,excp,msg:Message,bot:Bot=bot,help=""):
    err_str = f"ERR! [{GetTime()}] {def_name} Au:{msg.author_id}\n```\n{excp}\n```"
    print(err_str)
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

@bot.command(name="hh")
async def hello(msg:Message,*arg):
    logging(msg)
    try:
        await msg.reply(f"hello world!")
    except Exception as result:
        await BaseException_Handler("hh",traceback.format_exc(),msg,bot)
        err_str = f"ERR! [{GetTime()}] hh\n```\n{traceback.format_exc()}\n```"
        await bot.client.send(debug_ch, err_str)#发送错误信息到指定频道
        
@bot.command(name="sphelp")
async def help(msg:Message,*arg):
    logging(msg)
    try:
        text ="`/hh` 测试bot是否上线/是否有发言权限\n"
        text+="`/spr 助力者角色id` 在 当前 频道发送助力者感谢信息\n"
        text+="`/spr 助力者角色id 文字频道id` 在 指定 频道发送助力者感谢信息\n"
        text+="角色id获取方式：\n```\n个人设置-高级设置-打开开发者模式，进入服务器设置-角色设置-右键助力者角色-复制id\n文字频道id获取方式同上，打开开发者模式后，右键文字频道-复制id即可\n```"
        cm = CardMessage()
        c = Card(Module.Header(f"本bot支持的命令如下"),Module.Context(Element.Text("由MOAR#7134开发，开源代码见 [Github](https://github.com/Aewait/Kook-SponsorRole-Bot)",Types.Text.KMD)),Module.Divider())
        c.append(Module.Section(Element.Text(text, Types.Text.KMD)))
        c.append(Module.Divider())
        c.append(Module.Section('有任何问题，请加入帮助服务器与我联系', Element.Button('帮助', 'https://kook.top/gpbTwZ', Types.Click.LINK)))
        cm.append(c)
        await msg.reply(cm)
    except Exception as result:
        await BaseException_Handler("sphelp",traceback.format_exc(),msg,bot)
        err_str = f"ERR! [{GetTime()}] hh\n```\n{traceback.format_exc()}\n```"
        await bot.client.send(debug_ch, err_str)#发送错误信息到指定频道

##################################################################################################

# 获取服务器指定角色的用户列表
async def fetch_role_list(guild_id:str,role_id:str):
    api = f"https://www.kaiheila.cn/api/v3/guild/user-list?guild_id={guild_id}&role_id={role_id}"
    async with aiohttp.ClientSession() as session:
        async with session.post(api, headers=kook_headers) as response:
            json_dict = json.loads(await response.text())
    return json_dict

# 设置助力者
@bot.command(name="spr")
async def spr_set(msg:Message,role_id:str="err",ch_id:str="err",*arg):
    if not logging(msg):
        await msg.reply(f"当前命令需要在公共服务器内使用！")
        return
    elif role_id == "err":
        await msg.reply(f"您没有提供助力者角色id！获取方式：\n```\n个人设置-高级设置-打开开发者模式，进入服务器设置-角色设置-右键助力者角色-复制id\n```\n文字频道id获取方式同上，打开开发者模式后，右键文字频道-复制id即可")
        return
    try:
        global SponsorDict
        ret_dict = await fetch_role_list(msg.ctx.guild.id,role_id)
        if ret_dict['code']!=0:
            raise Exception("kook-api调用错误，请检查您的角色id是否正确")

        
        
    except Exception as result:
        await BaseException_Handler("spr",traceback.format_exc(),msg,bot)
        err_str = f"ERR! [{GetTime()}] hh\n```\n{traceback.format_exc()}\n```"
        await bot.client.send(debug_ch, err_str)#发送错误信息到指定频道
            
# 检查文件中是否有这个助力者的id
def check_sponsor(it: dict):
    return     

# 感谢助力者（每1h检查一次）
@bot.task.add_interval(hours=1)
async def thanks_sponser():
    print(f"[BOT.THX.TASK] start at {GetTime()}")
    #需要服务器id和助力者id
    
    #长度相同无需更新
    ret = await fetch_role_list()
    sz = len(SponsorDict)
    if ret['data']['meta']['total'] == sz:
        print(f"[BOT.THX.TASK] No new sponser, same_len [{sz}]")
        return

    for its in ret['data']['items']:
        if check_sponsor(its) == 0:
            channel = await bot.client.fetch_public_channel("8342620158040885")  #发送感谢信息的文字频道
            await bot.client.send(channel, f"感谢 (met){its['id']}(met) 对本服务器的助力")
            print(f"[%s] 感谢{its['nickname']}对本服务器的助力" % GetTime())
    print(f"[BOT.THX.TASK] finish at {GetTime()}")


# 开机获取debug频道
@bot.task.add_date()
async def loading_channel():
    try:
        global debug_ch
        debug_ch = await bot.client.fetch_public_channel("6248953582412867")
        print("[BOT.START] fetch_public_channel success")
    except:
        print("[BOT.START] fetch_public_channel failed")
        os._exit(-1)  #出现错误直接退出程序
        
# 开机的时候打印一次时间，记录重启时间
print(f"Start at: [%s]"%GetTime())
# 开机
bot.run()