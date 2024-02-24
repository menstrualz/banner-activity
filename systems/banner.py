import io
import datetime
import asyncio

from assets.enums import GuildId, BannerConstants
from collections import defaultdict
from disnake.ext import commands, tasks
from PIL import Image, ImageDraw, ImageFont


class BannerCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.user_activity = defaultdict(int)
        self.font_main = ImageFont.truetype("assets/MontserratAlternates-Bold.ttf", BannerConstants.FONT_MAIN_SIZE.value)
        self.font_name = ImageFont.truetype("assets/MontserratAlternates-SemiBold.ttf", BannerConstants.FONT_NAME_SIZE.value)

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.author.bot:
            self.user_activity[message.author.id] += 1

    @tasks.loop(minutes=BannerConstants.INFO_UPDATE_INTERVAL.value)
    async def update_member_voice_counts(self):
        await self.bot.wait_until_ready()
        guild = self.bot.get_guild(GuildId.GUILD.value)
        try:
            banner_data = await guild.banner.read()
        except AttributeError:
            print("guild not have banner, skipping member and voice counts update")
            return

        with Image.open(io.BytesIO(banner_data)) as img:
            draw = ImageDraw.Draw(img)

            member_total = len(guild.members)
            voice_total = len([m for m in guild.members if m.voice])

            draw.text(BannerConstants.MEMBER_TOTAL_POSITION.value, str(member_total), font=self.font_main, anchor="ma", fill=(255, 255, 255))
            draw.text(BannerConstants.VOICE_TOTAL_POSITION.value, str(voice_total), font=self.font_main, anchor="ma", fill=(255, 255, 255))

            output = io.BytesIO()
            img.save(output, format="PNG")
            output.seek(0)
            await guild.edit(banner=output.read())
            print("updated member and voice counts")

    @tasks.loop(minutes=BannerConstants.BANNER_UPDATE_INTERVAL.value)
    async def update_banner(self):
        await self.bot.wait_until_ready()
        guild = self.bot.get_guild(GuildId.GUILD.value)

        with Image.open("assets/Banner.png") as img:
            draw = ImageDraw.Draw(img)

            if not self.user_activity:
                print("no activity, skipping banner update")
                return

            active_user_id = max(self.user_activity, key=self.user_activity.get)
            active_user = self.bot.get_user(active_user_id) or await self.bot.fetch_user(active_user_id)
            avatar = await active_user.display_avatar.read()
            avatar_finaly = Image.open(io.BytesIO(avatar)).resize(BannerConstants.AVATAR_SIZE.value)

            mask = Image.new('L', avatar_finaly.size, 0)
            mask_draw = ImageDraw.Draw(mask)
            mask_draw.ellipse((0, 0, *avatar_finaly.size), fill=255)

            draw.text(BannerConstants.ACTIVE_USER_NAME_POSITION.value, str(active_user.display_name), font=self.font_name, anchor="ma", fill=(255, 255, 255))

            img.paste(avatar_finaly, BannerConstants.AVATAR_POSITION.value, mask)

            output = io.BytesIO()
            img.save(output, format="PNG")
            output.seek(0)
            await guild.edit(banner=output.read())
            self.user_activity.clear()
            next = datetime.datetime.now() + datetime.timedelta(minutes=BannerConstants.BANNER_UPDATE_INTERVAL.value)
            print(f"banner updated, activity cleared, waiting for next update: {next}")

    @commands.Cog.listener()
    async def on_ready(self):
        now = datetime.datetime.now()
        minutes_to_next_hour = 60 - now.minute
        seconds_to_next_hour = minutes_to_next_hour * 60 - now.second

        print(f"waiting for {seconds_to_next_hour} seconds to start banner update loop")
        await asyncio.sleep(seconds_to_next_hour)
        self.update_banner.start()
        self.update_member_voice_counts.start()
