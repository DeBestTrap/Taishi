import asyncio, os, discord
import json
import yaml
from discord.ext import commands
from .ColorView import ColorView, PersistentColorView, CustomColor
from .ColorSelectionModal import ColorSelectionModal

class ColorSelection(commands.GroupCog, name="color_selection"):
    '''
    Interactive polls that update based on who answered.
    '''
    def __init__(self, bot: commands.bot):
        self.bot: commands.bot = bot

    @commands.is_owner()
    @commands.guild_only()
    @discord.app_commands.command(name="setup")
    async def setup(self, interaction:discord.Interaction) -> None:
        '''
        Owner only and for guilds

        Creates a poll that users can select their color on.

        Parameters
        ----------
        interaction: :class:`discord.Interaction`
            The interaction that triggered this slash command.
        '''
        print(interaction.guild.roles)
        # for i in range(len(interaction.guild.roles)):
        #     print(interaction.guild.roles[i].color)
        
        # if not os.path.exists(f"server_data/{interaction.guild.id}/color_selection.json"):
        #     os.makedirs(f"server_data/{interaction.guild.id}/")
            # call update if it exists
        

        config_path = os.path.join(__file__, "..", "config.yaml")
        # f = open(config_path, "w", encoding="utf16")
        # d = {"default":{"red": {"name": "Red", "hexcode": 0xFF0000, "emoji": "🔴"},
        #                 "orange": {"name": "Orange", "hexcode": 0xFFA500, "emoji": "🟠"},
        #                 "yellow": {"name": "Yellow", "hexcode": 0xFFFF00, "emoji": "🟡"},
        #                 "green": {"name": "Green", "hexcode": 0x00FF00, "emoji": "🟢"},
        #                 "blue": {"name": "Blue", "hexcode": 0x0000FF, "emoji": "🔵"},
        #                 "purple": {"name": "Purple", "hexcode": 0x800080, "emoji": "🟣"},
        #                 "pink": {"name": "Pink", "hexcode": 0xFFC0CB, "emoji": "🌸"},
        #                 "brown": {"name": "Brown", "hexcode": 0xA52A2A, "emoji": "🟤"},
        #                 }}
        # yaml.dump(d, f, allow_unicode=True)
        # return
        with open(config_path, "r", encoding="utf16") as f:
            config = yaml.safe_load(f.read())
        default_colors = []
        for color in config["default"]:
            name = config["default"][color]["name"]
            hexcode = config["default"][color]["hexcode"]
            emoji = config["default"][color]["emoji"]
            default_colors.append(CustomColor(name, hexcode, emoji))
        print(default_colors)

        view = ColorView(default_colors)
        await interaction.response.send_message("Choose", ephemeral=True, view=view)
        await view.wait() 
        chosen_colors = view.chosen_colors

        color: CustomColor
        # TODO error check view for when person types wrong format in modal
        for color in chosen_colors:
            role = await interaction.guild.create_role(name=color.name, color=color.hexcode)
            color.role_id = role.id


        id = f"color_select:{interaction.guild_id}"
        if not os.path.exists(f"server_data/{interaction.guild.id}/"):
            os.makedirs(f"server_data/{interaction.guild.id}/")

        view = PersistentColorView(id=id, colors=chosen_colors)
        await interaction.followup.send("Make sure you move my role up and use /move_roles to automatically move the colors up!\nI won't be able to give roles otherwise.", ephemeral=True)
        msg = await interaction.channel.send("Select Your Color!", view=view)

        with open(f"server_data/{interaction.guild.id}/color_selection.json", "w") as f:
            json.dump({"colors":list(map(lambda x: x.get_dict(), chosen_colors)), "msg_id":msg.id}, f)
        
    @commands.is_owner()
    @commands.guild_only()
    @discord.app_commands.command(name="delete")
    async def delete(self, interaction:discord.Interaction) -> None:
        colors = CustomColor.fetch_colors(interaction.guild.id)
        roles = [interaction.guild.get_role(color.role_id) for color in colors]
        await interaction.response.send_message("Working on it", ephemeral=True)
        for role in roles:
            try:
                await role.delete()
            except:
                pass
        # TODO maybe delete the message?
        try:
            os.remove(f"server_data/{interaction.guild.id}/color_selection.json")
        except:
            pass
        await interaction.edit_original_response(content="Deleted roles and data (can't delete the message yet")
        # await interaction.followup.send("Deleted roles and data (can't delete the message yet)", ephemeral=True)

    @commands.is_owner()
    @commands.guild_only()
    @discord.app_commands.command(name="move_roles")
    async def move_roles(self, interaction:discord.Interaction) -> None:
        '''
        Moves roles to be in the same position as the bot's role.
        '''
        colors = CustomColor.fetch_colors(interaction.guild.id)
        if not colors:
            await interaction.response.send_message("No colors have been set up yet! Use /color_selection setup", ephemeral=True)

        await interaction.response.send_message("Working on it", ephemeral=True)
        bot_info: discord.AppInfo = await self.bot.application_info()
        for role in interaction.guild.roles:
            if role.name == bot_info.name:
                bot_role = role

        role_positions = {role:role.position for role in interaction.guild.roles}   
        l= [f"{role.position} {role.name}" for role in interaction.guild.roles]
        print(l)
        bot_role_position = role_positions[bot_role]
        for color in colors:
            role = interaction.guild.get_role(color.role_id)
            await role.edit(position=bot_role_position-1)
        l= [f"{role.position} {role.name}" for role in interaction.guild.roles]
        print(l)

        await interaction.edit_original_response(content="Moved roles")


        
        

    @commands.is_owner()
    @commands.guild_only()
    @discord.app_commands.command(name="add")
    async def add(self, interaction:discord.Interaction) -> None:
        '''
        H

        Parameters
        ----------
        interaction: :class:`discord.Interaction`
            The interaction that triggered this slash command.
        embed: :class:`discord.Embed`
            The embed to update the message with.
        view: :class:`discord.ui.View`
            The view to update the message with.
        '''
        # load server data
        # check roles if they exist
        # if they don't exist, create them and rewrite the config

        colors = CustomColor.fetch_colors(interaction.guild.id)
        with open(f"server_data/{interaction.guild.id}/color_selection.json", "r") as f:
            data = json.load(f)
            msg_id = data["msg_id"]

        modal = ColorSelectionModal()
        await interaction.response.send_modal(modal)
        await modal.wait()
        
        for i, color in enumerate(modal.color_list):
            role = await interaction.guild.create_role(name=color.name, color=color.hexcode)
            color.role_id = role.id

        modal.color_list.extend(colors)

        await discord.Message.edit(await interaction.channel.fetch_message(msg_id), content="Select Your Color!", view=PersistentColorView(id=f"color_select:{interaction.guild_id}", colors=modal.color_list))
        # TODO combine this with setup's in a function
        with open(f"server_data/{interaction.guild.id}/color_selection.json", "w") as f:
            json.dump({"colors":list(map(lambda x: x.get_dict(), modal.color_list)), "msg_id":msg_id}, f)

        # TODO update trap cave message id

        


    @commands.is_owner()
    @commands.guild_only()
    @discord.app_commands.command(name="edit")
    async def edit(self, interaction:discord.Interaction) -> None:
        '''
        Updates the message with the new embed and view.

        Parameters
        ----------
        interaction: :class:`discord.Interaction`
            The interaction that triggered this slash command.
        embed: :class:`discord.Embed`
            The embed to update the message with.
        view: :class:`discord.ui.View`
            The view to update the message with.
        '''
        # load server data
        # check roles if they exist
        # if they don't exist, create them and rewrite the config

        colors = CustomColor.fetch_colors(interaction.guild.id)
        with open(f"server_data/{interaction.guild.id}/color_selection.json", "r") as f:
            data = json.load(f)
            msg_id = data["msg_id"]

        modal = ColorSelectionModal(value="\n".join(map(lambda x: f"{x.name}:{x.hexcode:06X}"+ (f":{x.emoji}" if x.emoji else ""), colors)))
        await interaction.response.send_modal(modal)
        await modal.wait()
        if len(modal.color_list) != len(colors):
            raise Exception("Color list length mismatch")
        
        for i, color in enumerate(colors):
            role = await interaction.guild.get_role(color.role_id).edit(name=modal.color_list[i].name, color=modal.color_list[i].hexcode)
            modal.color_list[i].role_id = role.id

        await discord.Message.edit(await interaction.channel.fetch_message(msg_id), content="Select Your Color!", view=PersistentColorView(id=f"color_select:{interaction.guild_id}", colors=modal.color_list))
        # TODO combine this with setup's in a function
        with open(f"server_data/{interaction.guild.id}/color_selection.json", "w") as f:
            json.dump({"colors":list(map(lambda x: x.get_dict(), modal.color_list)), "msg_id":msg_id}, f)

        # TODO update trap cave message id


async def setup(bot: commands.bot) -> None:
    await bot.add_cog(ColorSelection(bot))