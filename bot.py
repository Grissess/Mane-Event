import discord, asyncio, re, os, datetime, traceback, random, threading, asyncio, time, sqlite3
import string
import ctypes
import json

ctypes.windll.kernel32.SetConsoleTitleW("Mane Event 0.0.1")

config = json.load(open('config.json'))
token = config['token']

def console_print(message):
	timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
	print(f'{timestamp} {message}')

db = sqlite3.connect('bot.sqlite3')
cur = db.cursor()
cur.execute('CREATE TABLE IF NOT EXISTS ban_scores (user_id INTEGER PRIMARY KEY, score)')

def get_score(uid):
	cur.execute('SELECT score FROM ban_scores WHERE user_id = ?', (uid,))
	row = cur.fetchone()
	if row is None:
		return 0
	return row[0]

def set_score(uid, score):
	cur.execute('INSERT OR REPLACE INTO ban_scores (user_id, score) VALUES (?, ?)', (uid, score))
	db.commit()

def add_score(uid, delta_score):
	set_score(uid, get_score(uid) + delta_score)

SCORE_LIM = 5  # XXX change when more severe increments occur

client = discord.Client()

async def add_score_with_ban(user, delta_score):
	add_score(user.id, delta_score)
	score = get_score(user.id)
	if score > SCORE_LIM:  # strictly > per design spec
		set_score(user.id, 0)  # XXX maybe delete to keep db small
		await send_mod_message(f'{user.name}\U0001F528 (score was {score})') # XXX ban

async def send_mod_message(msg):
	await client.send_message(discord.Object(id='400472944049913867'), msg)

# This converts 'badwords.txt' to a string and prints it in the console
#linestring = open('badwords.txt', 'r').read()
#print (linestring.split('\n'))

@client.event
async def on_ready():
	console_print(' ')
	console_print('Logged in as:')
	console_print(client.user.name)
	console_print(client.user.id)
	console_print(' ')
	console_print('--Server List--')
	for server in client.servers:
		console_print(server.name)
		console_print(' ')
		time.sleep(2)
		console_print('DONE!')
		console_print(' ')

ONE_DAY = datetime.timedelta(days=1)
goal_time = datetime.time(10, 0, 0)
now = datetime.datetime.now() + ONE_DAY
goal = now.replace(hour=goal_time.hour, minute=goal_time.minute, second=goal_time.second, microsecond=0)

loop = asyncio.get_event_loop()

async def good_morning():
	global goal

	now = datetime.datetime.now()
	#print('check', (now.year, now.month, now.day, now.hour, now.minute, now.second), (goal.year, goal.month, goal.day, goal.hour, goal.minute, goal.second))
	# Check for inequality down to the second
	if (now.year, now.month, now.day, now.hour, now.minute, now.second) >= (goal.year, goal.month, goal.day, goal.hour, goal.minute, goal.second):

		today   = datetime.date.today()
		# The date of the next convention (YYYY, MM, DD)
		futdate = datetime.date(2018, 7, 26)

		now     = datetime.datetime.now()
		mnight  = now.replace(hour=0, minute=0, second=0, microsecond=0)
		seconds = (mnight - now).seconds
		days    = (futdate - today).days
		hms     = str(datetime.timedelta(seconds=seconds))
		print ("%d days until BronyCon 2018" % (days))

		# Greeting
		msga = random.choice(['Good morning Baltimare!', 'Another lovely day in Baltimare!', 'It\'s PonyTime!', 'Today is going to be a good day!'])
		# Conversation starter
		msgb = random.choice(['How\'s everypony doing?', 'Today\'s topic: "Pancakes, syrup or butter?"', 'What\'s new with everypony?', 'Who\'s excited for BronyCon 2018?', 'Anypony have any interesting plans for today?'])
		# Time until BronyCon
		msgc = random.choice(['Only {} days until BronyCon!', '{} days left? BronyCon is right around the corner!', 'Oh Celestia, only {} days until BronyCon starts, how exciting!'])
		msgc = msgc.format(days)
		# Additional info
		msgd = random.choice(['Have you registered for your badge yet? https://www.bronycon.org/register', 'Have an event or panel you want to run this year? Don\'t hesitate! Put in your application now! https://www.bronycon.org/events/run-an-event', 'Do you have what it takes to help make BronyCon an amazing event for all ages? Apply for staff at https://www.bronycon.org/about/volunteer/staff'])
		#await client.send_message(discord.Object(id='370668218546913280'), msga + ' ' + msgb + ' ' + msgc + ' ' + msgd)
		print(msga + ' ' + msgb + ' ' + msgc + ' ' + msgd)
		print('Good Morning message sent!')
		# Prepare the next goal time
		goal = (now + ONE_DAY).replace(hour=goal_time.hour, minute=goal_time.minute, second=goal_time.second, microsecond=0)

	# In all cases, ensure this is rescheduled (0.5 might be a little eager, but the value does have to be strictly <1 for second accuracy)
	loop.call_later(0.5, asyncio.ensure_future, good_morning())

