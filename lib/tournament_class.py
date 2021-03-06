import os
from lib.meme_class import meme
from random import shuffle
import json
import requests
import discord
import numpy as np
    
def manche(tot: int) -> int:
    """Counts how many memes will be in a manche, given 'tot' meme remaining"""

    x = 2
    while (x<tot):
        x  *= 2
    return tot - (x-tot)

class Tournament:
    """Meme tournament: Creates 2v2 rounds until there is only one meme remaining!"""
    REACTIONS = ["⬆️","⬇️"]    
    
    def __init__(self,auto: bool, chatmemes: str = "", channel = None, path = ""  ):
        """Resume or starts anew the tournament (depends if the file 'state' exists or not)"""

        self.save_file = path+"data/tournament.json"
        self.path = path
        
        if auto:
            # Initialization has been called because tournament.json file exists
            with open(self.save_file) as file:
                jstring = file.readline()
            self.state = json.loads(jstring)

            #TODO fetch channel/ messages
            self.channel = None
            self.msg = None
            
            # Loads memes
            with open(self.state["chatmemes"], "r") as file:
                memedb = file.readlines()
            self.memedb = [meme(x) for x in memedb]


            print("Resuming tournament...")

        else:
            # It's a brand new tournament
            if chatmemes == "" or channel is None:
                '''If new tournament this parameters needs to be passed!'''
                raise Exception 

            # Loads memes
            with open(path+"data/"+chatmemes+".csv", "r") as file:
                memedb = file.readlines()
            self.memedb = [meme(x) for x in memedb]

            # state variables
            self.state = dict()
            self.state["channel_id"] = channel.id
            self.channel = channel
            self.state["chatmemes"] = path+"data/"+chatmemes+".csv"
            self.state["round"] = 0
            self.state["manche_memes"] = manche(len(self.memedb))
            self.state["msg_id"] = 0
            self.msg = None
            
            # Save memes shuffled
            shuffle(self.memedb)
            with open(self.state["chatmemes"], "w") as file:
                for m in self.memedb:
                    file.write(m.serialize())
            
            #Save tournament.json
            jstring = json.dumps(self.state)
            with open(self.save_file, "w") as file:
                file.write(jstring)


            print("Tournament started...")
  
    
    async def fetch(self, guild = None):
        """This needs to be called after initialization to fetch the last message sent"""

        if guild is not None and self.state["msg_id"] == 0:
            self.channel = guild.get_channel(self.state["channel_id"])
            await self.send_meme(self.memedb[0], self.memedb[1])
            
        elif guild is not None and self.state["msg_id"] != 0:
            #fetch channel and message
            channels = await guild.fetch_channels()
            for c in channels:
                if c.id == self.state["channel_id"]:
                    self.channel = c
                    break
            self.msg = await self.channel.fetch_message(self.state["msg_id"])
        else:
            self.msg = await self.channel.fetch_message(self.state["msg_id"])        
        

    async def send_meme(self, a: meme = None, b: meme = None, ) -> None:
        """Sends 2 memes with two reactions for the voting systems, it stores the message in self.state["msg"]"""
        
        img_a = requests.get(a.link[:-1]).content
        img_b = requests.get(b.link[:-1]).content
        
        name_a = a.link[:-1].split("/")[-1]
        name_b = b.link[:-1].split("/")[-1]

        with open(self.path+"data/"+name_a,"wb") as file:
            file.write(img_a)
        
        with open(self.path+"data/"+name_b,"wb") as file:
            file.write(img_b)

        
        img_a = discord.File(self.path+"data/"+name_a)
        img_b = discord.File(self.path+"data/"+name_b)

        self.msg = await self.channel.send("Round {0}/{1}".format(self.state["round"]+1, self.state["manche_memes"]//2), files = [img_a, img_b])
        self.state["msg_id"] = self.msg.id
        await self.msg.add_reaction(self.REACTIONS[0])
        await self.msg.add_reaction(self.REACTIONS[1])

        os.remove(self.path+"data/"+name_a)
        os.remove(self.path+"data/"+name_b)
        
        self.save_state()


    def save_state(self, db=False) -> None:
        """Call this to save the state of the tournamente into a file"""
        jstring = json.dumps(self.state)
        with open(self.save_file, "w") as file:
            file.write(jstring)
        
        if db:
            with open(self.state["chatmemes"], "w") as file:
                for x in self.memedb:
                    file.write(x.serialize())


    async def check(self, payload) -> None:
        """Check reactions"""
        bot_id =831494318333755442
        voters = dict()

        msg = payload.message_id
        await self.fetch()

        if msg != self.msg.id:
            return None

        count = [0,0] # vote for each reaction
        votes = 0 # Counts total votes
        voters = dict() # Used to check double votes
        i = -1
        for r in self.msg.reactions:
            if str(r.emoji) not in self.REACTIONS:
                return
            i+=1
            count[i] = r.count
            votes += count[i]
            
            # ---- double votes check
            if i==0:
                    async for u in r.users():
                        voters[u.id] = 1
            elif i==1:
                    async for u in r.users():
                        if u.id in voters and u.id != bot_id: 
                            print("Double Vote Detected")
                            await self.channel.send("<@{0}>Se non rimuovi il doppio voto non si continua".format(u.id))
                            return
            
                  
        if votes > 5:
            
            if count[0] == count[1]:
                winner = np.random.binomial(size=1,n=1,p=0.5)[0]
                await self.msg.channel.send("Facciamo che scelgo io...")
            else:
                winner = 0 if count[0]>count[1] else 1

            await self.next(winner)
        
    
    async def next(self, winner: int) -> None:
        """Called for next round, if manche is concluded calls 'next_manche()'"""
        end = False
        loser = (winner + 1)%2
        self.memedb.pop(self.state["round"] + loser)
        self.state["round"] += 1
        if self.state["manche_memes"] - self.state["round"] == self.state["round"]:
            end = await self.next_manche()
        else: 
            await self.send_meme(self.memedb[self.state["round"]], self.memedb[self.state["round"] + 1])
        
        if not end:self.save_state(True)


    async def next_manche(self):       
        """Resets round and creates new manche"""

        manche_str = '▀▄▀▄▀▄     𝒩𝑒𝓍𝓉 𝑀𝒶𝓃𝒸𝒽𝑒     ▄▀▄▀▄▀'

        self.state["round"] = 0
        l = len(self.memedb)
        self.state["manche_memes"] = manche(l)

        if self.state["manche_memes"] == 0:
            """WINNER"""
            await self.msg.channel.send("Congratulation <@{}> your meme was the best".format(str(self.memedb[0].author)))
            await self.msg.channel.send(self.memedb[0].link)
            os.remove(self.save_file)
            os.remove(self.state["chatmemes"])
            return True
        shuffle(self.memedb)
        await self.channel.send(manche_str)
        await self.send_meme(self.memedb[self.state["round"]], self.memedb[self.state["round"]+1])
        
        return False
