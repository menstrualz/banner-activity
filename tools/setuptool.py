import disnake
from systems import cogs
from disnake.ext import commands
from loguru import logger
from configs.config import Config

bot = commands.Bot(command_prefix = "!",
                   intents = disnake.Intents.all(),
                   help_command = None,
                   test_guilds=[1172217294546538566, 1160949876553695253, 1104144898157981760, 1208112069132427345],
                   command_sync_flags = commands.CommandSyncFlags.all(),
                   reload = True,
                   )

@bot.event
async def on_ready():
    logger.success(f"-> <DISCORD API  CONNECTED > {bot.user.name} запущен")

@bot.event
async def on_resumed():
    logger.warning(f"-> < DISCORD API RESUMED > {bot.user}")

@bot.event
async def on_disconnect():
    logger.critical(f"-> < DISCORD API DISCONNECTED > {bot.user}")

cogs.setup(bot)
bot.run(Config.get_bot().token)