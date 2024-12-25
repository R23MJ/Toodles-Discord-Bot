'''Button View for the Jump Controls'''

import time
import discord
import db
import utils
from modals import update_modal

class JumpControlsButtonView(discord.ui.View):
    '''Button view for the Jump Controls'''

    def __init__(self):
        self.started = False
        self.jump_id = None
        self.jumpers = []
        super().__init__(timeout=None)

    @discord.ui.button(label="Done", style=discord.ButtonStyle.primary, custom_id="done")
    async def schedule_callback(self, button, interaction: discord.Interaction):
        '''Handle button clicks'''
        await interaction.response.defer(ephemeral=True)

        if interaction.message.embeds.count == 0:
            return await interaction.followup.send("Message is ill-formed.", ephemeral=True)

        embed = interaction.message.embeds[0]
        if not embed:
            return await interaction.followup.send("Message is ill-formed.", ephemeral=True)

        if not self.started:
            if embed.author.name.find(interaction.user.display_name) == -1:
                return await interaction.followup.send("Wait for the host to start the jump.", ephemeral=True)

            timestamp = int(embed.description.split(":")[1])
            if (timestamp - time.time()) > 0:
                return await interaction.followup.send("You cannot start the jump yet.", ephemeral=True)

            self.jump_id = int(interaction.message.embeds[0].author.name.split("#")[1])

            jumpers = await db.get_jumpers(self.jump_id)
            self.jumpers = [jumper.display_name for jumper in jumpers]

            if not self.jumpers:
                return await interaction.followup.send("No jumpers found. Are you starting an empty jump?", ephemeral=True)

            self.started = True
            await interaction.followup.send(f"Host has started the jump. {interaction.guild.get_member_named(self.jumpers[0]).mention} it's your turn: GO!")
            return

        if self.jumpers[0] != interaction.user.display_name:
            return await interaction.followup.send("Wait your turn.", ephemeral=True)

        jumper = self.jumpers.pop(0)

        if not self.jumpers:
            await interaction.followup.send("Jump completed.")
            return

        await interaction.followup.send(f"{jumper} has jumped. {interaction.guild.get_member_named(self.jumpers[0]).mention} it's your turn: GO!", ephemeral=True)

    @discord.ui.button(label="Update", style=discord.ButtonStyle.secondary, custom_id="update")
    async def update_callback(self, button, interaction: discord.Interaction):
        '''Handle button clicks'''
        message = interaction.message
        embed = message.embeds[0]

        timestamp = int(embed.description.split(":")[1])
        if (timestamp - time.time()) < 0:
            return await interaction.response.send_message("The jump has already started!", ephemeral=True)

        if embed.author.name.find(interaction.user.display_name) == -1:
            return await interaction.response.send_message("You can only update your own jumps.", ephemeral=True)

        jump_id = int(interaction.message.embeds[0].author.name.split("#")[1])
        jump_time = int(embed.description.split(":")[1])
        jumpers = await db.get_jumpers(jump_id)

        self.jump_id = jump_id
        self.jumpers = [jumper.display_name for jumper in jumpers]

        await interaction.response.send_modal(modal=update_modal.UpdateModal(jump_id, jump_time, self.jumpers))

    @discord.ui.button(label="Skip", style=discord.ButtonStyle.danger, custom_id="skip")
    async def skip_callback(self, button, interaction: discord.Interaction):
        '''Handle button clicks'''
        await interaction.response.defer(ephemeral=True)

        message = interaction.message
        embed = message.embeds[0]

        if embed.author.name.find(interaction.user.display_name) == -1:
            return await interaction.followup.send("You can't skip another jumper.", ephemeral=True)

        if not self.jumpers:
            return await interaction.followup.send("No jumpers found.", ephemeral=True)
        
        jumper = self.jumpers.pop(0)

        await interaction.followup.send(f"{jumper} has been skipped. {interaction.guild.get_member_named(self.jumpers[0]).mention} it's your turn: GO!", ephemeral=True)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.danger, custom_id="cancel")
    async def cancel_callback(self, button, interaction: discord.Interaction):
        '''Handle button clicks'''
        await interaction.response.defer(ephemeral=True)

        message = interaction.message
        embed = message.embeds[0]

        # timestamp = int(embed.description.split(":")[1])
        # if (timestamp - time.time()) < 0:
        #     return await interaction.followup.send("The jump has already started!", ephemeral=True)

        if embed.author.name.find(interaction.user.display_name) == -1:
            return await interaction.followup.send("You can only cancel your own jumps.", ephemeral=True)

        if not self.jump_id:
            self.jump_id = int(interaction.message.embeds[0].author.name.split("#")[1])
            
        await utils.delete_jump(interaction.guild, self.jump_id)
        await interaction.followup.send("Jump canceled.", ephemeral=True)
        await interaction.message.delete()
