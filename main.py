#!/usr/bin/env python
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from time import gmtime, strftime
import string
import random
import time
import json

counter = 0

usernameArray = []
memes = raw_input("cocks")
def id_generator(size=12, chars=string.ascii_uppercase + string.digits):
	return ''.join(random.choice(chars) for _ in range(size))

driver = webdriver.Chrome("chromedriver.exe")
driver.get("https://club.pokemon.com/us/pokemon-trainer-club/sign-up/")

with open('accounts.txt', 'w') as outfile:
	while counter <= 2:
		#elem = driver.find_element_by_name("dob")
		driver.implicitly_wait(3)
		driver.execute_script("document.getElementById('id_dob').removeAttribute('readonly')")
		driver.execute_script("document.getElementById('id_dob').value='1986-12-12'")
		driver.find_element_by_class_name('continue-button').click()
		username = id_generator()
		password = "BlackLivesMatter555"
		email = username + "@dayrep.com"
		driver.find_element_by_id('id_username').send_keys(username)
		driver.find_element_by_id('id_password').send_keys(password)
		driver.find_element_by_id('id_confirm_password').send_keys(password)
		driver.find_element_by_id('id_email').send_keys(email)
		driver.find_element_by_id('id_confirm_email').send_keys(email)
		driver.find_element_by_id('id_screen_name').send_keys(username)
		driver.find_element_by_id('id_terms').click()
		driver.find_element_by_class_name('button-green').click()
		driver.refresh()
		counter+=1
		d = {
			'username': username,
			'password': password,
			'email': email,
			'created': strftime("%Y-%m-%d %H:%M:%S", gmtime())
		}
		json.dump(d, outfile, sort_keys=True, indent=4)