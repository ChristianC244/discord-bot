"""
TODO
-Salvare ultimo commit
-Controllare ultimo commit ### git log --abbrev-commit -1 
                           ### git remote -v update 
--Se è diverso -->  Send Message on Discord
"""

class Commit:
    def __init__(self, hash, author, date, comment) -> None:
        self.hash = hash
        self.author = author
        self.date = date
        self.comment = comment
    
    def toJSON(self) -> str:
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True)


# -------------------------------------------------------------------------------------- #

import re
import subprocess
import json
import os
import time

PATH = os.path.dirname(__file__)+"/../"
PATTERN = '''commit (\w*).*
Author: (.*) <.*
Date:\s*(.*) +.*

\s*(.*)
'''
CHANNEL_ID = 899640631515832340


def save_commit(commit: Commit, path=""):
    jstring = commit.toJSON()
    with open(path + "/data/commit.json", "w") as file:
        file.write(jstring)



def is_new_commit(commit: Commit, path="") -> bool:
    """Given a commit, it checks if it's the same as the saved one
        returns True if its the same, else False"""

    if not os.path.isfile(path+"/data/commit.json"):
        return True

    with open(path+"/data/commit.json", "r") as file:
        jstring = file.readline()
    saved_commit = json.loads(jstring)

    if saved_commit["hash"] == commit.hash: return False
    else: return True



def get_last_commit(wd="./") -> Commit:
    CMD_UPDATE = "git fetch"
    CMD_LOG = "git log --abbrev-commit -1"
    subprocess.Popen(CMD_UPDATE.split(),cwd=wd)

    process = subprocess.Popen(CMD_LOG.split(), stdout=subprocess.PIPE, cwd=wd)
    output = process.communicate()
    matched = re.match(PATTERN, output[0].decode())

    hash = matched.group(1)
    author = matched.group(2)
    date = matched.group(3)
    comment = matched.group(4)

    return Commit(hash, author, date, comment)


async def fetch_channel(guild):
    commit_channel= 899640631515832340
    channels = await guild.fetch_channels()
    for c in channels:
        if c.id == commit_channel:
            return c
    return None


async def git_stuff(guild, wd="./") -> str or None:

    channel = await fetch_channel(guild)
    if channel is None: return

    while(True):
        
        cmt = get_last_commit(wd=wd)

        if is_new_commit(cmt,path=PATH):
            save_commit(cmt, path=PATH)
            subprocess.Popen("git pull".split(), cwd=wd)
            await channel.send("New Commit:`{0}` by `{1}`\nin `{2}` -> `{3}`".format(cmt.hash, cmt.author, cmt.date, cmt.comment))
        
        
        time.sleep(10)