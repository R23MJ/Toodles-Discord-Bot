import discord
from discord.ext import commands

import requests
import cache
import locale
import db
import re

intents = discord.Intents.default();
# intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

TOKEN = 'MTI2NDIzNDE0MjY4NjUxMTM1OQ.GWsGnq.Hc9B7IaDe422AOI9qm7Y-8slUPubfsymSR8mAU'
TORN_URI = 'https://api.torn.com/user'
YATA_URI = 'https://yata.yt/api/v1/bs'
TORN_ENDPOINT = '?selections=personalstats,profile&stat=networth&key='
YATA_ENDPOINT = '?key='

# Add battle estimates from YATA
def add_bs_estimate(embedded: discord.Embed, yata_json, id):
    embedded.insert_field_at(0,
        name = "(ง⩺.⩹)ง Battle Stats",
        value = f'''{yata_json[id]["total"]:,} estimated total
{yata_json[id]["score"]:,} score
{yata_json[id]["type"]} build
{yata_json[id]["skewness"]}% skewed
        '''
    )

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

    employment = f"{data['job']['position']} at {data['job']['company_name']}\n[View Company](https://www.torn.com/joblist.php#/p=corpinfo&userID={data['player_id']})" if data['job']['position'] != "None" else "Unemployed"

    faction = f"{data['faction']['position']} at {data['faction']['faction_name']} for {data['faction']['days_in_faction']} days\n[View Faction](https://www.torn.com/factions.php?step=profile&userID={data['player_id']})" if data['faction']['position'] != "None" else "Not in a faction"

    marriage = f"Married to {data['married']['spouse_name']} for {data['married']['duration']} days\n[View Spouse](https://www.torn.com/profiles.php?XID={data['married']['spouse_id']})" if data['married']['spouse_name'] != "None" else "Single"

    profile_link = f"[Profile](https://www.torn.com/profiles.php?XID={data['player_id']})"
    attack_link = f"[Attack](https://www.torn.com/loader.php?sid=attack&user2ID={data['player_id']})"
    bounty_link = f"[Bounty](https://www.torn.com/bounties.php?p=add&XID={data['player_id']})"
    bazaar_link = f"[Bazaar](https://www.torn.com/bazaar.php?userId={data['player_id']})"
    display_link = f"[Display Case](https://www.torn.com/displaycase.php#display/{data['player_id']})"
    trade_link = f"[Start Trade](https://www.torn.com/trade.php#step=start&userID={data['player_id']})"

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
    ).add_field(
        name = "🔗 Links",
        value = f"{profile_link} | {attack_link} | {bounty_link} | {bazaar_link} | {display_link} | {trade_link}"
    )
    
    return embedded

def getTornId(display_name : str):
    match = re.search(r'\[(\d+)\]', display_name)
    if not match:
        return None
    
    return match.group(1)

# helper function to check if a string is a number
def is_integer(s: str):
    try:
        int(s)
        return True
    except ValueError:
        return False

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
    
    if '@everyone' in message.content:
        return
    
    if bot.user.mentioned_in(message):
        parts = message.content.split()
        if len(parts) == 2:
            id = parts[1]

            if (not is_integer(id)):
                return

            forced = False
            if len(parts) > 2:
                flag = parts[2]

                if flag == "--force":
                    forced = True

            server_id = str(message.guild.id)
            key = db.get_api_key(server_id)

            if not key:
                await message.channel.send("No Torn API Key set! Please use !setapikey <key>")
                return
        
            data = cache.fetch_api_data(f'{TORN_URI}/{id}{TORN_ENDPOINT}{key}', id, forced)
            yata_response = requests.get(f'{YATA_URI}/{id}/{YATA_ENDPOINT}{key}')

            if data:
                embedded = API_response_to_embed(data = data)

                if yata_response:
                    add_bs_estimate(embedded, yata_json = yata_response.json(), id=id)

                await message.channel.send(embed = embedded)
            else:
                await message.channel.send('Failed to fetch profile from Torn.')
            
            await message.delete()

@bot.slash_command(name="banker", guild_ids=[1183384620440494120])
async def banker_command(ctx, amount, offline_ok : bool = False):
    banker_role_id = 1269676070928519332
    role = ctx.guild.get_role(banker_role_id)

    torn_id = getTornId(ctx.author.display_name)
    if not isinstance(torn_id, str):
        await ctx.respond(f"Could not find Torn ID in your display name.", ephemeral=True)
        return

    embed = discord.Embed(
        title="Pay Request",
        description=(
            f"{role.mention} {ctx.author.display_name} has requested ${amount:,.0f} moneys!\n"
            f"[Pay Them!](https://www.torn.com/factions.php?step=your#/tab=controls&giveMoneyTo={torn_id}&money={amount})\n"
            f"Okay To Send If Online? -> {offline_ok}"
        )
    )

    await ctx.respond(embed=embed)

# Command to set the API key
@bot.command()
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

bot.run(TOKEN)