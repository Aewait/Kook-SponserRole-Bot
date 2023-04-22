import json
import aiohttp
import asyncio
import io
from khl import ChannelPrivacyTypes
from khl.card import Card, CardMessage, Module, Element, Types

from .file import config,bot,_log
# kook的base_url和headers
kook_base_url = "https://www.kookapp.cn"
kook_headers = {f'Authorization': f"Bot {config['bot']['token']}"}


#################################机器人在玩状态####################################


async def status_active_game(game: int):
    """让机器人开始打游戏"""
    url = kook_base_url + "/api/v3/game/activity"
    params = {"id": game, "data_type": 1}
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=params, headers=kook_headers) as response:
            return json.loads(await response.text())


async def status_active_music(name: str, singer: str):
    """机器人开始听歌"""
    url = kook_base_url + "/api/v3/game/activity"
    params = {"data_type": 2, "software": "qqmusic", "singer": singer, "music_name": name}
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=params, headers=kook_headers) as response:
            return json.loads(await response.text())


async def status_delete(d: int):
    """删除机器人的当前动态 1游戏 2音乐"""
    url = kook_base_url + "/api/v3/game/delete-activity"
    params = {"data_type": d}
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=params, headers=kook_headers) as response:
            return json.loads(await response.text())


async def guild_list():
    """获取机器人加入的服务器数量"""
    url = kook_base_url + "/api/v3/guild/list"
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=kook_headers) as response:
            ret1 = json.loads(await response.text())
            _log.debug(ret1)
            return ret1

async def guild_user_list(guild_id:str,channel_id="",role_id=-1,page=1):
    """获取服务器用户列表"""
    url = kook_base_url + "/api/v3/guild/user-list"
    params = {"guild_id":guild_id,'page':page}
    if channel_id:params['channel_id']=channel_id # 如果有才设置
    if role_id != -1:params['role_id'] = role_id
    # 请求api
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params,headers=kook_headers) as response:
            ret1 = json.loads(await response.text())
            _log.debug(ret1)
            return ret1

async def guild_user_list_role(guild_id:str,role_id:int):
    """获取指定服务器的指定角色的所有用户，实现了翻页
    - 返回结果：包含用户信息dict的list
    """
    ret = await guild_user_list(guild_id,role_id=role_id,page=1) # 首页
    page_total = ret['data']['meta']['page_total'] # 完整页面
    user_total = ret['data']['meta']['total']   # 该角色的所有用户
    user_list:list = ret['data']['items'] # 第一页的用户
    i = 2
    while i<=page_total:
        _log.debug(f"i{i} | len{len(user_list)} | total:{user_total}")
        ret = await guild_user_list(guild_id,role_id=role_id,page=i) # 查询指定页的数据
        user_list.extend(ret['data']['items'])
        i+=1
        await asyncio.sleep(0.1) # 睡一会避免api调用超速
    # 判断是否获取完毕了
    assert(len(user_list)==user_total)
    return user_list


async def guild_boost(guild_id:str,start_time=0,end_time=0,page=1):
    """获取服务器助力者列表,利用page进行翻页"""
    url = kook_base_url + "/api/v3/guild-boost/history"
    params = {"guild_id":guild_id,"page":page}
    if start_time:params['start_time']=start_time# 如果有才设置
    if end_time:params['end_time'] = end_time
    # 请求api
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params,headers=kook_headers) as response:
            ret1 = json.loads(await response.text())
            _log.debug(ret1)
            return ret1

async def guild_boost_all(guild_id:str,start_time=0,end_time=0):
    """获取指定服务器的指定角色的所有用户，实现了翻页
    - 返回结果：包含用户信息dict的list
    """
    ret = await guild_boost(guild_id,start_time,end_time,page=1) # 首页
    page_total = ret['data']['meta']['page_total'] # 完整页面
    user_total = ret['data']['meta']['total']   # 助力者的所有用户计数器
    user_list:list = ret['data']['items'] # 第一页的用户
    i = 2
    while i<=page_total:
        _log.debug(f"i{i} | len{len(user_list)} | total:{user_total}")
        ret = await guild_boost(guild_id,start_time,end_time,page=i) # 查询指定页的数据
        user_list.extend(ret['data']['items'])
        i+=1
        await asyncio.sleep(0.1) # 睡一会避免api调用超速
    # 判断是否获取完毕了
    assert(len(user_list)==user_total)
    return user_list
        
async def guild_nickname(guild_id:str,user_id:str,nick:str):
    """修改服务器内用户的昵称"""
    url = kook_base_url + "/api/v3/guild/nickname"
    params = {"guild_id": guild_id,"user_id":user_id,"nickname":nick}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params, headers=kook_headers) as response:
            ret1 = json.loads(await response.text())
            _log.debug(ret1)
            return ret1

async def bot_offline():
    """下线机器人"""
    url = kook_base_url + "/api/v3/user/offline"
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=kook_headers) as response:
            res = json.loads(await response.text())
            _log.debug(res)
    return res

async def msg_delete(msg_id:str):
    """删除频道内消息"""
    url = kook_base_url + "/api/v3/message/delete"
    params = {'msg_id':msg_id}
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=params,headers=kook_headers) as response:
            res = json.loads(await response.text())
            _log.debug(res)
    return res

async def leave_guild(guild_id:str):
    """离开指定服务器"""
    url = kook_base_url + "/api/v3/guild/leave"
    params = {'guild_id':guild_id}
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=params,headers=kook_headers) as response:
            res = json.loads(await response.text())
            _log.debug(res)
    return res



##########################################icon##############################################

from typing import Union


