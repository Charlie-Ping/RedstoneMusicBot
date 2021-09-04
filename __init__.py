from nonebot import on_command
from nonebot.typing import T_State
from nonebot.adapters import Bot, Event
from nonebot.rule import ArgumentParser
from .data_source import *


async def in_dict(bot: Bot, state: T_State, file_type, file_name):
    files = state[f"{file_type}_files_folder"]
    for i in files:
        if i["file_name"] == file_name:
            state["file_id"] = i["file_id"]
            resource_url = await bot.call_api("get_group_file_url",
                                              group_id=state["group_id"],
                                              file_id=state["file_id"],
                                              busid=102)
            return resource_url
    return False


async def get_folders(bot: Bot, event: Event, state: T_State, file_type):
    state["group_id"] = int(event.group_id)  # 群号
    folders = await bot.call_api("get_group_root_files", group_id=state["group_id"])  # 群根目录
    folders = folders["folders"]

    # print(folders)
    for i in folders:
        if i["folder_name"] == file_type:
            state[f"{i['folder_name']}_folder_id"] = i["folder_id"]
            files = await bot.call_api("get_group_files_by_folder",
                                       group_id=state["group_id"],
                                       folder_id=state[f"{i['folder_name']}_folder_id"])
            state[f"{i['folder_name']}_files_folder"] = files["files"]
    if not state[f"{file_type}_folder_id"]:
        return False
    return state[f"{file_type}_folder_id"]


async def get_file(bot: Bot, state: T_State, get_file_type):
    try:
        file_path = await bot.call_api("download_file", url=state[f"{get_file_type}_url"]["url"], thread_count=10)
        file_path = file_path["file"]
        state["file_path"] = file_path
        return file_path
    except BaseException as err:
        raise err


apply = on_command(cmd="apply", priority=5)


@apply.handle()
async def apply_music_list(bot: Bot, event: Event, state: T_State):
    state["group_id"] = str(event.group_id)  # 群号
    user_id = int(event.get_user_id())
    args = str(event.get_message()).split()
    event.get_user_id()
    parser = ArgumentParser()
    parser.add_argument("-n", "--name", action="store", nargs="?", type=str)
    parser.add_argument("-f", "--file", action="store", nargs="?", type=str)
    parser.add_argument("-a", "--author", action="store", nargs="?", type=str)
    parser.add_argument("-l", "--length", action="store", nargs="?", type=int, default=16, required=False)
    parser.add_argument("-w", "--width", action="store", nargs="?", type=int, default=16, required=False)
    parser.add_argument("-t", "--type", action="store", nargs="?", type=str, default="condition", required=False)
    parser.add_argument("-c", "--channel", action="store", nargs="?", type=int, default=-1, required=False)
    try:
        info = parser.parse_args(args)
    except:
        await apply.finish(f"异常参数\n正确格式： apply -n 音乐名 -f 文件名或bv号 -a 音乐作者")

    music_id = set_music_list(info.name, info.file, user_id, author=info.author, way=info.type,
                              length=info.length, width=info.width, channel=info.channel)
    await apply.finish(f"添加成功！音乐id：{music_id}")


donate = on_command("donate", priority=5)


@donate.handle()
async def donate_point(bot: Bot, event: Event, state: T_State):
    user_id = int(event.get_user_id())
    args = str(event.get_message()).split()
    parser = ArgumentParser()
    parser.add_argument("-i", "--id", action="store", nargs="?", type=int)
    parser.add_argument("-p", "--point", action="store", nargs="?", type=int)
    parser.add_argument("-a", "--anonymous", action="store", nargs="?", type=bool, default=False, required=False)

    try:
        info = parser.parse_args(args)
    except:
        await donate.finish(f"异常参数\n正确格式： donate -m 捐助点数 -l 长度 -w 宽度 -t 播放方式 -c 指定乐器")

    if info.point < 0.01:
        await donate.finish("真的有这么小的面值吗？")

    try:
        has_finished = update_music_list(music_id=info.id, apply_qq=user_id, cost=info.point)
    except BaseException as err:
        await donate.finish(f"异常：{err}")
    else:
        if has_finished:
            await donate.finish("投递成功！募捐已达上限，可以申请上传了。")
        await donate.finish("投递成功！")


