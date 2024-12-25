'''Modal for scheduling a jump.'''

import time
import discord

import db
import jump_embed
import utils

from views import controls_view

class ScheduleJumpModal(discord.ui.Modal):
    '''Modal for scheduling a jump.'''
    def __init__(self):
        super().__init__(title="Schedule a Jump")
        self.jump_time = None
        self.add_item(discord.ui.InputText(label="Jump Time", placeholder="Enter Timestamp Here."))

    async def callback(self, interaction: discord.Interaction):
        '''Callback for the modal.'''
        await interaction.response.defer(ephemeral=True)

        if not self.children[0].value:
            return await interaction.followup.send("You must provide a jump time.", ephemeral=True)
        
        if not self.children[0].value.startswith("<t:") or not self.children[0].value.endswith(">"):
            return await interaction.followup.send("Invalid timestamp format.", ephemeral=True)
        
        self.jump_time = int(self.children[0].value[3:-3])

        if not self.jump_time:
            return await interaction.followup.send("You must provide a jump time.", ephemeral=True)    

        if self.jump_time < time.time():
            return await interaction.followup.send("Jump time must be in the future.", ephemeral=True)

        jump_id = await db.add_jump(self.jump_time)

        embed = await utils.load_embed_from_file(
            "jump",
            {
                "jump_id": str(jump_id),
                "jump_time": str(self.jump_time),
                "host_name": interaction.user.display_name,
                "host_avatar": interaction.user.avatar.url
            }
        )

        message_id = await jump_embed.send_jump_to_schedule(interaction.guild, embed)

        if isinstance(message_id, dict):
            if "error" in message_id:
                return interaction.followup.send(message_id["error"], ephemeral=True)

        await db.update_jump_message_id(jump_id, message_id)
        await interaction.followup.send("Jump scheduled.", ephemeral=True)

        guild = interaction.guild
        channel = discord.utils.get(guild.channels, name="jumps")

        controls_embed = await utils.load_embed_from_file(
            "jump_controls",
            {
                "jump_id": str(jump_id),
                "jump_time": str(self.jump_time),
                "host_name": interaction.user.display_name,
                "host_avatar": interaction.user.avatar.url
            }
        )

        await channel.send(embed=controls_embed, view=controls_view.JumpControlsButtonView())
