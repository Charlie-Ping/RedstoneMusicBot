import datetime
import json
import os
from difflib import SequenceMatcher  # 导入库
from bdx.musicGenerator import RedstoneMusic
import smtplib
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart

resource = "D:\WorkPlus\Charlie_Python\QQBot\Dan-Bot\Dan-src\plugins\mp3ToWorld\info"

email_header = [
    {"host": "smtp.exmail.qq.com", "passwd": "cECbjAmh4Qwz7mqL", "email": "wangxuhui@musicraft999.onexmail.com"}]


def send_email(receiver: list, subject, content, file_path, file_name):
    host = "smtp.qq.com"
    passwd = "gwtctepwilvodcjd"
    # passwd_175 = "xrvyyyzrmcuvdgdd"
    email = "1758489207@qq.com"
    # email_175 = "1758489207@qq.com"
    textApart = MIMEText(content)
    with open(file_path, "rb") as f:
        file = f.read()
    scheApart = MIMEApplication(file)
    scheApart["From"] = "MoodyRhythm Official"
    scheApart.add_header("Content-Disposition", 'attachment', filename=file_name)

    message = MIMEMultipart()
    message.attach(scheApart)
    message.attach(textApart)
    message["Subject"] = subject

    try:
        smtpObj = smtplib.SMTP_SSL(host, 465)
        smtpObj.login(email, passwd)
        smtpObj.sendmail(email, receiver, message.as_string())
        smtpObj.quit()
    except BaseException as err:
        raise err


t0 = [
    {"music_name": str,  # args
     "author": str,  # args
     "progress": 0,
     "max_progress": int,  # 10
     "has_finished": bool,
     "resource": str,  # bvid/midi_path/audio_path
     "id": int,
     "apply_qq": int,
     "users": [
         {
             "qq": int,
             "cost": int,  # args
             "datetime": int,
             "anonymous": bool,  # 是否匿名
             "way": str,  # args
             "length": int,  # args
             "width": int,  # args
             "channel": int
         }
     ]
     }
]


def similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()  # 引用ratio方法，返回序列相似性的度量


def get_music_list(music_id=None):
    music_list = json.load(open(f"{resource}/music_list.json", "r", encoding="utf-8"))
    if music_id:
        if len(music_list) >= music_id:
            return music_list[music_id]
        else:
            raise ValueError("找不到这个歌曲序号")
    return music_list


def set_music_list(music_name, audio_resource: str, apply_qq: int, author="noName"):
    music_list = get_music_list()
    if audio_resource[0: 2] == "BV":
        resource_type = "bili"
    elif os.path.splitext(audio_resource)[1] == ".mid":
        resource_type = "mid"
    else:
        resource_type = "audio"
    # else:
    #     raise ValueError("Invalid audio type(BV/mid/audio)")

    music_list += [{"music_name": music_name,  # args
                    "author": author,  # args
                    "progress": 0,
                    "max_progress": 10,  # 10
                    "has_finished": False,
                    "has_send": False,
                    "resource": audio_resource,  # bvid/midi_path/audio_path
                    "id": music_list[-1]["id"] + 1,
                    "apply_qq": apply_qq,
                    "users": [],
                    "resource_type": resource_type
                    }]
    json.dump(music_list, open(f"{resource}/music_list.json", "w+", encoding="utf-8"))
    return music_list[-1]["id"] + 1


def update_music_list(music_id, apply_qq, cost=0, way="scb", length=16, width=16, channel=-1, anonymous=False):
    music_list = json.load(open(f"{resource}/music_list.json", "r", encoding="utf-8"))
    if len(music_list) >= music_id:
        if music_list[music_id]["has_finished"]:
            raise ValueError("这个音乐已经筹满啦！")
    else:
        raise ValueError(f"找不到这个音乐id,最大为{len(music_list)}")
    user_exists = False

    way = "scb" if way not in ["scb", "condition"] else way
    length = 16 if length < 4 else (length if length is not None else 16)
    width = 16 if width > 4 else (width if width is not None else 16)
    channel = -1 if channel is None else (channel if -1 <= channel <= 127 else -1)
    for i, user in enumerate(music_list[music_id]["users"]):
        if user["qq"] == apply_qq:
            music_list[music_id]["users"][i]["cost"] += cost
            # 笨比写法
            music_list[music_id]["users"][i]["width"] = width
            music_list[music_id]["users"][i]["length"] = length
            music_list[music_id]["users"][i]["channel"] = channel
            user_exists = True
            break

    if not user_exists:
        music_list[music_id]["users"] += [
            {
                "qq": apply_qq,
                "cost": cost,  # args
                "datetime": str(datetime.datetime.now()),
                "anonymous": anonymous,  # 是否匿名
                "way": way,  # args
                "length": length - 1,  # args
                "width": width - 1,  # args
                "channel": channel
            }
        ]
    music_list[music_id]["progress"] += cost
    has_finished = False
    if music_list[music_id]["progress"] >= 10:
        has_finished = music_list[music_id]["has_finished"] = True
    json.dump(music_list, open(f"{resource}/music_list.json", "w+", encoding="utf-8"))
    return has_finished


