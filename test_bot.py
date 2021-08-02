from lib import lib, tournament_class

import discord
import os
import json
from dotenv import load_dotenv
load_dotenv()

client = discord.Client()
prefix = "!"
myid = int(os.getenv("MY_ID"))
tour = None
guild = None
path = os.path.dirname(__file__)+"/"

state = dict()


cmds = {
    prefix+"hello":"Respond to the greeting.",
    prefix+"download":"Requires a chat tagged as a parameter, and downloads every image from that chat (ownler only)",
    prefix+"help":"I guess you somehow figured out.",
    prefix+"wumpus":"Chi è il wumpus?",
    prefix+"tournament":"Requires a chat tagged as a parameter, and starts the tournament with memes from that chat (owner only)",
    prefix+"lacomizer":"enable/disable lacomizer"
}
# ------------ FUNCTIONS

async def check_tournament_online():
    if os.path.isfile(path+"data/tournament.json"):
        global tour
        tour = tournament_class.Tournament(auto = True, path=path)
        await tour.fetch(guild=guild)

async def my_guild():
    async for guild in client.fetch_guilds(limit=150):
        return guild

def resume():
    global state
    if not os.path.isfile(path+"data/state.json"):
        print("Missing state.json file")
        state["lacom"]= True
        return
    with open(path+"data/state.json", "r") as file:
        jstring = file.readline()
    state = json.loads(jstring)

def save_state():
    jstring = json.dumps(state)
    with open(path+"data/state.json", "w") as file:
        file.write(jstring)

# ------------ CLIENT

@client.event
async def on_ready():
    global guild
    guild = await my_guild()
    resume()
    await check_tournament_online()
    print("Bot is now ready")

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    # Hello command
    if message.content.startswith(prefix+"hello"):
        await message.channel.send("Hey!")
    
    # Wumpus command
    elif message.content.startswith(prefix+"wumpus"):
        await message.channel.send("Nel gioco del wumpus, il wumpus è una bestia che emana un odore acre :nauseated_face:")

    # Help command
    elif message.content.startswith(prefix+"help"):
        msg = "Here's the list of commands available to the bot\n"
        for c in cmds:
            msg+="> **"+c+"** --> "+cmds[c]+"\n"
        await message.channel.send(msg)
    
    # Download meme database
    elif message.content.startswith(prefix+"download") and message.author.id == myid:
        try:
            await lib.download(message,path=path)
        except lib.InvalidArgument:
            await message.channel.send("Il messaggio deve contenere il canale da cui scaricare i meme: '!download #memes-chat'")
        except:
            await message.channel.send("Qualcosa è andato storto")

    elif message.content.startswith(prefix+"download") and message.author.id != myid:
        await message.channel.send("Chi ti credi di essere?"+message.author.mention)


   # Tournament
    elif message.content.startswith(prefix+"tournament") and message.author.id == myid:
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

    # Lacomizer
    elif message.content.startswith(prefix+"lacomizer"):
        state["lacom"] = not state["lacom"]
        await message.channel.send("Lacomizer: {}".format("enabled" if state["lacom"] else "disabled"))
        save_state()
    elif lib.lacomizer(message.content) and state["lacom"]: await message.add_reaction("🤡")



@client.event
async def on_raw_reaction_add(payload):
    if payload.user_id == client.user.id:
        return 
    if tour is not None:
        # print("+ Reaction Added")
        await tour.check(payload)

client.run(os.getenv("TOKEN"))
