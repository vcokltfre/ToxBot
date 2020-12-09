from discord import Embed
from discord.ext import commands
from vcoutils import has_any_guild_permissions

from bot.bot import Bot
from bot.utils.checks import is_dev


class Interface(commands.Cog):
    """A cog for toxicity detection"""

    def __init__(self, bot: Bot):
        self.bot = bot
        self.bot.add_check(commands.check_any(commands.has_guild_permissions(manage_messages=True), is_dev()))
        self.bot.add_check(commands.guild_only())

    def create_summary(*dbvalues):
        toxic, severe_toxic, obscene, threat, insult, identity_hate = dbvalues[6:12]
        summary = f"Toxicity: {toxic}\nSevere Toxicity: {severe_toxic}\nObscenity: {obscene}\nThreat: {threat}\nInsult: {insult}\nIdentity Hate: {identity_hate}"
        return summary

    @commands.command(name="cases", aliases=["logs"])
    @commands.has_guild_permissions(manage_messages=True)
    async def cases(self, ctx: commands.Context, member: int):
        cases = await self.bot.db.get_infractions_for(member, ctx.guild.id)

        if not cases or not cases[0]:
            await ctx.send(f"No cases were found for that user.")
            return

        try:
            embed = Embed(title=f"Cases for {member}", description=f"This member has {len(cases)} cases.", colour=0x87CEEB)
            for i, c in enumerate(cases):
                if i < 12:
                    embed.add_field(name=f"#{c[0]} - {c[11]}", value=self.create_summary(*c))
            await ctx.send(embed=embed)
        except Exception as e:
            self.bot.logger.error(str(e))

    @commands.command(name="case", aliases=["log"])
    @commands.has_guild_permissions(manage_messages=True)
    async def case(self, ctx: commands.Context, caseid: int):
        c = await self.bot.db.get_infraction(caseid, ctx.guild.id)

        if not c:
            await ctx.send(f"That case was not found.")
            return

        desc = f"```{c[4]}```"
        embed = Embed(title=f"**Case {caseid} - {c[11]}**", description=desc, colour=0x87CEEB)
        embed.add_field(name=f"Case {c[0]} Summary", value=self.create_summary(*c))
        await ctx.send(embed=embed)


def setup(bot: Bot):
    bot.add_cog(Interface(bot))
