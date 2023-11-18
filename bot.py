import discord
import os

from discord.ext import commands
from discord.ext.commands import Bot
from dotenv import load_dotenv

from sso import SSO

load_dotenv()

token = os.getenv('TOKEN')

bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())


@bot.event
async def on_ready():
    print('Bot is ready.')
    
@bot.command()
async def panel(ctx):
    guildid = ctx.guild.id
    authorid = ctx.author.id
    token = SSO.genSSOToken(guildid, authorid)
    await ctx.send('SSO URL: http://localhost:8800/sso/login/' + token)
    
@bot.command()
async def check(ctx, ssoToken):
    check = SSO.checkSSOToken(ssoToken)
    if check[0]:
        await ctx.send('Token is valid. Time remaining: ' + str(check[1]) + ' seconds. Guild ID: ' + str(check[2]) + '. Author ID: ' + str(check[3]) + '.')
    else:
        if check[1] == 0:
            await ctx.send('Token is invalid.')
        else:
            await ctx.send('Token is expired. Guild ID: ' + str(check[2]) + '. Author ID: ' + str(check[3]) + '.')

@bot.command()
async def generate(ctx):
    guildid = ctx.guild.id
    authorid = ctx.author.id
    await ctx.send(SSO.genSSOToken(guildid, authorid))
    
@bot.command()
async def initTable(ctx):
    await ctx.send(SSO.initTable())

bot.run(token)