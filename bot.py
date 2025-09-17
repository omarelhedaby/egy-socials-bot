import discord
import random
from discord.ext import commands, tasks
import datetime
import pytz

import os

# load_dotenv()  # loads variables from .env file


TOKEN = os.getenv("DISCORD_BOT_TOKEN")
if not TOKEN:
    raise ValueError("DISCORD_BOT_TOKEN not set!")

# Minimal intents
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="/", intents=intents)

ACTIVITIES = [
    "Meet in a cafe ☕",
    "Go for a walk 🚶‍♂️",
    "Visit a park 🌳",
    "Bowling 🎳",
    "Mini golf ⛳",
    "Board games 🎲",
    "Watch a movie 🎬",
    "Go to a museum 🏛️",
    "Ice cream outing 🍦",
    "Coffee & chat ☕💬",
    "Go eat something 🍽️",
    "Cinema 🎥",
    "Karaoke night 🎤",
    "Escape room 🔐",
    "Picnic in the park 🧺",
    "Visit a local market 🛍️",
]

# Dictionary of German city -> channel_id
city_channels = {
    "mannheim-heidelberg": 1417955923254710465,
    "hamburg": 1417956263362302022,
    "munich": 1417956078951333958,
    "cologne": 1417955942493851728,
    "frankfurt": 1417648525759479818,
    "stuttgart": 1417956401787179029,
    "dusseldorf": 1417955964551823421,
    "dortmund": 1417962922105110568,
    "essen": 1417955987024773190,
    "leipzig": 1417963019199053865,
    "freiburg": 1417956614606033086,
    "erfurt" : 1417956590614482995,
    "wiesbaden-mainz" : 1417956562353262623,
    "wurzburg" : 1417956502333030574,
    "thuringen" : 1417956452064165908,
    "bremen" : 1417956370581295225,
    "koblenz" : 1417956336838381690,
    "niedersachsen" : 1417956297965437199,
    "bonn" : 1417956058214961304,
    "duisburg" : 1417956009003057182
}

announcement_channel_id = 1417617923228307612
concerts_across_germany = 1417955767029469194
bot_test_channnel_id = 1417958275550412901

def pick_random_activities(n=3):
    return random.sample(ACTIVITIES, n)

@bot.event
async def on_ready():
    print(f"Bot is ready! Logged in as {bot.user}")
    weekly_task.start()
    
@bot.event
async def on_member_join(member):
    # Get the welcome channel
    channel = discord.utils.get(member.guild.text_channels, name="Welcome to EgyptianGermanySocials")  # change to your actual channel
    if channel:
        await channel.send(
            f"👋 Hi {member.mention}, welcome to **EgyptiansGermanyCommunity**! 🎉\n\n"
            "Make sure to check out the channel related to your city to connect with locals 🏙️.\n"
            "Say hi to **3AM Mohamed, our trusty Bawab bot** 🤖\n\n"
            "Also, don’t miss our voice channels for:\n"
            "- 💬 **Dardasha & Questions** – chat with the community in real-time\n"
            "- 🎓 **Careers** – share and get advice about work opportunities\n"
            "- 📢 **Announcements** – stay updated with community news\n"
            "- 🎶 **Concerts Around Germany** – keep track of events and gigs!\n\n"
            "Have fun and enjoy your stay! 🚀"
        )

    # Send a friendly DM
    try:
        await member.send(
            f"Hi {member.name}! Welcome to **EgyptiansGermanyCommunity** 🎉\n\n"
            "Check out your city channel, say hi to 3AM Mohamed the Bawab bot 🤖, "
            "and explore our voice channels for dardasha, careers, announcements, and concerts around Germany! 🎶\n\n"
            "Enjoy connecting with fellow Egyptians across Germany!"
        )
    except discord.Forbidden:
        print(f"Couldn't send DM to {member.name}")
        
@bot.event
async def on_reaction_add(reaction, user):
    # Ignore bot reactions
    if user.bot:
        return

    # Check if the reaction is on a Monday poll message
    if reaction.message.author == bot.user:
        if reaction.emoji == "🛠️":  # Organizer
            channel = reaction.message.channel  # This is the channel where the reaction happened
            await channel.send(
                f"🎉 {user.mention} is volunteering to be an **organizer** for this week! Thank you! 🛠️"
            )
            
             # Assign "Organizer" role
            role = discord.utils.get(user.guild.roles, name="Organizer")
            if role:
                await user.add_roles(role)

