import json
from khl.card import CardMessage,Card,Module,Element,Types

from ..myLog import _log
from ..file import AfdWebhook,bot

def get_order_id_dict(custom_order_id:str)->dict:
    """解析custom_order_id"""
    index = custom_order_id.find(':')
    user_id = custom_order_id[:index]
    day = custom_order_id[index+1:]
    day = int(day)
    return {"uid":user_id,"day":day}


async def afd_request(request):
    """爱发电webhook处理函数"""
    # 获取参数信息
    body = await request.content.read()
    params = json.loads(body.decode('UTF8'))
    # 插入到日志中
    global AfdWebhook
    if "data" not in AfdWebhook:
        AfdWebhook["data"] = []
    AfdWebhook['data'].append(params)
    plan_id = params['data']['order']['plan_id']
    # 商品id有被绑定
    if plan_id in AfdWebhook['plan']:
        # 初始化频道id和服务器id
        ch_id,guild_id = "none","none"
        try:
            # 发送到指定频道的信息
            guild_id = AfdWebhook['plan'][plan_id]['guild_id']
            ch_id = AfdWebhook['plan'][plan_id]['channel_id']
            ch = await bot.client.fetch_public_channel(ch_id) # 获取频道对象
            # 频道成功获取，才构造text
            text = ""
            if 'plan_title' in params['data']['order']:
                text = f"商品：{params['data']['order']['plan_title']}\n"
                text+= f"商品ID：{plan_id}"
            user_id = params['data']['order']['user_id'] # afd用户id
            user_id = user_id[0:6]
            text += f"用户：{user_id}\n"
            for i in params['data']['order']['sku_detail']:
                text += f"发电了{i['count']}个：{i['name']}\n"
            text += f"共计：{params['data']['order']['total_amount']} 元\n"
            # 将订单编号中间部分改为#
            trno = params['data']['order']['out_trade_no']
            trno_f = trno[0:8]
            trno_b = trno[-4:]
            trno_f += "####"
            trno_f += trno_b
            # 构造卡片
            c = Card(Module.Header(f"爱发电有新动态啦！"), Module.Context(Element.Text(f"订单号: {trno_f}")), Module.Divider(),
                    Module.Section(Element.Text(text, Types.Text.KMD)))
            cm = CardMessage(c)
            await ch.send(cm)
            _log.debug(f"trno:{params['data']['order']['out_trade_no']} | cm {json.dumps(cm)}")
            _log.info(f"afd-cm-send | G:{guild_id} C:{ch_id} | trno:{params['data']['order']['out_trade_no']}")
        except:
            _log.exception(f"cardmsg send err | G:{guild_id} C:{ch_id} | trno:{params['data']['order']['out_trade_no']}")
    
    # 返回状态码
    return {"ec": 200, "em": "success"}
