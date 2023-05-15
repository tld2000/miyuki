import discord
from enum import Enum


class ConfirmationType(Enum):
    DELETE = 1
    OVERWRITE = 2


class ConfirmationButtonView(discord.ui.View):
    def __init__(self, author: discord.Member, confirmation_type: ConfirmationType, timeout: float | int = None):
        super.__init__(timeout=timeout)

        self.confirm_label = None
        self.reject_label = None
        self.confirmed = None

        if confirmation_type == ConfirmationType.DELETE:
            self.confirm_label = "Delete"
            self.reject_label = "Do not delete"
        elif confirmation_type == ConfirmationType.OVERWRITE:
            self.confirm_label = "Overwrite"
            self.reject_label = "Keep the old one"

        self.create_buttons()

    async def interaction_check(self, interaction: discord.Interaction, /) -> bool:
        return interaction.user.id == self.author.id

    def create_buttons(self):
        confirm_button = discord.ui.Button(label=self.confirm_label, style=discord.ButtonStyle.green, custom_id="confirm")
        reject_button = discord.ui.Button(label=self.confirm_label, style=discord.ButtonStyle.green, custom_id="reject")

        async def callback(interaction: discord.Interaction, button: discord.ui.Button):
            print(button.custom_id)
            self.stop()