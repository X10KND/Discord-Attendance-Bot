import os
import time
from pymongo import MongoClient
import discord
from discord.ext import commands
from discord.utils import get

PREFIX = "!"

intents = discord.Intents.all()
bot = commands.Bot(command_prefix = PREFIX, intents=intents)

client = None
db = None

day_dict = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

@bot.event
async def on_ready():

    #await bot.change_presence(status=discord.Status.offline)

    global client, db
    client = MongoClient("REDACTED")
    db = client["Attendance"]

    print("EEE bot is ready at", time.ctime())

@bot.command()
async def ping(ctx):
    await ctx.send(f"{round(bot.latency*1000)} ms")

@bot.event
async def on_voice_state_update(member, before, after):

    if before.channel != None:
        guild = before.channel.guild.name
        category = bot.get_channel(before.channel.category_id).name
        channel = "None"

    if after.channel != None:
        guild = after.channel.guild.name
        category = bot.get_channel(after.channel.category_id).name
        channel = after.channel.name
        
    epoch = round(time.time()) + (6 * 3600)
    t = time.gmtime(epoch)
    dmy = time.strftime("%d %b %Y", t)
    
    collection = db[dmy]
    
    nick = member.display_name

    try:
        student_id = nick.split("_")[0]
        student_name = nick[9:].replace("_", " ")
    except:
        student_id = "None"
        student_name = nick


    item = {
            "discord_name" : member.name,
            "discriminator" : member.discriminator,
            "discord_id" : member.id,
            "nickname" : nick,

            "student_id" : student_id,
            "student_name" : student_name,

            "server" : guild,
            "category" : category,
            "channel" : channel,

            "mobile_status" : str(member.mobile_status),
            "desktop_status" : str(member.desktop_status),
            "web_status" : str(member.web_status),

            "epoch" : epoch,

            "year" : t.tm_year,
            "month" : t.tm_mon,
            "date" : t.tm_mday,

            "hour" : t.tm_hour,
            "minute" : t.tm_min,
            "sec" : t.tm_sec,

            "day" : day_dict[t.tm_wday]
        }
    
    collection.insert_one(item)

@bot.event
async def on_member_update(before, after):

    if before.status != after.status:
        embed = discord.Embed(title=f"Alert!")
        embed.add_field(name='User', value=before.mention)
        embed.add_field(name='Before', value=before.status)
        embed.add_field(name='After', value=after.status)
        channel = bot.get_channel("REDACTED")
        await channel.send(embed=embed)


bot.run("REDACTED")