"""
虽然我们深知红石音乐的价值不可用金钱来衡量，但是脱离任何成本就可以得到的红石音乐将会使它黯淡失色。

"""


def set_user_time(user_id, time=0):
    user_id = str(user_id)
    user_list = json.load(open(f"{resource}/user.json", "r", encoding="utf-8"))
    if user_id not in user_list.keys():
        user_list[user_id] = {"time": 1}
    user_list[user_id]["time"] += time
    if time:
        json.dump(user_list, open(f"{resource}/user.json", "w+", encoding="utf-8"))
    return user_list[user_id]["time"]



def conversion_all(music_id):
    _music = None
    for music in get_music_list():
        if music["id"] == music_id:
            _music = music
            break
    if not _music:
        raise KeyError("没有这个音乐id！")
    if not _music["has_finished"]:
        raise ValueError(f"这音乐还没筹满：{_music['progress']}")
    generator = RedstoneMusic()  # 别删
    # print(_music)
    for i, user in enumerate(_music["users"]):
        if _music["resource_type"] == "audio":
            uuid, bdx_path = eval(f"generator.bdx_from_{_music['resource_type']}")(music_name=f"{_music['music_name']}",
                                                                                   audio_path=_music["resource"],
                                                                                   kwargs={
                                                                                   "id":_music["id"],
                                                                                   "qq":user["qq"],
                                                                                   "way":user["way"],
                                                                                   "length":user["length"],
                                                                                   "width":user["width"],
                                                                                   "channel":user["channel"]}
                                                                                   )
        elif _music["resource_type"] == "mid":
            uuid, bdx_path = eval(f"generator.bdx_from_{_music['resource_type']}")(music_name=f"{_music['music_name']}",
                                                                                   midi_path=_music["resource"],
                                                                                   kwargs={
                                                                                       "id": _music["id"],
                                                                                       "qq": user["qq"],
                                                                                       "way": user["way"],
                                                                                       "length": user["length"],
                                                                                       "width": user["width"],
                                                                                       "channel": user["channel"]}
                                                                                   )
        else:
            uuid, bdx_path = eval(f"generator.bdx_from_{_music['resource_type']}")(music_name=f"{_music['music_name']}",
                                                                                   bvid=_music["resource"],
                                                                                   id=_music["id"],
                                                                                   qq=user["qq"],
                                                                                   way=user["way"],
                                                                                   length=user["length"],
                                                                                   width=user["width"],
                                                                                   channel=user["channel"],
                                                                                   )
        _music["users"][i]["uuid"] = uuid
        content = f"""
        音乐名称（及作者）：{_music["music_name"]}\n播放形式：{"计分板" if user["way"] == "scb" else "延迟"}\n
长度（x轴）：{user["length"]}, 宽度（y轴）：{user["width"]}\n
使用到MR_music对应分数（把玩家的这个计分板分数设置为此分数）：{uuid}\n
播放乐器：{f'自行查表：{user["channel"]}' if user["channel"] != -1 else "由原midi指定（如果类型是audio或bili则为纯钢琴）"}\n
类型：{_music["resource_type"]}
        """.strip()
        try:
            send_email(f'{user["qq"]}@qq.com', f"红石音乐：{_music['music_name']}", content, bdx_path,
                       f'{_music["music_name"]}-{_music["author"]}.bdx')
        except:
            raise TimeoutError("邮件发送失败了qwq")
        else:
            music_list = json.load(open(f"{resource}/music_list.json", "r", encoding="utf-8"))
            music_list[music_id]["has_send"] = True
            json.dump(music_list, open(f"{resource}/music_list.json", "w+", encoding="utf-8"))
            return True


if __name__ == '__main__':
    set_music_list("进击的巨人第二季op", "BV1kZ4y1c7nu", 1758489207, "Animenzzz")
    # conversion_all(1)
