'''Modal for updating a jump.'''

import discord
import db
import utils

TORN_PROFILE_URL = "https://www.torn.com/profiles.php?XID="

class UpdateModal(discord.ui.Modal):
    '''Modal for updating a jump.'''
    def __init__(self, jump_id: int, jump_time: int, jumpers: list):
        super().__init__(title="Update a Jump")

        self.jump_id = jump_id

        self.add_item(
            discord.ui.InputText(
                label="Jump Time",
                placeholder="Enter Jump Time Here.",
                value=str(jump_time)
            )
        )

        self.add_item(
            discord.ui.InputText(
                label="Jumper Order",
                style=discord.InputTextStyle.multiline,
                placeholder="Enter Jumpers Here.",
                value="\n".join(jumpers)
            )
        )

    async def callback(self, interaction: discord.Interaction):
        '''Callback for the modal.'''
        await interaction.response.defer(ephemeral=True)

        jump_time = self.children[0].value
        jumpers = self.children[1].value.split("\n")

        await db.update_jump_time_and_order(self.jump_id, jump_time, jumpers)

        # update the jump message
        message = interaction.message
        embed = message.embeds[0]
        embed.description = f"Jump scheduled for <t:{jump_time}:F>"
        jumpers_field = next((field for field in embed.fields if field.name == "Jumper Order"), None)

        jumpers = [f"[{jumper}]({TORN_PROFILE_URL}{utils.get_torn_id(jumper)})" for jumper in jumpers]
        
        if jumpers_field:
            jumpers_field.value = "\n".join(jumpers)
        else:
            embed.add_field(name="Jumper Order", value="\n".join(jumpers))

        await message.edit(embed=embed)
        await interaction.followup.send("Jump updated.", ephemeral=True)