send_finish = on_command("send", priority=5)


@send_finish.handle()
async def send_file(bot: Bot, event: Event, state: T_State):
    await send_finish.send("正在尝试上传...可能要等很久很久")

    args = int(str(event.get_message()))
    try:
        await bot.set_group_name(group_id=int(event.group_id), group_name="[Working] MoodyRhythm")
    except:
        await bot.send("在我下次发消息之前不要激活我！")
    try:
        file_path = None
        music = get_music_list()
        i, music_info = get_music_list(args)
        if music_info["resource_type"] in ["mid", "audio"]:
            _dict = await get_folders(bot, event, state, music_info["resource_type"])
            if not _dict:
                await send_finish.finish(f"请先联系管理员在群文件中创建目录{_dict}")
            print(music)
            url = await in_dict(bot=bot, state=state, file_name=music_info["resource"],
                                file_type=music_info["resource_type"])
            print(url)
            if not url:
                await send_finish.finish(f"在{music_info['resource_type']}文件夹里找不到{music_info['resource']}")
            file_path = await bot.call_api("download_file", url=url["url"], thread_count=10)
            # json.dump(music_info,
            #           open("D:\WorkPlus\Charlie_Python\QQBot\Dan-Bot\Dan-src\plugins\mp3ToWorld\info\\music_list.json",
            #                "w+", encoding="utf-8"))
        if file_path:
            bdx_path, file_name = conversion_all(args, file_path["file"])
        else:
            bdx_path, file_name = conversion_all(args)
        folder_id = await get_folders(bot, event, state, "bdx")
        if not folder_id:
            await send_finish.finish("没有找到群bdx文件夹")
        await bot.call_api("upload_group_file", group_id=int(event.group_id),
                           file=bdx_path, name=file_name, folder=state["bdx_folder_id"])

    except BaseException as err:
        await send_finish.finish(f"Error: {err}")
    else:
        pass

show_list = on_command("show_list", priority=5)


@show_list.handle()
async def show_music_list(bot: Bot, event: Event, state: T_State):
    args = int(str(event.get_message()))
    music_list = get_music_list()
    for music in music_list:
        if music["has_send"]:
            music_list.remove(music)
            continue

    music = [music_list[i: i + 5] for i in range(0, len(music_list), 5)]
    result = f"{args} / {music.__len__()}\n"
    if music.__len__() - 1 < args:
        await show_list.finish("它实在是太大了")
    music = music[args]
    for a, i in enumerate(music):
        result += f"{i['id']}:{i['music_name']} {i['progress']}/10\n"
    await show_list.finish(result)


search_list = on_command("search_list", priority=5)


@search_list.handle()
async def search_music_list(bot: Bot, event: Event, state: T_State):
    args = str(event.get_message())
    musics = [{"id": i["id"],
               "name": i["music_name"],
               "progress": i["progress"],
               "sml": similarity(i["music_name"], args)} if not i["has_send"] else {"name": None, "id": None, "sml": 0,
                                                                                    "progress": 0} for i in
              get_music_list()]
    musics.sort(key=lambda x: x["sml"])
    result = "你要找的？：\n"
    for i in reversed(musics[0: 5]):
        print(i)
        result += f"{i['id']}:{i['name']} {i['progress']}/10\n"
    await search_list.finish(result)


# set_time = on_command("time", priority=5)
#
#
# @set_time.handle()
# async def upload_user_time(bot: Bot, event: Event, state: T_State):
#     args = str(event.get_message()).strip().split()
#     user = event.get_user_id()
#     time = 0
#     if user in ["1758489207", "2010218143", "2863814992"]:
#         if args.__len__() == 2:
#             user = args[0]
#             time = int(args[1])
#     result = set_user_time(user_id=user, time=time)
#     await set_time.finish(f"{user}当前剩余：{result}点")


# register = on_command("register", priority=5)
#
#
# @register.handle()
# async def register_user(bot: Bot, event: Event, state: T_State):
#     set_user_time(event.get_user_id(), 0)
#     await register.send("注册成功！(或许你已经注册过了？)")
