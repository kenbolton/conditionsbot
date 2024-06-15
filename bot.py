#!/usr/bin/env python3

import aiohttp
import os
import re
import discord
import random
import pandas as pd

from datetime import date, timedelta, datetime

from discord.ext import commands

from dotenv import load_dotenv

from io import StringIO

from stations import STATIONS


"""
sudo pm2 start "/home/ubuntu/conditionsbot/bin/python /home/ubuntu/conditionsbot/bot.py" --name "conditionsbot"
sudo pm2 restart conditionsbot
sudo pm2 log conditionsbot
"""

load_dotenv()

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

description = ''' A bot that grabs data from various sources to populate discord
with important information for small boats.

Built by Hudson River Expeditions & kb
'''

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='$', description=description, intents=intents)


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')


@bot.command()
async def locations(ctx, location: str = ''):
    """ List locations and their available data """
    def _make_msg(key: str, station: str, msg: str):
        msg += "{}:".format(station['name'])
        msg += " `{}`\n".format(key)
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
        for key, station in STATIONS.items():
            await ctx.send(_make_msg(key, station, msg))
        return
    try:
        station = STATIONS[location.lower()]
    except KeyError:
        await ctx.send(
            "`{}` is not a valid station. Try one of these:\n{}".format(
                location.lower(), ''.join(
                    '\t`{}`\n'.format(n)
                    for n in STATIONS.keys()
                    if 'water' in STATIONS[n].keys())))
        return
    else:
        await ctx.send(_make_msg(key, station, msg))


@bot.command()
async def all(ctx, location: str = ''):
    """ Show all of the available data for a location """
    await water(ctx, location=location)
    await alerts(ctx, location=location)
    await forecast(ctx, location=location)
    await tides(ctx, location=location)
    await currents(ctx, location=location)


