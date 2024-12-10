'''This module contains functions for creating and sending jump embeds'''

import discord

from views import join_view

async def send_jump_to_schedule(bot, embed: discord.Embed):
    '''Send a jump to the schedule channel'''
    channel = discord.utils.get(bot.get_all_channels(), name="jump-schedule")
    button_view = join_view.JoinJumpButtonView()

    embed.insert_field_at(0, name="Jumper Order", value="", inline=False)

    message = await channel.send(embed=embed, view=button_view)
    button_view.jump_message_id = message.id
    return message.id
