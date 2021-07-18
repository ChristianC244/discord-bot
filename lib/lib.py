from discord import message
import re
import os 

from discord.errors import InvalidArgument

async def download(message: message):
    """"Download entire text-channel memes, passed through message, and stores in ./<channel-name>.csv"""
    
    content = message.content
    matcher = re.compile("<#(\d*)>")
    target = matcher.findall(content)
    if len(target) != 1:
        # Invalid argument
        raise InvalidArgument 

    channel = None
    for c in message.guild.channels:
        if c.id == int(target[0]):
            channel = c
            break
        
    print("Starting meme download")
    i =0

    with open('data/'+channel.name+'.csv', "w") as file:
        
        async for msg in channel.history(limit=10000):
            if len(msg.attachments) > 0:
                file.write(str(i)+","+str(msg.author.id)+","+msg.attachments[0].url+"\n")
                i+=1
    print(i," memes downloaded")
    return channel.name
    