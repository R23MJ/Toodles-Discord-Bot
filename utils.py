'''Utility functions'''

import json
import re
import time
import discord

import db

def get_torn_id(display_name : str):
    '''Utility function to extract Torn ID from display name'''
    match = re.search(r"\[(\d+)\]", display_name)
    if not match:
        return None

    return match.group(1)


async def load_embed_from_file(json_file : str, replacements : dict = None):
    '''Utility function to create an embed from a JSON file'''
    with open("embeds/" + json_file + ".json", "r", encoding="utf-8") as file:
            data = json.load(file)

    if replacements:
        for key, value in replacements.items():
            for field in data:
                if isinstance(data[field], str):
                    data[field] = data[field].replace("{" + key + "}", value)
                elif isinstance(data[field], dict):
                    for subfield in data[field]:
                        if isinstance(data[field][subfield], str):
                            data[field][subfield] = data[field][subfield].replace("{" + key + "}", value)

    return discord.Embed.from_dict(data)

async def save_embed_to_file(embed : dict, json_file : str):
    '''Utility function to save an embed to a JSON file'''
    with open("embeds/" + json_file + ".json", "w", encoding="utf-8") as file:
        json.dump(embed, file, indent=4)

async def get_jump_schedule_channel(guild : discord.Guild):
    '''Utility function to get the jump schedule channel'''
    return discord.utils.get(guild.channels, name="jump-schedule")

async def get_jump_seller_hub(guild : discord.Guild):
    '''Utility function to get the jump seller hub'''
    return discord.utils.get(guild.channels, name="jump-seller-hub")

async def delete_jump(guild, jump_id : int):
    '''Utility function to delete a jump'''
    jump = await db.get_jump(jump_id)
    if not jump:
        return {"error": "Jump not found."}

    join_message_id = jump["message_id"]
    schedule_channel = await get_jump_schedule_channel(guild)

    try:
        join_message = await schedule_channel.fetch_message(join_message_id)
    except discord.errors.NotFound:
        join_message = None

    if join_message:
        await join_message.delete()

    await db.delete_jump(jump_id)

    try:
        role = discord.utils.get(guild.roles, name=f"Jump #{jump_id}")
    except discord.errors.NotFound:
        role = None

    if role:
        await role.delete()

    try:
        channel = discord.utils.get(guild.channels, name=f"jump-{jump_id}")
    except discord.errors.NotFound:
        channel = None

    if channel:
        await channel.delete()

async def convert_to_timestamp(date_time : str):
    '''Converts a date time string to a timestamp'''
    try:
        return int(time.mktime(time.strptime(date_time, "%A, %B %d, %Y %I:%M %p")))
    except ValueError:
        return None
