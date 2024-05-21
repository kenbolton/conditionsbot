#!/usr/bin/env python3

# This example requires the 'members' and 'message_content' privileged intents to function.

import os
import re
import discord
import requests
import random
import pandas as pd

from datetime import date, timedelta

from discord.ext import commands

from dotenv import load_dotenv

from io import StringIO

from stations import STATIONS


"""
sudo pm2 start "/home/ubuntu/conditionsbot/bin/python /home/ubuntu/conditionsbot/bot.py" --name "conditionsbot"
sudo pm2 restart conditionsbot
"""

load_dotenv()

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

description = ''' A bot that grabs data from various sources to populate discord
with important information for small boats.

Built by Hudson River Expeditions & klb
'''

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='?', description=description, intents=intents)


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')


@bot.command()
async def locations(ctx, location: str=0):
    """ List locations and their available data """
    def _make_msg(station, msg):
        msg += "{}:\n".format(station['name'])
        try:
            _ = station['weather']
        except KeyError:
            pass
        else:
            msg += "- Weather\n"
        try:
            _ = station['currents']
        except KeyError:
            pass
        else:
            msg += "- Currents\n"
        try:
            _ = station['tides']
        except KeyError:
            pass
        else:
            msg += "- Tides\n"
        try:
            _ = station['water']
        except KeyError:
            pass
        else:
            msg += "- Water temperature\n"
        return msg
    msg = ""
    if not location:
        stations = STATIONS
    else:
        try:
            station = STATIONS[location.lower()]
        except KeyError:
            await ctx.send(
                "`{}` is not a valid station. Try one of these:\n{}".format(
                    location, ''.join(
                        '\t`{}`\n'.format(n)
                        for n in STATIONS.keys()
                        if 'water' in STATIONS[n].keys())))
            return
        else:
            await ctx.send(_make_msg(station, msg))
    for key, station in stations.items():
        msg = _make_msg(station, msg)
        await ctx.send(msg)


@bot.command()
async def all(ctx, location: str=None):
    """ Show all of the available data for a location """
    await water(ctx, location=location)
    await alerts(ctx, location=location)
    await forecast(ctx, location=location)
    await tides(ctx, location=location)
    await currents(ctx, location=location)


@bot.command()
async def _water(ctx, location: str=0):
    """ Display the water tempareture for a location. """
    if not location:
        location = ctx.channel.name
    try:
        station_id = STATIONS[location.lower()]['water']
    except KeyError:
        await ctx.send(
            "`{}` is not a valid water temperature station. Try one of these:\n{}".format(
                location, ''.join(
                    '\t`{}`\n'.format(n)
                    for n in STATIONS.keys()
                    if 'water' in STATIONS[n].keys())))
        return
    url = "https://waterservices.usgs.gov/nwis/iv/"
    params = {
        "sites": station_id,
        "agencyCd": "USGS",
        "parameterCd": "00010",
        "period": "P1D",
        "siteStatus": "all",
        "format": "json",
    }
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    site_name = resp.json()['value']['timeSeries'][0]['sourceInfo']['siteName']
    temp_c = resp.json()['value']['timeSeries'][0]['values'][-1]['value'][-1]['value']
    time = resp.json()['value']['timeSeries'][0]['values'][-1]['value'][-1]['dateTime']
    temp_f = float(temp_c) * (9/5) + 32
    return site_name, time, temp_f, temp_c


@bot.command()
async def water(ctx, location: str=0):
    site_name, time, temp_f, temp_c = await _water(ctx, location=location)
    msg = "{}\n{}\n{}°F / {}°C".format(site_name, time, temp_f, temp_c)
    await ctx.send(msg)


@bot.command()
async def current(ctx, location: str=None):
    df = await _currents(ctx, location=location)
    text_string = df.to_string()
    for row in text_string.split('\n'):
        await ctx.send(row)
    # for index, row in df.iterrows():
    #     print(row)
    #     await ctx.send(row)


