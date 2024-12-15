'''Commands for jump sellers.'''

import discord

from discord.commands import SlashCommandGroup
from decorators import permissions
import utils
import db
from views import controls_view

seller_commands = SlashCommandGroup(name="jump", description="Base command for all jump commands.")

@seller_commands.command(name="send_controls", description="Send jump controls.")
@permissions(required_roles=["Jump Seller"])
async def send_controls_command(ctx: discord.ApplicationContext):
    '''Send jump controls.'''
    await ctx.defer();
    jump_id = int(ctx.channel.name.split("-")[1])

    jump_time = (await db.get_jump(jump_id))["jump_time"]

    controls_embed = await utils.load_embed_from_file(
        "jump_controls",
        {
            "jump_id": str(jump_id),
            "jump_time": str(jump_time),
            "host_name": ctx.author.display_name,
            "host_avatar": ctx.author.avatar.url
        }
    )

    await ctx.followup.send(embed=controls_embed, view=controls_view.JumpControlsButtonView())
