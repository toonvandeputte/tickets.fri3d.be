#!/usr/bin/env python
from fr1ckets import app
from fr1ckets.model import setup, model
from flask import g
import sys
import datetime
import csv
import pprint
import os
import ho.pisa as pisa

try:
	app.config.from_pyfile('fr1ckets_priv.conf')
	app.debug = True
	app.secret_key = app.config['SECRET_KEY']
except IOError:
	for i in range(5):
		print "YOU ARE RUNNING THE STOCK CONFIG, which is not in git, smtp passwords and so on, ask jef for fr1ckets_priv.conf"
	app.config.from_pyfile('fr1ckets.conf')


t = """
<html>
<style>
@page {
	margin: 2cm;
	margin-bottom: 2.5cm;
	@frame footer {
		-pdf-frame-content: footerContent;
		bottom: 2cm;
		margin-left: 1cm;
		margin-right: 1cm;
		height: 1cm;
	}
	
}
</style>
<body>
%(entries)s
</body>
</html>
"""

def mk_page(email, d, volunteering):
	print email
	o = """
			<div vertical-align="1">
				<h2>Welkom op Fri3dcamp, %(email)s!</h2>
				<p>Dit is een overzicht van je bestelling.</p>
				<p>Mocht de inhoud van de totebag niet kloppen, kom even langs de infodesk.</p>
			</div>
			%(tickets)s
			%(others)s
			%(vol)s
			<div><pdf:nextpage /></div>
		"""
	tickets = [ p for p in d if 'ticket' in p['product'] ]
	others = [ p for p in d if 'ticket' not in p['product'] ]
	volunteers = [ p for p in tickets if p['person_id'] in volunteering ]

	print volunteers
	if len(volunteers):
		vol_html = """
		<div>
			<p><b>Volunteering</b>:</p>
			<table>
				<tr>
					<td>Naam</td>
					<td>Wanneer</td>
					<td>Wat</td>
				</tr>"""
		for v in volunteers:
			i = v['person_id']
			vol_html += """
				<tr>
					<td>{0}</td>
					<td>{1}</td>
					<td>{2}</td>
				</tr>""".format(v['name'], volunteering[i]['when']['name'], volunteering[i]['what']['name'])
		vol_html += "</table></div>"
	else:
		vol_html = ""

	tickets_html = """
	<div>
		<p><b>Tickets</b>:</p>
		<table>
			<tr>
				<td>Naam</td>
				<td>Ticket</td>
				<td>Volunteer</td>
				<td>Volunteer opkuis</td>
			</tr>"""
	for t in tickets:
		print t
		tickets_html += """
			<tr>
				<td>{0}</td>
				<td>{1}</td>
				<td>{2}</td>
				<td>{3}</td>
			</tr>""".format(t['name'], t['what'], t['volunteer_during'], t['volunteer_after'])
	tickets_html += "</table></div>"
	if len(others):
		others_html = """
		<div>
			<p><b>Andere</b>:</p>
			<table>
				<tr>
					<td>Item</td>
					<td>Aantal</td>
				</tr>"""
		for t in others:
			others_html += """
				<tr>
					<td>{0}</td>
					<td>{1}</td>
				</tr>""".format(t['what'], t['n'])
		others_html += "</table></div>"
	else:
		others_html = ""

	return o % {
		'email' : str(email),
		'tickets' : tickets_html,
		'others' : others_html,
		'vol' : vol_html,
	}

with app.app_context():
	setup.setup_db()
	purchases_all = model.purchases_get_all(g.db_cursor, strip_queued=False)
	when = model.get_volunteering_times(g.db_cursor)
	what = model.get_volunteering_posts(g.db_cursor)
	sched = model.get_volunteering_schedule(g.db_cursor)
	sched_by_person = {}
	for time in sched:
		for post in sched[time]:
			s = sched[time][post]
			for person in s['people_list']:
				sched_by_person[person] = { 'when' : when[time], 'what' : what[post] }

	print sched_by_person
	entries = []
	for email in purchases_all.keys()[:20]:
		entries.append(mk_page(email, purchases_all[email], sched_by_person))
	pdf = pisa.CreatePDF(t % { 'entries' : "".join(entries) }, file('ok.pdf', 'wb'))
	pprint.pprint(t % { 'entries' : ''.join(entries) })
	g.db_commit = True
	setup.wrapup_db(None)

