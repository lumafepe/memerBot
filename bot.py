from discord import guild
from utils import*
from botUtils import*
from sink import MySink
from botClass import MemeDiscordBot
from discord.utils import get
import discord
from discord.ext import tasks
import kanye as kanyeQuotes
from keep_alive import keep_alive

if __name__ == '__main__':
	client = MemeDiscordBot()	

	@tasks.loop(seconds = 1)
	async def rape():
		for ctx in client.ctxL.values():
			if random.random()<0.00001:
				await play(client,ctx,"earRape")

	def check_voice(ctx,sink:MySink):
		vc = get(ctx.bot.voice_clients, guild=ctx.guild)
		if not vc.recording:
			vc.start_recording(sink,voiceReceiver_callback,ctx)
			sink.updateData.start(3)
			sink.playAudio.start(ctx,client.locs[ctx.guild.id])


	@client.event
	async def on_ready():
		"""Bot-ready message"""
		print(client.user.name, 'ready!')


	@client.command(pass_context=True)
	async def genQuote(ctx):
		content=ctx.message.content
		args=content.split()
		if len(args)==3:
			id=int(args[1][2:-1])
			seconds=int(args[2])
			if 0>seconds>30:
				await ctx.send("not a valid time")
			elif id not in client.sink[ctx.guild.id].audio_data:
				await ctx.send("not a valid user to record")
			else: client.sink[ctx.guild.id].storeQuote(id,seconds)
		elif len(args)==2 and args[1]=='-h': await ctx.send("usage: genQuote {@person} {Number of seconds (max 30)}")
		else: await ctx.send("invalid number of arguments")

	@client.command(pass_context=True)
	async def saveQuote(ctx):
		content=ctx.message.content
		args=content.split()
		if len(args)!=2:
			await ctx.send("wrong number of arguments")
			return
		#else
		if args[1]=='-h':
			await ctx.send('usage: saveQuote command_name')
			return
		if client.sink[ctx.guild.id].saveQuote(removeAccentuation(args[1].lower()),client.locs[ctx.guild.id]):
			await ctx.send('saved with success')
		else:
			await ctx.send('nothing in the queue')

	@client.command(pass_context=True)
	async def quote(ctx):
		content=ctx.message.content
		args=content.split()
		if len(args)<2:
			await ctx.send("wrong number of arguments")
			return
		out=getFamousQuote(args[1])
		if out!="":
			await ctx.send(out)
			return

	@client.command(pass_context=True)
	async def kanye(ctx):
		await ctx.send(kanyeQuotes.quote())

	@client.command(pass_context=True)
	async def help(ctx):
		"""help to show helpfull Bot commands"""
		with open('bot.py') as f:
			lines = f.readlines()
		Commands=[]
		for i in range(len(lines)):
			if "@client.command(pass_context=True)" in lines[i] and "async def" in lines[i+1]:
				line=lines[i+1]
				space,untreatedcommand=line.split("async def ")
				command,newline=untreatedcommand.split("(ctx):")
				Commands.append(command)
		Commands+=list(client.locs[ctx.guild.id].keys())
		s="```\n"
		for i in Commands:
			s+=client.prefix+str(i)+"\n"
		s+="```"
		await ctx.send(s)

	@client.command(pass_context=True)
	async def connect(ctx):
		"""Bot to join voice room on "connect" command"""
		if ctx.author.voice:
			createFilesNeeded(ctx.guild.id)
			client.sink[ctx.guild.id] = MySink(client.recog,ctx.guild.id,client)
			client.locs[ctx.guild.id]=load_commands(ctx.guild.id)
			client.ctxL[ctx.guild.id]=ctx
			channel = ctx.message.author.voice.channel
			await channel.connect()
			check_voice(ctx,client.sink[ctx.guild.id])
			if len(client.ctxL)==0:
				check_sound.start()
				rape.start()
			try: client.SoundQueue[ctx.guild.id]
			except: client.SoundQueue[ctx.guild.id] = []
		else:
			await ctx.send("You're not in a voice room.")
		return

	@client.command(pass_context=True)
	async def leave(ctx):
		"""Bot to leave voice room on "leave" command"""
		if ctx.voice_client:
			await ctx.guild.voice_client.disconnect()
			try: del client.ctxL[ctx.guild.id]
			except: pass
			try: del client.sink[ctx.guild.id]
			except: pass
			try: del client.locs[ctx.guild.id]
			except: pass
			if len(client.ctxL)==0:
				check_sound.stop()
				rape.stop()
			try: del client.SoundQueue[ctx.guild.id]
			except: pass
		else:
			await ctx.send("I'm not in a voice room.")
		return

	@tasks.loop(seconds = 0.1)
	async def check_sound():
		"""Play sound in the queue if current music stops"""
		for ctx in client.ctxL.values():
			voice = get(client.voice_clients, guild=ctx.guild)
			if not client.SoundQueue[ctx.guild.id] or not client.SoundStatus[ctx.guild.id]:
				return
			if not voice.is_playing():
				if client.SoundPlaying[ctx.guild.id]:
					del client.SoundQueue[ctx.guild.id][0]
					if (client.SoundQueue[ctx.guild.id]):
						await play(client,ctx, client.SoundQueue[ctx.guild.id][0])


	@client.command(pass_context=True)
	async def skip(ctx):
		"""skip current sound"""
		voice = get(client.voice_clients, guild=ctx.guild)
		voice.pause()
		if len(client.SoundQueue[ctx.guild.id]) >= 1:
			del client.SoundQueue[ctx.guild.id][0]
		if (client.SoundQueue[ctx.guild.id]):
			await play(client,ctx, client.SoundQueue[ctx.guild.id][0])




    

	@client.command(pass_context=True)
	async def delCommand(ctx):
		content=ctx.message.content
		args=content.split()
		if len(args)!=2:
			await ctx.channel.send("invalid number of arguments")
			return
		if args[1]=="-h":
			await   ctx.send("usage: +delCommand name")
		else:
			try:
				Name=args[1].lower()
				values=client.locs[ctx.guild.id].pop(Name)
				save_commands(ctx.guild.id,client.locs[ctx.guild.id])
				[os.rm(i) for i in values["files"]]
				await ctx.send("Done")
				return
			except:
				await ctx.send("Not a name")
				return




	@client.command(pass_context=True)
	async def addCommand(ctx):
		content=ctx.message.content
		args=content.split()
		if len(args)!=2 and len(args)!=3:
			await ctx.channel.send("invalid number of arguments")
			return
		if args[1]=="-h":
			await   ctx.send("usage: +addCommand name Type(text/voice/image)")
		else:
			try:
				Name=removeAccentuation(args[1].lower())
				Type=args[2].lower()
			except:
				await ctx.send("invalid number of arguments")
				return
			client.locs[ctx.guild.id][Name]={"type":Type,"files":[]}
			save_commands(ctx.guild.id,client.locs[ctx.guild.id])
			await ctx.send("added a new command")



	@client.command(pass_context=True)
	async def addFile(ctx):
		content=ctx.message.content
		args=content.split()
		if len(args)!=2 and len(args)!=3:
			await ctx.channel.send("invalid number of arguments")
			return
		if args[1]=="-h":
			await   ctx.send("usage: +addFile name link/text")
		else:
			Name=removeAccentuation(args[1].lower())
			try:
				Type=client.locs[ctx.guild.id][Name]["type"]
			except:
				await ctx.channel.send("invalid command name")
				return
			if Type=="voice":
				NewEntrance=await addAudio(Name,ctx,client.locs[ctx.guild.id])
			elif Type=="image":
				NewEntrance=await addImage(Name,ctx,client.locs[ctx.guild.id])
			elif Type=="text":
				NewEntrance=await addText(ctx)
			else:
				await ctx.channel.send("not a type")
				return
			if NewEntrance==None: return
			client.locs[ctx.guild.id][Name]["files"].append(NewEntrance)
			save_commands(ctx.guild.id,client.locs[ctx.guild.id])
			await ctx.channel.send("added file with success")


	@client.event
	async def on_message(message):
		if message.author.bot:
			return
		content = message.content
		if list(filter(content.startswith, client.prefix)) == []:
			return
		content = content[1:]
		#actual commands
		try:
			command=client.locs[message.guild.id][content]
			Type = command["type"]
			files = command["files"]
			if files==[]:
				await message.channel.send("nothing to respond to that request")
			elif Type=="voice":
				await play(client,message,content)
				return
			elif Type=="text":
				if random.random()<0.01:
					await message.channel.send("RANDOMSORT=META")
					return
				else:
					await message.channel.send(random.choice(files))
					return
			elif Type=="image":
				await message.channel.send(file=discord.File(random.choice(files)))
				return
		except:
			try: await client.process_commands(message)
			except: await message.channel.send("wtf r u talking about")


	keep_alive()
	client.run(client.token)