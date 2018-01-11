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
        self.db.cur.execute('INSERT OR REPLACE INTO ban_scores (user_id, score) VALUES (?, ?)', (uid, score))

class Module(bot.Module):
    SIMPLIFY_MESSAGE = re.compile(r'[^\w\s]')
    SCORE_IMPLS = {
        'db': ScoreDB,
        'none': NullScoreDB,
    }

    def __init__(self, config):
        super().__init__(config)

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
        self.score.set_score(uid, 0)  # Reset
        if self.config['action'] == 'ban':
            print('Still not ready to actually ban yet!')
        elif self.config['action'] == 'test':
            await self.client.send_message(self.get_channel(self.config['log_channel']),
                f'{user.mention}\U0001F528 (user would have been banned, score was {score})'
            )

    async def on_any_message(self, message):
        if message.author.bot:
            return

        bad_matches = self.get_bad_matches(message.content)
        crisis_matches = self.get_crisis_matches(message.content)

        if bad_matches:
            await self.client.delete_message(message)
            await self.client.send_message(message.channel,
                f"{message.author.mention}, I've deleted your message and sent you a PM explaining why."
            )
            await self.client.send_message(message.author,
                f"Your message \"{message.content}\" contains the blacklisted words {bad_matches!r}. Please refrain from using them in the future!\n\nIf you believe this is in error, please contact @Alabaster#6514."
            )
            await self.client.send_message(self.get_channel(self.config['log_channel']),
                f"Message from {message.author.mention} deleted in #{message.channel.name} for containing the words {bad_matches!r}: \"{message.content}\"."
            )
            delta = sum(self.score_of(i) for i in bad_matches)
            final = self.score.add_score(message.author.id, delta)
            if final > self.config['ban_score']:
                await self.do_ban(message.author, final)

        if crisis_matches:
            await self.client.send_message(self.get_channel(self.config['crisis_channel']),
                f"{message.author.mention} sent a critical message containing {crisis_matches!r} in #{message.channel.name}: \"{message.content}\"."
            )
