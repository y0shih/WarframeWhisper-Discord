import os
import re
import asyncio
import discord
from discord.ext import commands
import config
from time import sleep
import logging

logging.basicConfig(format='{levelname:7} {message}', style='{', level=logging.DEBUG)

class WarframeLogParser:
    def __init__(self, log_path, bot):
        self.log_path = log_path
        self.bot = bot

    def clean_username(self, username):
        return username.encode("ascii", "ignore").decode("ascii")

    async def process_line(self, line):
        result = re.search(r'( F)(.*\S)( to index (?:[1-9]|[1-9]\d)$)', line)
        if result is not None:
            username = self.clean_username(result.group(2))
            logging.info(f"Whisper detected from: {username}")
            await self.send_discord_message(username)

    async def send_discord_message(self, username):
        try:
            channel = self.bot.get_channel(905441687566946315)  # Replace with your channel ID
            if channel:
                embed = discord.Embed(
                    title="New Conversation",
                    color=discord.Color.red()  # You can choose any color
                )
                embed.add_field(name="From: ", value=username, inline=False)

                await channel.send(content="<@421895120565043201>", embed=embed) # Replace with your user ID
                logging.info(f"Embed message sent for user: {username}")
            else:
                logging.error(f"Channel not found. ID: {905441687566946315}")
        except Exception as e:
            logging.error(f"Error sending embed message: {str(e)}")

    async def follow_and_parse_log(self):
        with open(self.log_path, 'r', encoding='latin-1') as file:
            file.seek(0, os.SEEK_END)
            while True:  # Run indefinitely
                line = file.readline()
                if line:
                    await self.process_line(line)
                else:
                    await asyncio.sleep(0.1)

class WarframeBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix='!', intents=intents)

    async def setup_hook(self):
        self.bg_task = self.loop.create_task(self.run_log_parser())

    async def run_log_parser(self):
        await self.wait_until_ready()
        appdata_path = '/appdata_warframe'
        log_path = os.path.join(appdata_path, 'EE.log')
        if not os.path.exists(log_path):
            log_path = os.path.join(os.getenv('LOCALAPPDATA'), 'Warframe', 'EE.log')
        logging.debug(log_path)

        parser = WarframeLogParser(log_path, self)
        await parser.follow_and_parse_log()

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')

bot = WarframeBot()

@bot.command()
async def ping(ctx):
    await ctx.send('Pong!')
if __name__ == "__main__":
    bot.run('123')  # Replace with your bot token