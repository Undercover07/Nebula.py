import time
import discord
import psutil
import os

from discord.ext.commands.context import Context
from discord.ext.commands._types import BotT
from discord.ext import commands
from utils import default, http


class Information(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.AutoShardedBot = bot
        self.config = default.load_json()
        self.process = psutil.Process(os.getpid())

    @commands.command(name="ping")
    async def ping(self, ctx: Context[BotT]):
        """ Pong! """
        before = time.monotonic()
        before_ws = int(round(self.bot.latency * 1000, 1))
        msg = await ctx.send("🏓 Pong")
        ping = (time.monotonic() - before) * 1000
        await msg.edit(content=f"🏓 WS: {before_ws}ms  |  REST: {int(ping)}ms")

    
    @commands.command()
    async def covid(self, ctx: Context[BotT], *, country: str):
        """Covid-19 Statistics for any countries"""
        async with ctx.channel.typing():
            r = await http.get(f"https://disease.sh/v3/covid-19/countries/{country.lower()}", res_method="json")

            if "message" in r:
                return await ctx.send(f"The API returned an error:\n{r['message']}")

            json_data = [
                ("Total Cases", r["cases"]), ("Total Deaths", r["deaths"]),
                ("Total Recover", r["recovered"]), ("Total Active Cases", r["active"]),
                ("Total Critical Condition", r["critical"]), ("New Cases Today", r["todayCases"]),
                ("New Deaths Today", r["todayDeaths"]), ("New Recovery Today", r["todayRecovered"])
            ]

            embed = discord.Embed(
                description=f"The information provided was last updated <t:{int(r['updated'] / 1000)}:R>"
            )


            for name, value in json_data:
                embed.add_field(
                    name=name, value=f"{value:,}" if isinstance(value, int) else value
                )

            await ctx.send(
                f"**COVID-19** statistics in :flag_{r['countryInfo']['iso2'].lower()}: "
                f"**{country.capitalize()}** *({r['countryInfo']['iso3']})*",
                embed=embed
            )

        await ctx.send(content=f"ℹ About **{ctx.bot.user}**", embed=embed)


async def setup(bot):
    await bot.add_cog(Information(bot))