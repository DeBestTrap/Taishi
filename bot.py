# bot.py
# Starter code from Overlord bot: https://github.com/overlord-bot/Overlord

import os
import sys
import random
import discord
import asyncio
from discord.ext import commands
from dotenv import load_dotenv

class Bot(commands.Bot):
    def __init__(self) -> None:
        args = sys.argv
        load_dotenv()

        # -test argument will set the bot to only sync slash commands on the testing server
        # whose server id stored in that env var (see cogs/general/startup.py).
        # Otherwise, app commands will sync globally (and take up to an hour to sync).
        testing_server_id = os.getenv("TESTING_SERVER_ID")
        if not testing_server_id:
            raise ValueError("TESTING_SERVER_ID environment variable not set")
        self.testing_server = discord.Object(testing_server_id) if "-test" in args else None

        # Necessary intents (permissions) for the bot to function
        intents = discord.Intents.default()
        intents.members = True  # permission to see server members
        intents.message_content = True  # permission to read message content

        # Set up the bot object and its descriptions
        self.bot_status = "~help"
        if "-test" in args:
            import time
            self.bot_status = f"{time.strftime('%H:%M:%S')} | Last Update"
        self.bot_description = "Taishi"
        super().__init__(command_prefix="~", description=self.bot_description, intents=intents,
                         activity=discord.Game(name=self.bot_status))

    async def setup_hook(self) -> None:
        await load_cogs(self)


# loads all subdirectories of folder, and loads all .py files that are inside a specified folder to load
async def load_folder(bot, folder, folder_names, flag_loadall):
    if folder.split('/')[-1] in folder_names or flag_loadall:
        print("loading folder: " + folder.split('/')[-1])

    # traversing all files within directory
    for file in os.listdir(os.path.join(f"{folder}")):
        # load all subdirectories
        if os.path.isdir(f"{str(folder)}/{file}") and not file.startswith("_") and not file.startswith("."):
            if folder.split('/')[-1] in folder_names:
                await load_folder(bot, folder + "/" + file, folder_names, True)
            await load_folder(bot, folder + "/" + file, folder_names, flag_loadall)
            continue

        # if the content of this folder should be loaded:
        elif folder.split('/')[-1] in folder_names or flag_loadall:
            if file.endswith(".py"):
                try:
                    await bot.load_extension(f"{folder.replace('/', '.')}.{file[:-3]}")
                    print(f"Success Loading: {folder}/{file}")
                except Exception as e:
                    exception = f"{type(e).__name__}: {e}"
                    print(f"Failed Loading: {folder}/{file} | Error: {exception}")


# Load all cogs inside the cogs folder
async def load_cogs(bot):
    print("\n------------------ Loading Cogs -----------------")
    arguments = sys.argv
    flag_loadall = False

    # adds folders specified to load from command line arguments into [folder_names]
    folder_names = []

    if "-all" in arguments or "-load" not in arguments:
        print(f"{'-all flag found,' if '-all' in arguments else 'no args specified,'} loading all modules \\(^.^)/")
        flag_loadall = True

    else:
        for i in range(0, len(arguments) - 1):
            if arguments[i] == "-load":
                folder_names = arguments[i + 1].split(",")
                folder_names = [name.strip() for name in folder_names]
                print("loading folders specified from command line input: " + str(folder_names))

    folder_names.append("general") # always load the general folder

    print("loading folders: " + str(folder_names))
    await load_folder(bot, os.path.join("cogs"), folder_names, flag_loadall)


if __name__ == "__main__":
    args = sys.argv
    if "-help" in args:
        print("Usage: python bot.py [-all] [-help] [-test] [-load <folder1,folder2,...>]")
        print("    -help: displays this message")
        print("    -test: only syncs slash commands on the testing server")
        print("    -all: load all cogs")
        print("    -load <folder1,folder2,...>: load only the specified folders")
        exit()

    bot = Bot()
    asyncio.run(bot.run(os.getenv("TOKEN")))  # fetches token from env file stored locally and starts bot