
from utils import *
import asyncio
import os
from u2be import *
import discord
import shutil
from discord.utils import get

#returns the newEntrance or NONE if invalid
async def addImage(Name:str,ctx,loc:dict):
    id=ctx.guild.id
    args=ctx.message.content.split()
    if len(args)==2:
        try:
            NewEntrance=f"{id}/imageFiles/{getNewLinkName(Name,loc)}.png"
            await ctx.message.attachments[0].save(NewEntrance)
            return NewEntrance
        except:
            await ctx.channel.send("invalid attatchment")
            return None
    else:
        await ctx.channel.send("invalid number of arguments to add an image")
        return None

async def addAudio(Name:str,ctx,loc:dict):
    id=ctx.guild.id
    args=ctx.message.content.split()
    if len(args)==2:
        try:
            if "mp3" in ctx.message.attachments[0].filename:
                NewEntrance=f"{id}/audioFiles/{getNewLinkName(Name,loc)}.mp3"
            if "wav" in ctx.message.attachments[0].filename:
                NewEntrance=f"{id}/audioFiles/{getNewLinkName(Name,loc)}.wav"
            await ctx.message.attachments[0].save(NewEntrance)
            return NewEntrance
        except Exception as e:
            print(e)
            await ctx.channel.send("invalid attachment")
            return None

    elif len(args)==3:
        link=args[2]
        try:
            NewEntrance=safeMp3File(link,id,getNewLinkName(Name,loc))
            if NewEntrance=="video is too big":
                await ctx.channel.send("the video is too big to be added")
                return None
            else: return NewEntrance
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




async def useless(sink,*args):
    await asyncio.sleep(0.001)

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
    


def copyServers(idOrigin:int,idDest:int,originDict:dict):
    cd=os.getcwd()
    folder=getfullPath(f"{idDest}")
    try:
        shutil.rmtree(folder)
    except OSError as e: pass
    shutil.copytree(f"{idOrigin}",f"{idDest}")
    strdic=json.dumps(originDict)
    strdic=strdic.replace(f"{idOrigin}",f"{idDest}")
    newDic=json.loads(strdic)
    save_commands(idDest,newDic)

