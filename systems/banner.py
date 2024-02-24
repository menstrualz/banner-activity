import io

from assets.enums import BannerType
from collections import defaultdict
from disnake.ext import commands, tasks
from PIL import Image, ImageDraw, ImageFont


class BannerCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.user_activity = defaultdict(int)
        self.font_main = ImageFont.truetype("assets/MontserratAlternates-Bold.ttf", 32)
        self.font_name = ImageFont.truetype("assets/MontserratAlternates-SemiBold.ttf", 54)

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.author.bot:
            self.user_activity[message.author.id] += 1

    @tasks.loop(seconds=10)
    async def update_banner(self):
        print("Updating banner")
        await self.bot.wait_until_ready()
        guild = self.bot.get_guild(BannerType.GUILD.value)
        
        if not self.user_activity:
            return

        with Image.open("assets/Banner.png") as img:
            draw = ImageDraw.Draw(img)

            active_user_id = max(self.user_activity, key=self.user_activity.get)
            active_user = self.bot.get_user(active_user_id) or await self.bot.fetch_user(active_user_id)
            avatar = await active_user.display_avatar.read()
            avatar_finaly = Image.open(io.BytesIO(avatar)).resize((250, 250))

            mask = Image.new('L', avatar_finaly.size, 0)
            mask_draw = ImageDraw.Draw(mask)
            mask_draw.ellipse((0, 0, *avatar_finaly.size), fill=255)

            member_total = len(guild.members)
            voice_total = len([m for m in guild.members if m.voice])

            draw.text((576, 245), str(member_total), font=self.font_main, anchor="ma", fill=(255, 255, 255))
            draw.text((853, 395), str(voice_total), font=self.font_main, anchor="ma", fill=(255, 255, 255))
            draw.text((477, 309), str(active_user.display_name), font=self.font_name, anchor="ma", fill=(255, 255, 255))

            img.paste(avatar_finaly, (65, 217), mask)

            output = io.BytesIO()
            img.save(output, format="PNG")
            output.seek(0)
            await guild.edit(banner=output.read())
            print("Banner updated")

    @commands.Cog.listener()
    async def on_ready(self):
        self.update_banner.start()