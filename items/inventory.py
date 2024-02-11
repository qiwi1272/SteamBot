import json
from items.get_inventory import get_inventory

class Inventory:
    def __init__(self, steamid64: str):
        self.steamid64 = steamid64
        self.inventory = self.load_inventory()

    def load_inventory(self):
        with open(f'/home/qiwi/Desktop/python/steam/csmoney/items/{self.steamid64}.json', 'r') as f:
            return json.load(f)
        
    def refresh_inventory(self):
        '''
        THE API USES A 1 DAY CACHE BY DEFAULT
        FLAG TO FORCE UPDATE COSTS 5 CREDITS
        '''
        get_inventory(self.steamid64)
        self.load_inventory()

    def delete_item(self, assetid):
        '''
        delete item from inventory,
        saves on an api call.
        '''
        for i, item in enumerate(self.inventory):
            if item['assetid'] == assetid:
                return self.inventory.pop(i)
        
    def get_item_counts(self) -> dict:
        '''
        return owner, items, and count
        '''
        item_counts = {}
        for item in self.inventory:
            market_hash_name = item['markethashname']
            assetid = item['assetid']
            if market_hash_name in item_counts.keys():
                item_counts[market_hash_name]['assetids'].append(assetid)
                item_counts[market_hash_name]['count'] += 1
            else:
                item_counts[market_hash_name] = {
                    'owner': self.steamid64,
                    'assetids': [assetid],
                    'count': 1,
                    
                    }
        return item_counts
