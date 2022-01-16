import unidecode
import sys
from io import StringIO
import random
import quote_generator
from os import path
import json
from vosk import Model, KaldiRecognizer,SetLogLevel

def convertToMono(audioData:bytearray):
    datamono=bytearray()
    for i in range(0,len(audioData),4):
        datamono+=bytes(audioData[i:i+2])
    return datamono



def removeAccentuation(input:str):
    return unidecode.unidecode(input)


def getFamousQuote(InputName:str):
    inputN=InputName.lower()
    fullName=""
    names=[("motivational",["motivational","motivation"]),("albert_einstein",["albert","einstein","genio"]),("mahatma_gandhi",["mahatma","gandhi","india"]),("steve_jobs",["steve","jobs","apple","merda"]),("bill_gates",["bill","gates","microsoft"]),("elon_musk",["elon","musk","tesla","spacex"]),("mark_zuckerberg",["mark","zuckerberg","facebook"])]
    for currentFullName,listOfNames in names:
        for name in listOfNames:
            if inputN==name:
                fullName=currentFullName
                break
        if fullName!="": break

    if fullName=="": return ""
    old_stdout = sys.stdout
    redirected_output = sys.stdout = StringIO()
    exec(f"quote_generator.{fullName}_quotes()")
    sys.stdout = old_stdout
    f=lambda x: x!="" and x[0]!="―"
    validList=list(filter(f,redirected_output.getvalue().split("\n")))
    return random.choice(validList)


def getNewLinkName(Name:str,loc:dict):
    n=len(loc[Name]["files"])
    if n==0: return Name
    else: return Name+str(n)








def load_commands(id:int):
    if (not path.exists(f'{id}/commands.json')): return {}
    with open(f'{id}/commands.json') as json_file:
        List_Of_Commands = json.load(json_file)
    return List_Of_Commands

def save_commands(id:int,loc:dict):
    with open(f'{id}/commands.json', 'w') as outfile:
        json.dump(loc, outfile)

def safe_Vosk_speech_to_text(rec:KaldiRecognizer,Monodata):
    breakingpoint = 0
    while True:
        data = bytes(Monodata[breakingpoint:breakingpoint+4000])
        if len(data) == 0: break
        rec.AcceptWaveform(data)
        breakingpoint += 4000
    return rec.FinalResult()

def unsafe_Vosk_speech_to_text(rec:KaldiRecognizer,Monodata):
    while True:
        data = bytes(Monodata[:4000])
        if len(data) == 0: break
        rec.AcceptWaveform(data)
        del Monodata[:4000]
    return rec.FinalResult()
