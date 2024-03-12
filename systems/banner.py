import io
import asyncio
import datetime

from disnake.ext import commands, tasks
from collections import deque, defaultdict
from PIL import Image, ImageDraw, ImageFont
from assets.enums import GuildId, BannerConstants


class UserActivity:
    def __init__(self):
        self.messages = deque()
        self.lock = asyncio.Lock()

    async def add_message(self, message):
        async with self.lock:
            self.messages.append((message, datetime.datetime.now()))
            await self._remove_old_messages()

    async def _remove_old_messages(self):
        two_hours = datetime.datetime.now() - datetime.timedelta(hours=2)
        while self.messages and self.messages[0][1] < two_hours:
            self.messages.popleft()

    async def count_messages(self):
        async with self.lock:
            return len(self.messages)


class BannerCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.user_activity = defaultdict(UserActivity)
        self.font_main = ImageFont.truetype("assets/MontserratAlternates-Bold.ttf", BannerConstants.FONT_MAIN_SIZE.value)
        self.font_name = ImageFont.truetype("assets/MontserratAlternates-SemiBold.ttf", BannerConstants.FONT_NAME_SIZE.value)
        self.original_image = Image.open("assets/Banner.png")
        self.working_image = self.original_image.copy()

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.author.bot:
            await self.user_activity[message.author.id].add_message(message)

    @tasks.loop(minutes=1)
    async def update_member_voice_counts(self):
        await self.bot.wait_until_ready()
        guild = self.bot.get_guild(GuildId.GUILD.value)
        try:
            banner_data = await guild.banner.read()
        except AttributeError:
            print("guild not have banner, skipping member and voice counts update")
            return

        with self.working_image as img:
            draw = ImageDraw.Draw(img)

            member_total = len(guild.members)
            voice_total = len([m for m in guild.members if m.voice])

            draw.text(BannerConstants.MEMBER_TOTAL_POSITION.value, str(member_total), font=self.font_main, anchor="ma", fill=(255, 255, 255))
            draw.text(BannerConstants.VOICE_TOTAL_POSITION.value, str(voice_total), font=self.font_main, anchor="ma", fill=(255, 255, 255))

            output = io.BytesIO()
            img.save(output, format="PNG")
            output.seek(0)
            await guild.edit(banner=output.read())
            next = datetime.datetime.now() + datetime.timedelta(minutes=1)
            print(f"updated member and voice counts, waiting for next update: {next}")

        self.working_image = self.original_image.copy()

    @tasks.loop(minutes=1)
    async def update_banner(self):
        await self.bot.wait_until_ready()
        guild = self.bot.get_guild(GuildId.GUILD.value)

        with self.working_image as img:
            draw = ImageDraw.Draw(img)

            if not self.user_activity:
                print("no activity, skipping banner update")
                return

            message_counts = {user_id: await activity.count_messages() for user_id, activity in self.user_activity.items()}
            active_user_id = max(message_counts, key=message_counts.get)
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
            next = datetime.now() + datetime.timedelta(minutes=1)
            print(f"banner updated, activity cleared, waiting for next update: {next}")

        self.working_image = self.original_image.copy()

    @commands.Cog.listener()
    async def on_ready(self):
        guild = self.bot.get_guild(GuildId.GUILD.value)
        if guild.premium_tier < 2:
            print("guild not have 2 premium tier, skipping banner update loop")
            return
        now = datetime.datetime.now()
        minutes_to_next_hour = 60 - now.minute
        seconds_to_next_hour = minutes_to_next_hour * 60 - now.second

        print(f"waiting for {seconds_to_next_hour} seconds to start banner update loop")
        await asyncio.sleep(seconds_to_next_hour)
        self.update_banner.start()
        self.update_member_voice_counts.start()
