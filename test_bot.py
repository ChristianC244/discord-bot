from lib import *
import discord
from discord import message

import os
from dotenv import load_dotenv
load_dotenv()

client = discord.Client()
prefix = "!"
myid = 83930319891238912

cmds = {
    prefix+"hello":"Respond to the greeting.",
    prefix+"download":"That's a secret!",
    prefix+"help":"I guess you somehow figured out.",
    prefix+"wumpus":"chi è il wumpus?"
}

@client.event
async def on_ready():
    print("Bot is now online")

@client.event
async def on_message(message):
    print(message.id," : ",message.content," : ",message.author)
    if message.author == client.user:
        return
    # Hello command
    if message.content.startswith(prefix+"hello"):
        await message.channel.send("Hey!")
    
    # Wumpus command
    if message.content.startswith(prefix+"wumpus"):
        await message.channel.send("Nel gioco del wumpus, il wumpus è una bestia che emana un odore acre :nauseated_face:")

    # Help command
    if message.content.startswith(prefix+"help"):
        msg = "Here's the list of commands available to the bot\n"
        for c in cmds:
            msg+="> **"+c+"** --> "+cmds[c]+"\n"
        await message.channel.send(msg)
    
    # Download meme database
    if message.content.startswith(prefix+"download") and message.author.id == myid:
        try:
            await download(message)
        except InvalidArgument:
            await message.channel.send("Il messaggio deve contenere il canale da cui scaricare i meme: '!download #memes-chat'")
        except:
            await message.channel.send("Qualcosa è andato storto")

    elif message.content.startswith(prefix+"download") and message.author.id != myid:
        await message.channel.send("Chi ti credi di essere?"+message.author.mention)





   #TODO Start Tournament
    if message.content.startswith(prefix+"tournament") and message.author.id == myid:
        0
    elif message.content.startswith(prefix+"tournament") and message.author.id != myid:
        await message.channel.send("Chi ti credi di essere?"+message.author.mention)
    

    

client.run(os.getenv("TOKEN"))
