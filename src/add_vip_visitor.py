#!/usr/bin/env python
from fr1ckets import app
from fr1ckets.model import setup, model
from flask import g
import sys
import datetime
import csv
import pprint
import os

try:
	app.config.from_pyfile('fr1ckets_priv.conf')
	app.debug = True
	app.secret_key = app.config['SECRET_KEY']
except IOError:
	for i in range(5):
		print "YOU ARE RUNNING THE STOCK CONFIG, which is not in git, smtp passwords and so on, ask jef for fr1ckets_priv.conf"
	app.config.from_pyfile('fr1ckets.conf')

if not len(sys.argv) == 2:
	print "usage: {0} filename".format(sys.argv[0])

with app.app_context():
	setup.setup_db()
	products_all = model.products_get(g.db_cursor)
	def find_product(name):
		for r in products_all:
			if r['name'] == name:
				return r
		return None

	with open(sys.argv[1], 'rb') as csvfile:
		r = csv.DictReader(csvfile, fieldnames=[ 'email', 'name', 'dob', 'vegitarian', 'when' ])

		persons = 0
		emails = {}
		for row in r:
			if row['email'] not in emails:
				emails[row['email']] = []
			emails[row['email']].append(row)

		pprint.pprint(emails)
		for email in emails:
			products = []
			for row in emails[email]:
				ticket = None
				if row['when'].lower() in [ 'fri', 'friday', 'vrij', 'vrijdag' ]:
					ticket = 'ticket_vip_friday'
				elif row['when'].lower() in [ 'sat', 'saturday', 'zat', 'zaterdag' ]:
					ticket = 'ticket_vip_saturday'
				elif row['when'].lower() in [ 'sun', 'sunday', 'zon', 'zondag' ]:
					ticket = 'ticket_vip_sunday'
				elif row['when'].lower() in [ 'mon', 'monday', 'maa', 'maandag' ]:
					ticket = 'ticket_vip_monday'
				elif row['when'].lower() in [ 'all', 'allemaal' ]:
					ticket = 'ticket_vip_all'
				p = find_product(ticket)
				if not ticket or not p:
					print "can't parse {0} in {1}! fail.".format(row['when'], row)
					sys.exit(1)

				products.append({
					'product_id' : p['id'],
					'n' : 1,
					'person_dob' : row['dob'],
					'person_name' : row['name'],
					'person_volunteers_during' : 0,
					'person_volunteers_after' : 0,
					'person_food_vegitarian' : int(row['vegitarian']),
				})
				persons += 1
			business_info = { 'name' : '', 'address' : '', 'vat' : '' }
			purchase = model.purchase_create(g.db_cursor, email, products, business_info, False)

			print "{0}({1}): {2}".format(email, purchase['id'], products)
			model.purchase_history_append(g.db_cursor, purchase['id'],
				msg='script created VIP purchase for={0}'.format(row['email']))

		print "persons={0}".format(persons)

		g.db_commit = True
		setup.wrapup_db(None)
