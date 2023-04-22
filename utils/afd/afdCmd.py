import traceback
import time
import copy
from khl import Message, PrivateMessage, Bot,Channel,requester
from khl.card import Card, CardMessage, Element, Module, Types, Struct

from ..file import AfdWebhook,_log,logging,BaseException_Handler
from ..kookApi import get_card_msg,icon_cm

def init(bot:Bot,debug_ch:Channel):

    @bot.command(name='afd',case_sensitive=False)
    async def afd_bind_cmd(msg:Message,plan="",channel="",*arg):
        try:
            if not logging(msg):return
            if not plan:return await msg.reply(f"请指定商品的plan_id")
            global AfdWebhook
            chid = msg.ctx.channel.id
            guild_id = msg.ctx.guild.id
            if "(chn)" in channel:
                chid = channel.replace("(chn)","")
            # 插入服务器记录
            if guild_id not in  AfdWebhook['guild']:
                AfdWebhook['guild'][guild_id] = {}
            if chid not in AfdWebhook['guild'][guild_id]:
                AfdWebhook['guild'][guild_id][chid] = []
            AfdWebhook['guild'][guild_id][chid].append({
                "plan_id":plan,
                "create_at":time.time(),
            })
            # 插入planid记录
            if plan not in AfdWebhook['plan'] or AfdWebhook['plan'][plan]['guild_id'] == guild_id:
                AfdWebhook['plan'][plan]={
                    "guild_id":guild_id,
                    "channel_id":chid,
                    "create_at":time.time()
                }
                text = f"**绑定爱发电plan成功！**\n"
                text+= f"plan: {plan}\n"
                text+= f"频道：(chn){chid}(chn)\n"
                text+= f"频道ID：{chid}"
                await msg.reply(await get_card_msg(text,img_url=icon_cm.correct))
                _log.info(f"[afd] G:{guild_id} | C:{chid} | Au:{msg.author_id} | plan:{plan}")
            elif AfdWebhook['plan'][plan]['guild_id'] != guild_id:
                await msg.reply(f"plan:`{plan}` 已被其他频道绑定！无法二次绑定")
                _log.info(f"[afd] Au:{msg.author_id} | plan:{plan} already bind by G:{AfdWebhook['plan'][plan]['guild_id']}")
        except:
            await BaseException_Handler("afd",traceback.format_exc(),msg)

    # 清除绑定
    @bot.command(name='afd-cl',case_sensitive=False)
    async def afd_bind_clear_cmd(msg:Message,plan="",*arg):
        try:
            if not logging(msg):return
            chid = msg.ctx.channel.id
            guild_id = msg.ctx.guild.id
            if guild_id not in AfdWebhook['guild']:
                _log.info(f"Au:{msg.author_id} | guild not exist")
                return await msg.reply(f"当前服务器尚未绑定过任何爱发电plan")
            if plan and plan not in AfdWebhook['plan']:
                _log.info(f"Au:{msg.author_id} | plan not exist")
                return await msg.reply(f"当前服务器尚未绑定过**该爱发电plan**\nplan_id: {plan}")

            # 没有指定plan，清除全部
            tmpAfdWh = copy.deepcopy(AfdWebhook)
            if not plan:
                # 遍历这个服务器设置的频道和plan
                text = "**清空成功**\n如下为被清空的plan_id:\n```\n"
                for ch,ch_list in tmpAfdWh['guild'][guild_id].items():
                    for plan_info in ch_list:
                        plan_id = plan_info['plan_id']
                        if plan_id in AfdWebhook['plan']:
                            text += f"{plan_id}\n"
                            del AfdWebhook['plan'][plan] # 删除这个plan
                            _log.info(f"G:{guild_id} | Au:{msg.author_id} | del plan:{plan}")

                AfdWebhook['guild'][guild_id] = {} # 清空日志
                text+="```\n"
                cm = await get_card_msg(text,f"服务器键值记录已被同步删除")
                await msg.reply(cm)
                _log.info(f"G:{guild_id} | Au:{msg.author_id} | del guild:{guild_id}")
            # 删除指定plan
            else:
                for ch,ch_list in tmpAfdWh['guild'][guild_id].items():
                    for plan_info in ch_list:
                        plan_id = plan_info['plan_id']
                        # 找到了，删除
                        if plan_id == plan:
                            AfdWebhook['guild'][guild_id][ch].remove(plan_info)
                            del AfdWebhook['plan'][plan]
                            text = "**删除指定plan成功**\n"
                            text+=f"plan: {plan}\n"
                            text+=f"绑定频道: (chn){ch}(chn)\n"
                            text+=f"频道ID: {ch}"
                            cm = await get_card_msg(text)
                            await msg.reply(cm)
                            _log.info(f"G:{guild_id} | C:{ch} | Au:{msg.author_id} | del plan:{plan}")
                            return
                
                # 没有提前退出，代表没有找到
                await msg.reply(f"当前服务器尚未绑定过**该爱发电plan**\nplan_id: {plan}")
                _log.info(f"Au:{msg.author_id} | plan not in guild:{guild_id}")
        except:
            await BaseException_Handler("afd-cl",traceback.format_exc(),msg)


    _log.info(f"[afd] load afdCmd.py")