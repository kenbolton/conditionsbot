#!/usr/bin/env python3


STATIONS = {
    'albany': {
        'water': '01359165',
        'name': 'Albany',
    },
    'beacon': {
        'name': 'Beacon',
        'water': '01374019',  # West Point
        'weather': 'ALY/73,10',
        'tides': '8518934',
        'currents': 'HUR0506',
        'latitude': 41.5048,
        'longitude': -73.9695,
    },
    'coldspring': {
        'name': 'Cold Spring',
        'water': '01374019',  # West Point
        'weather': 'OKX/30,67',
        'currents': 'ACT3726_1',  # West Point
        'tides': '8518949',  # Peekskill
        'tides_location': 'Peekskill',
        'latitude': 41.4114,
        'longitude': -73.9543,
    },
    'peekskill': {
        'name': 'Peekskill',
        'water': '01374019',  # West Point
        'weather':  'OKX/31,61',
        'tides': '8518949',
        'currents': 'ACT3711',
        'latitude': 41.2931,
        'longitude': -73.9387,
    },
    'norrie': {
        'name': 'Norrie Point',
        'water': '01359165',  # Albany
        'weather': 'ALY/72,25',
        'tides': '8518951',
        'currents': 'ACT3751',
        'latitude': 41.8323,
        'longitude': -73.9423,
    },
    'westpoint': {
        'name': 'West Point',
        'currents': 'ACT3726_1',
        'weather': 'OKX/30,67',  # Cold Spring
        'water': '01374019',
    },
    'piermont': {
        'name': 'Piermont',
        'water': '01376269',
    },
    'pier84': {
        'name': 'Pier 84',
        'water': '01376515',  # Piermont
    },
    # 'poughkeepsie': {
    #     'name': 'Poughkeepsie',
    # },
}
