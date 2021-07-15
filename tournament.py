import os.path
from discord import message

class tournament:
    """Meme tournament: Creates 2v2 rounds until there is only one meme remaining!"""
       
    @staticmethod
    def manche(tot: int) -> int:
        x = 2
        while (x<tot):
            x  *= 2
        return tot - (x-tot)
    
    def __init__(self, chatmemes: str ) -> None:
        """Reads variables form file, if not presents generates it"""
        self.STATE = ".state"
        
        if not os.path.isfile(chatmemes+".csv"):
            # No database
            print("Download memes first! <{0}>".format(chatmemes))
            raise FileNotFoundError

        
        with open(chatmemes+".csv", "r") as file:
            # Loads memes
            memedb = file.readlines()
        self.memdb = [meme(x) for x in memedb] 


        if os.path.isfile(self.STATE):

            with open(self.STATE, "r") as file:
                #TODO reads state

                print("Resuming tournament...")
        else:
            #TODO create file
            self.round = 0
            self.manche_meme = manche(len(memedb))
            self.msg = None
            print("Tournament started...")
        


    




class meme:
    """Typeof meme"""
    def __init__(self, serialized: str) -> None:
        params = serialized.split(",")
        self.id = int(params[0])
        self.author = int(params[1])
        self.link = params[2]
    
    def serialize(self) -> str:
        return str(self.id) + ',' + str(self.author) +',' + self.link
    