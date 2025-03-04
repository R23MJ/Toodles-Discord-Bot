'''Button View for the roll call command'''

import discord

from utils import load_embed_from_file

class RollCallButtonView(discord.ui.View):
    '''Button View for the roll call command'''

    def __init__(self):
        super().__init__(timeout=None)
        self.message_id = None

    @discord.ui.button(label="Ready", style=discord.ButtonStyle.primary, custom_id="ready")
    async def schedule_callback(self, button, interaction: discord.Interaction):
        '''Handle button clicks'''
        await interaction.response.defer(ephemeral=True)

        if not self.message_id:
            return await interaction.followup.send("Message constructing. Try again in a few minutes.", ephemeral=True)

        message = await interaction.channel.fetch_message(self.message_id)
        embed = message.embeds[0]

        names = embed.description.split("\n")

        if interaction.user.display_name in names:
            return await interaction.followup.send("You've already readied up.", ephemeral=True)

        names.append(interaction.user.display_name)

        await message.delete()

        rc_embed = await load_embed_from_file(
            "roll_call",
            {
                "guild_name": embed.title,
                "guild_image": embed.thumbnail.url,
                "names": "\n".join(names),
            }
        )

        view = RollCallButtonView()

        message = await interaction.channel.send(embed=rc_embed, view=view)
        view.message_id = message.id

        return await interaction.followup.send("You are now ready.", ephemeral=True)

async def send_rc_view(guild: discord.Guild, channel: discord.TextChannel):
    '''Send the Roll Call view to a channel'''
    if not channel:
        return

    rc_embed = await load_embed_from_file(
        "roll_call",
        {
            "guild_name": guild.name,
            "guild_image": guild.icon.url,
            "names": "No one is ready yet.",
        }
    )

    view = RollCallButtonView()

    message = await channel.send(embed=rc_embed, view=view)
    view.message_id = message.id
