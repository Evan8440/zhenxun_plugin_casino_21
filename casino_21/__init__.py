from nonebot_plugin_htmlrender import text_to_pic
from nonebot_plugin_alconna import (Args, Alconna, on_alconna)
from nonebot.adapters.onebot.v11 import Bot, MessageSegment
from nonebot.permission import SUPERUSER
from nonebot.plugin import PluginMetadata
from zhenxun.utils.enum import BlockType, PluginType, GoldHandle
from zhenxun.utils.message import MessageUtils
from zhenxun.utils.depends import UserName
from zhenxun.configs.utils import PluginExtraData, BaseBlock
from zhenxun.utils.rules import ensure_group
from zhenxun.models.user_console import UserConsole
from nonebot_plugin_alconna import Arparma, Match
from nonebot_plugin_uninfo import Uninfo
from zhenxun.utils.utils import get_entity_ids, UserBlockLimiter
import random
import time


__plugin_meta__ = PluginMetadata(
    name="21点",
    description="真寻的小赌场",
    usage="""
    第一位玩家发起活动，指令：21点 [赌注]
    接受21点赌局，指令：入场 [赌注]
    人齐后开局，指令：开局
    拿牌，指令：拿牌
    宣布停止，指令：停牌
    所有人停牌，或者超时90s后，结算指令：结束
    最后一位未停牌玩家可使用结束指令直接结算游戏
    小真寻入场费为玩家平均值，必要点数17
    起手2牌合计21点为黑杰克，比其他21点大
    获胜奖励为胜者按各自入场费，均分其他人金币
    数据显示/数据清空 （管理员用）
    """.strip(),
    extra=PluginExtraData(
        author="冥乐",
        version="3.0",
        plugin_type=PluginType.NORMAL,
        menu_type="群内小游戏",
        limits=[BaseBlock(check_type=BlockType.GROUP)],
    ).to_dict(),
)


dian_play = {}
blk = UserBlockLimiter()
msg_a = f"输入指令“21点帮助”获取详细信息"
msg_b = f"第一位玩家发起活动，指令：21点[赌注]\n接受21点赌局，指令：入场[赌注]\n人齐后开局，指令：开局\n拿牌指令：拿牌\n宣布停止，指令：停牌\n所有人停牌，或者超时90s后，结算指令：结束\n小真寻入场费为玩家平均值，必要点数17\n起手2牌合计21点为黑杰克，比其他21点大\n获胜奖励为胜者按各自入场费，均分其他人金币"

_matcher_21_help = on_alconna(
    Alconna(
        "21点帮助",
    ),
    rule=ensure_group,
    priority=5,
    block=True,
)

_matcher_21 = on_alconna(
    Alconna(
        "21点",
        Args["money?", int],
    ),
    rule=ensure_group,
    priority=5,
    block=True,
)

_matcher_21_join = on_alconna(
    Alconna(
        "入场",
        Args["money?", int],
    ),
    aliases={"21点入场"},
    rule=ensure_group,
    priority=5,
    block=True,
)
_matcher_21_start = on_alconna(
    Alconna(
        "开局",
    ),
    aliases={"21点开局"},
    rule=ensure_group,
    priority=5,
    block=True,
)
_matcher_21_napai = on_alconna(
    Alconna(
        "拿牌",
    ),
    aliases={"21点拿牌"},
    rule=ensure_group,
    priority=5,
    block=True,
)
_matcher_21_tingpai = on_alconna(
    Alconna(
        "停牌",
    ),
    aliases={"21点停牌"},
    rule=ensure_group,
    priority=5,
    block=True,
)
_matcher_21_end = on_alconna(
    Alconna(
        "结束",
    ),
    aliases={"21点结束"},
    rule=ensure_group,
    priority=5,
    block=True,
)

@_matcher_21_help.handle()
async def _(
    bot: Bot,
    session: Uninfo,
):
    global msg_b
    await _matcher_21_napai.finish(msg_b)

@_matcher_21.handle()
async def _(
    bot: Bot,
    session: Uninfo,
    money: Match[int],
    uname: str = UserName(),
):
    entity = get_entity_ids(session)
    global dian_play
    global msg_a
    global msg_b
    uid = entity.user_id
    group = entity.group_id
    cost = money.result if money.available else 0
    player_name = uname
    try:
        dian_play[group]

        if dian_play[group]["start"] == 0 or dian_play[group]["start"] == 1:
            await MessageUtils.build_message(f" 上一场21点还未结束，请输入入场\n" + msg_a).finish()
    except KeyError:
        pass
    if cost > 0:
        if cost > 10000000:
            await MessageUtils.build_message(f" 小真寻不接受10，000，000以上的赌注哦").finish(at_sender=True)
        if cost < 20:
            await MessageUtils.build_message(f" 小真寻觉得20以下的赌注不得劲哎").finish(at_sender=True)
    else:
        await MessageUtils.build_message(f" 请正确输入你的赌注").finish(at_sender=True)
    user = await UserConsole.get_user(uid)
    if user.gold < cost:
        await MessageUtils.build_message(f"\n金币不够还想来21点？\n您的金币余额为{str(user.gold)}").finish(at_sender=True)
    card = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
    random.shuffle(card)
    dian_play[group] = {
        "time": time.time(),
        "start": 0,
        "playnum": 0,
        "endnum": 0,
        "costall": 0,
        "BJ": 0,
        "cardnum": 0,
        "cardlist": card,
    }
    await ruchangx(group, uid, player_name, cost)
    await MessageUtils.build_message( f'{player_name}发起了一场21点挑战\n' + msg_a).finish()


