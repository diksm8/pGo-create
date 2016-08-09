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
<<<<<<< HEAD

	while counter != accounts:
		username = idGenerator(size)
		anonbox = pokeAnonbox()
		email = anonbox.email
		_password = password if password != None else idGenerator(12, string.ascii_uppercase + string.ascii_lowercase + string.digits)
=======
	driver = webdriver.Chrome()
	outfile = open(outfile, 'r+' if os.path.exists(outfile) else 'w+')

	'''
	# Load existing accounts
	if (outfile.read(1) == ""):
		accounts_array = []
	else:
		outfile.seek(0)
		accounts_array = json.load(outfile)
		'''
	while counter != accounts:
		username = id_generator(size)
		anonbox = make_anonbox()
		email = anonbox[0]
		_password = password if password != None else id_generator(12, string.ascii_uppercase + string.ascii_lowercase + string.digits)
		
		d = make_account(username, _password, email, driver)
		d['ToS accepted'] = accept_tos(username, _password)
		d['Email accepted'] = accept_email(anonbox[1], username)

		accountStore.accounts.append(d)
		accountStore.save()

		counter+=1
		click.echo('Account %s written to file. Completed %s accounts.' % (username, counter)) 
	accountStore.done()
>>>>>>> refs/remotes/origin/master

		d = [False, 0]

		d = makeClubAccount(username, _password, email)
		if type(d) == dict:
			click.echo('Account %s created' % username)
		else:
			click.echo('Account %s couldn\'t be created (error at stage %d), skipping.' % (username, d[1]))
			continue

		tosAcceptState = acceptTOS(username, _password)
		if tosAcceptState:
			click.echo('Accepted Terms of Service for user %s' % username)
		d['TOS accepted'] = tosAcceptState
		d['Email accepted'] = anonbox.accept()

		accountStore.accounts.append(d)
		accountStore.save()
		counter += 1

		click.echo('Account %s written to file. Completed %s accounts.' % (username, counter)) 
	accountStore.done()

def idGenerator(size, chars=string.ascii_uppercase + string.digits):
	return ''.join(random.choice(chars) for _ in range(size))

def acceptTOS(username, password):
	api = PGoApi()
	api.set_position(40.7127837, -74.005941, 0.0)
	api.login('ptc', username, password)
	time.sleep(2)
	req = api.create_request()
	req.mark_tutorial_complete(tutorials_completed = 0, send_marketing_emails = False, send_push_notifications = False)
	response = req.call()
<<<<<<< HEAD
	if type(response) == dict and response['status_code'] == 1 and response['responses']['MARK_TUTORIAL_COMPLETE']['success'] == True:
		return True
	else:
		return False

def makeClubAccount(username, password, email, dob='1986-12-12', country='US'):
	signupUrl  = 'https://club.pokemon.com/us/pokemon-trainer-club/sign-up/'
	parentSignupUrl = 'https://club.pokemon.com/us/pokemon-trainer-club/parents/sign-up'

	session = requests.Session()
	session.headers.update({
		'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
		'Accept-Encoding': 'gzip, deflate, sdch, br',
		'Accept-Language': 'pl-PL,pl;q=0.8,en-US;q=0.6,en;q=0.4',
		'Cache-Control': 'max-age=0',
		'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.79 Safari/537.36 Edge/14.14393'
	})
	
	# Get cookies first.
	retryCount = 0
	while True:
		try:
			req = session.get(signupUrl, timeout=3)
			if ('overwhelming demand for access' in req.text):
				print('under maintenance, retrying')
				continue
			break
		except:
			retryCount += 1
			if retryCount > 4:
				return [False, 0]
	if u'Create Your Pokémon Trainer Club Account' not in req.text:
		return [False, 0]
	csrfCookie = requests.utils.dict_from_cookiejar(session.cookies)['csrftoken']

	stageOneData = {
		'csrfmiddlewaretoken': csrfCookie,
		'dob': dob,
		'undefined': int(dob.split('-')[1])-1,
		'undefined': dob.split('-')[0],
		'country': country,
		'country': country,
	}
	stageTwoData = {
		'csrfmiddlewaretoken': csrfCookie,
		'username': username,
		'password': password,
		'confirm_password': password,
		'email': email,
		'confirm_email': email,
		'public_profile_opt_in': True,
		'screen_name': username,
		'terms': 'on',
	}

	retryCount = 0
	while True:
		try:
			req = session.post(signupUrl, data=stageOneData, headers = {'Referer': signupUrl}, timeout=3)
			if ('overwhelming demand for access' in req.text):
				print('under maintenance, retrying')
				continue
			break
		except:
			retryCount += 1
			if retryCount > 4:
				return [False, 1]
	
	if u'Your username is the name you will use to sign in to your account. Only you will see this name.' not in req.text:
		return [False, 1]

	retryCount = 0
	while True:
		try:
			req = session.post(parentSignupUrl, data=stageTwoData, headers = {'Referer': parentSignupUrl}, timeout=6)
			if ('overwhelming demand for access' in req.text):
				print('under maintenance, retrying')
				continue
			break
		except:
			retryCount +=1
			if retryCount > 8:
				return [False, 2]

	
		if u'Thank you for creating a Pokémon Trainer Club account.' not in req.text:
			return [False, 2]

