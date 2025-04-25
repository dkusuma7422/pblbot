import discord
from discord.ext import commands
import os
import json
from dotenv import load_dotenv
from flask import Flask
import threading
from pymongo import MongoClient

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run_flask():
    app.run(host="0.0.0.0", port=8080)

# Run Flask in a separate thread
threading.Thread(target=run_flask, daemon=True).start()

# Get MongoDB URI from the environment variable
mongo_uri = os.getenv("MONGODB_URI")

# Connect to MongoDB
client = MongoClient(mongo_uri)
db = client.get_database()  # Gets the database set in the connection string

# Example collection
collection = db["bot_data"]

# Example of storing some data
collection.insert_one({"user_id": 12345, "status": "active"})

# Example of retrieving data
user_data = collection.find_one({"user_id": 12345})
print(user_data)

y=0

# Set up the bot
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Event: When the bot is ready
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

# Command: Respond to a greeting
@bot.command()
async def hello(ctx):
    await ctx.send(f"Hello, {ctx.author.name}!")

@bot.command()
async def whatsgoodtrigga(ctx):
    await ctx.send(f"What's good my trigga {ctx.author.name}.")

file_name_map = {
    "mmg": {"file": "rmmg.json", "tag": "MMG"},
    "ses": {"file": "rses.json", "tag": "SES"},
    "atl": {"file": "ratl.json", "tag": "ATL"},
    "lal": {"file": "rlal.json", "tag": "LAL"},
    "chc": {"file": "rchc.json", "tag": "CHC"},
    "lvl": {"file": "rlvl.json", "tag": "LVL"},
    "wsh": {"file": "rwsh.json", "tag": "WSH"},
    "bax": {"file": "rbax.json", "tag": "BAX"},
    "void": {"file": "rvoid.json", "tag": "VOID"}
    }

