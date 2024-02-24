from systems.banner import BannerCog
from systems.listener import ListenerCog


cogs = (
    BannerCog,
    ListenerCog
)

def setup(bot):
    for cog in cogs:
        bot.add_cog(cog(bot)) 