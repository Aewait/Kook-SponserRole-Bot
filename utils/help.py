from khl.card import Card, CardMessage, Element, Module, Types, Struct
from .file import THX_TASK_INTERVEL,start_time

async def get_help_card():
    text = "`/hh` 测试bot是否上线/是否有发言权限\n"
    text+= "`/spr` 在 当前 频道发送助力者感谢信息\n"
    text+= "`/spr #文字频道` 在 指定 频道发送助力者感谢信息\n"
    text+= "`/spr-d` 取消助力者提醒\n"
    text+= "`/spr-text 内容` 配置感谢助力者的文字，需要有`(met)(met)`来标识@用户的位置。默认配置：\n"
    text+= "```\n感谢 (met)(met) 对本服务器的助力\n```\n"
    text+= "默认配置的效果：\n"
    text+= "```\n感谢 @用户A 对本服务器的助力\n```\n"
    text+=f"设置完成后，bot会每{THX_TASK_INTERVEL}m获取最新的助力者id，并在服务器内发送配置好的感谢信息\n"
    cm = CardMessage()
    c = Card(Module.Header(f"本bot支持的命令如下"),Module.Context(Element.Text(f"开机于：{start_time} | 开源代码见 [Github](https://github.com/musnwos/Kook-SponsorRole-Bot)",Types.Text.KMD)),Module.Divider())
    c.append(Module.Section(Element.Text(text, Types.Text.KMD)))
    c.append(Module.Divider())
    c.append(Module.Section('有任何问题，请加入帮助服务器与我联系', Element.Button('帮助', 'https://kook.top/gpbTwZ', Types.Click.LINK)))
    cm.append(c)
    return cm