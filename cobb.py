# cobb.py
import os
import random
import discord
import requests
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
bot = commands.Bot(command_prefix='!')

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

@bot.command(name='okay', help='Properly quotes okay to mango.')
async def mango(ctx):
    await ctx.send("-mango")

@bot.command(name='smh', help='Properly quotes smh to nap.')
async def mango(ctx):
    await ctx.send("-nap")

@bot.command(name='dank', help='Properly quotes dank to dm.')
async def mango(ctx):
    await ctx.send("-dm")

@bot.command(name='r', help="Roll some nice dice.")
async def roll_dice(ctx, num_dice: int, num_sides: int):
    rolls = random.choices(range(1, num_sides + 1), k=num_dice)
    total = sum(rolls)
    rolls = [str(roll) for roll in rolls]
    await ctx.send(' '.join(rolls) + '\nTotal: ' + str(total))

@bot.command(name='cast', help='Provide information about a certain spell.\nUsage: !cast name of spell')
async def describe_spell(ctx, *args):
    # More research on caching results from APIs to improve performance (requests-cache)
    payload = {'format': 'json', 'search': ' '.join(args)}
    url = 'https://api.open5e.com/spells'
    try:
        response = requests.get(url, params=payload)
        response.raise_for_status()
    except Exception:
        await ctx.send("There was some error in retrieving the information. Please try again later.")
    extracted_data = response.json()
    if extracted_data['count'] > 1:
        results = extracted_data['results']
        spell_names = []
        for result in results:
            spell_names.append(result['name'])
        await ctx.send('There are multiple results for that. Did you possibly mean any of the following spells:\n' + '\n'.join(spell_names))
    elif extracted_data['count'] == 1:
        spell_data = extracted_data['results'][0]
        final_desc = []
        final_desc.append(spell_data['name'])
        final_desc.append(spell_data['desc'])
        final_desc.append(spell_data['range'])
        final_desc.append(spell_data['components'])
        final_desc.append(spell_data['duration'])
        final_desc.append('Concentration: ' + spell_data['concentration'].capitalize())
        final_desc.append(spell_data['casting_time'])
        final_desc.append(spell_data['level'])
        await ctx.send('\n'.join(final_desc))
    elif extracted_data['count'] == 0:
        await ctx.send('It seems that there is no matching spell for this. Please try again.')

"""Implement a feature where you can provide a list of spell names that meet certain
    specifications. For example, provide a list of all 1st level spells.

    Classify according to level and class (1st level cleric spells)"""
@bot.command(name='spell', help='Provide all spells of a specified level and belonging to a specified class.\nUsage: !spell 1 cleric')
async def output_list_of_spells(ctx, level: int, dnd_class):
    # TODO: More research on caching results from APIs to improve performance (requests-cache)
    payload = {'format': 'json', 'level_int': level, 'dnd_class__icontains': dnd_class.capitalize()}
    url = 'https://api.open5e.com/spells'
    try:
        response = requests.get(url, params=payload)
        response.raise_for_status()
    except Exception:
        await ctx.send("There was some error in retrieving the information. Please try again later.")
    extracted_data = response.json()
    if extracted_data['count'] > 1:
        results = extracted_data['results']
        spell_names = []
        for result in results:
            spell_names.append(result['name'])
            # TODO: Modify string to give correct output
        await ctx.send('Here is a list of all ' + str(level) + ' level ' + dnd_class.capitalize() + ' spells:\n' + '\n'.join(spell_names))
    elif extracted_data['count'] == 0:
        await ctx.send('It seems that there are no matching spells for this. Please try again.')

"""Upcoming features:
- Monster blocks
- Allow DMs to track monster health
- Allow DMs to track initiative order?
"""
bot.run(TOKEN)
