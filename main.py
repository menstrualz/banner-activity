# from tools.setuptool import bot


# class Bot:
#     pass

# if __name__ == "__main__":
#     print("Starting bot...")
#     bot.run()

import disnake
from systems import setup
from disnake.ext import commands
from loguru import logger
from configs.config import Config

class Bot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix = "!",
                         intents = disnake.Intents.all(),
                         help_command = None,
                         test_guilds=[1104144898157981760],
                         command_sync_flags = commands.CommandSyncFlags.all(),
                         reload = True,
                         )

    async def on_ready(self):
        logger.success(f"-> <DISCORD API  CONNECTED > {self.user.name} запущен")

    async def on_resumed(self):
        logger.warning(f"-> < DISCORD API RESUMED > {self.user}")

    async def on_disconnect(self):
        logger.critical(f"-> < DISCORD API DISCONNECTED > {self.user}")

bot = Bot()
setup(bot)

if __name__ == "__main__":
    print("Starting bot...")
    bot.run(Config.get_bot().token)