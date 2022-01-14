from discord.ext.commands import AutoShardedBot
import os
import json
from sink import MySink
from botUtils import *
from utils import *
import random
import discord
from discord.ext import tasks


class MemeDiscordBot(AutoShardedBot):
    def __init__(self,recog="vosk"):
        with open('config.json') as json_file:
            config = json.load(json_file)
        super(MemeDiscordBot, self).__init__(command_prefix=config["Invocation"],fetch_offline_members=False,case_insensitive=False,help_command=None)
        if os.name=='nt': self.ffmpeg=config["ffmpegWindows"]
        else: self.ffmpeg=config["ffmpegLinux"]
        self.prefix=config["Invocation"]
        self.token=config["token"]
        self.recog=recog
        self.ptmodel = Model("modelPT")
        self.servers={}


    def addServer(self,ctx):
        id=ctx.guild.id
        sink=MySink(id,ctx)
        vc=None
        try:
            self.servers[id].ctx=ctx
            self.servers[id].vc=vc
            self.servers[id].sink=sink
            self.servers[id].addRecognizer(self.ptmodel,"pt")
        except:
            createFilesNeeded(id)
            loc=load_commands(id)
            self.servers[id]=serverClient(self.recog,id,ctx,vc,loc,sink,self.ffmpeg,self.ptmodel)

    def addNonVoiceSercer(self,message):
        id=message.guild.id
        createFilesNeeded(id)
        loc=load_commands(id)
        self.servers[id]=serverClient(self.recog,id,None,None,loc,None,self.ffmpeg,None)


    def KillServer(self,ctx):
        id=ctx.guild.id
        self.servers[id].suicide()
        del self.servers[id]
class serverClient():
    def __init__(self,recog:str,id:int,ctx,vc,loc:dict,sink:MySink,ffmpeg:str,ptmodel):
        self.id=id
        self.ctx=ctx
        self.vc=vc
        self.ffmpeg=ffmpeg
        self.waiting = False
        self.timer = 0
        self.SoundPlaying = False
        self.SoundQueue = []
        self.SoundTimer = 0
        self.SoundStatus = False
        self.loc=loc
        self.sink=sink
        self.recog=recog
        if recog=="vosk":
            SetLogLevel(0)
            if ptmodel:
                self.ptRecognizer = KaldiRecognizer(ptmodel,48000)
                self.ptRecognizer.SetWords(True)
            else: self.ptRecognizer = None

    def addRecognizer(self,model:Model,lang:str):
        if lang == 'pt':
            self.ptRecognizer = KaldiRecognizer(model,48000)
            self.ptRecognizer.SetWords(True)


    async def play(self,command: str):
        """Bot to play on "play command names" command"""
        if self.vc.is_playing():
            self.SoundQueue.append(command)
            return
        if not command in self.SoundQueue:
            self.SoundQueue.append(command)

        self.SoundPlaying = True
        if self.loc[command]["files"]:
            file=random.choice(self.loc[command]["files"])
            self.vc.play(discord.FFmpegPCMAudio(executable=self.ffmpeg, source=file))
            self.vc.source.volume = 2

    async def skip(self):
        """skip current sound"""
        self.vc.pause()
        if len(self.SoundQueue) >= 1:
            del self.SoundQueue[0]
        if (self.SoundQueue):
            await self.play(self.SoundQueue[0])

    @tasks.loop(seconds = 1)
    async def rape(self):
        if random.random()<0.00001:
            await self.play("earRape")

    @tasks.loop(seconds = 0.1)
    async def playAudio(self):
        for _ in range(len(self.sink.voiceQueue)):
            data=self.sink.voiceQueue.pop(0)
            if (self.recog=="vosk"):
                mono=convertToMono(data)

                textdict=json.loads(unsafe_Vosk_speech_to_text(self.ptRecognizer,mono))# remove if you don't want portuguese
                text=textdict["text"] # remove if you don't want portuguese
                print(text)
            for i in text.split():
                try:
                    name=removeAccentuation(i.lower())
                    if self.loc[name]["type"]=="voice":
                        await self.play(name)
                except: pass


    @tasks.loop(seconds = 0.1)
    async def check_sound(self):
        """Play sound in the queue if current music stops"""
        if not self.SoundQueue or not self.SoundStatus: return
        if not self.vc.is_playing():
            if self.SoundPlaying:
                del self.SoundQueue[0]
                if (self.SoundQueue):
                    await self.play(self.SoundQueue[0])


    def genQuote(self,content):
        args=content.split()
        if len(args)==3:
            id=int(args[1][2:-1])
            seconds=int(args[2])
            if 0>seconds>30:
                return "not a valid time"
            elif id not in self.sink.audio_data:
                return "not a valid user to record"
            else: 
                self.sink.storeQuote(id,seconds)
                return f"quote stored temporarly is now in the {len(self.sink.quoteQueue)} position"
        elif len(args)==2 and args[1]=='-h': return "usage: genQuote {@person} {Number of seconds (max 30)}"
        else: return "invalid number of arguments"


    def saveQuote(self,content):
        args=content.split()
        if len(args)!=2: return("wrong number of arguments")
        if args[1]=='-h': return('usage: saveQuote command_name')
        if self.sink.saveQuote(removeAccentuation(args[1].lower()),self.loc):
            return('saved with success')
        return('nothing in the queue')


    def delCommand(self,content):
        args=content.split()
        if len(args)!=2: return "invalid number of arguments"
        if args[1]=="-h": return "usage: +delCommand name"
        try:
            Name=args[1].lower()
            values=self.loc.pop(Name)
            save_commands(self.id,self.loc)
            [os.remove(i) for i in values["files"]]
            return "Done"
        except:
            return "Not a name"

    def addCommand(self,content):
        args=content.split()
        if len(args)==2 and args[1]=="h":return "usage: +addCommand name Type(text/voice/image)"
        if len(args)!=3: return "invalid number of arguments"
        try:
            Name=removeAccentuation(args[1].lower())
            Type=args[2].lower()
            if Type not in ["voice","text","image"]: return "not a valid type"
            if Name in self.loc: return "command already exists"
            self.loc[Name]={"type":Type,"files":[]}
            save_commands(self.id,self.loc)
            return "added a new command"
        except: return "invalid arguments"


    async def addFile(self,ctx):
        content=ctx.message.content
        args=content.split()
        if len(args)!=2 and len(args)!=3:
            await ctx.channel.send("invalid number of arguments")
            return
        if args[1]=="-h":
            await ctx.send("usage: +addFile name link/text")
            return
        Name=removeAccentuation(args[1].lower())
        try: Type=self.loc[Name]["type"]
        except:
            await ctx.channel.send("invalid command name")
            return
        if Type=="voice":NewEntrance=await addAudio(Name,ctx,self.loc)
        elif Type=="image":NewEntrance=await addImage(Name,ctx,self.loc)
        elif Type=="text":NewEntrance=await addText(ctx)
        else:
            await ctx.channel.send("not a type")
            return
        if NewEntrance==None: return
        self.loc[Name]["files"].append(NewEntrance)
        save_commands(self.id,self.loc)
        await ctx.channel.send("added file with success")

    def postConnect(self,vc):
        self.vc=vc
        if not self.vc.recording:
            self.vc.start_recording(self.sink,useless)
            self.sink.updateData.start(3)
            self.playAudio.start()
        self.check_sound.start()
        self.rape.start()

    def suicide(self):
        self.check_sound.stop()
        self.rape.stop()
        self.sink.updateData.stop()
        self.playAudio.stop()
