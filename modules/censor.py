import re

import bot

class NullScoreDB(object):
    def __init__(self, db):
        self.db = db

    def get_score(self, uid):
        return 0

    def set_score(self, uid, score):
        pass

    def add_score(self, uid, delta):
        final = self.get_score(uid) + delta
        self.set_score(uid, final)
        return final

    def get_all(self):
        return []

    def set_all(self, score):
        pass

class ScoreDB(NullScoreDB):
    def __init__(self, db):
        super().__init__(db)
        self.db.execute('CREATE TABLE IF NOT EXISTS ban_scores (user_id INTEGER PRIMARY KEY, score)')

    def get_score(self, uid):
        cur = self.db.execute('SELECT score FROM ban_scores WHERE user_id = ?', (uid,))
        row = cur.fetchone()
        if row is None:
            return 0
        return row[0]

    def set_score(self, uid, score):
        self.db.execute('INSERT OR REPLACE INTO ban_scores (user_id, score) VALUES (?, ?)', (uid, score))
        self.db.commit()

    def get_all(self):
        return self.db.execute('SELECT user_id, score FROM ban_scores').fetchall()

    def set_all(self, score):
        self.db.execute('UPDATE ban_scores SET score=?', (score,))
        self.db.commit()

class Module(bot.Module):
    SIMPLIFY_MESSAGE = re.compile(r'[^\w\s]')
    SCORE_IMPLS = {
        'db': ScoreDB,
        'none': NullScoreDB,
    }

    def __init__(self, config):
        super().__init__(config)

        self.re = self.config.get('re', False)
        if self.re:
            self.profane_re = self.load_re('profanity')
            self.crisis_re = self.load_re('crisis')
        else:
            self.profane_words = self.load_word_list('profanity')
            self.exception_words = self.load_word_list('exception')
            self.crisis_words = self.load_word_list('crisis')

        if 'score_impl' in self.config:
            self.score = self.SCORE_IMPLS[self.config['score_impl']](bot.db)
        else:
            self.score = ScoreDB(bot.db)

    def load_word_list(self, cat):
        if cat+'_list' in self.config:
            return self.config[cat+'_list']
        if cat+'_file' in self.config:
            return open(self.config[cat+'_file']).read().splitlines()
        raise RuntimeError(f"censor wanted a {cat!r} word list, please provide {cat}_list or {cat}_file in its config")

    def load_re(self, cat):
        if cat+'_re' in self.config:
            return re.compile(self.config[cat+'_re'])
        if cat+'_file' in self.config:
            return re.compile(open(self.config[cat+'_file']).readlines()[1].strip())
        raise RuntimeError(f"censor wanted a {cat!r} RE, please provide {cat}_re or {cat}_file containing a RE on its second line in its config")

    def simplify(self, message):
        return self.SIMPLIFY_MESSAGE.sub('', message.lower())

    def get_simple_matches(self, message, list):
        return [item for item in list if item in message]

    def get_bad_matches(self, message):
        testMessage = self.simplify(message)

        while True:
            #console_print 'Testing {0}'.format(testMessage)
            badMatches = self.get_simple_matches(testMessage, self.profane_words)
            if not badMatches:
                return badMatches
            badMatch = badMatches[0]
            #console_print 'Banned word {0}'.format(badMatch)
            possibleGoodWords = [word for word in self.exception_words if badMatch in word]
            matchingGoodWords = [word for word in possibleGoodWords if word in testMessage]
            #matchingGoodWords.sort(key=len, reverse=True)
            #console_print 'Matching good words {0}'.format(matchingGoodWords)

            if not matchingGoodWords:
                #console_print 'FAILED'
                return badMatches
            else:
                testMessage = testMessage.replace(matchingGoodWords[0], '', 1)

    def get_crisis_matches(self, message):
        return self.get_simple_matches(self.simplify(message), self.crisis_words)

    def score_of(self, word):
        return 1  # TODO

    async def do_ban(self, user, score):
        self.score.set_score(user.id, 0)  # Reset
        if self.config['action'] == 'ban':
            print('Still not ready to actually ban yet!')
        elif self.config['action'] == 'test':
            await self.client.send_message(self.get_channel(self.config['log_channel']),
                f'{user.mention}\U0001F528 (user would have been banned, score was {score})'
            )

    async def do_delete_message(self, message, bad_stuff):
        await self.client.delete_message(message)
        await self.client.send_message(message.channel,
            f"{message.author.mention}, I've deleted your message and sent you a PM explaining why."
        )
        await self.client.send_message(message.author,
            f"Your message, \"{message.content}\", contained {bad_stuff!r}. Please refrain saying this in the future!\n\nIf you believe this is in error, please contact <@{self.global_config['owner']['id']}>."
        )
        await self.client.send_message(self.get_channel(self.config['log_channel']),
            f"Message from {message.author.mention} deleted in #{message.channel.name} for containing {bad_stuff!r}: \"{message.content}\"."
        )
        final = self.score.add_score(message.author.id, 1)
        if final > self.config['ban_score']:
            await self.do_ban(message.author, final)

    async def do_crisis_message(self, message, notice):
        await self.client.send_message(self.get_channel(self.config['crisis_channel']),
            notice
        )

    async def on_any_message(self, message):
        if message.author.bot:
            return

        if self.re:
            match = self.profane_re.search(message.content)
            if match:
                await self.do_delete_message(message, match.group(0))
            match = self.crisis_re.search(message.content)
            if match:
                await self.do_crisis_message(message,
                    f"{message.author.mention} send a critical message containing \"{match.group()}\" in #{message.channel.name}: \"{message.content}\""
                )
        else:
            bad_matches = self.get_bad_matches(message.content)
            crisis_matches = self.get_crisis_matches(message.content)

            if bad_matches:
                await self.do_delete_message(message, bad_matches)

            if crisis_matches:
                await self.do_crisis_message(message,
                    f"{message.author.mention} sent a critical message containing {crisis_matches!r} in #{message.channel.name}: \"{message.content}\"."
                )

    MENTION_RE = re.compile(r'<@(\d+)>')

    async def on_message(self, message):
        if message.channel.id not in {self.get_channel(name).id for name in self.config.get('control_channels', [])}:
            return

        if message.content.startswith('!getscore ') or message.content.startswith('!setscore '):
            parts = message.content.split()
            if parts[1] == 'all':
                if parts[0] == '!getscore':
                    all_scores = self.score.get_all()
                    server = list(self.client.servers)[0]
                    named_scores = {}
                    for uid, score in all_scores:
                        if score == 0:
                            continue
                        member = server.get_member(str(uid))
                        if member is None:
                            named_scores[f'Unknown user {uid}'] = score
                        else:
                            named_scores[f'{member.name}#{member.discriminator}'] = score
                    await self.client.send_message(message.channel,
                        f"{message.author.mention}: I know about {len(all_scores)} users right now; currently nonzero: {', '.join(f'{name} ({score})' for name, score in named_scores.items())}"
                    )
                else:
                    self.score.set_all(int(parts[2]))
                    await self.client.send_message(message.channel,
                        f"{message.author.mention}: It is done.",
                    )
                return
            match = self.MENTION_RE.match(parts[1])
            if match:
                uid = match.group(1)
            else:
                member = list(self.client.servers)[0].get_member_named(parts[1])
                if member:
                    uid = member.id
                else:
                    uid = None
            if uid is None:
                await self.client.send_message(message.channel,
                    f"{message.author.mention}: I was unable to identify any member with that name."
                )
            else:
                if parts[0] == '!getscore':
                    await self.client.send_message(message.channel, 
                        f"{message.author.mention}: {self.score.get_score(uid)}"
                    )
                else:
                    self.score.set_score(uid, int(parts[2]))
                    await self.client.send_message(message.channel,
                        f"{message.author.mention}: finished"
                    )
