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
        'tides': {
            'id': '8518934',
            'name': 'Newburgh'
        },
        'currents': {
            'id': 'HUR0506',
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
    'peekskill': {
        'name': 'Peekskill',
        'water': '01374019',  # West Point
        'weather': 'OKX/31,61',
        'tides': {
            'id': '8518949',  # Peekskill
            'name': 'Peekskill',
        },
        'currents': {
            'id': 'ACT3711',
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
            'id': 'ACT3751',
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
            'id': 'ACT3751',
            'name': 'Norrie Point',
        },
        'latitude': 41.8323,
        'longitude': -73.9423,
    },
    'west-point': {
        'name': 'West Point',
        'currents': {
            'id': 'ACT3726_1',
            'name': 'West Point'
        },
        'weather': 'OKX/30,67',  # Cold Spring
        'water': '01374019',  # West Point
    },
    'piermont': {
        'name': 'Piermont',
        'water': '01376515',  # Piermont
        # 'water': '01376269',
    },
    'pier84': {
        'name': 'Pier 84',
        'water': '01376515',  # Piermont
    },
    # 'poughkeepsie': {
    #     'name': 'Poughkeepsie',
    # },
}
