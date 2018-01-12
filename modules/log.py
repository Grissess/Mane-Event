import bot

class Module(bot.Module):
    def __init__(self, config):
        super().__init__(config)

        if 'file' in self.config:
            self.file = open(self.config['file'], 'a')

    def print(self, *args):
        print(*args)
        self.file.write(' '.join(args))

    async def on_ready(self):
        self.print('log: ready')

    async def on_message(self, message):
        self.print('log: on_message', f'#{message.channel.name} <{message.author.name}>) message.content')

    async def on_any_message(self, message):
        self.print('log: on_any_message',  f'#{message.channel.name} <{message.author.name}>) message.content')

    async def on_occasion(self):
        if self.config.get('occasions'):
            self.print('log: on_occasion')
