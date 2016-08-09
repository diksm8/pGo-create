#!/usr/bin/python
# -*- coding: utf-8 -*-
from pgoapi import PGoApi
from pgoapi.utilities import f2i
from pgoapi import utilities as util
from pgoapi.exceptions import AuthException
from lxml import html
import click, time, random, string, json, sys, os, requests, threading, Queue

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
	global accountStore
	accountStore = pokeAccountStore(outfile)
	accountCounter = 0

	threads = []
	for _ in range(4):
		for x in [ worker_accountCreator, worker_tosAccepter, worker_mailAccepter ]:
			thread = threading.Thread(target=x)
			thread.daemon = True
			thread.start()
			threads.append(thread)

	def pushNewAccount():
		newAccount = accountObject(accountStore)
		newAccount.username = idGenerator(size)
		newAccount.password = password if password != None else idGenerator(12, string.ascii_uppercase + string.ascii_lowercase + string.digits)
		creatorQueue.put(newAccount)

	for _ in range(accounts):
		pushNewAccount()

	while True:
		if accountCounter == accounts:
			break
		logItem = logQueue.get()
		if type(logItem) != bool:
			if logItem == "WRITE BLYAD":
				accountStore.save()
			else:
				print(logItem)
		elif logItem == True:
			accountCounter += 1
		else:
			pushNewAccount()

	#for x in threads:
	#	thread.join()
	accountStore.done()

def worker_accountCreator():
	while True:
		Account = creatorQueue.get()
		while True:
			Account = makeClubAccount(Account)
			if Account.errorState == None:
				logQueue.put('Created account '+Account.username)
				Account.save()
				logQueue.put('WRITE BLYAD')
				tosQueue.put(Account)
				break
			else:
				logQueue.put(False)


def worker_tosAccepter():
	while True:
		Account = tosQueue.get()
		Account.acceptTos()
		if Account.tosAccept == True:
			logQueue.put('Accepted TOS for account '+Account.username)
		Account.save()
		logQueue.put('WRITE BLYAD')
		verifierQueue.put(Account)

def worker_mailAccepter():
	while True:
		Account = verifierQueue.get()
		Account.emailAccept = Account.mailbox.accept()
		if Account.emailAccept == True:
			logQueue.put('Accepted email for account '+Account.username)
		logQueue.put(True)
		Account.makeDictionary()
		Account.save()
		logQueue.put('WRITE BLYAD')

def idGenerator(size, chars=string.ascii_uppercase + string.digits):
	return ''.join(random.choice(chars) for _ in range(size))

def makeClubAccount(accObj):
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
				continue
			break
		except:
			retryCount += 1
			if retryCount > 4:
				accObj.errorState = 0
				return accObj
	if u'Create Your Pokémon Trainer Club Account' not in req.text:
		accObj.errorState = 0
		return accObj
	csrfCookie = requests.utils.dict_from_cookiejar(session.cookies)['csrftoken']

	stageOneData = {
		'csrfmiddlewaretoken': csrfCookie,
		'dob': accObj.dob,
		'undefined': int(accObj.dob.split('-')[1])-1,
		'undefined': accObj.dob.split('-')[0],
		'country': accObj.country,
		'country': accObj.country,
	}
	stageTwoData = {
		'csrfmiddlewaretoken': csrfCookie,
		'username': accObj.username,
		'password': accObj.password,
		'confirm_password': accObj.password,
		'email': accObj.mailbox.email,
		'confirm_email': accObj.mailbox.email,
		'public_profile_opt_in': True,
		'screen_name': accObj.username,
		'terms': 'on',
	}

	retryCount = 0
	while True:
		try:
			req = session.post(signupUrl, data=stageOneData, headers = {'Referer': signupUrl}, timeout=3)
			if ('overwhelming demand for access' in req.text):
				continue
			break
		except:
			retryCount += 1
			if retryCount > 4:
				accObj.errorState = 1
				return accObj
	
	if u'Your username is the name you will use to sign in to your account. Only you will see this name.' not in req.text:
		accObj.errorState = 1
		return accObj

	retryCount = 0
	while True:
		try:
			req = session.post(parentSignupUrl, data=stageTwoData, headers = {'Referer': parentSignupUrl}, timeout=6)
			if ('overwhelming demand for access' in req.text):
				continue
			break
		except:
			retryCount +=1
			if retryCount > 8:
				accObj.errorState = 1
				return accObj

		if u'Thank you for creating a Pokémon Trainer Club account.' not in req.text:
			accObj.errorState = 1
			return accObj

	accObj.makeDictionary()
	return accObj

class pokeAnonbox:
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
		self.accountsFile.truncate()
		json.dump(self.accounts, self.accountsFile, indent=2)
	def add(self, acc):
		self.accounts.append(acc)
	def upd(self, pos, acc):
		self.accounts[pos] = acc
	def done(self):
		self.save()
		self.accountsFile.close

class accountObject:
	def __init__(self, accountStore=None):
		self.username = None
		self.password = None
		self.country = 'US'
		self.dob = '1986-12-12'
		self.mailbox = pokeAnonbox()
		self.creationDate = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
		self.tosAccept = False
		self.emailAccept = False
		self.dictionary = {}
		self.errorState = None
		self.storeIndex = None
		self.accountStore = accountStore
	def acceptTos(self):
		api = PGoApi()
		api.set_position(40.7127837, -74.005941, 0.0)
		api.login('ptc', self.username, self.password)
		time.sleep(2)
		req = api.create_request()
		req.mark_tutorial_complete(tutorials_completed = 0, send_marketing_emails = False, send_push_notifications = False)
		response = req.call()
		if type(response) == dict and response['status_code'] == 1 and response['responses']['MARK_TUTORIAL_COMPLETE']['success'] == True:
			self.tosAccept = True
			self.makeDictionary()
	def makeDictionary(self):
		self.dictionary = {
			'Username': self.username,
			'Password': self.password,
			'Email': self.mailbox.email,
			'Date created': time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()),
			'TOS accepted': self.tosAccept,
			'Email accepted': self.emailAccept
		}
	def save(self):
		if self.accountStore != None:
			if self.storeIndex == None:
				self.storeIndex = len(self.accountStore.accounts)
				self.accountStore.add(self.dictionary)
			else:
				self.accountStore.upd(self.storeIndex, self.dictionary)
if __name__ == '__main__':
	creatorQueue = Queue.Queue()
	tosQueue = Queue.Queue()
	verifierQueue = Queue.Queue()
	logQueue = Queue.Queue()

	main()