@_matcher_21_join.handle()
async def _(
    bot: Bot,
    session: Uninfo,
    money: Match[int],
    uname: str = UserName(),
):
    entity = get_entity_ids(session)
    global dian_play
    global msg_a
    uid = entity.user_id
    group = entity.group_id
    cost = money.result if money.available else 0
    player_name = uname
    try:
        dian_play[group]
    except KeyError:
        await MessageUtils.build_message( f"21点未开场，请输入21点开场\n" + msg_a).finish()
    try:
        if dian_play[group]["start"] == 1:
            await _matcher_21_join.finish()
    except KeyError:
        await _matcher_21_join.finish()
    max = dian_play[group]["playnum"]
    if max >= 12:
        await MessageUtils.build_message( f"人太多啦，小真寻不行啦\n" ).finish()
    i = 1
    key = 0
    while i <= max:
        if dian_play[group][i]["playeruid"] == uid:
            key = i
        i += 1
    if key > 0:
        await MessageUtils.build_message( f"你已入场，请勿重复操作\n" + msg_a).finish()
    if cost > 0:
        if cost > 10000000:
            await MessageUtils.build_message(f" 小真寻不接受10，000，000以上的赌注哦").finish(at_sender=True)
        if cost < 20:
            await MessageUtils.build_message(f" 小真寻觉得20以下的赌注不得劲哎").finish(at_sender=True)
    else:
        await MessageUtils.build_message(f" 请正确输入你的赌注").finish(at_sender=True)
    if cost < (dian_play[group][1]["cost"] / 2):
        await MessageUtils.build_message(f" 赌注不得小于开局玩家的1/2").finish(at_sender=True)
    user = await UserConsole.get_user(uid)
    if user.gold < cost:
        await MessageUtils.build_message(f"\n金币不够还想来21点？\n您的金币余额为{str(user.gold)}").finish(at_sender=True)
    await ruchangx(group, uid, player_name, cost)
    await MessageUtils.build_message( f" 已入场，赌注为{str(cost)}金币" ).finish(at_sender=True)


@_matcher_21_start.handle()
async def _(
    bot: Bot,
    session: Uninfo,
):
    entity = get_entity_ids(session)
    global dian_play
    global msg_a
    group = entity.group_id
    try:
        if dian_play[group]["start"] == 0:
            dian_play[group]["start"] = 1
            dian_play[group]["time"] = time.time()
        elif dian_play[group]["start"] == 1:
            await _matcher_21_start.finish()
    except KeyError:
        await _matcher_21_start.finish()
    cost = dian_play[group]["costall"] / dian_play[group]["playnum"]
    dian_play[group]["costall"] += cost
    dian_play[group][0] = {
        "cost": cost,
        "player": f"小真寻",
        "cardall": f"：",
        "sum": 0,
        "keyA": 0,
        "double": 0,
        "end": 0,
    }
    turn = 0
    max = dian_play[group]["playnum"]
    while turn < 2:
        i = 0
        while i <= max:
            x = dian_play[group]["cardnum"]
            nextcard = dian_play[group]["cardlist"][x]
            dian_play[group]["cardnum"] += 1
            if nextcard == 'A':
                dian_play[group][i]["sum"] += 11
                dian_play[group][i]["keyA"] += 1
                dian_play[group][i]["cardall"] += nextcard
            elif nextcard == 'J' or nextcard == 'Q' or nextcard == 'K':
                dian_play[group][i]["sum"] += 10
                dian_play[group][i]["cardall"] += nextcard
            else:
                dian_play[group][i]["sum"] += int(nextcard)
                dian_play[group][i]["cardall"] += nextcard
            dian_play[group][i]["cardall"] += f", "
            if dian_play[group][i]["keyA"] > 0 and dian_play[group][i]["sum"] > 21:
                dian_play[group][i]["keyA"] -= 1
                dian_play[group][i]["sum"] -= 10
            i += 1
        turn += 1
    i = 0
    while i <= max:
        if dian_play[group][i]["sum"] == 21:
            dian_play[group][i]["cardall"] += f"已BlackJack，"
            dian_play[group]["BJ"] = 1
        i += 1
    i = 1
    if dian_play[group]["BJ"] == 1:
        await end(group)
    else:
        msgsend = await msgout(group)
        img = await text_to_pic(msgsend, None, 300)
        await _matcher_21_start.finish(MessageSegment.image(img))


