'''Button View for the done command'''

import discord

from utils import load_embed_from_file

class DoneButtonView(discord.ui.View):
    '''Button View for the done command'''

    def __init__(self):
        super().__init__(timeout=None)
        self.message_id = None

    @discord.ui.button(label="Going", style=discord.ButtonStyle.primary, custom_id="going")
    async def done_callback(self, button, interaction: discord.Interaction):
        '''Handle button clicks'''
        await interaction.response.defer(ephemeral=True)

        if not self.message_id:
            return await interaction.followup.send("Message constructing. Try again in a few minutes.", ephemeral=True)

        message = await interaction.channel.fetch_message(self.message_id)
        embed = message.embeds[0]

        if interaction.user.display_name in embed.description:
            return await interaction.followup.send("But you just went?!", ephemeral=True)

        await message.delete()

        embed = await load_embed_from_file(
            "going",
            {
                "guild_name": interaction.guild.name,
                "guild_image": interaction.guild.icon.url,
                "name": interaction.user.display_name,
            }
        )

        view = GoingButtonView()

        message = await interaction.channel.send(embed=embed, view=view)
        view.message_id = message.id

        return await interaction.followup.send("You are now ready.", ephemeral=True)
    
class GoingButtonView(discord.ui.View):
    '''Button View for the going command'''

    def __init__(self):
        super().__init__(timeout=None)
        self.message_id = None

    @discord.ui.button(label="Done", style=discord.ButtonStyle.primary, custom_id="done")
    async def going_callback(self, button, interaction: discord.Interaction):
        '''Handle button clicks'''
        await interaction.response.defer(ephemeral=True)

        if not self.message_id:
            return await interaction.followup.send("Message constructing. Try again in a few minutes.", ephemeral=True)

        message = await interaction.channel.fetch_message(self.message_id)
        embed = message.embeds[0]

        if interaction.user.display_name not in embed.description:
            return await interaction.followup.send("Wait your turn.", ephemeral=True)

        await message.delete()

        embed = await load_embed_from_file(
            "done",
            {
                "guild_name": interaction.guild.name,
                "guild_image": interaction.guild.icon.url,
                "name": interaction.user.display_name,
            }
        )

        view = DoneButtonView()

        message = await interaction.channel.send(embed=embed, view=view)
        view.message_id = message.id

        return await interaction.followup.send("You are now ready.", ephemeral=True)

async def send_done_view(guild: discord.Guild, channel: discord.TextChannel, name: str):
    '''Send the done view to a channel'''
    if not channel:
        return

    embed = await load_embed_from_file(
        "done",
        {
            "guild_name": guild.name,
            "guild_image": guild.icon.url,
            "name": name
        }
    )

    view = DoneButtonView()

    message = await channel.send(embed=embed, view=view)
    view.message_id = message.id
