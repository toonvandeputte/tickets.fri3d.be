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
	print "usage: {0} path_to_csv_file".format(sys.argv[0])

with app.app_context():
	setup.setup_db()
	with open(sys.argv[1], 'rb') as csvfile:
		r = csv.DictReader(csvfile, fieldnames=[ 'email',
			'discount', 'available_from', 'comments'])
		statics = {
			'claimed' : False,
			'claimed_at' : None,
		}
		static_comment = 'set by {0} on {1}'.format(os.path.basename(sys.argv[0])
				, datetime.datetime.today().isoformat())

		all_reservations = { res['email'] : res for res in model.reservation_get(g.db_cursor) }
		for row in r:
			row['discount'] = int(row['discount'])
			row['comments'] = '{0} ({1})'.format(row['comments'] if row['comments'] else '', static_comment)
			row.update(statics)
			if row['email'] in all_reservations:
				print "updating %(email)s to discount=%(discount)d av_from=%(available_from)s" % row
				model.reservation_update(g.db_cursor, all_reservations[row['email']]['id'], row)
			else:
				print "creating %(email)s to discount=%(discount)d av_from=%(available_from)s" % row
				model.reservation_create(g.db_cursor, row)
		g.db_commit = True
		setup.wrapup_db(None)
