import discord
from discord.ext import commands

import requests
import locale
import db

intents = discord.Intents.default();
# intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

TOKEN = 'MTI2NDIzNDE0MjY4NjUxMTM1OQ.GWsGnq.Hc9B7IaDe422AOI9qm7Y-8slUPubfsymSR8mAU'
TORN_URI = 'https://api.torn.com/user' 
ENDPOINT = '?selections=personalstats,profile&key='

# Format API response and return embeded message
def API_response_to_embed(data):
    revivable = "Yes" if data['revivable'] == 1 else "No"

    status_icon = "🟢"
    color = discord.Colour.green()
    if data['last_action']['status'] == "Idle":
        status_icon = "🟡"
        color = discord.Colour.yellow()
    elif data['last_action']['status'] == "Offline":
        status_icon = "🔴"
        color = discord.Colour.red()

    gender = "⚥"
    if data['gender'] == "Male":
        gender = "♂️" 
    elif data['gender'] == "Female":
        gender = "♀️" 

    donator = "⭐" if data['donator'] == 1 else ""

    networth = format_currency(data['personalstats']['networth'])

    employment = f"{data['job']['position']} at {data['job']['company_name']}\n[View Company](https://www.torn.com/joblist.php#/p=corpinfo&userID={id})" if data['job']['position'] != "None" else "Unemployed"

    faction = f"{data['faction']['position']} at {data['faction']['faction_name']} for {data['faction']['days_in_faction']} days\n[View Faction](https://www.torn.com/factions.php?step=profile&userID={id})" if data['faction']['position'] != "None" else "Not in a faction"

    marriage = f"Married to {data['married']['spouse_name']} for {data['married']['duration']} days\n[View Spouse](https://www.torn.com/profiles.php?XID={data['married']['spouse_id']})" if data['married']['spouse_name'] != "None" else "Single"

    embedded = discord.Embed(
        color = color,
        title = f"{data['name']} [{data['player_id']}] {status_icon} {gender} {donator}",
        description = f"Revivable: {revivable}\n\
Role: {data['role']}\n\
Level: {data['level']}, {data['rank']}\n\
Last Action: {data['last_action']['relative']} - {data['last_action']['status']}\n"
    ).add_field(
        name = f"💙 Status: {data['life']['current']}/{data['life']['maximum']}", 
        value = f"{data['status']['state']}"
    ).add_field(
        name = "💼 Employment",
        value = employment
    ).add_field(
        name = "👥 Faction",
        value = faction
    ).add_field(
        name = "❤️ Marriage",
        value = marriage
    ).add_field(
        name = "📊 Social Statistics",
        value = f"Awards: {data['awards']}\n\
Networth: {networth}\n\
Friends: {data['friends']}\n\
Enemies: {data['enemies']}"
                )
    
    return embedded

# Format numbers into currency
def format_currency(amount):
    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
    currency = locale.currency(amount, grouping=True)

    if currency.endswith('.00'):
        currency = currency[:-3]

    return currency

# On load
@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}.')

# Whenever a message is received
@bot.event
async def on_message(message):
    await bot.process_commands(message)

    if message.author == bot.user:
        return
    
    if bot.user.mentioned_in(message):
        parts = message.content.split()
        if len(parts) > 1:
            id = parts[1]

            server_id = str(message.guild.id)
            key = db.get_api_key(server_id)

            if not key:
                await message.channel.send("No Torn API Key set! Please use !setapikey <key>")
                return

            response = requests.get(f'{TORN_URI}/{id}{ENDPOINT}{key}')

            if response.status_code == 200:
                data = response.json()

                embedded = API_response_to_embed(data = data)

                await message.channel.send(embed=embedded)
            else:
                await message.channel.send('Failed to fetch profile from Torn.')
            await message.delete()

# Command to set the API keyBTq9fkKNdkF6BDYI
@commands.command()
@commands.has_permissions(administrator=True)
async def setapikey(ctx, key: str):
    server_id = str(ctx.guild.id)
    db.set_api_key(server_id, key)
    await ctx.send(f'API key set for server {ctx.guild.name}')

@bot.command()
@commands.has_permissions(administrator=True)
async def getapikey(ctx):
    server_id = str(ctx.guild.id)
    key = db.get_api_key(server_id)
    await ctx.send(f'{key}')

bot.add_command(setapikey)

bot.run(TOKEN)