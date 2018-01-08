import discord
import asyncio
import re
import os
import datetime
import traceback

client = discord.Client()

# This converts 'badwords.txt' to a string and prints it in the console
#linestring = open('badwords.txt', 'r').read()
#print (linestring.split('\n'))

@client.event
async def on_ready():
	print('Logged in as')
	print(client.user.name)
	print(client.user.id)
	print('--Server List--')
	for server in client.servers:
		print(server.name)

# string a is words to delete
BannedWords = ['ahole', 'anus', 'ash0le', 'ash0les', 'asholes', 'ass ', ' ass', 'assmonkey', 'assface', 'assh0le', 'assh0lez', 'asshole', 'asshole', 'assholes', 'assholz', 'asswipe', 'azzhole', 'bassterds', 'bastard', 'bastards', 'bastardz', 'basterds', 'basterdz', 'biatch', 'bitch', 'bitches', 'blowjob', 'boffing', 'bullshit', 'butthole', 'buttwipe', 'c0ck', 'c0cks', 'c0k', 'carpetmuncher', 'cawk', 'cawks', 'clit', 'cnts', 'cntz', 'cock', 'cockhead', 'cockhead', 'cocks', 'cocksucker', 'cocksucker', 'cum ', ' cum', 'cunt', 'cunts', 'cuntz', 'dick', 'dild0', 'dild0s', 'dildo', 'dildos', 'dilld0', 'dilld0s', 'dominatricks', 'dominatrics', 'dominatrix', 'dyke', 'enema', 'fag', 'fag1t', 'faget', 'fagg1t', 'faggit', 'faggot', 'fagit', 'fags', 'fagz', 'faig', 'faigs', 'fart', 'flipping', 'fuck', 'fucker', 'fuckin', 'fucking', 'fucks', 'fudgepacker', 'fuk', 'fukah', 'fuken', 'fuker', 'fukin', 'fukk', 'fukkah', 'fukken', 'fukker', 'fukkin', 'g00k', 'gay', 'gaybor', 'gayboy', 'gaygirl', 'gays', 'gayz', 'goddamned', 'h00r', 'h0ar', 'h0re', 'hells', 'hoar', 'hoor', 'hoore', 'jackoff', 'jap', 'japs', 'jerkoff', 'jisim', 'jiss', 'jizm', 'jizz', 'knob', 'knobs', 'knobz', 'kunt', 'kunts', 'kuntz', 'lesbian', 'lezzian', 'lipshits', 'lipshitz', 'masochist', 'masokist', 'massterbait', 'masstrbait', 'masstrbate', 'masterbaiter', 'masterbate', 'masterbates', 'mutha', 'fuker', 'motha', 'fucker', 'fuker', 'fukka', 'fukkah', 'fucka', 'fuchah', 'fukker', 'fukah', 'mothafucker', 'mothafuker', 'mothafukkah', 'mothafukker', 'motherfucker', 'motherfukah', 'motherfuker', 'motherfukkah', 'motherfukker', 'motherfucker', 'muthafucker', 'muthafukah', 'muthafuker', 'muthafukkah', 'muthafukker', 'mutha', 'n1gr', 'nastt', 'nasty', 'nigger', 'nigur', 'niiger', 'niigr', 'orafis', 'orgasim', 'orgasm', 'orgasum', 'oriface', 'orifice', 'orifiss', 'packi', 'packie', 'packy', 'paki', 'pakie', 'paky', 'pecker', 'peeenus', 'peeenusss', 'peenus', 'peinus', 'pen1s', 'penas', 'penis', 'penisbreath', 'penus', 'penuus', 'phuc', 'phuck', 'phuk', 'phuker', 'phukker', 'polac', 'polack', 'polak', 'poonani', 'pr1c', 'pr1ck', 'pr1k', 'pusse', 'pussee', 'pussy', 'puuke', 'puuker', 'queer', 'queers', 'queerz', 'qweers', 'qweerz', 'qweir', 'recktum', 'rectum', 'retard', 'sadist', 'scank', 'schlong', 'screwing', 'semen', 'sex', 'sexx', 'sexxx', 'sx', 'sexy', 'sht', 'sh1t', 'sh1ter', 'sh1ts', 'sh1tter', 'sh1tz', 'shit', 'shits', 'shitter', 'shitty', 'shity', 'shitz', 'shyt', 'shyte', 'shytty', 'shyt', 'skanck', 'skank', 'skankee', 'skankey', 'skanks', 'skanky', 'slut', 'sluts', 'slutty', 'slutz', 'sonofabitch', 'tit', 'turd', 'va1jina', 'vag1na', 'vagiina', 'vagina', 'vaj1na', 'vajina', 'vullva', 'vulva', 'w0p', 'wh00r', 'wh0re', 'whore', 'xrated', 'xxx', 'bch', 'bitch', 'blowjob', 'clit', 'arschloch', 'fuck', 'shit', 'ass', 'asshole', 'btch', 'b17ch', 'b1tch', 'bastard', 'bich', 'boiolas', 'buceta', 'c0ck', 'cawk', 'chink', 'cipa', 'clits', 'cock', 'cum', 'cunt', 'dildo', 'dirsa', 'ejakulate', 'fatass', 'fcuk', 'fuk', 'fux0r', 'hoer', 'hore', 'jism', 'kawk', 'l3itch', 'l3i+ch', 'lesbian', 'masturbate', 'masterbat', 'masterbat3', 'motherfucker', 's.o.b.', 'mofo', 'nazi', 'nigga', 'niggas', 'nigger', 'nutsack', 'phuck', 'pimpis', 'pusse', 'pussy', 'scrotum', 'shemale', 'shi+', 'shitt', 'slut', 'smut', 'teets', 'tits', 'boobs', 'b00bs', 'teez', 'testical', 'testicle', 'titt', 'w00se', 'jackoff', 'wank', 'whoar', 'whore', 'damn', 'dyke', 'fuck', 'shit', '@$$', 'amcik', 'andskota', 'arse', 'assrammer', 'ayir', 'bi7ch', 'bitch', 'bollock', 'breasts', 'buttpirate', 'cabron', 'cazzo', 'chraa', 'chuj', 'cock', 'cunt', 'd4mn', 'daygo', 'dego', 'dick', 'dike', 'dupa', 'dziwka', 'ejackulate', 'ekrem', 'ekto', 'enculer', 'faen', 'fag', 'fanculo', 'fanny', 'feces', 'feg', 'felcher', 'ficken', 'fitt', 'flikker', 'foreskin', 'fotze', 'fu', 'fuk', 'futkretzn', 'gay', 'gook', 'guiena', 'h0r', 'h4x0r', 'hell', 'helvete', 'hoer', 'honkey', 'huevon', 'hui', 'injun', 'jizz', 'kanker', 'kike', 'klootzak', 'kraut', 'knulle', 'kuk', 'kuksuger', 'kurac', 'kurwa', 'kusi', 'kyrpa', 'lesbo', 'mamhoon', 'masturbat', 'merd', 'mibun', 'monkleigh', 'mouliewop', 'muie', 'mulkku', 'muschi', 'nazis', 'nepesaurio', 'nigger', 'orospu', 'paska', 'perse', 'picka', 'pierdol', 'pillu', 'pimmel', 'piss', 'pizda', 'poontsee', 'poop', 'porn', 'p0rn', 'pr0n', 'preteen', 'pula', 'pule', 'puta', 'puto', 'qahbeh', 'queef', 'rautenberg', 'schaffer', 'scheiss', 'schlampe', 'schmuck', 'screw', 'sharmuta', 'sharmute', 'shipal', 'shiz', 'skrib']
# string b is keywords to notify the mod team about
KeyWords = ['keyword', 'suicide', 'kill myself', 'cut myself', 'hang myself', 'noose']

