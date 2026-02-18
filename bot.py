import disnake
from disnake import Permissions
from disnake.activity import create_activity
from disnake.ext import commands
from dotenv import load_dotenv
import datetime
import os
import random
import subprocess
from admins import check_perm
import whois as wi
from gtts import gTTS

load_dotenv()
token = os.getenv("DISCORD_TOKEN")

intents = disnake.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(
    command_prefix=">_ ",
    intents=intents,
    test_guilds=[1419312302821212191, 1217099931420983327, 1420452193416511498, 1473697372834893975],
)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    activity = disnake.Game(random.choice(["SuperTuxCart", "SuperTux"]))
    await bot.change_presence(activity=activity)
    channel = bot.get_channel(1419407048294138027)
    if channel:
        await channel.send("started")


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if "shit" in message.content.lower():
        await message.delete()
        await message.channel.send(f"{message.author.mention} - don't use that word!")
    if "sybau" in message.content.lower():
        await message.delete()
        await message.channel.send(f"{message.author.mention} - dont say that or ban -god")

    await bot.process_commands(message)


@bot.slash_command(description="Server lockdown")
@commands.default_member_permissions(administrator=True)
async def lockdown(inter):
    await inter.guild.default_role.edit(
        permissions=Permissions(
            send_messages=False, create_instant_invite=False, view_channel=False
        )
    )
    await inter.response.send_message("Lockdown activated.", ephemeral=True)


@bot.slash_command(description="Server unlock")
@commands.default_member_permissions(administrator=True)
async def unlock(inter):
    await inter.guild.default_role.edit(
        permissions=Permissions(
            send_messages=True,
            send_messages_in_threads=True,
            create_public_threads=True,
            create_private_threads=True,
            add_reactions=True,
            attach_files=True,
            connect=True,
            speak=True,
            stream=True,
        )
    )
    await inter.response.send_message("Server unlocked.", ephemeral=True)


@bot.slash_command(description="says the line in specified vc")
@commands.default_member_permissions(manage_guild=True, moderate_members=True)
async def say(inter, text: str, channel: str):
    await connect(timeout=10, reconnect=True)
    await change_voice_state(channel, self_mute=False, self_deaf=False)  # type: ignore


@bot.slash_command(description="Tells you your ipv4 address")
async def ip(inter):
    await inter.response.send_message(
        f"**One** of your **ipv4** address is likely 127.0.0.1."
    )


