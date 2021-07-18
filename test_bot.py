import tournament_class
from lib import lib

import discord
import os
import os.path
from dotenv import load_dotenv
load_dotenv()

client = discord.Client()
prefix = "!"
myid = int(os.getenv("MY_ID"))
tour = None
guild = None
path = os.path.dirname(__file__)+"/"

cmds = {
    prefix+"hello":"Respond to the greeting.",
    prefix+"download":"That's a secret!",
    prefix+"help":"I guess you somehow figured out.",
    prefix+"wumpus":"chi è il wumpus?"
}
# ------------ FUNCTIONS

async def check_tournament_online():
    if os.path.isfile(path+"data/state.json"):
        global tour
        tour = tournament_class.Tournament(auto = True, path=path)
        await tour.fetch(guild=guild)

async def my_guild():
    async for guild in client.fetch_guilds(limit=150):
        return guild


# ------------ CLIENT
@client.event
async def on_ready():
    global guild
    guild = await my_guild()
    print("Bot is now online")
    await check_tournament_online()

@client.event
async def on_message(message):
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
            await lib.download(message,path=path)
        except lib.InvalidArgument:
            await message.channel.send("Il messaggio deve contenere il canale da cui scaricare i meme: '!download #memes-chat'")
        except:
            await message.channel.send("Qualcosa è andato storto")

    elif message.content.startswith(prefix+"download") and message.author.id != myid:
        await message.channel.send("Chi ti credi di essere?"+message.author.mention)


   # Tournament
    if message.content.startswith(prefix+"tournament") and message.author.id == myid:
        global tour
        chat = ""
        try:
            chat = await lib.download(message, path=path)
        except lib.InvalidArgument:
            await message.channel.send("Il messaggio deve contenere il canale da cui scaricare i meme: '!tournament #memes-chat'")
        except:
            await message.channel.send("Qualcosa è andato storto")
        tour = tournament_class.Tournament( False, chat, message.channel, path=path)
        await tour.fetch(guild = message.guild)
        
    elif message.content.startswith(prefix+"tournament") and message.author.id != myid:
        await message.channel.send("Chi ti credi di essere?"+message.author.mention)



@client.event
async def on_raw_reaction_add(payload):
    if payload.user_id == client.user.id:
        return 
    if tour is not None:
        # print("+ Reaction Added")
        await tour.check(payload)

client.run(os.getenv("TOKEN"))
