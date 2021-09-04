import os
from random import randint
import mido
from piano_transcription_inference import PianoTranscription, sample_rate, load_audio
from bdx.bdx_01 import BdxConverter
from bdx.AudioDownload import download_bv


def music2mid(path, newpath):
    (audio, _) = load_audio(path, sr=sample_rate, mono=True)
    transcription = PianoTranscription(device="cpu")
    # 转换
    transcription.transcribe(audio, newpath)
    return newpath


class RedstoneMusic:
    """
    类：转换器
    对象：绑定歌曲的转换器
    """
    version="3.0.1"

    programs = {
        0: "harp",
        1: "harp",
        2: "pling",
        3: "harp",
        4: "pling",
        5: "pling",
        6: "harp",
        7: "harp",
        8: "xylophone",
        9: "harp",
        10: "didgeridoo",
        11: "harp",
        12: "xylophone",
        13: "chime",
        14: "harp",
        15: "harp",
        16: "bass",
        17: "harp",
        18: "harp",
        19: "harp",
        20: "harp",
        21: "harp",
        22: "harp",
        23: "guitar",
        24: "guitar",
        25: "guitar",
        26: "guitar",
        27: "guitar",
        28: "guitar",
        29: "guitar",
        30: "guitar",
        31: "bass",
        32: "bass",
        33: "bass",
        34: "bass",
        35: "bass",
        36: "bass",
        37: "bass",
        38: "bass",
        39: "bass",
        40: "harp",
        41: "harp",
        42: "harp",
        43: "harp",
        44: "iron_xylophone",
        45: "guitar",
        46: "harp",
        47: "harp",
        48: "guitar",
        49: "guitar",
        50: "bit",
        51: "bit",
        52: "harp",
        53: "harp",
        54: "bit",
        55: "flute",
        56: "flute",
        57: "flute",
        58: "flute",
        59: "flute",
        60: "flute",
        61: "flute",
        62: "flute",
        63: "flute",
        64: "bit",
        65: "bit",
        66: "bit",
        67: "bit",
        68: "flute",
        69: "harp",
        70: "harp",
        71: "flute",
        72: "flute",
        73: "flute",
        74: "harp",
        75: "flute",
        76: "harp",
        77: "harp",
        78: "harp",
        79: "harp",
        80: "bit",
        81: "bit",
        82: "bit",
        83: "bit",
        84: "bit",
        85: "bit",
        86: "bit",
        87: "bit",
        88: "bit",
        89: "bit",
        90: "bit",
        91: "bit",
        92: "bit",
        93: "bit",
        94: "bit",
        95: "bit",
        96: "bit",
        97: "bit",
        98: "bit",
        99: "bit",
        100: "bit",
        101: "bit",
        102: "bit",
        103: "bit",
        104: "hrap",
        105: "banjo",
        106: "harp",
        107: "harp",
        108: "harp",
        109: "harp",
        110: "harp",
        111: "guitar",
        112: "harp",
        113: "bell",
        114: "harp",
        115: "cow_bell",
        116: "basedrum",
        117: "bass",
        118: "bit",
        119: "basedrum",
        120: "guitar",
        121: "harp",
        122: "harp",
        123: "harp",
        124: "harp",
        125: "hat",
        126: "basedrum",
        127: "snare",
    }

    def __init__(self,
                 audio_path="D:/WorkPlus/Charlie_Python/QQBot/Dan-Bot/Dan-src/plugins/mp3ToWorld/audio",
                 bdx_path="D:/WorkPlus/Charlie_Python/QQBot/Dan-Bot/Dan-src/plugins/mp3ToWorld/bdx",
                 _mid_path="D:\WorkPlus\Charlie_Python\QQBot\Dan-Bot\Dan-src\plugins\mp3ToWorld\mid"
                 ):
        """

        @param audio_path:
        @param bdx_path:
        @param _mid_path:
        """
        self.channel = -1
        self.basename = ""
        self.mid_path = ""
        self.mid = None
        self._mid_path = _mid_path
        self.bdx_path = bdx_path
        self.audio_path = audio_path
        self.program = {}
        self.notes = []
        self.tempo = 500000  # 默认tempo值，用来计算音符的实际间隔时间
        self.channel = -1

    def mid2data_1(self, channel):
        """

        :return:
        """
        self.channel = channel  # 这个channel是乐器id，其他channel是通道
        note_num = 0
        c_time = 0  # 用来抽走邪恶的零音量时间
        cache_time = 0  # 用来缓存间隔时间在1秒内的音符时间
        for message in self.mid:  # 遍历mid事件
            if hasattr(message, "channel"):  # 如果事件有channel属性
                if not (message.channel in self.program):  # 如果这个channel不在program字典里
                    self.program[message.channel] = 0  # 这个channel的乐器（program）为0
            if message.type == "note_on":  # 如果是音符事件
                self.notes += [{"mid_note": message.note,
                                "mid_velocity": message.velocity,
                                "note": round(2 ** ((message.note - 66) / 12), 6),
                                "velocity": round(message.velocity / 127, 3),
                                "time": 0,
                                "tick": 0,
                                "program": self.program[message.channel],
                                "global_tick": 0,
                                "global_time": 0,
                                "type": "note"}
                                ]
                note_num += 1
            if self.notes.__len__() > 0:  # 如果音符数大于0
                self.notes[-1]["time"] += message.time * (500000 / self.tempo) + c_time  # 最后一个音符的时间
                c_time = 0
            if message.type != "note_on":  # 如果不是音符
                if message.type == "set_tempo":  # 如果是set——tempo
                    self.tempo = message.tempo
                if message.type == "program_change" and self.channel == -1:  # 如果是programchange的同时channel又是按原mid定的音色
                    self.program[message.channel] = message.program  # 这个channel的program定位这个mid事件的program
                elif hasattr(message, "channel"):  # 如果（不是programchange且channel不是-1）
                    if self.channel == -1:  # 无关是不是programchange
                        self.program[message.channel] = 0
                    else:  # 如果不是-1：
                        self.program[message.channel] = self.channel
            else:
                if message.velocity == 0:
                    c_time = self.notes.pop(-1)["time"]
                    # self.notes[-1]["time"] += c_time
                    note_num -= 1
                    pass
        # print("note", note_num)
        # [print(i) for i in self.notes]

        for i, note in enumerate(self.notes):
            time = note["time"] + cache_time  # 此音符距离上一音符的间隔时间
            # 0.05 % 0.05 会变成 0 从而跳过这段延迟，所以不得不单独处理,
            # 至于为什么要加上0.025： 两个音符时间间隔大于半游戏刻 小于一游戏刻时 如果强行把两个音符放在一个游戏刻内 会显得比较突兀
            if 0.025 < time <= 0.05:

                self.notes[-1]["tick"] = 1  # 写入延迟
                self.notes[i]["global_tick"] = self.notes[i - 1]["global_tick"]
                cache_time = 0  # 清空缓存间隔时间
                continue

            self.notes[i]["tick"] = round(time * 20 // 1)  # 此间隔时间换算后的游戏刻
            cache_time = time % 0.05
            if i > 0:
                self.notes[i]["global_time"] = self.notes[i - 1]["global_time"] + self.notes[i]["time"]
            else:
                self.notes[i]["global_time"] = self.notes[i]["time"]
            self.notes[i]["global_tick"] = self.notes[i - 1]["global_tick"] + self.notes[i]["tick"]
            self.notes[i]["type"] = "note"
        # cache_time = 0za
        # for note in self.notes:
        #     cache_time
        # for i in range(0, 11):
        #     self.notes.insert({"type": "progress", "progress": i}, self.notes.__len__() // 10 * i)
        # [print(i) for i in self.notes]
        # import pygame.mid
        # import time
        # pygame.mid.init()
        # player = pygame.mid.Output(0)
        # player.set_instrument(0)
        # for i, note in enumerate(self.notes):
        #     if 0.025 < note["time"] <= 0.05:
        #         pass
        #     print(f"{note['tick']}, {note['global_tick']}")
        #     time.sleep(self.notes[i]["tick"]/20)
        #     player.note_on(self.notes[i]["mid_note"], self.notes[i]["mid_velocity"])

        # [print(i) for i in self.notes]
        return self.notes.__len__()
        # 一个黑乐谱才220kb 根本不用担心（虽然已经很大了 但是懒得去想什么迭代器怎么整了



    def data2cb_1(self, song_name, **kwargs):
        """

        0: y-1                        [y]
        1: y+1                        |     [z]
        2: z-1                        |    /
        3: z+1                        |   /
        4: x-1                        |  /
        5: x+1                        | /
        一个生动的坐标轴                 |
        如果不生动请把制表符长度改成四个空格  ---------------------- [x]

        :param max_length: 最长
        :param max_width: 最宽
        :param song_name: 音乐名称
        :return:
            如果x轴计数器没有到达最大值，则：
                如果x轴状态为正向，则
                    方块朝向 5
                    x+=1
                或 如果x轴状态为反向，则
                    方块朝向4
                    x-=1
                如果计数器为0，则
                    方块无条件
                或 如果计数器不为0，则
                    方块有条件
                x轴计数器+1
            或 如果x轴到达最大值，则：
                x轴计数器清零
                改变x轴状态
                如果z轴没有到达最大值，则：
                    如果z轴状态为正向，则
                        方块朝向3
                        z+1
                    或 如果z轴状态为反向，则
                        方块朝向2
                        z-1
                    z轴计数器+1
                或 如果z轴到达最大值，则：
                    z轴计数器清零
                    方块朝向1
                    y+1
                    改变z轴状态
                方块无条件
            直接写代码的时候我整个人是懵的，想了一上午没搞懂这个逻辑
            后来写一遍伪代码就搞懂出来了草
        """
        kwargs = kwargs["kwargs"]
        music_id = randint(-2147483646, 2147483646)

        self.notes.insert(0, {"type": "command",
                              "command": "tag @a remove MR_listen",
                              "customName": "By MoodyRhythm"})
        self.notes.insert(0, {"type": "command",
                              "command": f"scoreboard players set @a[scores={{MR_music={music_id}}}, tag=MR_listen] MR_progress 0",
                              "customName": "By MoodyRhythm"})
        self.notes.insert(0, {"type": "command",
                              "command": f"say @a[scores={{MR_music={music_id}}}] §7[{self.version}] 正在播放: {song_name}",
                              "customName": "§7MoodyRhythm"})
        self.notes.insert(0, {"type": "command",
                              "command": f"scoreboard players set @a[tag=MR_listen] MR_music {music_id}",
                              "customName": "群号⑨⑥1⑦4⑧⑤0⑥"})
        self.notes.insert(0, {"type": "command",
                              "command": f"scoreboard objectives add MR_progress dummy",
                              "customName": "Have fun !"})
        self.notes.insert(0, {"type": "command",
                              "command": f"scoreboard objectives add MR_music dummy",
                              "customName": song_name})
        blocks = []
        length = 0
        width = 0  # 计数器
        y = z = 0  # 实际位置
        x = 1
        facing_z = facing_x = True  # 是否正方向

        for note in self.notes:
            # print(note)
            if note["type"] == "progress":
                blocks += [{"direction": [x, y, z],
                            "block_name": "chain_command_block",
                            "particular_value": 0,
                            "impluse": 1,
                            "command": f'title @a[scores={{MR_music={music_id}}}] actionbar {{"rawtext":[{{"text"}}:"MoodyRhythm\n"]}}',
                            "customName": f"MR Charity",
                            "lastOutput": "",
                            "tickdelay": 0,
                            "executeOnFirstTick": 0,
                            "trackOutput": 1,
                            "conditional": 0,
                            "needRedstone": 0}]

            elif note["type"] == "note":
                blocks += [{"direction": [x, y, z],
                            "block_name": "chain_command_block",
                            "particular_value": 0,
                            "impluse": 2,
                            "command": f'execute @a[scores={{MR_music={music_id}, MR_progress={note["global_tick"]}}}] ~~1~ playsound note.{self.programs[note["program"]]} @s ~~~ {note["velocity"]} {note["note"]}',
                            "customName": "MoodyRhythm",
                            "lastOutput": "By MoodyRhythm. 群号⑨⑥1⑦4⑧⑤0⑥，欢迎入群了解，可自定义任意音乐。",
                            "tickdelay": note["tick"],
                            "executeOnFirstTick": 0,
                            "trackOutput": 1,
                            "conditional": 0,
                            "needRedstone": 0}]
            elif note["type"] == "command":
                blocks += [{"direction": [x, y, z],
                            "block_name": "chain_command_block",
                            # "particular_value": facing_direction,
                            "particular_value": "",
                            "impluse": 2,
                            "command": note["command"],
                            "customName": note["customName"],
                            "lastOutput": "",
                            "tickdelay": 0,
                            "executeOnFirstTick": 0,
                            "trackOutput": 1,
                            "conditional": 0,
                            "needRedstone": 0}]
                # print(note)
            if length < kwargs["length"]:
                if facing_x:
                    facing_direction = 5
                    x += 1
                else:
                    facing_direction = 4
                    x -= 1
                if length == 0:
                    conditional = 0
                else:
                    # conditional = 1
                    conditional = 0
                length += 1
            else:
                length = 0
                facing_x = not facing_x
                if width < kwargs["width"]:
                    if facing_z:
                        facing_direction = 3
                        z += 1
                    else:
                        facing_direction = 2
                        z -= 1
                    width += 1
                else:
                    width = 0
                    facing_direction = 1
                    y += 1
                    if facing_direction == 1:
                        facing_z = not facing_z
                conditional = 0
            blocks[-1]["conditional"] = conditional
            blocks[-1]["particular_value"] = facing_direction
        blocks[0]["impluse"] = 0
        blocks[0]["needRedstone"] = 1
        blocks[1]["conditional"] = 0
        # print(blocks)
        print(blocks.__len__())
        return blocks, music_id

    def mid2data_2(self, channel):
        self.channel = channel
        note_num = 0
        c_time = 0  # 用来抽走邪恶的零音量时间
        for message in self.mid:
            if hasattr(message, "channel"):
                if not (message.channel in self.program):
                    self.program[message.channel] = 0
            if message.type == "note_on":
                self.notes += [{"mid_note": message.note,
                                "mid_velocity": message.velocity,
                                "note": round(2 ** ((message.note - 66) / 12), 6),
                                "velocity": round(message.velocity / 127, 3),
                                "time": 0,
                                "program": self.program[message.channel],
                                "type": "note"}]
                note_num += 1
            if self.notes.__len__() > 0:
                self.notes[-1]["time"] += message.time * (500000 / self.tempo) + c_time
                c_time = 0
            if message.type != "note_on":
                if message.type == "set_tempo":
                    self.tempo = message.tempo
                if message.type == "program_change" and channel == -1:
                    self.program[message.channel] = message.program
                elif message.type == "program_change" and channel != -1:
                    self.program[message.channel] = channel
            else:
                if message.velocity == 0:
                    c_time = self.notes.pop(-1)["time"]

                    note_num -= 1
                    pass
        for i, note in enumerate(self.notes):
            if i > 0:
                self.notes[i]["global_time"] = self.notes[i - 1]["global_time"] + self.notes[i]["time"]
            else:
                self.notes[i]["global_time"] = self.notes[i]["time"]
            self.notes[i]["global_tick"] = note["global_time"] * 20
        # print(self.notes)
        pass

    def data2cb_2(self, song_name="", **kwargs):
        kwargs = kwargs["kwargs"]
        music_id = randint(-2147483646, 2147483646)

        self.notes.insert(0, {"type": "command",
                              "command": f"scoreboard players set @a[scores={{MR_music={music_id}, MR_progress={self.notes[-1]['global_tick']}}}] MR_music 0",
                              "customName": song_name})
        self.notes.insert(0, {"type": "command",
                              "command": f"scoreboard objectives add MR_progress dummy",
                              "customName": ""})
        self.notes.insert(0, {"type": "command",
                              "command": f"scoreboard objectives add MR_music dummy",
                              "customName": "Have fun !"})
        self.notes.insert(0, {"type": "command",
                              "command": f"scoreboard players add @a[scores={{MR_music={music_id}}}, tag=!MR_pause] MR_progress 1",
                              "customName": song_name})
        max_time = self.notes[-1]["global_time"]
        max_tick = self.notes[-1]["global_tick"]
        for i, time, in enumerate(range(0, round(max_tick), round(max_tick//10))):
            self.notes.insert(-1, {"type": "progress",
                                   "global_time": round(i),
                                   "progress": i})
        blocks = []
        length = 0
        width = 0  # 计数器
        y = z = 0  # 实际位置
        x = 1
        facing_z = facing_x = True

        for note in self.notes:
            if note["type"] == "progress":
                blocks += [{"direction": [x, y, z],
                            "block_name": "chain_command_block",
                            "particular_value": 0,
                            "impluse": 1,
                            "command": f'titleraw @a[tag=MR_title, scores={{MR_music={music_id}}}] actionbar {{"rawtext":[{{"text"}}:"{song_name}\\n{round(note["global_time"] // 60)}:{round(note["global_time"] % 60)} [{"|" * note["progress"] + "-" * (10 - note["progress"])}] {round(max_time//60)}:{round(max_time%60)}\\n Powered by MoodyRhythm"]}}',
                            "customName": f"进度条：{10 * note['progress']}%",
                            "lastOutput": "",
                            "tickdelay": 0,
                            "executeOnFirstTick": 0,
                            "trackOutput": 1,
                            "conditional": 0,
                            "needRedstone": 0}]
            elif note["type"] == "note":
                blocks += [{"direction": [x, y, z],
                            "block_name": "chain_command_block",
                            "particular_value": 0,
                            "impluse": 2,
                            "command": f'execute @a[scores={{MR_music={music_id}, MR_progress={round(note["global_tick"])}}}] ~~1~ playsound note.{self.programs[note["program"]]} @s ~~~ {note["velocity"]} {note["note"]}',
                            "customName": f"MoodyRhythm",
                            "lastOutput": "From MoodyRhythm(TencentGroup 961748506): Have fun !",
                            "tickdelay": 0,
                            "executeOnFirstTick": 0,
                            "trackOutput": 1,
                            "conditional": 0,
                            "needRedstone": 0}]
            elif note["type"] == "command":
                blocks += [{"direction": [x, y, z],
                            "block_name": "chain_command_block",
                            # "particular_value": facing_direction,
                            "particular_value": "",
                            "impluse": 2,
                            "command": note["command"],
                            "customName": note["customName"],
                            "lastOutput": "",
                            "tickdelay": 0,
                            "executeOnFirstTick": 0,
                            "trackOutput": 1,
                            "conditional": 0,
                            "needRedstone": 0}]
            if length < kwargs["length"]:
                if facing_x:
                    facing_direction = 5
                    x += 1
                else:
                    facing_direction = 4
                    x -= 1
                if length == 0:
                    conditional = 0
                else:
                    # conditional = 1
                    conditional = 0
                length += 1
            else:
                length = 0
                facing_x = not facing_x
                if width < kwargs["width"]:
                    if facing_z:
                        facing_direction = 3
                        z += 1
                    else:
                        facing_direction = 2
                        z -= 1
                    width += 1
                else:
                    width = 0
                    facing_direction = 1
                    y += 1
                    if facing_direction == 1:
                        facing_z = not facing_z
                conditional = 0
            blocks[-1]["conditional"] = conditional
            blocks[-1]["particular_value"] = facing_direction
        blocks[0]["impluse"] = 1
        blocks[0]["needRedstone"] = 1
        blocks[1]["conditional"] = 0
        return blocks, music_id

    def mid2bdx(self, basename, kwargs):
        if kwargs["way"] == "condition":
            self.mid2data_1(kwargs["channel"])
            blocks, music_id = self.data2cb_1(song_name=basename[0: 15], kwargs=kwargs)
        else:  # scb
            self.mid2data_2(kwargs["channel"])
            blocks, music_id = self.data2cb_2(song_name=basename[0: 15], kwargs=kwargs)
        bdx_path = f"{self.bdx_path}//{basename}&MoodyRhythm.bdx"
        BdxConverter(bdx_path, "MoodyRhythm", blocks)
        return music_id, bdx_path

    def bdx_from_mid(self, music_name, mid_path, kwargs):
        """
                :param music_name:
                :param mid_path:
                :param kwargs: way, length, width, channel
                :return:
                """
        self.mid = mido.MidiFile(mid_path)
        music_id, bdx_path = self.mid2bdx(basename=music_name, kwargs=kwargs)
        return music_id, bdx_path

    def bdx_from_audio(self, music_name, audio_path, kwargs):
        self.basename = music_name

        mid_path = f"{self._mid_path}//{self.basename}.mid"
        if not os.path.exists(mid_path):
            try:
                self.mid_path = music2mid(audio_path, mid_path)
            except BaseException as err:
                raise err
        music_id, bdx_path = self.bdx_from_mid(music_name, mid_path, kwargs=kwargs)
        return music_id, bdx_path

    def bdx_from_bili(self, music_name, bvid, **kwargs):

        self.basename = music_name
        audio_path = self.audio_path + f"//{music_name}.aac"
        if not os.path.exists(audio_path):
            try:
                download_bv(bvid, audio_path, has_await=False)
            except BaseException as err:
                raise err
        music_id, bdx_path = self.bdx_from_audio(music_name, audio_path, kwargs=kwargs)
        return music_id, bdx_path


if __name__ == '__main__':
    music = RedstoneMusic()
    # print(music.music2bdx("condition"))
    kwargs = {"way":"condition", "length":15, "width":15, "channel":-1, "id":10}
    # music.bdx_from_bili("The Kid LAROI--oskarpianist(BV15P4y1p7gJ)", "BV15P4y1p7gJ", way="condition", length=15, width=15, channel=-1, qq="MoodyRhythm", id=10)

    music.bdx_from_audio("LOVETHING", "D:\DataMessage\\1758489207\FileRecv\LOVETHING.mp3", kwargs=kwargs)
    # music.bdx_from_mid("crossing_field", "D:\WorkPlus\Charlie_Python\QQBot\Dan-Bot\Dan-src\plugins\mp3ToWorld\mid\crossing_field.mid", kwargs=kwargs)
    # music = mido.midFile("D:\WorkPlus\Charlie_Python\QQBot\Dan-Bot\Dan-src\plugins\mp3ToWorld\mid\敢杀我的马.mid")
    