=======
	return True if type(response) == dict and response['status_code'] == 1 and response['responses']['MARK_TUTORIAL_COMPLETE']['success'] == True else False

def make_account(username, password, email, driver):
	driver.get("https://club.pokemon.com/us/pokemon-trainer-club/sign-up/")
	#elem = driver.find_element_by_name("dob")
	driver.implicitly_wait(3)
	driver.execute_script("document.getElementById('id_dob').removeAttribute('readonly')")
	driver.execute_script("document.getElementById('id_dob').value='1986-12-12'")
	driver.find_element_by_class_name('continue-button').click()
	driver.find_element_by_id('id_username').send_keys(username)
	driver.find_element_by_id('id_password').send_keys(password)
	driver.find_element_by_id('id_confirm_password').send_keys(password)
	driver.find_element_by_id('id_email').send_keys(email)
	driver.find_element_by_id('id_confirm_email').send_keys(email)
	driver.find_element_by_id('id_screen_name').send_keys(username)
	driver.find_element_by_id('id_terms').click()
	driver.find_element_by_class_name('button-green').click()
>>>>>>> refs/remotes/origin/master
	return {
			'Username': username,
			'Password': password,
			'Email': email,
			'Date created': time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()),
<<<<<<< HEAD
			'TOS accepted': False,
			'Email accepted': False
	}

class pokeAnonbox():
	def __init__(self):
		req = requests.get('https://anonbox.net/en/', verify=False)
		tree = html.fromstring(req.text.encode())
		self.email = tree.get_element_by_id('content').find('dl')[1].text_content()
		self.inbox = tree.get_element_by_id('content').find('dl')[3].text_content()
		self.accepted = False
	def accept(self):
		counter = 0
		while counter != 60:
			emails = requests.get(self.inbox, verify=False).text
			if len(emails) <= 1:
				time.sleep(0.2)
				counter += 1
				continue
			for line in emails.split('\n'):
				if line.startswith('https://'):
					if 'Thank you for signing up! Your account is now active.' in requests.get(line).text:
						self.accepted = True
						return True
					return False
		return False


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
=======
			'ToS accepted': False,
			'Email accepted': False
		}

def make_anonbox():
	anonbox = requests.get('https://anonbox.net/en/', verify=False)
	tree = html.fromstring(anonbox.text.encode())
	address = tree.get_element_by_id('content').find('dl')[1].text_content()
	inbox = tree.get_element_by_id('content').find('dl')[3].text_content()
	return([address,inbox])
>>>>>>> refs/remotes/origin/master

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
		json.dump(self.accounts, self.accountsFile, indent=4)
	def done(self):
		self.accountsFile.seek(0)
		json.dump(self.accounts, self.accountsFile, indent=4)
		self.accountsFile.close

if __name__ == '__main__':
	main()