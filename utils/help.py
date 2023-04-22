from khl.card import Card, CardMessage, Element, Module, Types, Struct
from .file import THX_TASK_INTERVEL,start_time

async def get_help_card():
    text = "`/hh` 测试bot是否上线/是否有发言权限\n"
    text = "**感谢服务器助力者**\n"
    text+= "`/spr` 在 当前 频道发送助力者感谢信息\n"
    text+= "`/spr #文字频道` 在 指定 频道发送助力者感谢信息\n"
    text+= "`/spr-d` 取消助力者提醒\n"
    text+= "`/spr-text 内容` 配置感谢助力者的文字，需要有`(met)(met)`来标识@用户的位置。默认配置：\n"
    text+= "```\n感谢 (met)(met) 对本服务器的助力\n```\n"
    text+= "默认配置的效果：\n"
    text+= "```\n感谢 @用户A 对本服务器的助力\n```\n"
    text+=f"设置完成后，bot会每{THX_TASK_INTERVEL}m获取最新的助力者id，并在服务器内发送配置好的感谢信息\n"

    text+=f"\n**爱发电webhook绑定**\n"
    text+= "`/afd 商品id` 在 当前 频道发送爱发电webhook信息\n"
    text+= "`/afd 商品id #文字频道` 在 指定 频道发送爱发电webhook信息\n"
    text+= "`/afd-cl` 删除本服务器所有绑定的爱发电webhook\n"
    text+= "`/afd-cl 商品id` 删除指定商品id的爱发电webhook\n"
    text+= "商品id获取：在爱发电主页，点击你的赞助商品，进入付款页面。页面url中的plan_id=后面就是商品id，一直到&截止。示例如下\n"
    text+= "```\nplan_id=a45353328af911eb973052540025c37&\na45353328af911eb973052540025c37即为商品id\n```\n"
    text+=f"设置完成后，如果爱发电有人购买指定商品，则会发送信息到当前频道。"
    text+=f"商品id只能被一个服务器绑定。绑定后，其余服务器无法绑定\n"
    text+=f"爱发电webhook管理页：[开发者](https://afdian.net/dashboard/dev)\n"
    text+=f"机器人webhook回调地址：[填我](https://afd-wh.musnow.top/afd)\n"
    cm = CardMessage()
    c = Card(Module.Header(f"本bot支持的命令如下"),Module.Context(Element.Text(f"开机于：{start_time} | 开源代码见 [Github](https://github.com/musnwos/Kook-SponsorRole-Bot)",Types.Text.KMD)),Module.Divider())
    c.append(Module.Section(Element.Text(text, Types.Text.KMD)))
    c.append(Module.Divider())
    c.append(Module.Section('有任何问题，请加入帮助服务器与我联系', Element.Button('帮助', 'https://kook.top/gpbTwZ', Types.Click.LINK)))
    cm.append(c)
    return cm