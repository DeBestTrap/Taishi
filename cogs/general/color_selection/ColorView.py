import discord
from typing import Dict, List, Union
import json
from .ColorSelectionModal import ColorSelectionModal
from .CustomColor import CustomColor
import logging
import os

class ColorView(discord.ui.View):

    def __init__(self, default_colors:Dict[str, int]):
        super().__init__()
        self.default_colors = default_colors
        self.chosen_colors = None
    
    @discord.ui.button(label="Default", style=discord.ButtonStyle.blurple)
    async def default_color(self, interaction:discord.Interaction, button:discord.ui.Button):
        self.chosen_colors = self.default_colors
        await interaction.response.defer()
        super().stop()
    
    @discord.ui.button(label="Default and Custom", style=discord.ButtonStyle.green)
    async def default_and_custom_color(self, interaction:discord.Interaction, button:discord.ui.Button):
        modal = ColorSelectionModal()
        await interaction.response.send_modal(modal)
        await modal.wait()
        self.chosen_colors = self.default_colors.copy()
        self.chosen_colors.extend(modal.color_list)
        super().stop()

    @discord.ui.button(label="Custom", style=discord.ButtonStyle.blurple)
    async def custom_color(self, interaction:discord.Interaction, button:discord.ui.Button):
        modal = ColorSelectionModal()
        await interaction.response.send_modal(modal)
        await modal.wait()
        self.chosen_colors = modal.color_list
        super().stop()
    
        

class PersistentColorView(discord.ui.View):
    def __init__(self, id:str = None, colors:List[CustomColor] = None):
        self.select = None
        self.colors = None

        super().__init__(timeout=None)
        if id and colors:
            self.setup_view(id, colors)

    def setup_view(self, id:str, colors:List[CustomColor]) -> None:
        self.colors = colors
        select_options = []
        for color in colors:
            select_options.append(discord.SelectOption(
            label=color.name,
            emoji=color.emoji,
            ))

        select = discord.ui.Select(
            custom_id=id,
            placeholder="Select your color",
            options=select_options
        )
        select.callback = self.change_color_callback
        self.add_item(select)
        self.select = select

    def setup_peristent_views() -> None:
        print("gjiafjdlksafjkdsladjflka")
        if not os.path.exists("server_data"):
            os.makedirs("server_data")
        guild_dirs = os.listdir("server_data")
        views = []
        for guild_id in guild_dirs:
            colors = CustomColor.fetch_colors(guild_id)
            views.append(PersistentColorView(id=f"color_select:{guild_id}", colors=colors))
        return views

    async def change_color_callback(self, interaction:discord.Interaction):
        selected_color = self.select.values[0]
        for color in self.colors:
            if color.name == selected_color:
                role_id = color.role_id
                print(f"found role id {role_id}")
                break
        selected_role = interaction.guild.get_role(role_id)
        print(f"role: {selected_role}")
        if selected_role in interaction.user.roles:
            await interaction.user.remove_roles(selected_role)
            await interaction.response.send_message(f"Removed {selected_role.name}", ephemeral=True, delete_after=10)
        else:
            await interaction.user.add_roles(selected_role)
            await interaction.response.send_message(f"Added {selected_role.name}", ephemeral=True, delete_after=10)
            for role in interaction.user.roles:
                if role in self.colors:
                    await interaction.user.remove_roles(role)
        # await interaction.user.remove_roles()
    
    # async def s