@bot.command()
async def now(ctx, location: str=None):
    """ Pin an alert for the location that combines a bunch of data points. """
    # alerts
    # forecast: analyze air + water temp, alert if winds over ten, high alert over 15
    # currents
    # tides
    alerts = await _alerts(ctx, location=location)
    site_name, time, temp_f, temp_c = await _water(ctx, location=location)
    forecast = await _forecast(ctx, location=location)
    period = forecast.json()['properties']['periods'][0]
    wind_speed = period["windSpeed"].split(' ')[0]  # [1] = "mph"
    wind_direction = period['windDirection']
    msg = 'Wind is up at {} mph from the {}'.format(wind_speed, wind_direction)
    if wind_speed > 10:
        """ this is the good stuff if the currents are right """
        pass
    air_temp = period['temperature']
    if air_temp + temp_f < 120:
        msg = (
            " + + + + Warning! Cold water temps!! + + + +\n\n"
            "With the air temperature at {}°F the risk of hypothermia is real.\n"
            "Dress for immersion!\n"
            "\n{}\n{}\n{}°F / {}°C\n"
            "\n + + + + Cold water temps!! Warning! + + + + ".format(
                site_name, time, temp_f, temp_c, air_temp))
    else:
        msg = "Water temperature at {}\n{}\n{}°F / {}°C".format(
            site_name, time, temp_f, temp_c)
    water_temp = await ctx.send(msg)
    await water_temp.pin()
    if alerts:
        for alert in alerts.reverse():
            await alert.pin()
# {
#         "number": 1,
#         "name": "This Afternoon",
#         "startTime": "2024-04-09T17:00:00-04:00",
#         "endTime": "2024-04-09T18:00:00-04:00",
#         "isDaytime": true,
#         "temperature": 73,
#         "temperatureUnit": "F",
#         "temperatureTrend": "falling",
#         "probabilityOfPrecipitation": {
#           "unitCode": "wmoUnit:percent",
#           "value": null
#         },
#         "dewpoint": {
#           "unitCode": "wmoUnit:degC",
#           "value": 6.111111111111111
#         },
#         "relativeHumidity": {
#           "unitCode": "wmoUnit:percent",
#           "value": 38
#         },
#         "windSpeed": "2 mph",
#         "windDirection": "NE",
#         "icon": "https://api.weather.gov/icons/land/day/sct?size=medium",
#         "shortForecast": "Mostly Sunny",
#         "detailedForecast": "Mostly sunny. High near 73, with temperatures falling to around 70 in the afternoon. Northeast wind around 2 mph."
#       },

@bot.command()
async def alerts(ctx, location: str=None):
    """ Display the weather forecast for a location. """
    await _alerts(ctx, location=location)


@bot.command()
async def weather(ctx, location: str=None):
    """ Display the weather forecast for a location. """
    await alerts(ctx, location=location)
    await forecast(ctx, location=location)


async def _forecast(ctx, location: str=None):
    """ Display the weather forecast for a location. """
    if not location:
        location = ctx.channel.name
    try:
        station_id = STATIONS[location.lower()]['weather']
    except KeyError:
        await ctx.send(
            "`{}` is not a valid weather station. Try one of these:\n{}".format(
                location, ''.join(
                    '\t`{}`\n'.format(n)
                    for n in STATIONS.keys()
                    if 'weather' in STATIONS[n].keys())))
        return
    headers = {
        'User-Agent': '(bscientific.org, weather@bscientific.org)',
        }
    url = "https://api.weather.gov/gridpoints/{}/forecast".format(station_id)
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    return resp


@bot.command()
async def forecast(ctx, location: str=None):
    resp = await _forecast(ctx, location=location)
    periods = resp.json()['properties']['periods']
    content = 'Seven day forecast for {}:\n'.format(STATIONS[location]['name'])
    for period in periods:
        content += '{}: {}\n'.format(period['name'], period['detailedForecast'])
    await ctx.send(content)


@bot.command()
async def currents(ctx, location: str=None):
    df = await _currents(ctx, location=location)
    mdtable = df.to_markdown(tablefmt="grid")
    mdtable = mdtable.replace('+----+', '+')
    mdtable = mdtable.replace('+====+', '+')
    mdtable = "".join([s for s in mdtable.splitlines(True) if s.strip("\r\n")])
    mdtable = re.sub(r'\|\s..\s\|', '|', mdtable)
    await ctx.send(str('```{}:\n{}```'.format(location, mdtable)))


