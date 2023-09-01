import discord
from .CustomColor import CustomColor
from typing import List

class ColorSelectionModal(discord.ui.Modal, title="Color Selection"):
    example_format = "Color Name:Hexcode:(optional Emoji)\nExample:\nPeriwinkle:CCCCFF:🔮\nChartreuse:80FF00"
    options_field: discord.ui.TextInput
    color_list: List[CustomColor]

    def __init__(self, value:str = None):
        super().__init__(timeout=None)
        self.options_field = discord.ui.TextInput(
            label = "Custom Color Options",
            placeholder=f"{ColorSelectionModal.example_format}\n...",
            style=discord.TextStyle.long,
            default=value,
        )
        self.add_item(self.options_field)
    
    async def on_submit(self, interaction: discord.Interaction) -> None:
        self.color_list = []
        lines = self.options_field.value.strip().split("\n")
        for i, line in enumerate(lines):
            try:
                if line.count(":") == 1:
                    print("1 found")
                    # TODO error checking for valid hexcode
                    color, value = line.split(":")
                    self.color_list.append(CustomColor(name=color, hexcode=int(value, 16)))
                elif line.count(":") == 2:
                    print("2 found")
                    color, value, emoji = line.split(":")
                    self.color_list.append(CustomColor(name=color, hexcode=int(value, 16), emoji=emoji))
                else:
                    print("not found")
                    raise ParsingError(i, line)
            except:
                print("bruhed")
                raise ParsingError(i, line)

        await interaction.response.defer()
        # await interaction.response.send_message(f'Thanks for your response!', ephemeral=True)
    
    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        print(error)
        await interaction.response.send_message(f'{error}', ephemeral=True)


class ParsingError(Exception):
    '''

    Init Parameters	
    ----------
    '''
    def __init__(self, index:int, line:str) -> None:
        self.message = f"Error parsing at line {index+1} : {line}\n\nPlease follow the format:\n{ColorSelectionModal.example_format}\n"
        super().__init__()
    def __str__(self):
        return self.message