# Helper function to load data
def load_data(file_name):
    try:
        with open(file_name, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []  # Return an empty list if the file doesn't exist

# Helper function to save data
def save_data(data, file_name):
    with open(file_name, "a") as file:
        json.dump(data, file, indent=1)

def clear_file(file_name):
    with open(file_name, "w") as file:
        # Just open in "w" mode; it will clear the file automatically
        pass

@bot.command()
async def add(ctx, type_of_data: str = None, *, info: str = None):
    # Get the data type mapping from the file_name_map
    data_map = file_name_map.get(type_of_data.lower())

    if data_map is None or info is None:
        await ctx.send("Missing team abbreviation. Can't process request.")
        return

    # Load the existing data from the specified file
    data = load_data(data_map["file"])

    if any(entry["info"] == info for entry in data):
        await ctx.send(f"{data_map['tag']} already has this mon.")
        return
    
    # Enforcing the 9 mon maximum
    elif len(data) >= 9:
        await ctx.send(f"{data_map['tag']} already has 9 mons. Please drop a mon before adding a new one.")
        return
    
    clear_file(data_map["file"])

    # Append the new info to the list
    data.append({"kills": 0, "info": info})
    
    # Save the updated data back to the file
    save_data(data, data_map["file"])

    # Send the confirmation message using the mapped template
    await ctx.send(f"{data_map['tag']} Roster Updated")

@bot.command()
async def draft(ctx, type_of_data: str = None, *, info: str = None):
    # Get the data type mapping from the file_name_map
    data_map = file_name_map.get(type_of_data.lower())

    if data_map is None or info is None:
        await ctx.send("Missing team abbreviation. Can't process request.")
        return

    # Load the existing data from the specified file
    data = load_data(data_map["file"])

    if any(entry["info"] == info for entry in data):
        await ctx.send(f"{data_map['tag']} already has this mon.")
        return
    
    # Enforcing the 9 mon maximum
    elif len(data) >= 9:
        await ctx.send(f"{data_map['tag']} already has 9 mons. Please drop a mon before adding a new one.")
        return
    
    clear_file(data_map["file"])

    # Append the new info to the list
    data.append({"kills": 0, "info": info})
    
    # Save the updated data back to the file
    save_data(data, data_map["file"])

    # Send the confirmation message using the mapped template
    await ctx.send(f"With the {y%8}th/rd pick in the {y-y%8}th/rd round of the Season 4 PBL draft {data_map['tag']} has selected {info}.")
    
    return

@bot.command()
async def drop(ctx, type_of_data: str = None, *, info: str = None):
    # Get the data type mapping from the file_name_map
    data_map = file_name_map.get(type_of_data.lower())

    if data_map is None or type_of_data is None or info is None:
        await ctx.send("Missing team abbreviation. Can't process request.")
        return
    
    # Load the existing data from the specified file
    data = load_data(data_map["file"])

    entry_to_remove = None

    for entry in data:
        if entry["info"] == info:
            entry_to_remove = entry
            break
    
    if entry_to_remove is None:
        await ctx.send(f"{data_map['tag']} does not have this mon.")
    else:
        data.remove(entry)
        clear_file(data_map["file"])
        save_data(data, data_map["file"])
        await ctx.send(f"{data_map['tag']} Roster Updated")    

    return
    
@bot.command()
async def addkills(ctx, type_of_data: str = None, *, info: str = None):
    
    data_map = file_name_map.get(type_of_data.lower())

    parts = info.split()
    if len(parts) != 2:
        await ctx.send("Missing info. Can't process")
        return
    
    info = parts[0]
    kills = int(parts[1])

    if data_map is None or info is None:
        await ctx.send("Missing team abbreviation. Can't process request.")
        return
    
    data = load_data(data_map["file"])
    
    for entry in data:
        if entry["info"] == info:
            if kills == 0:
                await ctx.send(f"No kills added.")
                return
            else:
                entry["kills"] += kills
                clear_file(data_map["file"])
                sorted_data = sorted(data, key=lambda entry: entry.get("kills", 0), reverse=True)
                save_data(sorted_data, data_map["file"])  # Save the updated data after modifying it
                await ctx.send(f"{entry['info']}'s kills were updated.")
                return  # Exit after updating

# If we reach here, it means the entry wasn't found
    await ctx.send(f"{data_map['tag']} does not have this mon.")
    return

@bot.command()
async def kills(ctx, type_of_data: str = None, *, info: str = None):

    data_map = file_name_map.get(type_of_data.lower())

    if data_map is None or info is None:
        await ctx.send("Missing team abbreviation. Can't process request.")
        return
    
    data = load_data(data_map["file"])

    for entry in data:
        if entry["info"] == info:
            await ctx.send(f"{entry['info']} has {entry['kills']} kills.")
            return

    await ctx.send(f"{data_map['tag']} does not have this mon.")
    return

@bot.command()
async def teamkills(ctx, type_of_data: str = None):

    data_map = file_name_map.get(type_of_data.lower())

    if data_map is None:
        await ctx.send("Missing team abbreviation. Can't process request.")
        return
    
    data = load_data(data_map["file"])

    output = 0

    for entry in data:
        output += entry['kills']
    
    await ctx.send(f"{data_map['tag']} has {output} kills.")

@bot.command()
async def roster(ctx, type_of_data: str = None):
    # Get the data type mapping from the file_name_map
    data_map = file_name_map.get(type_of_data.lower())

    if data_map is None:
        await ctx.send("Missing team abbreviation. Can't process request.")
        return

    # Load the data from the specified file
    data = load_data(data_map["file"])
    
    output = f"{data_map['tag']} Roster:"
    # Send the message using the mapped template
    for entry in data:
        output += f"\n{entry['info']} ({entry['kills']})"
    await ctx.send(output)

# Run the bot
load_dotenv()  # Load variables from .env file

TOKEN = os.getenv("DISCORD_TOKEN")

print("Token Loaded Successfully!" if TOKEN else "Failed to Load Token.")

bot.run(TOKEN)