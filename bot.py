import asyncio
import os
from datetime import datetime
from dotenv import load_dotenv
import discord
from discord.ext import commands

# Load environment variables
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Create a bot instance
intents = discord.Intents.default()
intents.typing = False
intents.presences = False
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

reminder_threads = {}

# Define a function to set a reminder
async def set_reminder(date, message, author, channel, thread_id):
    now = datetime.now()
    delta = date - now
    seconds = delta.total_seconds()    
    await asyncio.sleep(seconds)
    response = f"Hey {author.mention}, it's time for your reminder: {message}"
    await channel.send(response)
    del reminder_threads[thread_id]

# Define a command to set a reminder
@bot.command(name='reminder')
async def reminder(ctx, *, args):
    try:
        # Split the arguments by space
        args = args.split()
        # Parse the date and time from the first argument
        date_str = ' '.join(args[:2])
        date = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
        # Parse the message from the rest of the arguments
        message = ' '.join(args[2:])
        await ctx.send(f"Reminder set for {date.strftime('%Y-%m-%d %H:%M:%S')} with message: {message}")

        # Create unique thread id
        thread_id = f"{ctx.guild.id}-{ctx.channel.id}-{ctx.author.id}-{date.strftime('%Y-%m-%d %H:%M:%S')-{message}}"

        # Cancel any existing reminder for the same user/channel/guild
        if thread_id in reminder_threads:
            reminder_threads[thread_id].cancel()

         # Start a new reminder thread
        reminder_thread = asyncio.create_task(set_reminder(date, message, ctx.author, ctx.channel, thread_id))
        reminder_threads[thread_id] = reminder_thread
    except ValueError:
        await ctx.send(f"Invalid date format: {date}. Please use the format 'YYYY-MM-DD HH:MM:SS'. Message was {message}")

# Start the bot
bot.run(TOKEN)
