import os
from StatsDB import StatsDB
from IScraper import IScraper
import discord
import render
from ids import series_short_hands

scraper = IScraper()
client = discord.Client()
db = StatsDB('stats.db')


def resolve_shorthand(text):
    if not text.isnumeric():
        if text not in series_short_hands.keys():
            return False, f'Series shorthand {text} not recognized. You can add it with "_shorthand {text} <series_id>".'

        return True, series_short_hands[text]
    return True, text


def register_driver(message):
    parts = message.content.split(maxsplit=2)

    if len(parts) != 3:
        return False, 'Invalid command, try "_register me Max Mustermann"'
    _, discord_id, iracing_name = parts

    if discord_id == 'me':
        discord_id = message.author.id

    db.add_driver(iracing_name, discord_id)
    return f'Registered driver {iracing_name}.'


def lastrace(message):
    result = db.lookup_driver(message.author.id)

    if len(result) != 1:
        return 'You are currently not registered as a driver, by typing "_register me <Your iRacing display name>".'

    driver = result[0]
    race_info = scraper.get_driver_recent_races(driver)
    subsession_info = scraper.get_subsession_details(race_info[0]['subsession_id'])

    image = render.last_race(race_info, subsession_info)

    return 'Done.'


def strength_of_field(message):
    parts = message.content.split(maxsplit=1)

    if len(parts) != 2:
        return False, 'Invalid command, try "_sof lmp2"'

    season_id = parts[1]

    if not season_id.isnumeric():
        if season_id not in series_short_hands.keys():
            return False, f'Series shorthand {season_id} not recognized. You can add it with "_shorthand {season_id} <series_id>".'

        season_id = series_short_hands[season_id]

    season_details = scraper.get_season_details(season_id)

    return True, render.participation(season_details)


def participation_or_sof(message, p_or_s):
    parts = message.content.split(maxsplit=1)

    if len(parts) != 2:
        if p_or_s == 'p':
            return False, 'Invalid command, try "_participation lmp2"'
        else:
            return False, 'Invalid command, try "_sof lmp2"'

    success, response = resolve_shorthand(parts[1])
    if not success:
        return False, response

    season_id = response

    season_details = scraper.get_season_details(season_id)

    # get car info for series


    # get series info to lookup name
    meta_info = scraper.get_series_meta()
    series_name = [x['season_name'] for x in meta_info if x['season_id'] == season_id][0]

    return True, render.participation_or_sof(season_details, p_or_s, series_name)


def schedule(message):
    parts = message.content.split(maxsplit=1)
    if len(parts) != 2:
        return False, 'Invalid command, try "_schedule lmp2"'

    success, response = resolve_shorthand(parts[1])
    if not success:
        return False, response

    season_id = response

    # get series info
    meta_info = scraper.get_series_meta()

    # get schedule for series
    schedules = [x['schedules'] for x in meta_info if x['season_id'] == season_id][0]

    return render.schedule(schedules)


def bop(message):
    parts = message.content.split(maxsplit=1)

    if len(parts) != 2:
        return False, 'Invalid command, try "_bop lmp2"'

    season_id = parts[1]

    success, response = resolve_shorthand(parts[1])
    if not success:
        return False, response

    season_id = response

    season_details = scraper.get_season_details(season_id)
    return ''


def series(message):
    parts = message.content.split()
    if len(parts) != 2 or parts[1] not in ('oval', 'road', 'dirt_oval', 'dirt_road'):
        return "No valid category specified, must be one of: 'oval', 'road', 'dirt_oval', 'dirt_road'"

    meta_info = scraper.get_series_meta()
    series = [x['season_name'] for x in meta_info if x['track_types'][0]['track_type'] == parts[1]]

    ret = f'Series for type "{parts[1]}":\n'
    for s in sorted(series):
        ret += f' - {s}\n'

    return ret


@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content == '_hi':
        response = 'Hi, I am the iRacing stats bot'
        await message.channel.send(response)

    if message.content.startswith('_series'):
        await message.channel.send(series(message))

    if message.content.startswith('_register'):
        await message.channel.send(register_driver(message))

    if message.content == '_lastrace':
        await message.channel.send(lastrace(message))

    if message.content.startswith('_participation'):
        success, response = participation_or_sof(message, 'p')
        if success:
            await message.channel.send(file=discord.File(response))
        else:
            await message.channel.send(response)

    if message.content.startswith('_sof'):
        success, response = participation_or_sof(message, 's')
        if success:
            await message.channel.send(file=discord.File(response))
        else:
            await message.channel.send(response)

    if message.content.startswith('_bop'):
        await message.channel.send(bop(message))

    if message.content.startswith('_schedule'):
        await message.channel.send(schedule(message))

    if message.content == '_help':
        answer = """
            Register drivers with '_register me <iracing name>' or '_register <discord id> <iracing name>.
            Get Series participation with '_participation <series name>'.
            Get info on your latest race with '_lastrace'
            Currently tracked series:
              - lmp2
        """

        await message.channel.send(answer)

client.run(os.environ['TOKEN'])

