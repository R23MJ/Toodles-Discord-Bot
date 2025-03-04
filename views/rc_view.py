'''Button View for the roll call command'''

import discord

from utils import load_embed_from_file, get_torn_id

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
        
        torn_id = get_torn_id(interaction.user.display_name)
        torn_url = f"https://www.torn.com/profiles.php?XID={torn_id}"

        if f"[{interaction.user.display_name}]({torn_url})" in names:
            return await interaction.followup.send("You've already readied up.", ephemeral=True)

        if names[0] == "I CAN'T HEAR YOU!":
            names[0] = f"[{interaction.user.display_name}]({torn_url})"
        else:
            names.append(f"[{interaction.user.display_name}]({torn_url})")

        await message.delete()

        rc_embed = await load_embed_from_file(
            "roll_call",
            {
                "guild_name": interaction.guild.name,
                "guild_image": interaction.guild.icon.url,
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
            "names": "I CAN'T HEAR YOU!",
        }
    )

    view = RollCallButtonView()

    message = await channel.send(embed=rc_embed, view=view)
    view.message_id = message.id
