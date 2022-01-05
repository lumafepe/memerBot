from discord.ext.commands import AutoShardedBot
import os
import json

class MemeDiscordBot(AutoShardedBot):
    def __init__(self,recog="vosk"):
        with open('config.json') as json_file:
            config = json.load(json_file)
        super(MemeDiscordBot, self).__init__(command_prefix=config["Invocation"],fetch_offline_members=False,case_insensitive=False,help_command=None)
        if os.name=='nt': self.ffmpeg=config["ffmpegWindows"]
        else: self.ffmpeg=config["ffmpegLinux"]
        self.prefix=config["Invocation"]
        self.token=config["token"]
        self.waiting = {}
        self.timer = {}
        self.SoundPlaying = {}
        self.SoundQueue = {}
        self.SoundTimer = {}
        self.SoundStatus = {}
        self.locs={}
        self.sink={}
        self.recog=recog
        self.ctxL={}