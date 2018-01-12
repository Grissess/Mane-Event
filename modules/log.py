import bot

class Module(bot.Module):
    async def on_ready(self):
        print('log: ready')

    async def on_message(self, message):
        print('log: on_message', f'#{message.channel.name} <{message.author.name}>) message.content')

    async def on_any_message(self, message):
        print('log: on_any_message',  f'#{message.channel.name} <{message.author.name}>) message.content')

    async def on_occasion(self):
        if self.config.get('occasions'):
            print('log: on_occasion')
