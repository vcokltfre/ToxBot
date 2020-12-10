from discord import Embed
from discord.ext import commands
from vcoutils import LeakyBucketManager

from config.config import max_urls, logs
from bot.bot import Bot
from bot.utils.http import detect

desc = """
[Message]({jump}) from {author} ({author.id}) triggered detection filters!
Action taken: **{action}**
{bucket}

**Snippet:**
```
{snippet}
```
"""


class Detection(commands.Cog):
    """The core cog for toxicity detection"""

    def __init__(self, bot: Bot):
        self.bot = bot
        self.urls = max_urls
        self.buckets = LeakyBucketManager()

    def get_url(self) -> str:
        url = self.urls.pop(0)
        self.urls.append(url)
        return url

    def get_actions(self, results: dict, guild: int) -> list:
        actions = []
        levels = self.bot.config.load(f"./guilds/{guild}.yml")["levels"]
        for result, value in results.items():
            level = levels[result]
            if value >= level["delete"]:
                actions.append(("delete", result, value))
            elif value >= level["alert"]:
                actions.append(("alert", result, value))
        return actions

    def get_bucket(self, message):
        bconf = self.bot.config.load(f"./guilds/{message.guild.id}.yml")["buckets"]
        bid = f"{message.guild.id}::{message.author.id}"
        self.buckets.add(bid, bconf["duration"])
        return self.buckets.get(bid), bconf

    def get_embed(self, actions, message, infr):
        bucket, bconf = self.get_bucket(message)
        send = True
        if bucket < bconf["count"] and bconf["mode"] == "bucket-only":
            send = False
        bucket = "" if bucket < bconf["count"] else f"⚠️ User has exceeded cooldown bucket! ({bconf['count']}/{bconf['duration']}s)"
        action = "alert"
        for a in actions:
            if a[0] == "delete": action = "delete"
        description = desc.format(jump=message.jump_url, author=message.author, action=action, bucket=bucket, snippet=message.content[:1200])
        embed = Embed(title=f"Toxicity Detection Warning in {message.guild}", description=description, colour=0x87CEEB)
        embed.set_footer(text=f"Infraction ID: {infr}")
        for a in actions:
            embed.add_field(name=a[1], value=f"Rate: {a[2]}\nAction: {a[0]}")
        return embed, send, action

    @commands.Cog.listener()
    async def on_message(self, message):
        await self.bot.wait_until_ready()
        results = await detect(message, self.get_url(), self.bot)
        if not results: return

        actions = self.get_actions(results, message.guild.id)
        if not actions: return

        try:
            infraction_id = await self.bot.db.create_infraction(message, results)
        except:
            infraction_id = "DB_ERR"

        cfg = self.bot.config.load(f"./guilds/{message.guild.id}.yml")
        channel = self.bot.get_channel(cfg["alerts"])
        logchannel = self.bot.get_channel(logs)
        embed, send, action = self.get_embed(actions, message, infraction_id)
        await logchannel.send(embed=embed)

        if send:
            await channel.send(embed=embed)
        if action == "delete":
            await message.delete()


def setup(bot: Bot):
    bot.add_cog(Detection(bot))
