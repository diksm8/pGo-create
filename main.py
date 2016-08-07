#!/usr/bin/python
# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from pgoapi import PGoApi
from pgoapi.utilities import f2i
from pgoapi import utilities as util
from pgoapi.exceptions import AuthException
import string
import random
import time
import json
import pprint
import threading
import sys, getopt

#set counter and password. Edit password if you want to
counter = 0
password = "4k9dzlm39"
userSize = 10

#Set numbers of accounts to create to valuve after script name, 500 if nothing entered
if len(sys.argv) > 1:
    times = int(sys.argv[1])
else:
    times = 500

#Generate username
def id_generator(size, chars=string.ascii_uppercase + string.digits):
	return ''.join(random.choice(chars) for _ in range(size))

#Accept TOS
def accept_tos(username, password):
	api = PGoApi()
	api.set_position(40.7127837, -74.005941, 0.0)
	api.login('ptc', username, password)
	time.sleep(2)
	req = api.create_request()
	req.mark_tutorial_complete(tutorials_completed = 0, send_marketing_emails = False, send_push_notifications = False)
	response = req.call()
	print('Accepted Terms of Service for {}'.format(username))

def make_account(username, email):
	driver = webdriver.Chrome()
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

with open('accounts.txt', 'w') as outfile:
	while counter < times:
		#get username and email
		username = id_generator(userSize)
		email = username + "@yopmail.com"

		#make account
		make_account(username, email)

		counter+=1 #add one to counter
		print '%s created, made %s accounts.' % (username, counter) #print status

		accept_tos(username, password) #accept tos for account just created

		d = {
			'Username': username,
			'Password': password,
			'Email': email,
			'Date created': strftime("%Y-%m-%d %H:%M:%S", gmtime()),
			'ToS accepted': True
		}
		json.dump(d, outfile, sort_keys=True, indent=4)