# Schedule the first run to kick off the loop
loop.call_soon(asyncio.ensure_future, good_morning())

# string 'BannedWords' is words to delete
BannedWords = []
with open('badwords.txt') as f:
    BannedWords = f.read().splitlines()
BannedWords = set([x.lower() for x in BannedWords])
BannedScores = dict((word, 1) for word in BannedWords)

# string 'KeyWords' is keywords to notify the mod team about
KeyWords = ['keyword', 'suicide', 'kill myself', 'cut myself', 'hang myself', 'noose']

puncTranslator = str.maketrans('', '', string.punctuation)

with open('words.txt') as f:
    GoodWords = set(f.read().splitlines())

def getBadMatches(message):
    testMessage = message.lower()

    while True:
        #print 'Testing {0}'.format(testMessage)
        badMatches = [word for word in BannedWords if word in testMessage]
        if not badMatches:
            return badMatches
        badMatch = badMatches[0]
        #print 'Banned word {0}'.format(badMatch)
        possibleGoodWords = [word for word in GoodWords if badMatch in word]
        matchingGoodWords = [word for word in possibleGoodWords if word in testMessage]
        matchingGoodWords.sort(key=len, reverse=True)

        #print 'Matching good words {0}'.format(matchingGoodWords)

        if not matchingGoodWords:
            #print 'FAILED'
            return badMatches
        else:
            testMessage = testMessage.replace(matchingGoodWords[0], '', 1)

@client.event
async def on_message_edit(beforeMsg, afterMsg):
	await on_message(afterMsg)

@client.event
async def on_message(message):
	"""if message.channel.id != '370700700809691136':
		print('Ignoring a message not from #bot-testing for now...')
		return"""

	testMsg = message.content.lower().translate(puncTranslator)
	testWords = testMsg.lower().split()

	# Uncomment this line / comment "getBadMatches" to switch away from word whitelist
	#badMatches = [word for word in testWords if word in BannedWords]
	badMatches = getBadMatches(testMsg)
	badScore = sum([BannedScores[word] for word in badMatches])

	keyMatches = [word for word in KeyWords if word in testMsg]
	if message.author.bot:
		print('I ignored a bot message!')
	elif any(badMatches):
		#await client.delete_message(message)
		msg = '{0.author.mention}, I\'ve deleted your message and sent you a PM explaining why.'.format(message)
		#await client.send_message(message.channel, msg)
		msg = 'Your message "{}" contains the blacklisted word(s) "{}". Please refrain from using them in the future!'.format(message.content, badMatches)
		#await client.send_message(message.author, msg)
		msg = 'I\'ve deleted a message from @{} in #{} containing the words {}: "{}".'.format(
			message.author.name, message.channel.name, badMatches, message.content)
		await send_mod_message(msg)
		await add_score_with_ban(message.author, badScore)
		print(msg)
	elif any(keyMatches):
		msg = 'User @{} mentioned keyword {} in #{}: "{}"'.format(
			message.author.name, keyMatches, message.channel.name, message.content)
		await client.send_message(discord.Object(id='370664588167086090'), msg)
		print(msg)
	return

#	elif message.content.startswith('!help') and "panel" or "activity" or "event" in message.content:
#			await client.send_message(message.channel, 'For panel and activity registration, go to: http://bronycon.org/events/run-an-event/')

client.run(token)
