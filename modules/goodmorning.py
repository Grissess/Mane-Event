import datetime, random

import bot

class Module(bot.Module):
    ONE_DAY = datetime.timedelta(days=1)
    # XXX Move these into config at some point
    GREETINGS = [
        'Good morning Baltimare!',
        'Another lovely day in Baltimare!',
        "It's PonyTime!",
        'Good morning everypony!',
    ]
    CONVERSATIONS = [
        "How's everypony doing?",
        "Today's topic: Pancakes, syrup or butter?",
        "What's new with everypony?",
        "Who's excited for BronyCon 2018?",
        "Anypony have interesting plans today?",
    ]
    COUNTDOWN = [
        "Only {} days to BronyCon!",
        "{} days until BronyCon!",
        "Only {} days left? BronyCon is right around the corner!",
        "Oh Celestia, only {} days until BronyCon, how exciting!",
    ]
    COUNTUP = [
        "Day {} of BronyCon!",
    ]
    MOTD = [
        "Have you registered for your badge yet? https://www.bronycon.org/register",
        "Have a question about BronyCon? Email info@bronycon.org!",
        "Have an event or panel you want to run this year? Don't hesitate, put in your application today! https:///www.bronycon.org/events/run-an-event",
        "Do you have what it takes to help make BronyCon an amazing event for all ages? Sign up for staff at https://www.bronycon.org/about/volunteer/staff !",
    ]

    def __init__(self, config):
        super().__init__(config)

        self.goal_time = datetime.time(*self.config['at'])
        # XXX Dedup this
        self.goal = self.at_goal_time(datetime.datetime.now())
        if datetime.datetime.now() >= self.goal:
            self.goal += self.ONE_DAY
        print('Goodmorning happens at', self.goal)
        self.con_dt = datetime.datetime(*self.config['convention'])

    def at_goal_time(self, dt):
        return dt.replace(
            hour = self.goal_time.hour,
            minute = self.goal_time.minute,
            second = self.goal_time.second,
            microsecond = 0
        )

    async def on_occasion(self):
        now = datetime.datetime.now()
        if (now.year, now.month, now.day, now.hour, now.minute, now.second) >= (self.goal.year, self.goal.month, self.goal.day, self.goal.hour, self.goal.minute, self.goal.second):
            await self.say_good_morning()
            self.goal = self.at_goal_time(now + self.ONE_DAY)

    async def say_good_morning(self):
        now = datetime.datetime.now()
        delta = self.con_dt - now
        greeting = random.choice(self.GREETINGS)
        conv = random.choice(self.CONVERSATIONS)
        motd = random.choice(self.MOTD)
        if delta.days > 0:
            ct = random.choice(self.COUNTDOWN).format(delta.days)
        else:
            ct = random.choice(self.COUNTUP).format(1 - delta.days)

        await self.client.send_message(self.get_channel(self.config['into']),
            f'{greeting} {ct} {conv}\n\n{motd}'
        )
