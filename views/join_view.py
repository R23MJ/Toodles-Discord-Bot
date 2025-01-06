'''Button View for joining a jump'''

import re
import time
import discord
import db

from utils import get_torn_id

# function to abstract out common checks
async def check_jump(interaction: discord.Interaction):
    '''Check if jump is valid'''
    if not interaction.message.embeds:
        return await interaction.followup.send("Jump message is ill-formed.", ephemeral=True)

    embed = interaction.message.embeds[0]
    if not embed:
        return await interaction.followup.send("Jump message is ill-formed.", ephemeral=True)

    jumpers_field = next((field for field in embed.fields if field.name == "Jumper Order"), None)
    if not jumpers_field:
        return await interaction.followup.send("Jump message is ill-formed.", ephemeral=True)

    return embed, jumpers_field

class JoinJumpButtonView(discord.ui.View):
    '''Button view for joining a jump'''

    def __init__(self):
        super().__init__(timeout=None)
        self.jump_message_id = None

    @discord.ui.button(label="Join", style=discord.ButtonStyle.primary, custom_id="join")
    async def join_callback(self, button, interaction: discord.Interaction):
        '''Handle button clicks'''
        await interaction.response.defer(ephemeral=True)

        if not self.jump_message_id:
            return await interaction.followup.send("Message constructing. Try again in a few minutes.", ephemeral=True)

        embed, jumpers_field = await check_jump(interaction)

        timestamp = int(embed.description.split(":")[1])
        if (timestamp - time.time()) < 0:
            return await interaction.followup.send("The jump has already started!", ephemeral=True)

        jumpers = jumpers_field.value.split("\n")
        if interaction.user.display_name in jumpers:
            return await interaction.followup.send("You are already in the jump.", ephemeral=True)

        if len(jumpers) >= 6:
            return await interaction.followup.send("Jump is full! Please join another jump.", ephemeral=True)

        match = re.search(r"#(\d+)", embed.title)
        if not match:
            return await interaction.followup.send("Jump id not found.", ephemeral=True)

        jump_id = match.group(1)

        guild = interaction.guild
        role = discord.utils.get(guild.roles, name=f"Jump #{jump_id}")
        if not role:
            return await interaction.followup.send("Jump role not found.", ephemeral=True)

        await interaction.user.add_roles(role)
        jumpers.append(interaction.user.display_name)
        jumpers_field.value = "\n".join(jumpers)
        await interaction.message.edit(embed=embed)

        await db.add_jumper(jump_id, interaction.user.display_name, get_torn_id(interaction.user.display_name))

        await interaction.followup.send("Jump joined.", ephemeral=True)

    @discord.ui.button(label="Leave", style=discord.ButtonStyle.danger, custom_id="leave")
    async def leave_callback(self, button, interaction: discord.Interaction):
        '''Handle button clicks'''
        await interaction.response.defer(ephemeral=True)

        if not self.jump_message_id:
            return await interaction.followup.send("Message constructing. Try again in a few minutes.", ephemeral=True)

        embed, jumpers_field = await check_jump(interaction)

        timestamp = int(embed.description.split(":")[1])
        if (timestamp - time.time()) < 0:
            print(timestamp, time.time())
            return await interaction.followup.send("The jump has already started!", ephemeral=True)

        jumpers = jumpers_field.value.split("\n")
        if interaction.user.display_name not in jumpers:
            return await interaction.followup.send("You are not in the jump.", ephemeral=True)

        match = re.search(r"#(\d+)", embed.title)
        if not match:
            return await interaction.followup.send("Jump id not found.", ephemeral=True)

        jump_id = match.group(1)

        guild = interaction.guild
        role = discord.utils.get(guild.roles, name=f"Jump #{jump_id}")
        if not role:
            return await interaction.followup.send("Jump role not found.", ephemeral=True)

        await interaction.user.remove_roles(role)
        jumpers.remove(interaction.user.display_name)
        jumpers_field.value = "\n".join(jumpers)
        await interaction.message.edit(embed=embed)

        await db.delete_jumper_from_jump(get_torn_id(interaction.user.display_name), jump_id)
        await interaction.followup.send("Jump left.", ephemeral=True)
