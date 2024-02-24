from main import bot
from systems import cogs
from configs.config import Config


cogs.setup(bot)
bot.run(Config.get_bot().token)
