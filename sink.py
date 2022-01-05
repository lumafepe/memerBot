
from utils import *
import discord
from discord.utils import get
from discord.ext import tasks
import wave

class MySink(discord.Filters):
    """
    Buffer to store the information exported by the startRecording
    Not stock supported
    """
    def __init__(self,id:int,client,filters=None):
        self.filters = {'time': 0,'users': [],'max_size': 0,}
        discord.Filters.__init__(self, **self.filters)
        self.sample_width = 2
        self.sample_rate = 96000
        self.bytes_ps = 192000

        self.bytesto30 = {}
        self.voiceQueue = []
        self.vc = None
        self.audio_data = {}
        self.quoteQueue=[]
        self.guild=id
        self.client=client


    def init(self, vc):  # called under start_recording
        self.vc = vc
        super().init()

    @discord.Filters.filter_decorator
    def write(self, data, user):
        #add user to the dict
        if user not in self.audio_data:
            self.audio_data.update({user:bytearray()})
            self.bytesto30.update({user:0})
        #add data to user
        self.audio_data[user] += data

    def storeQuote(self,id:int,seconds:int): # stores the quote temporarly
        numberOfBytes=seconds*self.bytes_ps
        numberof30sec=30*self.bytes_ps
        byteWhereToStart=numberof30sec-numberOfBytes
        bytesAvaiable=len(self.audio_data[id])
        if bytesAvaiable<numberOfBytes: byteWhereToStart=0
        self.quoteQueue.append(self.audio_data[id][byteWhereToStart:])

    def saveQuote(self,name:str,loc:dict): #saves the quote permently and ads it to the dictionary
        if len(self.quoteQueue)==0: return False
        audioData=self.quoteQueue.pop(0)
        if name not in loc: loc[name]={"files": [], "type": "voice"}
        filename=f'{self.guild}/audioFiles/{getNewLinkName(name,loc)}.wav'
        loc[name]["files"].append(filename)
        save_commands(self.guild,loc)
        with wave.open(filename, mode='wb') as f:
            f.setparams((2, 2, 48000, 0, 'NONE', 'NONE'))
            f.writeframes(audioData)
        return True


    @tasks.loop(seconds = 0.1)
    async def updateData(self,second:int):
        bytesToRead = self.bytes_ps*second
        bytes30seg = self.bytes_ps*30
        for user in self.audio_data:
            userData = self.audio_data[user]
            bytesUntil30=bytesToRead+self.bytesto30[user]
            if len(userData)>bytesToRead+bytes30seg:
                self.voiceQueue.append(userData[bytes30seg:bytes30seg+bytesToRead])
                del userData[:bytesToRead]
            elif bytesUntil30<len(userData)<bytes30seg:
                self.voiceQueue.append(userData[self.bytesto30[user]:bytesUntil30])
                self.bytesto30[user]+=bytesToRead

    def cleanup(self):
        self.finished = True