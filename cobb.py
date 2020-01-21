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
                await ctx.send(provide_spell_description(result))
        if no_match_exists:
            await ctx.send('There are multiple results for that. Did you possibly mean any of the following spells:\n' + '\n'.join(spell_names))
    elif extracted_data['count'] == 1:
        await ctx.send(provide_spell_description(extracted_data['results'][0]))
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

@bot.command(name='monster', help='')
async def describe_monster_stats(ctx, *monster_name):
    combined_monster_name = ' '.join(monster_name)
    payload = {'format': 'json', 'search': combined_monster_name}
    url = 'https://api.open5e.com/monsters'
    try:
        response = requests.get(url, params=payload)
        response.raise_for_status()
    except Exception:
        await ctx.send('There was some error in retrieving the information. Please try again later.')
    extracted_data = response.json()
    if extracted_data['count'] > 1:
        no_match_exists = True
        monster_names = []
        for result in extracted_data['results']:
            monster_names.append(result['name'])
            if result['name'] == combined_monster_name.title():
                no_match_exists = False
                await ctx.send(provide_monster_stats(result))
        if no_match_exists:
            await ctx.send('There are multiple results for that. Did you possibly mean any of the following monsters:\n' + '\n'.join(monster_names))
    elif extracted_data['count'] == 1:
        await ctx.send(provide_monster_stats(extracted_data['results'][0]))
    elif extracted_data['count'] == 0:
        await ctx.send('It seems that there is no matching monster for this. You might have misspelled the name. Please try again.')

@bot.command(name='commands', help='Provide a list of all the commands that the bot accepts.')
async def provide_command_list(ctx):
    await ctx.send('Here is a list of all of the commands that you can use:\n!okay\n!smh\n!dank\n!r\n!cast\n!spell\n!commands\nUse !help command name to learn more about a specific command.')

def provide_spell_description(response):
    final_desc = [response['name'], response['desc'], response['range'], response['components'], response['duration'],
                  'Concentration: ' + response['concentration'].capitalize(), response['casting_time'], response['level']]

def provide_monster_stats(response):
    ability_values_format = 'STR: {0}   DEX: {1}   CON: {2}   INT: {3}   WIS: {4}   CHA: {5}'
    ability_values = ability_values_format.format(str(response['strength']), str(response['dexterity']), str(response['constitution']), str(response['intelligence']), str(response['wisdom']), str(response['charisma']))
    final_desc = [response['name'], response['size'] + ' ' + response['type'] + ' ' + response['subtype'], 'HP: ' + str(response['hit_points']) + ' (' + response['hit_dice']+ ')', 'AC: ' + str(response['armor_class'])]
    speed_stats = []
    for type, speed in response['speed'].items():
        speed_stats.append(type + ' ' + str(speed) + ' ft.')
    speed_stats = ', '.join(speed_stats)
    final_desc.extend(['Speed: ' + speed_stats, ability_values])
    saving_throws = []
    if response['strength_save']:
        saving_throws.append('STR +' + str(response['strength_save']))
    if response['dexterity_save']:
        saving_throws.append('DEX +' + str(response['dexterity_save']))
    if response['constitution_save']:
        saving_throws.append('CON +' + str(response['constitution_save']))
    if response['intelligence_save']:
        saving_throws.append('INT +' + str(response['intelligence_save']))
    if response['wisdom_save']:
        saving_throws.append('WIS +' + str(response['wisdom_save']))
    if response['charisma_save']:
        saving_throws.append('CHA +' + str(response['charisma_save']))
    if saving_throws:
        saving_throws = ', '.join(saving_throws)
        final_desc.append('Saving Throws: ' + saving_throws)
    skills = []
    for ability, boost in response['skills'].items():
        skills.append(ability + ' +' + str(boost))
    skills = ', '.join(skills)
    final_desc.append('Skills: ' + skills)
    if response['damage_vulnerabilities'] != "":
        final_desc.append('Damage Vulnerabilities: ' + response['damage_vulnerabilities'])
    if response['damage_resistances'] != "":
        final_desc.append('Damage Resistances: ' + response['damage_resistances'])
    if response['damage_immunities'] != "":
        final_desc.append('Damage Immunities: ' + response['damage_immunities'])
    if response['condition_immunities'] != "":
        final_desc.append('Condition Immunities: ' + response['condition_immunities'])
    final_desc.append('Senses: ' + response['senses'])
    if response['languages'] != "":
        final_desc.append('Languages: ' + response['languages'])
    final_desc.append('Challenge Rating: ' + response['challenge_rating'])
    return '\n'.join(final_desc)

"""Upcoming features:
- Monster blocks
- Allow DMs to track monster health
- Allow DMs to track initiative order?
"""

bot.run(TOKEN)