# 图标
class icon_cm:
    val_logo = "https://img.kookapp.cn/assets/2022-09/gVBtXI0ZSg03n03n.png"
    val_logo_gif = "https://img.kookapp.cn/assets/2022-09/5skrwZcjGJ0dc07i.gif"
    whats_that = "https://img.kookapp.cn/assets/2022-09/uhm2AewC1i0e80e8.png"
    dont_do_that = "https://img.kookapp.cn/assets/2022-09/wUNDAfzBlr0e80e8.png"
    lagging = "https://img.kookapp.cn/assets/2022-09/D1nqrTszjQ0e80e8.png"
    correct = "https://img.kookapp.cn/assets/2022-09/DknXSpwrlQ0e80e8.gif"
    duck = "https://img.kookapp.cn/assets/2022-09/qARsaxW6lp0e80e8.gif"
    that_it = "https://img.kookapp.cn/assets/2022-09/LqD0pQY2P70e80e8.png"
    no_time = "https://img.kookapp.cn/assets/2023-03/hNrtZg68pZ03k03k.png"
    to_much_money = "https://img.kookapp.cn/assets/2022-09/y17ZhjjaVf0e80e8.png"
    shaka = "https://img.kookapp.cn/assets/2022-09/kMWT5AoEic0e80e8.png"
    say_hello_to_camera = "https://img.kookapp.cn/assets/2022-09/sHh8VJrMp20e80e8.png"
    crying_crab = "https://img.kookapp.cn/assets/2022-09/DfveorD0lS0e80e8.png"
    im_good_phoniex = "https://img.kookapp.cn/assets/2022-09/RdiFsx16Aw0e80e8.png"
    rgx_card = "https://img.kookapp.cn/assets/2022-09/p1VwoNZZWD0e80e8.gif"
    rgx_broken = "https://img.kookapp.cn/assets/2022-09/A8wPGOtJmz0e80e8.gif"
    shot_on_fire = "https://img.kookapp.cn/assets/2022-09/L5EeqS3GDC0e80e8.png"
    powder = "https://img.kookapp.cn/assets/2022-09/nwXm6aNzj20e80e8.png"
    ahri1 = "https://img.kookapp.cn/assets/2022-09/TU9bVQdHiz08c08c.jpg"
    ahri2 = "https://img.kookapp.cn/assets/2022-09/bK1v7R6D7j08c08c.jpg"
    ahri3 = "https://img.kookapp.cn/assets/2022-09/zS5B2wkBvG08c08c.jpg"
    ahri_kda1 = "https://img.kookapp.cn/assets/2022-09/kOwzlg7x6M0rs0rs.jpg"
    ahri_kda2 = "https://img.kookapp.cn/assets/2022-09/OMcQuhcrXo0sc0sc.jpg"
    ahri_kda3 = "https://img.kookapp.cn/assets/2022-09/JHUxBavOeC0xg0xg.jpg"
    ahri_star = "https://img.kookapp.cn/assets/2022-09/NY1m6182Ae0v80v8.jpg"
    ahri_dark = "https://img.kookapp.cn/assets/2022-09/HJJJPrYxUo14w14w.jpg"
    ahri_sour = "https://img.kookapp.cn/assets/2022-09/bnPK4GhBfc0x40x4.jpg"
    ahri_forest = "https://img.kookapp.cn/assets/2022-09/9ObV0banuE1ew1ew.jpg"
    ahri_game = "https://img.kookapp.cn/assets/2022-09/Rp6bnjsLnZ0cg0cg.jpg"


#更新卡片消息
async def upd_card(msg_id: str,
                   content,
                   target_id='',
                   channel_type: Union[ChannelPrivacyTypes, str] = 'public',
                   bot=bot):
    content = json.dumps(content)
    data = {'msg_id': msg_id, 'content': content}
    if target_id != '':
        data['temp_target_id'] = target_id
    if channel_type == 'public' or channel_type == ChannelPrivacyTypes.GROUP:
        result = await bot.client.gate.request('POST', 'message/update', data=data)
    else:
        result = await bot.client.gate.request('POST', 'direct-message/update', data=data)
    return result


async def get_card(text: str, sub_text='e', img_url='e', card_color='#fb4b57', img_sz='sm') ->Card:
    """获取常用的卡片消息的卡片。有缺省值的参数，留空就代表不添加该模块.

    Args:
    - text: Section 中的文字
    - sub_text: Context 中的文字
    - img_url: 图片url（此处图片是和text在一起的，不是独立的图片）
    - card_color: 卡片边栏颜色
    - img_sz: 图片大小，只能为sm或者lg
    """
    c = Card(color=card_color)
    if img_url != 'e':
        c.append(Module.Section(Element.Text(text, Types.Text.KMD), Element.Image(src=img_url, size=img_sz)))
    else:
        c.append(Module.Section(Element.Text(text, Types.Text.KMD)))
    if sub_text != 'e':
        c.append(Module.Context(Element.Text(sub_text, Types.Text.KMD)))
    
    return c
    
async def get_card_msg(text: str, sub_text='e', img_url='e', card_color='#fb4b57', img_sz='sm') -> CardMessage:
    """获取常用的卡片消息的卡片。有缺省值的参数，留空就代表不添加该模块.

    Args:
    - text: Section 中的文字
    - sub_text: Context 中的文字
    - img_url: 图片url（此处图片是和text在一起的，不是独立的图片）
    - card_color: 卡片边栏颜色
    - img_sz: 图片大小，只能为sm或者lg
    """
    cm = CardMessage()
    cm.append(await get_card(text,sub_text,img_url,card_color,img_sz))
    return cm