@client.event
async def on_message(message):
	testMessage = message.content.lower()
	badMatches = [word for word in BannedWords if word + ' ' in testMessage or ' ' + word in testMessage]
	keyMatches = [word for word in KeyWords if word + ' ' in testMessage or ' ' + word in testMessage]
	if message.author.bot:
		print('I ignored a bot message!')
	elif any(badMatches):
		await client.delete_message(message)
		msg = '{0.author.mention}, I\'ve deleted your message and sent you a PM explaining why.'.format(message)
		await client.send_message(message.channel, msg)
		msg = 'The content {} is on the word blacklist for the BronyCon Discord Server. Please refrain from using it in the future.'.format(badMatches)
		await client.send_message(message.author, msg)
		msg = 'I\'ve deleted a message from @{} in #{} containing the word {}.'.format(message.author.name, message.channel.name, badMatches)
		await client.send_message(discord.Object(id='370664588167086090'), msg)
		print(msg)
	elif any(keyMatches):
		msg = 'User @{} mentioned keyword {} in #{}'.format(message.author.name, keyMatches, message.channel.name)
		await client.send_message(discord.Object(id='370664588167086090'), msg)
		print(msg)
	return


#	elif message.content.startswith('!help') and "panel" or "activity" or "event" in message.content:
#			await client.send_message(message.channel, 'For panel and activity registration, go to: http://bronycon.org/events/run-an-event/')

client.run('Mzk5NDczNDc1NTM1NzY1NTA1.DTNq1A.nabOxq8x-OLi_pOmG3VOfMQ53JE')