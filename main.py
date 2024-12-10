'''Entry Point for Jump Bot'''

import discord
from discord.ext import commands

import db
import env

from utils import load_embed_from_file
import utils
from views import schedule_view, join_view, controls_view
from config_commands import config_commands

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='/', intents=intents)

TOKEN = env.os.getenv("DISCORD_TOKEN")

####### Setup functions ##########

async def create_jump_seller_role(guild: discord.Guild):
    '''Creates the jump seller role'''
    for role in guild.roles:
        if role.name == "Jump Seller":
            return role

    return await guild.create_role(name="Jump Seller", mentionable=True, reason="Required role for the jump bot to function.")

async def create_jump_category(guild: discord.Guild):
    '''Creates the jump category'''
    for category in guild.categories:
        if category.name == "Jumps":
            return category

    return await guild.create_category("Jumps")

async def create_jump_seller_hub(guild, category, jump_seller_role):
    '''Creates the jump seller hub channel'''
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False, send_messages=False),
        jump_seller_role: discord.PermissionOverwrite(read_messages=True, send_messages=False),
        guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True),
    }

    for channel in guild.channels:
        if channel.name == "jump-seller-hub":
            return channel

    return await guild.create_text_channel("jump-seller-hub", category=category, overwrites=overwrites)

async def create_jump_schedule_channel(guild, category):
    '''Creates the jump schedule channel'''
    for channel in guild.channels:
        if channel.name == "jump-schedule":
            return channel

    return await guild.create_text_channel("jump-schedule", category=category)

##################################

@bot.event
async def on_connect():
    '''Prints a message to the console when the bot connects'''
    await db.connect_databases()
    await db.create_tables()

@bot.event
async def on_disconnect():
    '''Prints a message to the console when the bot disconnects'''
    await db.disconnect_databases()

@bot.event
async def on_guild_join(guild):
    '''Handles guild joins'''
    jump_seller_role = await create_jump_seller_role(guild)
    category = await create_jump_category(guild)
    jump_seller_hub = await create_jump_seller_hub(guild, category, jump_seller_role)
    jump_schedule = await create_jump_schedule_channel(guild, category)

    await schedule_view.send_schedule_view(guild, jump_seller_hub)

@bot.event
async def on_ready():
    '''Prints a message to the console when the bot is ready'''
    await bot.sync_commands(force=True)
    bot.add_view(schedule_view.ScheduleButtonView())
    bot.add_view(join_view.JoinJumpButtonView())
    bot.add_view(controls_view.JumpControlsButtonView())

    for guild in bot.guilds:
        jump_seller_role = await create_jump_seller_role(guild)
        category = await create_jump_category(guild)
        jump_seller_hub = await create_jump_seller_hub(guild, category, jump_seller_role)
        jump_schedule = await create_jump_schedule_channel(guild, category)

        await schedule_view.send_schedule_view(guild, jump_seller_hub)

        async for message in jump_schedule.history():
            if not message.embeds:
                continue

            embed = message.embeds[0]
            if embed.title.find("Jump") == -1:
                continue

            view = join_view.JoinJumpButtonView()
            view.jump_message_id = message.id
            await message.edit(view=view)

    print("Bot ready.")

@bot.event
async def on_message_delete(message: discord.Message):
    '''Handle message deletions'''
    if not message.embeds:
        print("No embeds.")
        return

    embed = await load_embed_from_file("schedule", {
        "guild_name": message.guild.name,
        "guild_image": message.guild.icon.url,
    })

    if message.embeds[0].title == embed.title:
        await message.channel.send(embed=embed, view=schedule_view.ScheduleButtonView())
        return

    embed = message.embeds[0]
    if embed.title.find("Jump") == -1:
        return
    
    await utils.delete_jump(message.guild, int(embed.title.split("#")[1]))

bot.add_application_command(config_commands)
bot.run(TOKEN)