async def _water(ctx, station_id: str):
    url = "https://waterservices.usgs.gov/nwis/iv/"
    params = {
        "sites": station_id,
        "agencyCd": "USGS",
        "parameterCd": "00010",
        "period": "P1D",
        "siteStatus": "all",
        "format": "json",
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as resp:
            if resp.status == 200:
                js = await resp.json()
                site_name = js['value']['timeSeries'][0]['sourceInfo']['siteName']
                temp_c = js['value']['timeSeries'][0]['values'][-1]['value'][-1]['value']
                time = js['value']['timeSeries'][0]['values'][-1]['value'][-1]['dateTime']
                temp_f = float(temp_c) * (9 / 5) + 32
                return site_name, time, "{:.1f}".format(temp_f), temp_c


@bot.command()
async def water(ctx, location: str = ''):
    """ Display the water temperature for a location. """
    if not location:
        location = ctx.channel.name
    try:
        station_id = STATIONS[location.lower()]['water']
    except KeyError:
        await ctx.send(
            "`{}` is not a valid water temperature station. Try one of these:\n{}".format(
                location.lower(), ''.join(
                    '\t`{}`\n'.format(n)
                    for n in STATIONS.keys()
                    if 'water' in STATIONS[n].keys())))
        return
    site_name, time, temp_f, temp_c = await _water(ctx, station_id=station_id)
    msg = "{}\n{}\n{}°F / {}°C".format(site_name, time, temp_f, temp_c)
    await ctx.send(msg)


@bot.command()
async def now(ctx, location: str = ''):
    """ Pin an alert for the location that combines a bunch of data points. """
    # alerts
    # forecast: analyze air + water temp, alert if winds over ten, high alert over 15
    # currents
    # tides
    if not location:
        location = ctx.channel.name
    alerts = await _alerts(ctx, location=location)
    try:
        station_id = STATIONS[location.lower()]['water']
    except KeyError:
        await ctx.send(
            "`{}` is not a valid water temperature station. Try one of these:\n{}".format(
                location.lower(), ''.join(
                    '\t`{}`\n'.format(n)
                    for n in STATIONS.keys()
                    if 'water' in STATIONS[n].keys())))
    else:
        site_name, time, temp_f, temp_c = await _water(
            ctx, station_id=station_id)
    results = await _forecast(ctx, location=location)
    period = results['properties']['periods'][0]
    wind_speed = period["windSpeed"].split(' ')[0]  # [1] = "mph"
    wind_direction = period['windDirection']
    msg = 'Wind is up at {} mph from the {}'.format(wind_speed, wind_direction)
    if float(wind_speed) > 10:
        """ this is the good stuff if the currents are right """
        pass
    air_temp = period['temperature']
    if float(air_temp) + float(temp_f) < 120:
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
    # await water_temp.pin()
    # if alerts:
    #     for alert in alerts:
    #         await alert.pin()
    if (
            location == 'cold-spring' or
            location == 'west-point'):
        tides_df = await _get_cold_spring_tides()
    else:
        try:
            station_id = STATIONS[location.lower()]['tides']['id']
        except KeyError:
            await ctx.send(
                '`{}` is not a valid tidal currents station. '
                'Try one of these:\n{}'.format(
                    location.lower(), ''.join(
                        '\t`{}`\n'.format(n)
                        for n in STATIONS.keys()
                        if 'tides' in STATIONS[n].keys())))
        tides = await _get_tides(station_id)
        tides_csvfile = StringIO(tides.decode('utf-8'))
        tides_df = pd.read_csv(tides_csvfile)
    tides_df['Date Time'] = pd.to_datetime(tides_df['Date Time'])
    filtered_tides_df = tides_df.loc[(tides_df['Date Time'] >= datetime.now())]
    tidal_event = filtered_tides_df.head(1)
    try:
        loc = STATIONS[location.lower()]['tides']['name']
    except KeyError:
        loc = location.lower()
    await ctx.send(
        "{} tide {} feet at {} for {}.".format(
            "High" if tidal_event[' Type'].values[0] == "H" else "Low",
            tidal_event[' Prediction'].values[0],
            tidal_event['Date Time'].dt.strftime("%H:%M").values[0],
            loc
        ))
    currents_df = await _currents(ctx, location=location)
    currents_df['Date_Time (LST/LDT)'] = pd.to_datetime(
        currents_df['Date_Time (LST/LDT)'])
    filtered_currents_df = currents_df.loc[
        (currents_df['Date_Time (LST/LDT)'] >= datetime.now())]
    events = filtered_currents_df.head(2)
    try:
        loc = STATIONS[location.lower()]['currents']['name']
    except KeyError:
        loc = location.lower()
    if events.values[0][1].lstrip() == 'slack':
        msg = '{} at {} before max {} at {} for {}.'.format(
            events.values[0][1].lstrip().title(),
            pd.to_datetime(events.values[0][0]).strftime("%H:%M"),
            events.values[1][1].lstrip(),
            pd.to_datetime(events.values[1][0]).strftime("%H:%M"),
            loc)
    else:
        msg = '{} of {} knots at {} before {} at {} for {}.'.format(
            events.values[0][1].lstrip().title(),
            events.values[0][2].lstrip(),
            pd.to_datetime(events.values[0][0]).strftime("%H:%M"),
            events.values[1][1].lstrip(),
            pd.to_datetime(events.values[1][0]).strftime("%H:%M"),
            loc)
    await ctx.send(msg)



@bot.command()
async def alerts(ctx, location: str = ''):
    """ Display the weather forecast for a location. """
    await _alerts(ctx, location=location)


@bot.command()
async def weather(ctx, location: str = ''):
    """ Display the weather forecast for a location. """
    await alerts(ctx, location=location)
    await forecast(ctx, location=location)


async def _forecast(ctx, location: str = ''):
    if not location:
        location = ctx.channel.name
    try:
        station_id = STATIONS[location.lower()]['weather']
    except KeyError:
        await ctx.send(
            "`{}` is not a valid weather station. Try one of these:\n{}".format(
                location.lower(), ''.join(
                    '\t`{}`\n'.format(n)
                    for n in STATIONS.keys()
                    if 'weather' in STATIONS[n].keys())))
        return
    headers = {
        'User-Agent': '(bscientific.org, weather@bscientific.org)',
        }
    url = "https://api.weather.gov/gridpoints/{}/forecast".format(station_id)
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as resp:
            if resp.status == 200:
                js = await resp.json()
                return js

@bot.command()
async def forecast(ctx, location: str = ''):
    """ Display the weather forecast for a location. """
    if not location:
        location = ctx.channel.name
    resp = await _forecast(ctx, location=location)
    periods = resp['properties']['periods']
    content = 'Seven day forecast for {}:\n'.format(
        STATIONS[location.lower()]['name'])
    for period in periods:
        content += '{}: {}\n'.format(
            period['name'], period['detailedForecast'])
    await ctx.send(content)


@bot.command()
async def currents(ctx, location: str = ''):
    """ Display the tidal current predictions for a location. """
    if not location:
        location = ctx.channel.name
    df = await _currents(ctx, location=location)
    df.rename(
        columns={
            'Date_Time (LST/LDT)': 'Local Time',
            ' Speed (knots)': 'Knots'}, inplace=True)
    df['Local Time'] = pd.to_datetime(df['Local Time'])
    df['Local Time'] = df['Local Time'].dt.strftime("%m-%d %H:%M")
    df = df.drop(' Event', axis=1)
    mdtable = df.to_markdown(tablefmt="grid")
    mdtable = mdtable.replace('+----+', '+')
    mdtable = mdtable.replace('+====+', '+')
    mdtable = "".join([s for s in mdtable.splitlines(True) if s.strip("\r\n")])
    mdtable = re.sub(r'\|\s..\s\|', '|', mdtable)
    try:
        loc = STATIONS[location.lower()]['currents']['name']
    except KeyError:
        loc = location.lower()
    await ctx.send(str('```{}\n{} currents predictions```'.format(
        mdtable, loc)))


async def _currents(ctx, location: str = ''):
    if not location:
        location = ctx.channel.name
    try:
        station_id = STATIONS[location.lower()]['currents']['id']
    except KeyError:
        await ctx.send(
            '`{}` is not a valid tidal currents station. '
            'Try one of these:\n{}'.format(
                location.lower(), ''.join(
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
        'id': station_id,
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as resp:
            if resp.status == 200:
                content = await resp.read()
                csvfile = StringIO(content.decode('utf-8'))
                df = pd.read_csv(csvfile)
                return df


async def _get_tides(station_id, file_format: str = "csv"):
    url = 'https://tidesandcurrents.noaa.gov/api/datagetter'
    begin_date = date.today()
    end_date = begin_date + timedelta(days=1)
    begin_date_string = begin_date.strftime('%Y%m%d')
    end_date_string = end_date.strftime('%Y%m%d')
    params = {
        "product": "predictions",
        "application": "NOS.COOPS.TAC.WL",
        "begin_date": begin_date_string.replace('-', ''),
        "end_date": end_date_string.replace('-', ''),
        "datum": "MLLW",
        "station": station_id,
        "time_zone": "lst_ldt",
        "units": "english",
        "interval": "hilo",
        "format": file_format,
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as resp:
            if resp.status == 200:
                return await resp.read()


async def _get_cold_spring_tides():
    peekskill_id = STATIONS['peekskill']['tides']['id']
    peekskill_tides = await _get_tides(peekskill_id)
    peekskill_csvfile = StringIO(peekskill_tides.decode('utf-8'))
    peekskill = pd.read_csv(peekskill_csvfile)
    beacon_id = STATIONS['beacon']['tides']['id']
    beacon_tides = await _get_tides(beacon_id)
    beacon_csvfile = StringIO(beacon_tides.decode('utf-8'))
    beacon = pd.read_csv(beacon_csvfile)
    beacon['Date Time'] = pd.to_datetime(beacon['Date Time'])
    peekskill['Date Time'] = pd.to_datetime(peekskill['Date Time'])
    date_time = beacon['Date Time'] - (beacon['Date Time'] - peekskill[
        'Date Time']) / 3
    prediction = (beacon[' Prediction'] + peekskill[' Prediction']) / 2
    df = pd.DataFrame(beacon[' Type'])
    df = df.join(prediction)
    df = df.join(date_time)
    return df


@bot.command()
async def tides(ctx, location: str = ''):
    """ Display the tidal height predictions for a location. """
    if not location:
        location = ctx.channel.name
    if (
            location == 'cold-spring' or
            location == 'west-point'):
        df = await _get_cold_spring_tides()
    else:
        try:
            station_id = STATIONS[location.lower()]['tides']['id']
        except KeyError:
            await ctx.send(
                '`{}` is not a valid tidal currents station. '
                'Try one of these:\n{}'.format(
                    location.lower(), ''.join(
                        '\t`{}`\n'.format(n)
                        for n in STATIONS.keys()
                        if 'tides' in STATIONS[n].keys())))
            return
        resp = await _get_tides(station_id)
        csvfile = StringIO(resp.decode('utf-8'))
        df = pd.read_csv(csvfile)
    df = df.drop(' Type', axis=1)
    df['Date Time'] = pd.to_datetime(df['Date Time'])
    df['Date Time'] = df['Date Time'].dt.strftime("%m-%d %H:%M")
    df.rename(
        columns={
            ' Prediction': 'Feet',
            'Date Time': 'Local Time'}, inplace=True)
    mdtable = df.to_markdown(tablefmt="grid")
    mdtable = mdtable.replace('+----+', '+')
    mdtable = mdtable.replace('+====+', '+')
    mdtable = "".join([s for s in mdtable.splitlines(True) if s.strip("\r\n")])
    mdtable = re.sub(r'\|\s..\s\|', '|', mdtable)
    try:
        loc = STATIONS[location.lower()]['tides']['name']
    except KeyError:
        loc = location.lower()
    await ctx.send(
        str('```{}\n{} tidal height predictions```'.format(mdtable, loc)))


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


async def _alerts(ctx, location: str):
    alerts = []
    if not location:
        location = ctx.channel.name
    try:
        _ = STATIONS[location.lower()]['weather']
    except KeyError:
        await ctx.send(
            "`{}` is not a valid weather station. Try one of these:\n{}".format(
                location.lower(), ''.join(
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
    async with aiohttp.ClientSession() as session:
        async with session.get(alerts_url, headers=headers) as resp:
            if resp.status == 200:
                json_obj = await resp.json()
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
