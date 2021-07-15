import os.path
import discord
from discord import message
from discord import client
import meme

    
def manche(tot: int) -> int:
        x = 2
        while (x<tot):
            x  *= 2
        return tot - (x-tot)

class Tournament:
    """Meme tournament: Creates 2v2 rounds until there is only one meme remaining!"""
           
    
    def __init__(self, chatmemes: str, channel ) -> None:
        """Resume or starts anew the tournament (depends if the file 'state' exists or not)"""
        self.STATE = "state"
        self.channel = channel
        
        if not os.path.isfile(chatmemes+".csv"):
            # No database
            print("Download memes first! <#{0}>".format(chatmemes))
            raise FileNotFoundError

        
        with open(chatmemes+".csv", "r") as file:
            # Loads memes
            memedb = file.readlines()
            memedb.pop(0)
        self.memedb = [meme.meme(x) for x in memedb] 


        if os.path.isfile(self.STATE):

            with open(self.STATE, "r") as file:
                self.round = int(file.readline().split("=")[1])
                self.manche_memes = int(file.readline().split("=")[1])
                self.msg = file.readline().split("=")[1][:-1]
                

                print("Resuming tournament...")
        else:
            self.round = 0
            self.manche_memes = manche(len(self.memedb))
            self.msg = ""

            with open(self.STATE, "w") as file:
                file.write("round="+str(self.round)+"\n")
                file.write("manche_memes="+str(self.manche_memes)+"\n")
                file.write("msg="+self.msg+"\n")

            print("Tournament started...")

    def status(self) -> None:
        print("\nRound: {0}\nMemes in this Manche: {1}\nLast message id: {2}\nTotal memes remaining: {3}\n".format(self.round, self.manche_memes, self.msg, len(self.memedb)))

    
    #TODO TUTTO
    async def send_meme(self, a: meme, b:meme) -> None:
        await self.channel