@bot.slash_command(description="Find subdomains of a domain.")
@commands.default_member_permissions(manage_guild=True, moderate_members=True)
async def subdomain(inter, domain: str):
    await inter.response.defer()

    subdomains = subprocess.run(
        ["subfinder", "-d", domain, "-silent", "-sources", "crtsh,anubis,threatcrowd"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=True,
    ).stdout.strip()

    embed = disnake.Embed(
        title=f"Subdomains on {domain}",
        timestamp=datetime.datetime.now(),
        color=random.randint(0, 0xFFFFFF),
        description=f"```{subdomains}```",
    )
    embed.set_author(name="Utilities")
    embed.set_footer(text=domain)
    await inter.followup.send(embed=embed)


@bot.slash_command(description="Multiplies the number by specified number")
async def multiply(inter, factor: float, factor2: float):
    await inter.response.send_message(factor * factor2)

class MyModal(disnake.ui.Modal):
    def __init__(self):
        # The details of the modal, and its components
        components = [
            disnake.ui.TextInput(
                label="Fullt namn",
                placeholder="Ex: Hubert Rutsson",
                custom_id="name",
                style=disnake.TextInputStyle.short,
                max_length=50,
            ),
            disnake.ui.TextInput(
                label="Klass",
                placeholder="Ex: 24NV",
                custom_id="class",
                max_length=5,
                style=disnake.TextInputStyle.short,
            ),
            disnake.ui.TextInput(
                label="Preferenser för platser",
                placeholder="Ex: inga",
                required=False,
                custom_id="preferences",
                style=disnake.TextInputStyle.paragraph,
                max_length=128,
            ),
        ]
        super().__init__(title="Anmälan", components=components)

    # The callback received when the user input is completed.
    async def callback(self, inter: disnake.ModalInteraction):
        embed = disnake.Embed(title="FriskoLAN Anmälan", description="Anmälan registrerad!")
        for key, value in inter.text_values.items():
            embed.add_field(
                name=key.capitalize(),
                value=value[:1024],
                inline=False,
            )
        await inter.response.send_message(embed=embed, ephemeral=True)


@bot.slash_command(name="anmälan", description="Anmäl dig till LAN!")
async def anmalan(inter: disnake.AppCmdInter):
    await inter.response.send_modal(modal=MyModal())

@bot.slash_command(description="get the latency of the bot")
async def ping(ctx):
    latency = bot.latency * 1000
    await ctx.send(f"Pong! Latency: {latency:.2f}ms")


@bot.slash_command(description="a test for embeds")
@commands.default_member_permissions(manage_guild=True, moderate_members=True)
async def embedtest(ctx):
    embed = disnake.Embed(
        title="Choose your roles",
        description="React with the roles you want",
        color=disnake.Colour.yellow(),
        timestamp=datetime.datetime.now(),
    )
    await ctx.send(embed=embed)


@bot.slash_command()
@commands.default_member_permissions(manage_guild=True, moderate_members=True)
async def purge(ctx, amount: int):
    """Purges a specific number of messages in the channel."""
    if ctx.author.guild_permissions.manage_messages:
        deleted = await ctx.channel.purge(limit=amount)
        await ctx.send(f"Deleted {len(deleted)} message(s)")
    else:
        await ctx.send("You do not have permission to purge messages.")


@bot.slash_command()
@commands.default_member_permissions(manage_guild=True, moderate_members=True)
async def repeat(ctx, message: str):
    if check_perm(ctx.author.id):
        id = ctx.channel.id
        channel = bot.get_channel(id)
        if channel:
            await channel.send(message)
        await ctx.response.delete()
    return


# The slash command that responds with a message.
@bot.slash_command()
async def buttons(inter: disnake.ApplicationCommandInteraction):
    await inter.response.send_message(
        "Need help?",
        components=[
            disnake.ui.Button(
                label="Yes", style=disnake.ButtonStyle.success, custom_id="yes"
            ),
            disnake.ui.Button(
                label="No", style=disnake.ButtonStyle.danger, custom_id="no"
            ),
        ],
    )


@bot.listen("on_button_click")
async def help_listener(inter: disnake.MessageInteraction):
    if inter.component.custom_id not in ["yes", "no"]:
        # We filter out any other button presses except
        # the components we wish to process.
        return

    if inter.component.custom_id == "yes":
        await inter.response.send_message("Contact us at https://discord.gg/disnake!")
    elif inter.component.custom_id == "no":
        await inter.response.send_message("Got it. Signing off!")


@bot.command()
async def ping(ctx):
    latency = bot.latency * 1000
    await ctx.send(f"Pong! Latency: {latency:.2f}ms")


@bot.command()
async def webserver(ctx):
    if check_perm(ctx.author.id):
        await ctx.send("(RE)Starting webserver...")
        subprocess.run(["sh", "/var/www/update.sh"])


@bot.slash_command()
@commands.default_member_permissions(manage_guild=True, moderate_members=True)
async def whois(ctx, domain: str):
    w = wi.whois(domain)
    embed = disnake.Embed(
        title=f"Whois lookup on {domain}",
        timestamp=datetime.datetime.now(),
        color=random.randint(0, 0xFFFFFF),
        description=f"```{w}```",
    )
    embed.set_author(name="Utilities")
    embed.set_footer(text=domain)

    # embed.add_field(name="Whois lookup:", value=f"```{w}```", inline=True)
    await ctx.send(embed=embed)


async def reaction_role(payload):
    if payload.message_id == 1419337604775542877:
        guild = bot.get_guild(payload.guild_id)
        member = await guild.fetch_member(payload.user_id)

        if str(payload.emoji) == "👓":
            role = guild.get_role(1419313128750973110)  # Nerd!
        if str(payload.emoji) == "<:tux:1419329223302057984>":
            role = guild.get_role(1419316786918068346)
        if str(payload.emoji) == "<:tuxmono:1419329003361407037>":
            role = guild.get_role(1419315782986502244)
    return member, role


@bot.event
async def on_raw_reaction_add(payload):
    member, role = await reaction_role(payload)
    try:
        await member.add_roles(role)
    except Exception as e:
        print("An unexpected error has occured: " + e)


@bot.event
async def on_raw_reaction_remove(payload):
    member, role = await reaction_role(payload)
    try:
        await member.remove_roles(role)
    except Exception as e:
        print("An unexpected error has occured: " + e)


bot.run(token)
