from aiohttp import ClientSession
from discord import Message

from bot.bot import Bot

def message_check(message: Message, bot: Bot):
    if not message.guild: return False
    if message.author.bot: return False
    if message.webhook_id: return False

    config = bot.config.load(f"./guilds/{message.guild.id}.yml")
    if not config: return False
    bl = config["blacklist"]

    if message.channel.id in bl["channels"]: return False
    if message.channel.category and message.channel.category.id in bl["channels"]: return False
    if message.author.id in bl["users"]: return False

    for role in message.author.roles:
        if role.id in bl["roles"]:
            return False

    return True

async def detect(message: Message, url: str, bot: Bot):
    if not message_check(message, bot): return False # Message was exempt so detection was not performed

    async with ClientSession() as sess:
        async with sess.post(url, json={"text":[message.content]}) as resp:
            data = await resp.json()
            return data["results"][0]["predictions"]