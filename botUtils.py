
from utils import *
import asyncio
import os
from u2be import *
import discord
from discord.utils import get

#returns the newEntrance or NONE if invalid
async def addImage(Name:str,ctx,loc:dict):
    args=ctx.message.content.split()
    if len(args)==2:
        try:
            NewEntrance=f"imageFiles/{getNewLinkName(Name,loc)}.png"
            await ctx.attachments[0].save(NewEntrance)
            return NewEntrance
        except:
            await ctx.channel.send("invalid attatchment")
            return None
    else:
        await ctx.channel.send("invalid number of arguments to add an image")
        return None

async def addAudio(Name:str,ctx,loc:dict):
    args=ctx.message.content.split()
    if len(args)==2:
        try:
            NewEntrance=f"audioFiles/{getNewLinkName(Name,loc)}.mp3"
            await ctx.attachments[0].save(NewEntrance)
            return NewEntrance
        except:
            await ctx.channel.send("invalid attachment")
            return None

    elif len(args)==3:
        link=args[2]
        try:
            NewEntrance=safeMp3File(link,getNewLinkName(Name,loc))
            return NewEntrance
        except:
            await ctx.channel.send("invalid link")
            return None
    else:
        await ctx.channel.send("invalid number of arguments to add a audio")
        return None

async def addText(ctx):
    args=ctx.message.content.split()
    if args!=3:
        return args[2]
    else:
        await ctx.channel.send("invalid number of arguments to add a text")
        return None




async def voiceReceiver_callback(sink, channel, *args):
    await asyncio.sleep(0.1)

def getfullPath(name:str):
    path=os.getcwd()
    return os.path.join(path,name)

def createFilesNeeded(id:int):
    cd=os.getcwd()
    files=map(getfullPath,[f"{id}",f"{id}/imageFiles",f"{id}/audioFiles"])
    for file in files:
        if (not os.path.exists(file)): 
            os.mkdir(file)
    file=getfullPath(f"{id}/commands.json")
    if (not os.path.exists(file)):
        with open(file,"w") as f:
            json.dump({},f)
    

async def play(client,ctx, command: str):
    """Bot to play on "play command names" command"""
    voice = get(client.voice_clients, guild=ctx.guild)

    if voice.is_playing():
        client.SoundQueue[ctx.guild.id].append(command)
        return

    if not command in client.SoundQueue[ctx.guild.id]:
        client.SoundQueue[ctx.guild.id].append(command)

    client.SoundPlaying[ctx.guild.id] = True
    file=random.choice(client.locs[ctx.guild.id][command]["files"])
    voice.play(discord.FFmpegPCMAudio(executable=client.ffmpeg, source=file))
    voice.source.volume = 2