@_matcher_21_napai.handle()
async def _(
    bot: Bot,
    session: Uninfo,
):
    entity = get_entity_ids(session)
    global dian_play
    global msg_a
    uid = entity.user_id
    group = entity.group_id
    try:
        if dian_play[group]["start"] == 0:
            await _matcher_21_napai.finish()
    except KeyError:
        await _matcher_21_napai.finish()
    i = 0
    key = 1
    max = dian_play[group]["playnum"]
    while key <= max:
        if dian_play[group][key]["playeruid"] == uid:
            i = key
        key += 1
    if i == 0:
        await _matcher_21_napai.finish()
    if dian_play[group][i]["end"] == 1:
        await _matcher_21_napai.finish(f'{dian_play[group][i]["player"]}已经停牌，抽到的卡为{dian_play[group][i]["cardall"]}')
    x = dian_play[group]["cardnum"]
    nextcard = dian_play[group]["cardlist"][x]
    dian_play[group]["cardnum"] += 1
    if nextcard == 'A':
        dian_play[group][i]["sum"] += 11
        dian_play[group][i]["keyA"] += 1
        dian_play[group][i]["cardall"] += nextcard
    elif nextcard == 'J' or nextcard == 'Q' or nextcard == 'K':
        dian_play[group][i]["sum"] += 10
        dian_play[group][i]["cardall"] += nextcard
    else:
        dian_play[group][i]["sum"] += int(nextcard)
        dian_play[group][i]["cardall"] += nextcard
    dian_play[group][i]["cardall"] += f", "
    if dian_play[group][i]["keyA"] > 0 and dian_play[group][i]["sum"] > 21:
        dian_play[group][i]["keyA"] -= 1
        dian_play[group][i]["sum"] -= 10
    if dian_play[group][i]["sum"] > 21:
        dian_play[group][i]["end"] = 1
        dian_play[group]["endnum"] += 1
        dian_play[group][i]["cardall"] += f"炸了"
        await _matcher_21_napai.finish(f'{dian_play[group][i]["player"]}抽到的卡为{dian_play[group][i]["cardall"]}总点数为{dian_play[group][i]["sum"]}，停牌处理')
    if  dian_play[group][i]["sum"] == 21:
        dian_play[group][i]["end"] = 1
        dian_play[group][i]["cardall"] += f"已21点，停牌"
        dian_play[group]["endnum"] += 1
        await _matcher_21_napai.finish(f'{dian_play[group][i]["player"]}抽到的卡为{dian_play[group][i]["cardall"]}')
    await _matcher_21_napai.finish(f'{dian_play[group][i]["player"]}抽到的卡为{dian_play[group][i]["cardall"]}总点数为{dian_play[group][i]["sum"]}')


@_matcher_21_tingpai.handle()
async def _(
    bot: Bot,
    session: Uninfo,
):
    entity = get_entity_ids(session)
    global dian_play
    uid = entity.user_id
    group = entity.group_id
    try:
        if dian_play[group]["start"] == 0:
            await _matcher_21_tingpai.finish()
    except KeyError:
        await _matcher_21_tingpai.finish()
    i = 0
    key = 1
    max = dian_play[group]["playnum"]
    while key <= max:
        if dian_play[group][key]["playeruid"] == uid:
            i = key
        key += 1
    if i == 0:
        await _matcher_21_tingpai.finish()
    if dian_play[group][i]["end"] == 0:
        dian_play[group][i]["end"] = 1
        dian_play[group]["endnum"] += 1
        dian_play[group][i]["cardall"] += f"已停牌"
    await _matcher_21_tingpai.finish(f'{dian_play[group][i]["player"]}已停牌')


@_matcher_21_end.handle()
async def _(
    bot: Bot,
    session: Uninfo,
):
    entity = get_entity_ids(session)
    global dian_play
    uid = entity.user_id
    group = entity.group_id
    try:
        if dian_play[group]["start"] == 0:
            await _matcher_21_end.finish()
    except KeyError:
        await _matcher_21_end.finish()
    if time.time() - dian_play[group]["time"] > 90:
        await end(group)
        await _matcher_21_end.finish()
    i = 0
    key = 1
    max = dian_play[group]["playnum"]
    while key <= max:
        if dian_play[group][key]["playeruid"] == uid:
            i = key
        key += 1
    if i == 0:
        await _matcher_21_end.finish()
    if dian_play[group][i]["end"] == 0:
        dian_play[group][i]["end"] = 1
        dian_play[group]["endnum"] += 1
        dian_play[group][i]["cardall"] += f"已停牌"
    if dian_play[group]["endnum"] == dian_play[group]["playnum"]:
        await end(group)
    else:
        out = await msgout(group) + f"\n有人没停牌"
        img = await text_to_pic(out, None, 400)
        await _matcher_21_end.finish(group_id=group, message=MessageSegment.image(img))


