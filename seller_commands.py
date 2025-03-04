'''Commands for jump sellers.'''

import discord

from discord.commands import SlashCommandGroup
from decorators import permissions
import utils
import db
from views import controls_view, rc_view, done_view

seller_commands = SlashCommandGroup(name="jump", description="Base command for all jump commands.")

@seller_commands.command(name="send_controls", description="Send jump controls.")
@permissions(required_roles=["Jump Seller"])
async def send_controls_command(ctx: discord.ApplicationContext):
    '''Send jump controls.'''
    await ctx.defer()
    jump_id = int(ctx.channel.name.split("-")[1])

    jump = await db.get_jump(jump_id)
    jump_time = jump["jump_time"]

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

@seller_commands.command(name="rc", description="Start roll call.")
@permissions(required_roles=["Jump Seller"])
async def rc_command(ctx: discord.ApplicationContext):
    '''Start roll call.'''
    await ctx.defer(ephemeral=True)

    await rc_view.send_rc_view(ctx.guild, ctx.channel)

    await ctx.followup.send("Roll call started.", ephemeral=True)

@seller_commands.command(name="go", description="Start going message.")
@permissions(required_roles=["Jump Seller"])
async def rc_command(ctx: discord.ApplicationContext):
    '''Start going message.'''
    await ctx.defer(ephemeral=True)

    await done_view.send_done_view(ctx.guild, ctx.channel)

    await ctx.followup.send("Jump started.", ephemeral=True)

