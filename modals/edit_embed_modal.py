'''Modal for Editing the basic info of an Embed.'''

import json
import discord
import utils

class BasicEditEmbedModal(discord.ui.Modal):
    '''Modal for Editing the basic info of an Embed.'''
    def __init__(self, json_file: str):
        super().__init__(title="Edit an Embed")

        self.filename = json_file

        try:
            with open("embeds/" + json_file + ".json", "r", encoding="utf-8") as file:
                data = json.load(file)
        except FileNotFoundError:
            self.add_item(discord.ui.InputText(label="Error.", value="Embed not found."))
            return
        
        try:
            embed = json.dumps(data, indent=4)
        except json.JSONDecodeError:
            self.add_item(discord.ui.InputText(label="Error.", value="Invalid JSON."))
            return

        self.add_item(discord.ui.InputText(label="JSON", style=discord.InputTextStyle.multiline, placeholder="Enter JSON Here.", value=embed))


    async def callback(self, interaction: discord.Interaction):
        '''Callback for the modal.'''
        await interaction.response.defer(ephemeral=True)

        try:
            data = json.loads(self.children[0].value)
        except json.JSONDecodeError:
            return await interaction.followup.send("Invalid JSON.", ephemeral=True)
        
        try:
            await utils.save_embed_to_file(data, self.filename)
        except Exception as e:
            return await interaction.followup.send(f"Error saving embed: {e}", ephemeral=True)

        try:
            embed = await utils.load_embed_from_file(
                self.filename,
                {
                    "guild_name": interaction.guild.name,
                    "guild_image": interaction.guild.icon.url
                })
        except Exception as e:
            return await interaction.followup.send(f"Error loading embed: {e}", ephemeral=True)

        await interaction.followup.send("Embed updated. Here is a preview: ", embed=embed, ephemeral=True)