async def ruchangx(group: int, uid: int, player_name: str,  cost: str):
    global dian_play
    dian_play[group]["playnum"] += 1
    num = dian_play[group]["playnum"]
    dian_play[group][num] = {
        "cost": cost,
        "playeruid": uid,
        "player": player_name,
        "cardall": f"：",
        "sum": 0,
        "keyA": 0,
        "end": 0,
    }
    dian_play[group]["costall"] += cost
    await UserConsole.reduce_gold(uid, cost, GoldHandle.PLUGIN,"21点下注")


async def end(group: int):
    global dian_play
    while dian_play[group][0]["sum"] < 17 and dian_play[group]["BJ"] == 0:
        x = dian_play[group]["cardnum"]
        nextcard = dian_play[group]["cardlist"][x]
        dian_play[group]["cardnum"] += 1
        if nextcard == 'A':
            dian_play[group][0]["sum"] += 11
            dian_play[group][0]["keyA"] += 1
            dian_play[group][0]["cardall"] += nextcard
        elif nextcard == 'J' or nextcard == 'Q' or nextcard == 'K':
            dian_play[group][0]["sum"] += 10
            dian_play[group][0]["cardall"] += nextcard
        else:
            dian_play[group][0]["sum"] += int(nextcard)
            dian_play[group][0]["cardall"] += nextcard
        dian_play[group][0]["cardall"] += f", "
        if dian_play[group][0]["keyA"] > 0 and dian_play[group][0]["sum"] > 21:
            dian_play[group][0]["keyA"] -= 1
            dian_play[group][0]["sum"] -= 10
    if dian_play[group][0]["sum"] > 21:
        dian_play[group][0]["cardall"] += f"炸了"
    out = await msgout(group)
    winer = 0
    key = 0
    winall = 0
    max = dian_play[group]["playnum"]
    i = 0
    while i <= max:
        if dian_play[group][i]["sum"] > key and dian_play[group][i]["sum"] < 22:
            key = dian_play[group][i]["sum"]
        i += 1
    i = 0
    while i <= max:
        if dian_play[group][i]["sum"] == key:
            winall += dian_play[group][i]["cost"]
            winer += 1
        i += 1
    if winer == 0:
        out += f'无人生还，金币返还\n'
        i = 1
        while i <= max:
            gold = dian_play[group][i]["cost"]
            await wingold(group, i, gold)
            i += 1
    i = 0
    while i <= max:
        if dian_play[group][i]["sum"] == key:
            gold = int(dian_play[group][i]["cost"] / winall * dian_play[group]["costall"])
            await wingold(group, i, gold)
            out += f'{dian_play[group][i]["player"]}赢得了{str(gold)}金币\n'
        i += 1
    img = await text_to_pic(out, None, 400)
    await _matcher_21_end.send(group_id=group, message=MessageSegment.image(img))
    del(dian_play[group])


async def wingold(group: int, i: int, gold: int):
    global dian_play
    if i > 0:
        uid = dian_play[group][i]["playeruid"]
        await UserConsole.add_gold(uid, gold, "21点收入")
    else:
        pass


async def msgout(group: int) -> str:
    global dian_play
    msg = f'{dian_play[group][0]["player"]}到的卡为{dian_play[group][0]["cardall"]}总点数为{dian_play[group][0]["sum"]}\n'
    i = 1
    max = dian_play[group]["playnum"]
    while i <= max:
        msg += f'{dian_play[group][i]["player"]}到的卡为{dian_play[group][i]["cardall"]}总点数为{dian_play[group][i]["sum"]}\n'
        i += 1
    return msg


tttt = on_alconna(
    Alconna(
        "数据显示",
    ),
    permission=SUPERUSER,
    rule=ensure_group,
    priority=5,
    block=True,
)
xxxx = on_alconna(
    Alconna(
        "数据清空",
    ),
    permission = SUPERUSER,
    rule=ensure_group,
    priority=5,
    block=True,
)


@tttt.handle()
async def _(
    bot: Bot,
    session: Uninfo,
):
    global dian_play
    await tttt.finish(MessageSegment.image(await text_to_pic(dian_play)))

@xxxx.handle()
async def _(
    bot: Bot,
    session: Uninfo,
):
    entity = get_entity_ids(session)
    global dian_play
    group = entity.group_id
    del(dian_play[group])

