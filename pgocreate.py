#!/usr/bin/python
# -*- coding: utf-8 -*-
from pgoapi import PGoApi
from pgoapi.utilities import f2i
from pgoapi import utilities as util
from pgoapi.exceptions import AuthException, NotLoggedInException, ServerSideRequestThrottlingException
from lxml import html
import click, colorama, time, random, string, json, sys, os, requests, threading, Queue

requests.packages.urllib3.disable_warnings()
reload(sys)
sys.setdefaultencoding('utf-8')


@click.option('--accounts', default=50, help='Number of accounts to make, default is 50.')
@click.option('--size', default=10, type=click.IntRange(6, 16, clamp=True), help='Username size, range between 5 and 20.')
@click.option('--password', default=None, help='Password to use for all accounts. If this option is not used passwords will be randomized for each account.')
@click.option('--threads', default=4, type=click.IntRange(1,128, clamp=True), help='Amount of threads for each task, range between 1 and 128. Default is 4, no more than 16 is recommended.')
@click.option('--pos', nargs=2, type=float, required=True, help='Position in LAT and LON, ex. --pos LAT LON.')
@click.argument('outfile', default='accounts.json', required=False)
@click.command()
def main(accounts, size, password, threads, pos, outfile):
	"""This is a script to create Pokémon Go (PTC) accounts and accept the Terms of Service. Made by two skids who can't code for shit."""
	global accountStore
	accountStore = pokeAccountStore(outfile)

	accountCounters = [0,0,0,accounts]

	threadsArr = []
	if threads > accounts:
		threads = accounts
	for _ in range(threads):
		for x in [ worker_accountCreator, worker_tosAccepter, worker_mailAccepter ]:
			thread = threading.Thread(target=x, args=(accountCounters, ))
			thread.daemon = True
			thread.start()
			threadsArr.append(thread)

	def pushNewAccount():
		newAccount = accountObject(accountStore)
		newAccount.username = idGenerator(size)
		newAccount.password = password if password != None else idGenerator(12, string.ascii_uppercase + string.ascii_lowercase + string.digits)
		newAccount.pos = pos
		creatorQueue.put(newAccount)

	for _ in range(accounts):
		pushNewAccount()

	while True:
		logItem = logQueue.get()
		if type(logItem) != bool:
			if logItem == "WRITE BLYAD":
				accountStore.save()
			else:
				click.echo(logItem)
		elif logItem == False:
			pushNewAccount()
		if accountCounters[0] == accountCounters[1] and accountCounters[1] == accountCounters[2] and accountCounters[2] == accountCounters[3]:
			break

	accountStore.done()

def worker_accountCreator(counters):
	while counters[0] != counters[3]:
		Account = creatorQueue.get()
		Account.setupMailbox()
		Account = makeClubAccount(Account)
		if Account.errorState == None:
			logQueue.put(click.style('Created account %s.' % Account.username, fg = 'green', bold=True))
			Account.save()
			counters[0]+=1
			logQueue.put('WRITE BLYAD')
			tosQueue.put(Account)
			verifierQueue.put(Account)
		else:
			logQueue.put(False)
			logQueue.put(click.style('Error occured at stage %d when creating account %s' % (Account.errorState, Account.username), fg='red', bold=True))
	return True


def worker_tosAccepter(counters):
	while counters[1] != counters[3]:
		Account = tosQueue.get()
		if Account.acceptTos() == True:
			logQueue.put(click.style('Accepted TOS for account %s.' % Account.username, fg = 'cyan', bold=False))
		Account.save()
		counters[1]+=1
		logQueue.put('WRITE BLYAD')
	return True

def worker_mailAccepter(counters):
	while counters[2] != counters[3]:
		Account = verifierQueue.get()
		Account.emailAccept = Account.mailbox.accept()
		if Account.emailAccept == True:
			logQueue.put(click.style('Accepted email for account %s.' % Account.username, fg = 'magenta', bold=False))
		Account.save()
		counters[2]+=1
		logQueue.put('WRITE BLYAD')
	return True

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

	return accObj