async def _currents(ctx, location: str=None):
    """ Display the tidal current predictions for a location. """
    if not location:
        location = ctx.channel.name
    try:
        station_id = STATIONS[location.lower()]['currents']
    except KeyError:
        await ctx.send(
            '`{}` is not a valid tidal currents station. Try one of these:\n{}'.format(
                location, ''.join(
                    '\t`{}`\n'.format(n)
                    for n in STATIONS.keys()
                    if 'currents' in STATIONS[n].keys())))
        return
    url = 'https://tidesandcurrents.noaa.gov/noaacurrents/DownloadPredictions'
    params = {
        'fmt': 'csv',
        'product': 'currents',
        'date': 'Today',
        'range': 12,
        'id': station_id ,
    }
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    csvfile = StringIO(resp.content.decode('utf-8'))
    df = pd.read_csv(csvfile)
    return df


@bot.command()
async def tides(ctx, location: str=None):
    """ Display the tidal height predictions for a location. """
    if not location:
        location = ctx.channel.name
    try:
        station_id = STATIONS[location.lower()]['tides']
    except KeyError:
        await ctx.send(
            '`{}` is not a valid tidal currents station. Try one of these:\n{}'.format(
                location, ''.join(
                    '\t`{}`\n'.format(n)
                    for n in STATIONS.keys()
                    if 'tides' in STATIONS[n].keys())))
        return
    url = 'https://tidesandcurrents.noaa.gov/api/datagetter'
    begin_date = date.today()
    end_date = begin_date + timedelta(days=1)
    begin_date = begin_date.strftime('%Y%m%d')
    end_date = end_date.strftime('%Y%m%d')
    params = {
        "product": "predictions",
        "application": "NOS.COOPS.TAC.WL",
        "begin_date": begin_date.replace('-', ''),
        "end_date": end_date.replace('-', ''),
        "datum": "MLLW",
        "station": station_id,
        "time_zone": "lst_ldt",
        "units": "english",
        "interval": "hilo",
        "format": "csv",
    }
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    csvfile=StringIO(resp.content.decode('utf-8'))
    df=pd.read_csv(csvfile)
    mdtable = df.to_markdown(tablefmt="grid")
    mdtable = mdtable.replace('+----+', '+')
    mdtable = mdtable.replace('+====+', '+')
    mdtable = "".join([s for s in mdtable.splitlines(True) if s.strip("\r\n")])
    mdtable = re.sub(r'\|\s..\s\|', '|', mdtable)
    await ctx.send(str('```{}:\n{}```'.format(location, mdtable)))

    
@bot.command()
async def add(ctx, left: int, right: int):
    """Adds two numbers together."""
    await ctx.send(left + right)


@bot.command()
async def roll(ctx, dice: str):
    """Rolls a dice in NdN format."""
    try:
        rolls, limit = map(int, dice.split('d'))
    except Exception:
        await ctx.send('Format has to be in NdN!')
        return

    result = ', '.join(str(random.randint(1, limit)) for r in range(rolls))
    await ctx.send(result)


@bot.command(description='For when you wanna settle the score some other way')
async def choose(ctx, *choices: str):
    """Chooses between multiple choices."""
    await ctx.send(random.choice(choices))


async def _alerts(ctx, location: str=None):
    alerts = []
    if not location:
        location = ctx.channel.name
    try:
        _ = STATIONS[location.lower()]['weather']
    except KeyError:
        await ctx.send(
            "`{}` is not a valid weather station. Try one of these:\n{}".format(
                location, ''.join(
                    '\t`{}`\n'.format(n)
                    for n in STATIONS.keys()
                    if 'weather' in STATIONS[n].keys())))
        return
    else:
        point = '{},{}'.format(
            STATIONS[location.lower()]['latitude'],
            STATIONS[location.lower()]['longitude']
            )
    alerts_url = 'https://api.weather.gov/alerts/active?point={}'.format(point)
    headers = {
        'User-Agent': '(bscientific.org, weather@bscientific.org)',
        }
    resp = requests.get(alerts_url, headers=headers)
    resp.raise_for_status()
    try:
        json_obj = resp.json()
    except AttributeError:
        pass
    if not json_obj['features']:
        alert = await ctx.send('No weather alerts found')
        alerts.append(alert)
    for feature in json_obj['features']:
        try:
            headline = feature['properties']['headline']
        except KeyError:
            headline = ''
        try:
            severity = feature['properties']['severity']
        except KeyError:
            severity = ''
        try:
            description = feature['properties']['description']
        except KeyError:
            description = ''
        alert = await ctx.send(
            '{}\n{}n{}'.format(
                headline,
                severity,
                description
            ))
        alerts.append(alert)
    return alerts


bot.run(
    DISCORD_TOKEN
)
