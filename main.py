from bot.bot import run

run([
    "jishaku",
    "bot.cogs.utility.general",
    "bot.cogs.core.detection",
    "bot.cogs.core.interface"
], debug=False)