def acceptTos(username, password, pos):
	api = PGoApi()
	api.set_position(pos[0], pos[1], 0.0)

	retryCount = 0
	while True:
		try:
			api.login('ptc', username, password)
			break
		except AuthException, NotLoggedInException:
			time.sleep(0.15)
			if retryCount > 3:
				return False
			retryCount += 1
		except ServerSideRequestThrottlingException:
			time.sleep(requestSleepTimer)
			if requestSleepTimer == 5.1:
				logQueue.put(click.style('[TOS accepter] Received slow down warning. Using max delay of 5.1 already.', fg='red', bold=True))
			else:
				logQueue.put(click.style('[TOS accepter] Received slow down warning. Increasing delay from %d to %d.' % (requestSleepTimer, requestSleepTimer+0.2), fg='red', bold=True))
				requestSleepTimer += 0.2

	time.sleep(2)
	req = api.create_request()
	req.mark_tutorial_complete(tutorials_completed = 0, send_marketing_emails = False, send_push_notifications = False)
	response = req.call()
	if type(response) == dict and response['status_code'] == 1 and response['responses']['MARK_TUTORIAL_COMPLETE']['success'] == True:
		return True
	return False

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
					try:
						if 'Thank you for signing up! Your account is now active.' in requests.get(line).text:
							self.accepted = True
							return True
					except requests.ConnectionError:
						time.sleep(requestSleepTimerB)
						if requestSleepTimerB == 5.1:
							logQueue.put(click.style('[Mail accepter] Received slow down warning. Using max delay of 5.1 already.', fg='red', bold=True))
						else:
							logQueue.put(click.style('[Mail accepter] Received slow down warning. Increasing delay from %d to %d.' % (requestSleepTimerB, requestSleepTimerB+0.2), fg='red', bold=True))
							requestSleepTimerB += 0.2
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
		self.accountsFile.flush()
	def add(self, acc):
		self.accounts.append(acc)
	def upd(self, pos, acc):
		self.accounts[pos] = acc
	def done(self):
		self.save()
		self.accountsFile.close()

class accountObject:
	def __init__(self, accountStore=None):
		self.username = None
		self.password = None
		self.country = 'US'
		self.dob = '1986-12-12'
		self.mailbox = None
		self.creationDate = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
		self.tosAccept = False
		self.emailAccept = False
		self.errorState = None
		self.storeIndex = None
		self.pos = [40.7127837, -74.005941]
		self.accountStore = accountStore
	def setupMailbox(self):
		self.mailbox = pokeAnonbox()
	def to_dict(self):
		return {
			'Username': self.username,
			'Password': self.password,
			'Email': self.mailbox.email,
			'Date created': time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()),
			'TOS accepted': self.tosAccept,
			'Email accepted': self.emailAccept
		}
	def acceptTos(self):
		s = acceptTos(self.username, self.password, self.pos)
		self.tosAccept = s
		return s
	def save(self):
		if self.accountStore != None:
			if self.storeIndex == None:
				self.storeIndex = len(self.accountStore.accounts)
				self.accountStore.add(self.to_dict())
			else:
				self.accountStore.upd(self.storeIndex, self.to_dict())

def run():
	global creatorQueue, tosQueue, verifierQueue, logQueue, requestSleepTimer, requestSleepTimerB
	creatorQueue = Queue.Queue()
	tosQueue = Queue.Queue()
	verifierQueue = Queue.Queue()
	logQueue = Queue.Queue()
	requestSleepTimer  = 0.1
	requestSleepTimerB = 0.1

	try:
		main(standalone_mode=False)
	except (EOFError, KeyboardInterrupt):
		raise click.Abort()
	except click.ClickException as e:
		e.show()
		sys.exit(e.exit_code)
	except click.Abort:
		global accountStore
		accountStore.done()
		click.echo('Aborted!', file=sys.stderr)
		sys.exit(1)

	sys.exit(0)

if __name__ == '__main__':
	run()