from logging import error
from discord import message, GroupChannel
import re
from discord import channel
from discord.channel import TextChannel

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
    for m in message.guild.channels:
        if m.id == int(target[0]):
            channel = m
            break
        
    print("Starting meme download")
    i =0
    with open(channel.name+".csv", "w") as file:
        file.write("message_id"+","+"author_id"+","+"attachment_url"+"\n")
        async for msg in message.channel.history(limit=10000):
            if len(msg.attachments) > 0:
                file.write(str(i)+","+str(msg.author.id)+","+msg.attachments[0].url+"\n")
                i+=1
    print(i," memes downloaded")
    