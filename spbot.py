# encoding: utf-8:
from copy import deepcopy
import time
import os
import aiohttp
import traceback
import asyncio
from khl import Message, PrivateMessage, Bot,Channel,requester
from khl.card import Card, CardMessage, Element, Module, Types, Struct

from utils.file import bot,config,SponsorDict,logging,BaseException_Handler,save_all_files
from utils.myLog import _log
from utils.gtime import getTime,getTimeFromStamp
from utils import kookApi

debug_ch:Channel
"""发送错误日志的频道"""
start_time = getTime()
"""机器人启动时间"""
THX_TASK_INTERVEL=30
"""感谢助力者任务触发时间间隔（分钟）"""

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
        text = "`/hh` 测试bot是否上线/是否有发言权限\n"
        text+= "`/spr` 在 当前 频道发送助力者感谢信息\n"
        text+= "`/spr #文字频道` 在 指定 频道发送助力者感谢信息\n"
        text+=f"设置完成后，bot会每{THX_TASK_INTERVEL}m获取最新的助力者id，并在服务器内发送感谢信息\n"
        text+= "`/spr-d` 取消助力者提醒\n"
        cm = CardMessage()
        c = Card(Module.Header(f"本bot支持的命令如下"),Module.Context(Element.Text(f"开机于：{start_time} | 开源代码见 [Github](https://github.com/musnwos/Kook-SponsorRole-Bot)",Types.Text.KMD)),Module.Divider())
        c.append(Module.Section(Element.Text(text, Types.Text.KMD)))
        c.append(Module.Divider())
        c.append(Module.Section('有任何问题，请加入帮助服务器与我联系', Element.Button('帮助', 'https://kook.top/gpbTwZ', Types.Click.LINK)))
        cm.append(c)
        await msg.reply(cm)
    except Exception as result:
        await BaseException_Handler("sphep",traceback.format_exc(),msg,debug_ch)

##################################################################################################

async def del_guild_log(guild_id:str):
    """删除出错服务器"""
    global SponsorDict
    SponsorDict['err_guild'][guild_id] = SponsorDict['guild'][guild_id]
    del SponsorDict['data'][guild_id]
    del SponsorDict['guild'][guild_id]

async def check_sponsor(sp_dict:dict,guild_id:str,user_info:str)->bool:
    """检查一个助力者信息是否在已有日志中"""
    return user_info in sp_dict[guild_id]

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
async def spr_set(msg:Message,channel:str="",*arg):
    if not logging(msg):
        await msg.reply(f"当前命令需要在公共服务器内使用！")
        _log.info(f"[PrivateMessage] Au:{msg.author_id} inform reply, return")
        return
    try:
        global SponsorDict
        guild_id = msg.ctx.guild.id
        # 有显式设置频道
        ch_id = msg.ctx.channel.id
        if channel and "(chn)" in channel:
            ch_id = channel.replace("(chn)","")
        # 测试是否有发言权限
        ch = await bot.client.fetch_public_channel(ch_id)
        await ch.send(f"这是一个发言权限测试，请忽略本条消息")
        # 判断服务器在不在（是否已有）
        guild_text = "更新" if guild_id in SponsorDict['guild'] else "初始化设置"
        # 设置信息        
        SponsorDict['guild'][guild_id]={
            "channel_id":ch_id,
            'set_time':time.time(),
            'set_user':msg.author_id,
            "send_text":""
        }
        # 获取所有助力者
        ret = await kookApi.guild_boost_all(guild_id)
        # 新建data键值
        SponsorDict['data'][guild_id]= ret
        page = 1
        text = f"**这是一个助力者感谢的测试**\n本服务器助力者感谢初始化 page: {page}\n\n"
        for its in ret:
            text+= f"感谢 (met){its['user_id']}(met) 对本服务器的助力 {getTimeFromStamp(its['start_time'])}\n"
            if len(text) >= 3000: # 长度超限
                cm = await kookApi.get_card_msg(text)
                await ch.send(cm)
                text = f"**这是一个助力者感谢的测试**\n本服务器助力者感谢初始化 page: {page}\n\n"
                page+=1
                _log.info(f"[spr] msg send {page}")
                await asyncio.sleep(0.2)
        # 遍历完成之后一次性发送
        cm = await kookApi.get_card_msg(text)
        await ch.send(cm)
        # 发送成功提示信息
        text_reply = f"{guild_text}成功! 第一波感谢信息已送出~\n频道：(chn){ch.id}(chn)\n频道id：{ch_id}\n"
        cm = await kookApi.get_card_msg(text_reply,img_url=kookApi.icon_cm.correct)
        await msg.reply(cm)
        # 写入文件
        await save_all_files()
        _log.info(f"[spr] G:{guild_id} | C:{ch_id} | Au:{msg.author_id} | set success")
    except Exception as result:
        await BaseException_Handler("spr",traceback.format_exc(),msg,bot)
        err_str = f"ERR! [{getTime()}] spr\n```\n{traceback.format_exc()}\n```"
        await bot.client.send(debug_ch, err_str)#发送错误信息到指定频道

