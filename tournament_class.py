import os.path
from meme import meme
from random import shuffle

    
def manche(tot: int) -> int:
        x = 2
        while (x<tot):
            x  *= 2
        return tot - (x-tot)

class Tournament:
    """Meme tournament: Creates 2v2 rounds until there is only one meme remaining!"""
    REACTIONS = ["⬆️","⬇️"]    
    
    def __init__(self, chatmemes: str, channel ):
        """Resume or starts anew the tournament (depends if the file 'state' exists or not)"""
        self.STATE = "state"
        self.channel = channel
        self.chatmemes = chatmemes+".csv"
        
        if not os.path.isfile(self.chatmemes):
            # No database
            print("Download memes first! <#{0}>".format(chatmemes))
            raise FileNotFoundError

        
        with open(self.chatmemes, "r") as file:
            # Loads memes
            memedb = file.readlines()
            #memedb.pop(0)
        self.memedb = [meme(x) for x in memedb] 


        if os.path.isfile(self.STATE):

            with open(self.STATE, "r") as file:
                self.round = int(file.readline().split("=")[1])
                self.manche_memes = int(file.readline().split("=")[1])
                self.msg = int(file.readline().split("=")[1][:-1]) # This needs 'fetch()' to be called after initialization to fetch message
                

                print("Resuming tournament...")
        else:
            self.round = 0
            self.manche_memes = manche(len(self.memedb))
            self.msg = None
            shuffle(self.memedb)

            with open(self.chatmemes, "w") as file:
                for m in self.memedb:
                    file.write(m.serialize())

            with open(self.STATE, "w") as file:
                file.write("round="+str(self.round)+"\n")
                file.write("manche_memes="+str(self.manche_memes)+"\n")
                file.write("msg=0\n")

            print("Tournament started...")

    
    async def fetch(self):
        """This needs to be called after initialization to fetch the last message sent"""
        if isinstance(self.msg, int):
            self.msg = await self.channel.fetch_message(self.msg)
        elif self.msg is None: await self.send_meme(self.memedb[0], self.memedb[1])
        else: self.msg = await self.channel.fetch_message(self.msg.id)
    
    def status(self) -> None:
        """Print the status of the tournament"""
        print("\nRound: {0}\nMemes in this Manche: {1}\nLast message id: {2}\nTotal memes remaining: {3}\n".format(self.round, self.manche_memes, self.msg, len(self.memedb)))

    
    
    async def send_meme(self, a: meme = None, b: meme = None) -> None:
        """Sends 2 memes with two reactions for the voting systems, it stores the message in self.msg"""
        self.msg = await self.channel.send(a.link + " " + b.link)
        await self.msg.add_reaction(self.REACTIONS[0])
        await self.msg.add_reaction(self.REACTIONS[1])
        
        self.save_state()


    def save_state(self, db=False) -> None:
        """Call this to save the state of the tournamente into a file"""
        with open(self.STATE, "w") as file:
                file.write("round="+str(self.round)+"\n")
                file.write("manche_memes="+str(self.manche_memes)+"\n")
                file.write("msg="+str(self.msg.id)+"\n")
        
        if db:
            with open(self.chatmemes, "w") as file:
                for x in self.memedb:
                    file.write(x.serialize())


    async def check(self, payload) -> None:
        """Check reactions"""
        # Needs to check if user voted twice !!!
        msg = payload.message_id
        react = str(payload.emoji)
        await self.fetch()

        if msg != self.msg.id:
            return None
        
        count = 0
        max = 0
        winner = -1
        for r,i in zip(self.msg.reactions, range(2)):
            if str(r.emoji) in self.REACTIONS:
                count += r.count
                if r.count > max:
                    max = r.count
                    winner = i
                  
        if count > 4: 
            await self.next(winner)
        
    
    async def next(self, winner: int) -> None:
        loser = (winner + 1)%2
        self.memedb.pop(self.round + loser)
        self.round += 1
        if self.manche_memes - self.round == self.round:
            #TODO
            await self.next_manche()
        else: 
            await self.send_meme(self.memedb[self.round], self.memedb[self.round + 1])
        self.save_state(True)
        

        
    async def next_manche(self) -> None:
        """Resets round and creates new manche"""
        self.round = 0
        l = len(self.memedb)
        self.manche_memes = manche(l)

        if self.manche_memes == 0:
            """WINNER"""
            await self.msg.channel.send("Congratulation <@{}> your meme was the best".format(str(self.memedb[0].author)))
            return None
        shuffle(self.memedb)
        await self.send_meme(self.memedb[self.round], self.memedb[self.round+1])




