#!/usr/bin/python
# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
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
	driver = webdriver.Chrome()
	outfile = open(outfile, 'r+' if os.path.exists(outfile) else 'w+')

	# Load existing accounts
	if (outfile.read(1) == ""):
		accounts_array = []
	else:
		outfile.seek(0)
		accounts_array = json.load(outfile)

	while counter != accounts:
		username = id_generator(size)
		anonbox = make_anonbox()
		email = anonbox[0]
		_password = password if password != None else id_generator(12, string.ascii_uppercase + string.ascii_lowercase + string.digits)
		
		d = make_account(username, _password, email, driver)
		d['ToS accepted'] = accept_tos(username, _password)
		d['Email accepted'] = accept_email(anonbox[1], username)

		accounts_array.append(d)
		outfile.seek(0)
		json.dump(accounts_array, outfile, indent=4)
		
		counter+=1
		click.echo('Account %s written to file. Completed %s accounts.' % (username, counter)) 
	outfile.close()

def id_generator(size, chars=string.ascii_uppercase + string.digits):
	return ''.join(random.choice(chars) for _ in range(size))

def accept_email(box, username):
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

def accept_tos(username, password):
	api = PGoApi()
	api.set_position(40.7127837, -74.005941, 0.0)
	api.login('ptc', username, password)
	time.sleep(2)
	req = api.create_request()
	req.mark_tutorial_complete(tutorials_completed = 0, send_marketing_emails = False, send_push_notifications = False)
	response = req.call()
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
	return {
			'Username': username,
			'Password': password,
			'Email': email,
			'Date created': time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()),
			'ToS accepted': False,
			'Email accepted': False
		}

def make_anonbox():
	anonbox = requests.get('https://anonbox.net/en/', verify=False)
	tree = html.fromstring(anonbox.text.encode())
	address = tree.get_element_by_id('content').find('dl')[1].text_content()
	inbox = tree.get_element_by_id('content').find('dl')[3].text_content()
	return([address,inbox])

if __name__ == '__main__':
	main()