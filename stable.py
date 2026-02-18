import os
import disnake
import subprocess
from disnake.ext import commands
from admins import check_perm
from dotenv import load_dotenv

load_dotenv()
token = os.getenv("DISCORD_TOKEN1")

intents = disnake.Intents.default()
intents.message_content = True
bot = commands.Bot(
    command_prefix=">_ ", intents=intents, test_guilds=[1419312302821212191, 1387893813992886443]
)

@bot.slash_command(description="get the latency of the bot")
@commands.contexts(bot_dm=True, guild=True)
async def ping(ctx):
    latency = bot.latency * 1000
    await ctx.send(f"Pong! Latency: {latency:.2f}ms")

@bot.slash_command()
@commands.contexts(bot_dm=True, guild=True)
async def update(ctx):
    if check_perm(ctx.author.id):
        await ctx.send("Updating bot...")
        subprocess.run(
            "git -C /root/bot/ fetch && git -C /root/bot/ pull && systemctl restart bot.service",
            shell=True,
        )
        return

    await ctx.send("You don't have permission to update the bot.")
    return


@bot.slash_command()
@commands.contexts(bot_dm=True, guild=True)
async def restart(ctx):
    if check_perm(ctx.author.id):
        await ctx.send("Restarting bot...")
        subprocess.run(
            "systemctl restart bot.service",
            shell=True,
        )
        return

    await ctx.send("You don't have permission to restart the bot.")
    return


@bot.slash_command()
@commands.contexts(bot_dm=True, guild=True)
async def checkperm(ctx, id:str):
    if check_perm(int(id)):
        await ctx.send(f"{id} is authorized to use this bot")
    else:
        await ctx.send(f"Nope! {id} is not able to use this bot")


bot.run(token)
