import datetime, random

import bot

class BirthdayDB(object):
    def __init__(self, db):
        self.db = db
        self.db.execute('CREATE TABLE IF NOT EXISTS birthdays (user_id INTEGER PRIMARY KEY, year, month, day)')

    def set_birthday(self, uid, year, month, day):
        self.db.execute('INSERT OR REPLACE INTO birthdays (user_id, year, month, day) VALUES (?, ?, ?, ?)', (uid, year, month, day))
        self.db.commit()

    def get_birthdays(self, month, day):
        cur = self.db.execute('SELECT user_id, year FROM birthdays WHERE month=? AND day=?', (month, day))
        return cur.fetchall()

class Module(bot.Module):
    ONE_DAY = datetime.timedelta(days=1)
    # XXX Move these into config as well
    PLURAL_MESSAGES = [
        "We have {num} birthdays today: {list}. Happy birthday, everypony!",
        "There are {num} birthdays today: {list}. Happy birthdays!",
        "Wish {list} a happy birthday!",
        "Happy birthday, {list}!",
    ]
    SINGULAR_MESSAGES = [
        "Wish {sing} a happy birthday!",
        "Happy birthday, {sing}!",
        "Just one birthday today: {sing}. Happy birthday!",
    ]
    NIL_MESSAGES = [
        "No birthdays today :(",
    ]

    def __init__(self, config):
        super().__init__(config)

        self.birthdays = BirthdayDB(bot.db)
        self.goal_time = datetime.time(*self.config['at'])
        self.goal = self.at_goal_time(datetime.datetime.now() + self.ONE_DAY)

    def at_goal_time(self, dt):
        return dt.replace(
            hour = self.goal_time.hour,
            minute = self.goal_time.minute,
            second = self.goal_time.second,
            microsecond = 0
        )

    def english_list(self, strs):
        if not strs:
            return ''
        if len(strs) == 1:
            return strs[0]
        if len(strs) == 2:
            return ' and '.join(strs)
        return ', '.join(strs[:-1]) + ', and ' + strs[-1]

    async def on_occasion(self):
        now = datetime.datetime.now()
        if (now.year, now.month, now.day, now.hour, now.minute, now.second) >= (self.goal.year, self.goal.month, self.goal.day, self.goal.hour, self.goal.minute, self.goal.second):
            await self.list_birthdays()
            self.goal = self.at_goal_time(now + self.ONE_DAY)

    async def list_birthdays(self):
        now = datetime.datetime.now()
        birthdays = self.birthdays.get_birthdays(now.month, now.day)
        birthdays = [(list(self.client.servers)[0].get_member(str(uid)), year) for uid, year in birthdays]
        filt_birthdays = [(member, year) for member, year in birthdays if member is not None]
        unrec = len(birthdays) - len(filt_birthdays)

        strs = [
            member.mention + (f' ({now.year - year})' if year is not None else '')
            for member, year in filt_birthdays
        ]
        if unrec:
            strs.append(f'{unrec} {"other " if filt_birthdays else ""}{"users" if unrec > 1 else "user"} I can\'t look up')

        if len(birthdays) > 1:
            msg = random.choice(self.PLURAL_MESSAGES).format(num=len(birthdays), list=self.english_list(strs))
        elif len(birthdays) == 1:
            msg = random.choice(self.SINGULAR_MESSAGES).format(sing=strs[0])
        else:
            msg = random.choice(self.NIL_MESSAGES)

        await self.client.send_message(self.get_channel(self.config['into']),
            f"{msg}\nIf I don't know your birthday yet, you can tell me with `!setbirthday month day` or `!setbirthday year month day` if you want ponies to know how old you are!\nFor example, Alabaster is born on December 22nd 1996, so he would use `!setbirthday 1996 12 22`"
        )

    async def on_message(self, message):
        if message.content == '!birthdays':
            await self.list_birthdays()
            return
        if not message.content.startswith('!setbirthday '):
            return
        try:
            parts = list(map(int, message.content.split()[1:]))
        except ValueError:
            return
        if len(parts) not in (2, 3):
            await self.client.send_message(message.channel,
                f"{message.author.mention}: Just `month day` or `year month day`, please :)"
            )
            return
        if len(parts) == 2:
            year, month, day = None, *parts
        else:
            year, month, day = parts
        now = datetime.datetime.now()
        try:
            datetime.date(now.year if year is None else year, month, day)
        except ValueError:
            await self.client.send_message(message.channel,
                f"{message.author.mention}: Your numbers are out of range, check that you got the order right: `year month day` or just `month day` :)"
            )
            return
        self.birthdays.set_birthday(message.author.id, year, month, day)
        next_bday = datetime.datetime(now.year, month, day, self.goal_time.hour, self.goal_time.minute, self.goal_time.second)
        if next_bday < now:
            next_bday = next_bday.replace(year=now.year + 1)
        delta = next_bday - now
        delta -= datetime.timedelta(microseconds=delta.microseconds)
        await self.client.send_message(message.channel,
            f'Thanks, {message.author.mention}! We\'ll celebrate in {delta}.'
        )
