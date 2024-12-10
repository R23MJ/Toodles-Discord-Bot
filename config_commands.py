'''Commands for configuring the bot.'''

import os

import discord

from discord.commands import SlashCommandGroup
from modals import edit_embed_modal
from decorators import permissions

config_commands = SlashCommandGroup(name="config", description="Base command for all jump commands.")
embed_config_commands = config_commands.create_subgroup(name="embeds", description="Base command for all embed commands.")

@embed_config_commands.command(name="edit", description="Edit embed.")
async def embed_config_command(ctx: discord.ApplicationContext, embed_name: str):
    '''Base command for all embed commands.'''
    if os.path.exists(f"embeds/{embed_name}.json"):
        return await ctx.send_modal(edit_embed_modal.BasicEditEmbedModal(embed_name))
    
    await ctx.send_response("Embed not found.", ephemeral=True)

@embed_config_commands.command(name="list", description="List embeds.")
async def embed_list_command(ctx: discord.ApplicationContext):
    '''List embeds.'''
    embeds = os.listdir("embeds")

    for i, embed in enumerate(embeds):
        embeds[i] = embed.replace(".json", "")
        embeds[i] = f"{i + 1}. {embeds[i]}"

    await ctx.send_response("\n".join(embeds), ephemeral=True)
