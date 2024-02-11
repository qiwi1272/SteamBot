from items.inventory import Inventory
from ipc_interface import IPCInterface
from driver_manager import ParallelDriverManager
import web_controller as wc
import time

class SteamAccountInterface(Inventory):
    def __init__(self, name: str,  password):
        self.name = name
        self.password = password
        self.ipc = IPCInterface()
        self.driver_manager = ParallelDriverManager(1)
        self.driver = self.driver_manager.drivers[0]
        super().__init__(self.excecute('sid'))

    def excecute(self, cmd):
        return self.ipc.command(f'{cmd} {self.name}')
    
    def get_2fa(self):
        return self.excecute('2fa')
    
    def approve_2fa(self):
        return self.excecute('2faok')
    
    def login(self):
        self.driver_manager.set_urls([wc.CSMONEY_LOGIN_URL])
        self.driver_manager.url_task(wc.steam_login, self.driver,self.name, self.password, self.get_2fa)

    def temp(self):
        d = self.get_item_counts()
        for i in d.keys():
            print(f'{d[i]}')
        

creds = {
    'username1': 'password',
    'username2': 'password',
    'username3':'password',
    'username4':'password',
    'username5': 'password'
}


a = SteamAccountInterface('username1', 'password')
#a.temp()
a.login()
time.sleep(60)