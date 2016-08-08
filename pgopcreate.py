#!/usr/bin/python
# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from pgoapi import PGoApi
from pgoapi.utilities import f2i
from pgoapi import utilities as util
from pgoapi.exceptions import AuthException
import click, time, random, string, json

@click.command()
@click.option('--accounts', default=50, help='Number of accounts to make, default is 50.')
@click.option('--size', default=10, type=click.IntRange(6, 16, clamp=True), help='Username size, range between 5 and 20.')
@click.option('--domain', default="yopmail.com", help='Email domain, default is yopmail.com.')
@click.option('--password', prompt='Password', help='Password for accounts')
@click.argument('outfile', type=click.File('w'), default='accounts.json', required=False)
def main(accounts, size, password, domain, outfile):
	"""This is a script to create Pokémon Go (PTC) accounts and accept the Terms of Service. Made by two skids who can't code for shit."""
	counter = 0
	driver = webdriver.Chrome()
	while counter < accounts:
		username = id_generator(size)
		email = '%s@%s' % (username, domain)
		make_account(username, password, email, driver)
		accept_tos(username, password)
		d = {
			'Username': username,
			'Password': password,
			'Email': email,
			'Date created': time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()),
			'ToS accepted': True
		}
		json.dump(d, outfile, indent=4)
		counter+=1
		click.echo('Account %s written to file. Completed %s accounts.' % (username, counter)) 

def id_generator(size, chars=string.ascii_uppercase + string.digits):
	return ''.join(random.choice(chars) for _ in range(size))

def accept_tos(username, password):
	api = PGoApi()
	api.set_position(40.7127837, -74.005941, 0.0)
	api.login('ptc', username, password)
	time.sleep(2)
	req = api.create_request()
	req.mark_tutorial_complete(tutorials_completed = 0, send_marketing_emails = False, send_push_notifications = False)
	response = req.call()
	click.echo('Accepted Terms of Service for user {}'.format(username))

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
	driver.refresh()
	click.echo('Account %s created' % username)

if __name__ == '__main__':
	main()