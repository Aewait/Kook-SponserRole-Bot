# encoding: utf-8:
from copy import deepcopy
import json
import time
import os
import aiohttp
import traceback
from khl import Message, PrivateMessage, Bot,Channel
from khl.card import Card, CardMessage, Element, Module, Types, Struct

from utils.file import bot,config,SponsorDict,logging,loggingE,BaseException_Handler,save_all_files
from utils.myLog import _log
from utils.gtime import getTime

debug_ch:Channel
"""发送错误日志的频道"""
start_time = getTime()
"""机器人启动时间"""

# 向botmarket通信
@bot.task.add_interval(minutes=20)
async def botmarket():
    api ="http://bot.gekj.net/api/v1/online.bot"
    headers = {'uuid':'cbc11a5f-609f-4274-8656-765c5f96e19b'}
    async with aiohttp.ClientSession() as session:
        await session.post(api, headers=headers)
# 保存文件
@bot.task.add_interval(minutes=5)
async def save_file_task():
    await save_all_files()

######################################################################################


@bot.command(name="hh")
async def hello(msg:Message,*arg):
    logging(msg)
    try:
        await msg.reply(f"hello world!")
    except Exception as result:
        await BaseException_Handler("hh",traceback.format_exc(),msg,debug_ch)
        
@bot.command(name="sphelp")
async def help(msg:Message,*arg):
    logging(msg)
    try:
        text ="`/hh` 测试bot是否上线/是否有发言权限\n"
        text+="`/spr 助力者角色id` 在 当前 频道发送助力者感谢信息\n"
        text+="`/spr 助力者角色id 文字频道id` 在 指定 频道发送助力者感谢信息\n"
        text+="角色id获取方式：\n```\n个人设置-高级设置-打开开发者模式，进入服务器设置-角色设置-右键助力者角色-复制id\n文字频道id获取方式同上，打开开发者模式后，右键文字频道-复制id即可\n```"
        text+="设置完成后，bot会每30m获取最新的助力者id，并在服务器内发送感谢信息"
        text+="`/spr-d` 取消助力者提醒\n"
        cm = CardMessage()
        c = Card(Module.Header(f"本bot支持的命令如下"),Module.Context(Element.Text("开源代码见 [Github](https://github.com/musnwos/Kook-SponsorRole-Bot)",Types.Text.KMD)),Module.Divider())
        c.append(Module.Section(Element.Text(text, Types.Text.KMD)))
        c.append(Module.Divider())
        c.append(Module.Section('有任何问题，请加入帮助服务器与我联系', Element.Button('帮助', 'https://kook.top/gpbTwZ', Types.Click.LINK)))
        cm.append(c)
        await msg.reply(cm)
    except Exception as result:
        await BaseException_Handler("sphep",traceback.format_exc(),msg,debug_ch)

##################################################################################################


# 检查文件中是否有这个助力者的id
def check_sponsor(SpDict:dict,it: dict,guild_id:str):
    # 需要先保证原有txt里面没有保存该用户的id，才进行追加
    if it['id'] in SponsorDict['data'][guild_id]:
        return False

    #原有txt内没有该用户信息，进行追加操作
    SpDict['data'][guild_id][it['id']] = {}
    SpDict['data'][guild_id][it['id']]['time'] = getTime()
    SpDict['data'][guild_id][it['id']]['name'] = f"{it['nickname']}#{it['identify_num']}"
    return True

# 删除提醒
@bot.command(name="spr-d")
async def spr_delete(msg:Message,*arg):
    if not logging(msg):
        await msg.reply(f"当前命令需要在公共服务器内使用！")
        _log.info(f"[PrivateMessage] Au:{msg.author_id} inform reply, return")
        return
    try:
        global SponsorDict
        guild_id = msg.ctx.guild.id
        if guild_id not in SponsorDict['guild']:
            await msg.reply(f"您没有设置过当前服务器的助力者提醒！")
            return
        # 移动键值到删除列表中
        SponsorDict['del_guild'][guild_id] = {}
        SponsorDict['del_guild'][guild_id] = SponsorDict['guild'][guild_id]
        del SponsorDict['guild'][guild_id]
        # 回复
        await msg.reply(f"助力者提醒删除成功")
        _log.info(f"[spr-d] G:{guild_id} Au:{msg.author_id} move to del_guild")
    except Exception as result:
        await BaseException_Handler("spr-d",traceback.format_exc(),msg,bot)
        err_str = f"ERR! [{getTime()}] spr-d\n```\n{traceback.format_exc()}\n```"
        await bot.client.send(debug_ch, err_str)#发送错误信息到指定频道

