import os
import random
import discord
import requests
import requests_cache
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
bot = commands.Bot(command_prefix='!')
requests_cache.install_cache('dnd_cache')

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

@bot.command(name='okay', help='Properly cites okay to mango.')
async def cite_okay(ctx):
    await ctx.send("-mango")

@bot.command(name='smh', help='Properly cites smh to nap.')
async def cite_smh(ctx):
    await ctx.send("-nap")

@bot.command(name='dank', help='Properly cites dank to dm.')
async def cite_dank(ctx):
    await ctx.send("-dm")

@bot.command(name='r', help='Rolls a specified number of dice with a specified number of sides.')
async def roll_dice(ctx, num_dice: int, num_sides: int):
    rolls = random.choices(range(1, num_sides + 1), k=num_dice)
    total = sum(rolls)
    rolls = [str(roll) for roll in rolls]
    await ctx.send(' '.join(rolls) + '\nTotal: ' + str(total))

@bot.command(name='cast', help='Provides information about a specified spell.')
async def describe_spell(ctx, *spell_name):
    combined_spell_name = ' '.join(spell_name)
    payload = {'format': 'json', 'search': combined_spell_name}
    url = 'https://api.open5e.com/spells'
    try:
        response = requests.get(url, params=payload)
        response.raise_for_status()
    except Exception:
        await ctx.send('There was some error in retrieving the information. Please try again later.')
    extracted_data = response.json()
    if extracted_data['count'] > 1:
        no_match_exists = True
        spell_names = []
        for result in extracted_data['results']:
            spell_names.append(result['name'])
            if result['name'] == combined_spell_name.title():
                no_match_exists = False
                await ctx.send(provide_spell_info(result))
        if no_match_exists:
            await ctx.send('There are multiple results for that. Did you possibly mean any of the following spells:\n' + '\n'.join(spell_names))
    elif extracted_data['count'] == 1:
        await ctx.send(provide_spell_info(extracted_data['results'][0]))
    elif extracted_data['count'] == 0:
        await ctx.send('It seems that there is no matching spell for this. You might have misspelled the name. Please try again.')

@bot.command(name='spell', help='Provides all spells of a specified level and specified class.')
async def output_list_of_spells(ctx, level: int, dnd_class):
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
        level_endings = {'1': 'st', '2': 'nd', '3': 'rd'}
        for result in results:
            spell_names.append(result['name'])
        await ctx.send('Here is a list of all ' + str(level) + level_endings.get(str(level), 'th') + ' level ' + dnd_class.capitalize() + ' spells:\n' + '\n'.join(spell_names))
    elif extracted_data['count'] == 0:
        await ctx.send('It seems that there are no matching spells for this. Please try again.')

def provide_spell_info(spell_response):
    final_desc = [spell_response['name'], spell_response['desc'], spell_response['range'], spell_response['components'], spell_response['duration'],
                  'Concentration: ' + spell_response['concentration'].capitalize(), spell_response['casting_time'], spell_response['level']]
    return '\n'.join(final_desc)

bot.run(TOKEN)
