import requests
import json

key = 'AQGAV5PP1V3KG50Z'
BASE_URL = 'https://www.steamwebapi.com/steam/api/inventory'

def get_inventory(steamid64):
    params = {
        'key': key,
        'steam_id': steamid64,
        'sort': 'count'
    }

    response = requests.get(BASE_URL, params=params, timeout=1000)
    data = response.json()

    file_name = f'{steamid64}.json'

    with open(file_name, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, indent = 4)
    
    return file_name