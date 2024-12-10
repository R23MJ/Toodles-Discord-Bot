'''Button View for the schedule command'''

import discord

from modals import schedule_modal

from utils import load_embed_from_file

class ScheduleButtonView(discord.ui.View):
    '''Button view for the schedule command'''

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Schedule", style=discord.ButtonStyle.primary, custom_id="schedule")
    async def schedule_callback(self, button, interaction: discord.Interaction):
        '''Handle button clicks'''
        return await interaction.response.send_modal(modal=schedule_modal.ScheduleJumpModal())

async def send_schedule_view(guild: discord.Guild, channel: discord.TextChannel):
    '''Send the schedule view to a channel'''
    if not channel:
        return

    embed = await load_embed_from_file("schedule", {
        "guild_name": guild.name,
        "guild_image": guild.icon.url
    })

    async for message in channel.history():
        if message.embeds and message.embeds[0].title == embed.title:
            await message.edit(embed=embed, view=ScheduleButtonView())
            return

    await channel.send(embed=embed, view=ScheduleButtonView())
