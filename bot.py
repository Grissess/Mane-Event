import asyncio, sys, ctypes, json, functools

import discord

import db

__version__ = '0.0.3'

if sys.platform.startswith('win'):
    ctypes.windll.kernel32.SetConsoleTitleW(f"Mane Event {__version__}")
else:
    print(f'\x1b]0;Mane Event {__version__}\a')

if len(sys.argv) < 2:
    sys.argv.append('config.json')

config = json.load(open(sys.argv[1]))

client = discord.Client()

class _Namespace(object):
    pass

bot = _Namespace()

class _ClassPropDescriptor(object):
    def __init__(self, get):
        self.get = get

    def __get__(self, obj, tp=None):
        if tp is None:
            tp = type(obj)
        return self.get(tp)

def classproperty(get):
    return _ClassPropDescriptor(get)

class Module(object):
    bot = bot

    @classproperty
    def client(cls):
        return cls.bot.client

    @classproperty
    def global_config(cls):
        return cls.bot.config

    @classmethod
    def get_channel(cls, name):
        id = cls.global_config['channels'][name]
        chan = list(cls.client.servers)[0].get_channel(id)
        if chan is None:
            return discord.Object(id=id)
        return chan

    def __init__(self, config):
        self.config = config

    async def on_message(self, message):
        pass

    async def on_any_message(self, message):
        pass

    async def on_occasion(self):
        pass

    async def on_ready(self):
        pass

bot.db = db.DB(config)
bot.config = config
bot.client = client
bot.Module = Module
bot.modules = []

sys.modules['bot'] = bot

for modname, modcfg in config['modules'].items():
    mod = getattr(__import__('modules.' + modname), modname)
    inst = mod.Module(modcfg)
    inst.name = modname
    bot.modules.append(inst)

@client.event
async def on_ready():
    print('Logged in as', client.user.name, client.user.id)
    print('--Server List--')
    for server in client.servers:
        print('-', server.name)
    print()
    print('-- Modules loaded --')
    for mod in bot.modules:
        print('-', mod.name)
    await asyncio.gather(
        *[mod.on_ready() for mod in bot.modules]
    )

loop = client.loop

async def timer():
    # Doing this now prevents an error from killing the timer completely
    loop.call_later(config['occasion_tick'], functools.partial(asyncio.ensure_future, timer(), loop=loop))

    await asyncio.gather(
        *[mod.on_occasion() for mod in bot.modules]
    )

loop.call_soon(asyncio.ensure_future, timer())

ALLOWED_CHANNELS = None
IGNORED_CHANNELS = None
def check_message_ctx(message):
    global ALLOWED_CHANNELS, IGNORED_CHANNELS

    if IGNORED_CHANNELS is None:
        IGNORED_CHANNELS = {config['channels'][name] for name in config.get('ignore', [])}

    if message.channel.id in IGNORED_CHANNELS:
        print('Ignoring a message in', message.channel.name, 'due to `ignore`')
        return False

    if ALLOWED_CHANNELS is None:
        if 'only_recv_in' in config:
            ALLOWED_CHANNELS = {config['channels'][name] for name in config['only_recv_in']}
        else:
            ALLOWED_CHANNELS = True

    if ALLOWED_CHANNELS is True:
        return True
    if message.channel.id not in ALLOWED_CHANNELS:
        print('Ignoring a message in', message.channel.name, 'due to `only_recv_in`')
        return False
    return True

@client.event
async def on_message_edit(beforeMsg, afterMsg):
    if not check_message_ctx(afterMsg):
        return

    await asyncio.gather(
        *[mod.on_any_message(afterMsg) for mod in bot.modules]
    )

@client.event
async def on_message(message):
    if not check_message_ctx(message):
        return

    await asyncio.gather(*(
        [mod.on_message(message) for mod in bot.modules] +
        [mod.on_any_message(message) for mod in bot.modules]
    ))

client.run(config['token'])