# --- Core reusable functions ---
async def send_announcement(channels, message, title=None):
    """Send an announcement to a list of channel objects or IDs."""
    for ch in channels:
        if isinstance(ch, int):
            ch = bot.get_channel(ch)
        if ch:
            t = title if title else "Announcement"
            await ch.send(f"📢 **{t}**\n{message}")

async def weekly_event_poll(channel_ids):
    """Send the Monday meetup poll to a list of channel IDs."""
    for ch_id in channel_ids:
        channel = bot.get_channel(ch_id)
        if channel:
            message = (
                "👋 Happy Monday everyone! Hope you had a great weekend.\n"
                "Who wants to **organize** this week's meetup, and who just wants to **join**?\n\n"
                "React below:\n"
                "🛠️ Organizer\n"
                "✅ Join"
            )
            poll_message = await channel.send(message)
            await poll_message.add_reaction("🛠️")
            await poll_message.add_reaction("✅")
            
async def fun_activity_poll(channel_ids):
    """
    Sends a poll with 3 random activities + 'Other' option to all specified channels.
    Users can vote via reactions.
    """
    for ch_id in channel_ids:
        channel = bot.get_channel(ch_id)
        if channel:
            choices = pick_random_activities()
            choices.append("Other ❓")  # Add the fourth option

            emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣"]
            description = "\n".join(f"{emojis[i]} {choices[i]}" for i in range(4))

            poll_message = await channel.send(
                f"🎉 Here’s a **fun poll** to give you some ideas for next weekend:\n{description}\nReact with your favorite!"
            )

            for i in range(4):
                await poll_message.add_reaction(emojis[i])

                
                
# --- Scheduled task ---
@tasks.loop(hours=24)
async def weekly_task():
    tz = pytz.timezone("Europe/Berlin")
    now = datetime.datetime.now(tz)

    # Run only on Monday at 13:00 
    if now.weekday() == 0 and now.hour == 13 and now.minute == 0:
        await weekly_event_poll(city_channels.values())
        await fun_activity_poll(city_channels.values())
        
    # Thursday at 18:00 → reminder/announcement
    if now.weekday() == 3 and now.hour == 18 and now.minute == 0:
        message = '''📢 Hope you guys organized the event and will have a great time! 🎉\n" 
                    "Don’t forget to share photos in **#photos** 📸\n" 
                    "Have a fantastic weekend ahead! 🌟'''
        await send_announcement(city_channels.values(), message)
    # --- Friday at 16:00 → Happy Friday message in announcement channel ---
    if now.weekday() == 4 and now.hour == 16 and now.minute == 0:
        message = (
            "🎉 Happy Friday everyone! 🌞\n"
            "Hope you had a great week and enjoy your weekend!\n"
            "Don’t forget to play some games online on **#games**"
        )
        await send_announcement(announcement_channel_id, message)
        
# --- Auto Moderation ---
BAD_WORDS = ["a7a", "kosom", "metnak", "zeby","manyak","m3rs","a7eh","sharmoot","5awal"]
@bot.event
async def on_message(message):
    if message.author.bot:
        return
    if any(word == message.content.lower() for word in BAD_WORDS):
        await message.delete()
        await message.channel.send(f"⚠️ {message.author.mention}, watch your language!", delete_after=5)
    await bot.process_commands(message)


# --- Commands ---
@bot.command()
async def announce(ctx, *, message: str):
    """Send announcement to all Announcement channel"""
    await send_announcement(announcement_channel_id, message)
    await ctx.send("✅ Announcement sent to accouncement channel")
    
@bot.command()
async def announce_cities(ctx, *, message: str):
    """Send announcement to all Germany channels"""
    await send_announcement(city_channels.values(), message)
    await ctx.send("✅ Announcement sent to Germany")
    
@bot.command()
async def announce_test(ctx, *, message: str):
    """Send announcement to all test channels"""
    await send_announcement([bot_test_channnel_id], message)
    await ctx.send("✅ Announcement sent to test")
    
@bot.command()
@commands.has_permissions(manage_messages=True)  # Only allow moderators
async def clear_all(ctx, amount: int = 100):
    """
    Clears messages in all German city channels.
    - amount: number of messages to delete per channel (default 100)
    """
    for city, ch_id in city_channels.items():
        channel = bot.get_channel(ch_id)
        if channel:
            deleted = await channel.purge(limit=amount)
            await ctx.send(f"🧹 Cleared {len(deleted)} messages in {city.title()}!", delete_after=5)

    
# --- Manual command to trigger Monday polls ---
@bot.command()
async def monday_poll(ctx):
    await weekly_event_poll(city_channels.values())
    await fun_activity_poll(city_channels.values())
    await ctx.send("✅ Monday polls sent!")
    
bot.run(TOKEN)