async def guild_test(guild_id:str):
    """机器人不在服务器，没办法获取服务器信息，直接删除键值"""
    try:
        guild = await bot.fetch_guild(guild_id)
        return True
    except requester.HTTPRequester.APIRequestFailed as result:
        if '该用户不在该服务器内' in str(result) or '权限' in str(result):
            await del_guild_log(guild_id) # 赋值后删除（留档）
            _log.warning(f"ERR! [BOT.THX.TASK] {str(result)} | del {guild_id}")
            return False
        raise result # 其他情况，抛出

# 感谢助力者
@bot.task.add_interval(minutes=THX_TASK_INTERVEL)
async def thanks_sponser_task():
    try:
        global SponsorDict
        _log.info(f"[BOT.THX.TASK] start at {getTime()}")
        TempDict = deepcopy(SponsorDict)
        for guild_id in TempDict['guild']:
            send_text = ""
            channel = debug_ch
            try:
                if not await guild_test(guild_id):
                    continue
                # 获取当前服务器所有助力者
                ret = await kookApi.guild_boost_all(guild_id)
                # 用户数量相同，无需更新
                sz = len(TempDict['data'][guild_id])
                if len(ret) == sz:
                    _log.info(f"[BOT.THX.TASK] G:{guild_id} No New_Sp, same_len [{sz}]")
                    continue
                # 用户数量不同，遍历检查
                log_text = f"[BOT.THX.TASK] {getTime()} | G:{guild_id} NewSp:"
                # 发送感谢信息的文字频道
                channel = await bot.client.fetch_public_channel(TempDict['guild'][guild_id]['channel_id'])
                # 配置的感谢信息
                base_send_text:str = TempDict['guild'][guild_id]['send_text']
                is_met_in = "(met)(met)" in base_send_text # 正确配置了
                for its in ret:
                    # 信息不在，才发送
                    if not await check_sponsor(TempDict,guild_id,its):
                        if is_met_in:
                            send_text+= base_send_text.replace("(met)(met)",f"(met){its['user']['id']}(met)")
                        else:
                            send_text+= f"感谢 (met){its['user']['id']}(met)\n"
                        log_text += f"({its['user']['id']}_{its['user']['username']}#{its['user']['identify_num']}) "
                    # 如果感谢信息超过了3000字，就需要提前发出
                    if len(send_text) > 3000:
                        cm = await kookApi.get_card_msg(send_text)
                        await channel.send(cm)
                        send_text = ""
                        _log.info(f"[BOT.THX.TASK] G:{guild_id} | len>3000, ch.send")
                        await asyncio.sleep(0.2)
                # 感谢信息不为空
                if send_text!="":
                    cm = await kookApi.get_card_msg(send_text)
                    await channel.send(cm)
                _log.info(log_text)
            except Exception as result:
                _log.exception(f"Err [BOT.THX.TASK] G:{guild_id}")
                # 赋值后删除（留档）
                await del_guild_log(guild_id)
                err_str = f"ERR! [{getTime()}] [BOT.THX.TASK] G:{guild_id}\n```\n{traceback.format_exc()}\n```"
                await channel.send(await kookApi.get_card_msg(err_str))#发送错误信息到指定频道
                _log.info(f"debug msg send to {channel.id}")
        
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
        _log.exception("[BOT.START] fetch_public_channel failed")
        os._exit(-1)  #出现错误直接退出程序
        
if __name__ == '__main__':
    # 开机的时候打印一次时间，记录开启时间
    _log.info(f"[BOT] Start at {start_time}")
    # 开机
    bot.run() 