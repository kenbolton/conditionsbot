#!/usr/bin/env python3

"""
tides: https://tidesandcurrents.noaa.gov/tide_predictions.html?gid=1407
currents: https://tidesandcurrents.noaa.gov/noaacurrents/Stations?g=458
weather w/ lat/lon: https://api.weather.gov/points/<lat>,<lon>
"""
STATIONS = {
    'albany': {
        'water': '01359165',
        'name': 'Albany',
        'weather': 'ALY/70,60',
        'latitdue': 42.6232,
        'longitude': -73.7556,
        'tides': {
            'id': '',
            'name': 'Port of Albany'
        },
        'currents': {
            'id': 'HUR0618',
            'name': 'Port of Albany'
        }
    },
    'beacon': {
        'name': 'Beacon',
        'water': '01374019',  # West Point
        'weather': 'ALY/73,10',
        'tides': {
            'id': '8518934',
            'name': 'Newburgh'
        },
        'currents': {
            'id': 'HUR0506_7',
            'name': 'Newburgh'
        },
        'latitude': 41.5048,
        'longitude': -73.9695,
    },
    'cold-spring': {
        'name': 'Cold Spring',
        'water': '01374019',  # West Point
        'weather': 'OKX/30,67',
        'currents': {
            'id': 'ACT3726_1',
            'name': 'West Point'
        },
        'tides': {
            'name': 'Cold Spring (calculated from offsets)',
        },
        'latitude': 41.4114,
        'longitude': -73.9543,
    },
    'athens': {
        'name': 'Athens',
        'water': '01359165',
        'weather': 'ALY/74,45',
        'currents': {
            'id': 'HUR0614',
            'name': 'Hudson',
        },
        'tides': {
            'id': '8518974',
            'name': 'Hudson',
        },
        'latitude': 42.251775,
        'longitude': -73.787882,
    },
    'hudson': {
        'name': 'Hudson',
        'water': '01359165',
        'weather': 'ALY/74,45',
        'currents': {
            'id': 'HUR0614',
            'name': 'Hudson',
        },
        'tides': {
            'id': '8518974',
            'name': 'Hudson',
        },
        'latitude': 42.251775,
        'longitude': -73.787882,
    },
    'ossining': {
        'name': 'Ossining',
        'water': '01376515',  # Piermont
        'weather': 'OKX/35,56',
        'currents': {
            'id': 'ACT3696',  # TODO fixme
            'name': 'Ossining'
        },
        'tides': {
            'id': '8518924',
            'name': 'Haverstraw'
        },
        'latitude': 41.1611,
        'longitude': -73.8536,
    },
    'peekskill': {
        'name': 'Peekskill',
        'water': '01374019',  # West Point
        'weather': 'OKX/31,61',
        'tides': {
            'id': '8518949',  # Peekskill
            'name': 'Peekskill',
        },
        'currents': {
            'id': 'ACT3711',  # TODO fixme
            'name': 'Peekskill',
        },
        'latitude': 41.2931,
        'longitude': -73.9387,
    },
    'norrie': {
        'name': 'Norrie Point',
        'water': '01359165',  # Albany
        'weather': 'ALY/72,25',
        'tides': {
            'id': '8518951',
            'name': 'Norrie Point',
        },
        'currents': {
            'id': 'ACT3751',  # TODO fixme
            'name': 'Norrie Point',
        },
        'latitude': 41.8323,
        'longitude': -73.9423,
    },
    'norrie-point': {
        'name': 'Norrie Point',
        'water': '01359165',  # Albany
        'weather': 'ALY/72,25',
        'tides': {
            'id': '8518951',
            'name': 'Norrie Point',
        },
        'currents': {
            'id': 'ACT3751',  # TODO fixme
            'name': 'Norrie Point',
        },
        'latitude': 41.8323,
        'longitude': -73.9423,
    },
    'west-point': {
        'name': 'West Point',
        'tides': {
            'name': 'Cold Spring (calculated from offsets)',
        },
        'currents': {
            'id': 'ACT3726_1',  # TODO fixme
            'name': 'West Point'
        },
        'weather': 'OKX/30,67',  # Cold Spring
        'water': '01374019',  # West Point
    },
    'piermont': {
        'name': 'Piermont',
        'water': '01376515',  # Piermont
        'latitude': 41.0474,
        'longitude': -73.9098,
        'weather': 'OKX/34,51',
        'currents': {
            'id': 'HUR0502',
            'name': 'Tappan Zee Bridge'
        },
        'tide': {
            'name': 'Alpine NJ',
            'id': '8530095'
        },
    },
    'pier84': {
        'name': 'Pier 84',
        'weather': 'OKX/33,38',
        'latitude': 40.7707,
        'longitude': -74.0028,
        # Piermont, https://waterdata.usgs.gov/monitoring-location/01376515/#parameterCode=00010&period=P7D&showMedian=true
        'water': '01376515',
        'tide': {
            'name': 'Dyckman Street',
            'id': '8518902'
        },
        'current': {
            'name': 'Pier 92',
            'id': 'NYH1928'
        },
    },
    # 'poughkeepsie': {
    #     'name': 'Poughkeepsie',
    # },
}
