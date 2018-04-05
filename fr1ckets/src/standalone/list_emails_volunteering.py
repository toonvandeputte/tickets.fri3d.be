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

if not len(sys.argv) == 1:
	print "usage: {0}".format(sys.argv[0])

with app.app_context():
	setup.setup_db()
	volunteering = model.get_volunteer_purchases(g.db_cursor)
	purchases = model.purchases_get_all(g.db_cursor)
	volunteers = {}
	for p in volunteering:
		vol = "ok"
		if p['n_volunteers'] > p['shifts_booked']:
			vol = "notok"

		volunteers[p['email']] = { 'vol' : vol }
	
	for p in purchases:
		if p not in volunteers:
			volunteers[p] = { 'vol' : "notneeded" }
		is_day = 0
		for i in purchases[p]:
			if 'ticket_vip' in i['product'] and i['product'] != 'ticket_vip_all':
				is_day = 1
		volunteers[p]['one_day'] = is_day


	for v in sorted(volunteers):
		print "{0},{1},{2}".format(v, volunteers[v]['vol'], volunteers[v]['one_day'])
	setup.wrapup_db(None)
