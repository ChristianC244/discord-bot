async def download(message: message):
    """Download entire text-channel memes and stores in ./<channel-name>.csv"""
    print("Starting download memes")
    await message.channel.send("Scarico memes...")
    i =0
    with open(message.channel.name+".csv", "w") as file:
        file.write("message_id"+","+"author_id"+","+"attachment_url"+"\n")
        async for msg in message.channel.history(limit=10000):
            if len(msg.attachments) > 0:
                file.write(str(i)+","+str(msg.author.id)+","+msg.attachments[0].url+"\n")
                i+=1
    print(i," memes downloaded")
    file.close()