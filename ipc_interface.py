import asyncio
from ASF import IPC

bots = [
    'asf_username1',
    'asf_username2',
    'asf_username3',
    'asf_username4',
    'asf_username5'
]

def parse(s):
    '''removes username from response'''
    resp = []
    less_than = False
    for c in s:
        if c == '>':
            less_than = True
            continue
        if less_than and c != ' ':
            resp.append(c)
    return ''.join(resp)


class IPCInterface():
    '''
    Interface for connecting to ArchiSteamFarm.
    Gives us very high level control over steam accounts.
    '''
    def __init__(self):
        self.ipc: IPC = None
        self.loop: asyncio.BaseEventLoop = None
        self.start()

    async def _command(self, cmd: str):
        '''submits a comand asynchronusly'''
        async with self.ipc as asf:
            return await asf.Api.Command.post(body={
                'Command': cmd
            })
        
    def start(self):
        '''opens ipc interface, starts the loop'''
        self.ipc = IPC('ASF_URL', 'ASF_IPC_PASSWORD')
        self.loop = asyncio.get_event_loop()

    def stop(self):
        '''close the commmand loop'''
        self.loop.close()

    def command(self, cmd):
        '''submits an IPC command to the event loop'''
        resp = self.loop.run_until_complete(self._command(cmd))
        parsed = parse(resp.result)
        return parsed
