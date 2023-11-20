import discord
import os

from discord.ext import commands, ipc
from discord.ext.commands import Bot
from dotenv import load_dotenv
import mysql.connector


from sso import SSO

load_dotenv()

token = os.getenv('TOKEN')

connection = mysql.connector.connect(host='', database='', user='', password='')


bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())


async def get_bot():
    return bot


@bot.event
async def on_ready():
    print('Bot is ready.')


@bot.event
async def on_disconnect():
    await connection.close()
    
    
@bot.event
async def on_guild_join(guild):
    guildId = guild.id
    await SSO.initGuildTable(guildId)
    print('Joined guild ' + str(guildId) + '.')

    
@bot.command()
async def panel(ctx):
    guildid = ctx.guild.id
    authorid = ctx.author.id
    token = SSO.genSSOToken(guildid, authorid)
    await ctx.send('SSO URL: http://localhost:8800/sso/login/' + token)
    
@bot.command()
async def check(ctx, ssoToken):
    if ssoToken == 'recent':
        guildid = ctx.guild.id
        authorid = ctx.author.id
        ssoToken = SSO.getRecentToken(guildid, authorid)
        if ssoToken is None:
            await ctx.send('No recent token found. Or, the recent token has expired.')
            return
        else:
            pass
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
    
@bot.command()
async def hello(ctx):
    guildID = ctx.guild.id
    cursor = connection.cursor()
    newHelloMessageQuery = "SELECT helloMessage FROM config WHERE guildid = %s"
    cursor.execute(newHelloMessageQuery, (guildID,))
    newHelloMessage = cursor.fetchall()
    cursor.close()
    await ctx.send(newHelloMessage)
    


if __name__ == '__main__':
    bot.run(token)