# 设置助力者
@bot.command(name="spr")
async def spr_set(msg:Message,role_id:str="err",ch_id:str="err",*arg):
    if not logging(msg):
        await msg.reply(f"当前命令需要在公共服务器内使用！")
        _log.info(f"[PrivateMessage] Au:{msg.author_id} inform reply, return")
        return
    elif role_id == "err":
        await msg.reply(f"您没有提供助力者角色id！获取方式：\n```\n个人设置-高级设置-打开开发者模式，进入服务器设置-角色设置-右键助力者角色-复制id\n```\n文字频道id获取方式同上，打开开发者模式后，右键文字频道-复制id即可")
        return
    try:
        global SponsorDict
        guild_id = msg.ctx.guild.id
        ret = await fetch_role_list(guild_id,role_id)
        if ret['code']!=0:
            raise Exception("kook-api调用错误，请检查您的角色id是否正确")
        if ch_id == "err":
            ch_id = msg.ctx.channel.id
        # 测试是否有发言权限
        ch = await bot.client.fetch_public_channel(ch_id)
        await bot.client.send(ch,f"这是一个发言权限测试，请忽略本条消息")
        isGuIN = False
        if guild_id in SponsorDict['guild']:
            isGuIN = True
        # 设置信息        
        SponsorDict['guild'][guild_id]={}
        SponsorDict['guild'][guild_id]['role_id'] = role_id
        SponsorDict['guild'][guild_id]['channel_id']= ch_id
        SponsorDict['guild'][guild_id]['set_time'] = getTime()
        SponsorDict['guild'][guild_id]['set_user'] = msg.author_id
        
        SponsorDict['data'][guild_id]={}
        text = "这是一个助力者感谢的测试\n"
        for its in ret['data']['items']:
            if check_sponsor(SponsorDict,its,guild_id):
                text+= f"感谢 (met){its['id']}(met) 对本服务器的助力\n"
        # 遍历完成之后一次性发送
        await bot.client.send(ch,text)
        if isGuIN:
            text_reply = f"更新成功!第一波感谢信息已送出~\n频道：{ch.name}\n频道id：{ch_id}\n助力者角色id：{role_id}"
        else:
            text_reply = f"设置成功!第一波感谢信息已送出~\n频道：{ch.name}\n频道id：{ch_id}\n助力者角色id：{role_id}"
        await msg.reply(text_reply)

        await save_all_files()
        _log.info(f"[spr] G:{guild_id} C:{ch_id} Au:{msg.author_id} R:{role_id} set success")
    except Exception as result:
        await BaseException_Handler("spr",traceback.format_exc(),msg,bot)
        err_str = f"ERR! [{getTime()}] spr\n```\n{traceback.format_exc()}\n```"
        await bot.client.send(debug_ch, err_str)#发送错误信息到指定频道

async def del_guild_log(guild_id:str):
    """删除出错服务器"""
    global SponsorDict
    SponsorDict['err_guild'][guild_id] = SponsorDict['guild'][guild_id]
    del SponsorDict['data'][guild_id]
    del SponsorDict['guild'][guild_id]

# 感谢助力者（每1h检查一次）
@bot.task.add_interval(minutes=30)
async def thanks_sponser():
    try:
        global SponsorDict
        _log.info(f"[BOT.THX.TASK] start at {getTime()}")
        TempDict = deepcopy(SponsorDict)
        for guild_id in TempDict['guild']:
            try:
                ret = await fetch_role_list(guild_id,TempDict['guild'][guild_id]['role_id'])
                # 机器人不在服务器，直接删除键值
                if ('该用户不在该服务器内' in ret['message']) or ret['code']!=0:
                    log_str = f"ERR! [BOT.THX.TASK] {ret}\n[BOT.THX.TASK] del {guild_id}"
                    # 赋值后删除（留档）
                    await del_guild_log(guild_id)
                    _log.info(log_str)
                    continue
                # 用户数量相同，无需更新
                sz = len(TempDict['data'][guild_id])
                if ret['data']['meta']['total'] == sz:
                    _log.info(f"[BOT.THX.TASK] G:{guild_id} No New_Sp, same_len [{sz}]")
                    continue
                # 用户数量不同，遍历检查
                log_text = f"[BOT.THX.TASK] {getTime()} G:{guild_id} NewSp:"
                send_text = ""
                channel = await bot.client.fetch_public_channel(TempDict['guild'][guild_id]['channel_id'])#发送感谢信息的文字频道
                for its in ret['data']['items']:
                    if check_sponsor(SponsorDict,its,guild_id):
                        send_text+= f"感谢 (met){its['id']}(met) 对本服务器的助力\n"
                        log_text += f"({its['id']}_{its['username']}#{its['identify_num']}) "
                if send_text!="":
                    await bot.client.send(channel, send_text)
                _log.info(log_text)
            except Exception as result:
                _log.exception(f"Err [BOT.THX.TASK] G:{guild_id}")
                # 赋值后删除（留档）
                await del_guild_log(guild_id)
                err_str = f"ERR! [{getTime()}] [BOT.THX.TASK] G:{guild_id}\n```\n{traceback.format_exc()}\n```"
                await bot.client.send(debug_ch, err_str)#发送错误信息到指定频道
        
        # 保存到文件
        await save_all_files()
        _log.info(f"[BOT.THX.TASK] finish at {getTime()}")
    except Exception as result:
        _log.exception("Err in [BOT.THX.TASK]")
        err_str = f"ERR! [{getTime()}] [BOT.THX.TASK]\n```\n{traceback.format_exc()}\n```"
        await bot.client.send(debug_ch, err_str)#发送错误信息到指定频道


# 开机获取debug频道
@bot.on_startup
async def loading_channel(b:Bot):
    try:
        global debug_ch
        debug_ch = await bot.client.fetch_public_channel(config['debug_ch'])
        _log.info("[BOT.START] fetch_public_channel success")
    except:
        _log.critical("[BOT.START] fetch_public_channel failed")
        os._exit(-1)  #出现错误直接退出程序
        
if __name__ == '__main__':
    # 开机的时候打印一次时间，记录开启时间
    _log.info(f"[BOT] Start at {start_time}")
    # 开机
    bot.run() 