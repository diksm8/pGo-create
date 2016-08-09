#!/usr/bin/python
# -*- coding: utf-8 -*-
from pgoapi import PGoApi
from pgoapi.utilities import f2i
from pgoapi import utilities as util
from pgoapi.exceptions import AuthException
from lxml import html
import click, time, random, string, json, sys, os, requests

requests.packages.urllib3.disable_warnings()
reload(sys)
sys.setdefaultencoding('utf-8')

@click.command()
@click.option('--accounts', default=50, help='Number of accounts to make, default is 50.')
@click.option('--size', default=10, type=click.IntRange(6, 16, clamp=True), help='Username size, range between 5 and 20.')
@click.option('--password', default=None, help='Password for accounts')
@click.argument('outfile', default='accounts.json', required=False)

def main(accounts, size, password, outfile):
	"""This is a script to create Pokémon Go (PTC) accounts and accept the Terms of Service. Made by two skids who can't code for shit."""
	counter = 0
	accountStore = pokeAccountStore(outfile)

	while counter != accounts:
		username = idGenerator(size)
		anonbox = make_anonbox()
		email = anonbox[0]
		_password = password if password != None else idGenerator(12, string.ascii_uppercase + string.ascii_lowercase + string.digits)

		retryCount = 0
		d = False
		while retryCount < 10:
			d = makeClubAccount(username, _password, email)
			if d:
				click.echo('Account %s created' % username)
				break
			else:
				click.echo('Error while creating account %s, retrying (retry count %d)' % (username, retryCount))
				retryCount += 1
				continue
		if d == False:
			click.echo('Account %s couldn\'t be created, skipping.' % username)
			continue

		acceptTOS(username, _password)
		click.echo('Accepted Terms of Service for user {}'.format(username))
		d['TOS accepted'] = True
		d['Email accepted'] = acceptEmail(anonbox[1], username)

		accountStore.accounts.append(d)
		accountStore.save()
		counter += 1
		
		click.echo('Account %s written to file. Completed %s accounts.' % (username, counter)) 
	accountStore.done()

def idGenerator(size, chars=string.ascii_uppercase + string.digits):
	return ''.join(random.choice(chars) for _ in range(size))

def acceptEmail(box, username):
	counter = 0
	while counter != 60:
		emails = requests.get(box, verify=False).text
		if len(emails) <= 1:
			time.sleep(0.2)
			counter += 1
			continue
		for line in emails.split('\n'):
			if line.startswith('https://'):
				return True if 'Thank you for signing up! Your account is now active.' in requests.get(line).text else False
	return False

def acceptTOS(username, password):
	api = PGoApi()
	api.set_position(40.7127837, -74.005941, 0.0)
	api.login('ptc', username, password)
	time.sleep(2)
	req = api.create_request()
	req.mark_tutorial_complete(tutorials_completed = 0, send_marketing_emails = False, send_push_notifications = False)
	response = req.call()

def makeClubAccount(username, password, email, dob='1986-12-12', country='US'):
	headers = {
		'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
		'Accept-Encoding': 'gzip, deflate, sdch, br',
		'Accept-Language': 'pl-PL,pl;q=0.8,en-US;q=0.6,en;q=0.4',
		'Cache-Control': 'max-age=0',
		'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.79 Safari/537.36 Edge/14.14393'
	}
	signupUrl  = 'https://club.pokemon.com/us/pokemon-trainer-club/sign-up/'
	parentSignupUrl = 'https://club.pokemon.com/us/pokemon-trainer-club/parents/sign-up'

	session = requests.Session()
	session.headers.update(headers)
	
	# Get cookies first.
	req = session.get(signupUrl)
	if u'Create Your Pokémon Trainer Club Account' not in req.text:
		return False
	csrfCookie = requests.utils.dict_from_cookiejar(session.cookies)['csrftoken']

	req = session.post(signupUrl, data={
		'csrfmiddlewaretoken': csrfCookie,
		'dob': dob,
		'undefined': 7,
		'undefined': dob.split('-')[0],
		'country': country,
		'country': country,
	}, headers = {'Referer': signupUrl})
	
	if u'Your username is the name you will use to sign in to your account. Only you will see this name.' not in req.text:
		return False

	req = session.post(parentSignupUrl, data={
		'csrfmiddlewaretoken': csrfCookie,
		'username': username,
		'password': password,
		'confirm_password': password,
		'email': email,
		'confirm_email': email,
		'public_profile_opt_in': True,
		'screen_name': username,
		'terms': 'on',
	}, headers = {'Referer': parentSignupUrl})

	if u'Thank you for creating a Pokémon Trainer Club account.' not in req.text:
		return False

	return {
			'Username': username,
			'Password': password,
			'Email': email,
			'Date created': time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()),
			'TOS accepted': False,
			'Email accepted': False
	}

def make_anonbox():
	anonbox = requests.get('https://anonbox.net/en/', verify=False)
	tree = html.fromstring(anonbox.text.encode())
	address = tree.get_element_by_id('content').find('dl')[1].text_content()
	inbox = tree.get_element_by_id('content').find('dl')[3].text_content()
	return([address,inbox])

class pokeAccountStore:
	def __init__(self, accountsFile):
		self.accountsFile = open(accountsFile, 'r+' if os.path.exists(accountsFile) else 'w+')
		if (self.accountsFile.read(1) == ""):
			self.accounts = []
		else:
			self.accountsFile.seek(0)
			self.accounts = json.load(self.accountsFile)
	def save(self):
		self.accountsFile.seek(0)
		json.dump(self.accounts, self.accountsFile, indent=2)
	def done(self):
		self.accountsFile.seek(0)
		json.dump(self.accounts, self.accountsFile, indent=2)
		self.accountsFile.close

if __name__ == '__main__':
	main()