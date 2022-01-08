from discord import guild, threads
from utils import*
from botUtils import*
from threading import Thread
from botClass import MemeDiscordBot
from discord.utils import get
import discord
from discord.ext import tasks
import kanye as kanyeQuotes
from keep_alive import keep_alive
from vosk import Model, KaldiRecognizer,SetLogLevel

if __name__ == '__main__':
	client = MemeDiscordBot()	
	
	@client.event
	async def on_ready():
		"""Bot-ready message"""
		print(client.user.name, 'ready!')


	@client.command(pass_context=True)
	async def genQuote(ctx):
		await ctx.send(client.servers[ctx.guild.id].genQuote(ctx.message.content))

	@client.command(pass_context=True)
	async def saveQuote(ctx):
		await ctx.send(client.servers[ctx.guild.id].saveQuote(ctx.message.content))

	@client.command(pass_context=True)
	async def quote(ctx):
		content=ctx.message.content
		args=content.split()
		if len(args)<2:
			await ctx.send("wrong number of arguments")
			return
		out=getFamousQuote(args[1])
		if out!="": await ctx.send(out)
		else: await ctx.send("who the fuck is that")

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
		Commands+=list(client.servers[ctx.guild.id].loc.keys())
		s="```\n"
		for i in Commands:
			s+=client.prefix+str(i)+"\n"
		s+="```"
		await ctx.send(s)
		return

	@client.command(pass_context=True)
	async def connect(ctx):
		"""Bot to join voice room on "connect" command"""
		if ctx.author.voice:
			channel = ctx.message.author.voice.channel
			client.addServer(ctx)			
			await channel.connect()
			client.servers[ctx.guild.id].postConnect(get(client.voice_clients, guild=ctx.guild))
		else: await ctx.send("You're not in a voice room.")
		return

	@client.command(pass_context=True)
	async def leave(ctx):
		"""Bot to leave voice room on "leave" command"""
		if ctx.voice_client:
			await ctx.guild.voice_client.disconnect()
			client.KillServer(ctx)
		else: await ctx.send("I'm not in a voice room.")
		return


	@client.command(pass_context=True)
	async def skip(ctx):
		"""skip current sound"""
		await client.servers[ctx.guild.id].skip()
    

	@client.command(pass_context=True)
	async def delCommand(ctx):
		await ctx.send(client.delCommand(ctx.message.content))

	@client.command(pass_context=True)
	async def addCommand(ctx):
		await ctx.send(client.servers[ctx.guild.id].addCommand(ctx.message.content))


	@client.command(pass_context=True)
	async def addFile(ctx):
		t=Thread(target=client.servers[ctx.guild.id].addFile,args=(ctx,))
		t.start()
		await asyncio.sleep(0.001)
		


	@client.event
	async def on_message(message):
		if message.author.bot: return
		content = message.content
		if list(filter(content.startswith, client.prefix)) == []: return
		content = content[1:]
		try:
			try: client.servers[message.guild.id]
			except: client.addNonVoiceSercer(message)
			command=client.servers[message.guild.id].loc[content]
			Type = command["type"]
			files = command["files"]
			if files==[]: await message.channel.send("nothing to respond to that request")
			elif Type=="voice":
				await client.servers[message.guild.id].play(content)
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