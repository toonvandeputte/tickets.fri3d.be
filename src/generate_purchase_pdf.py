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
		height: 2cm;
	}
}
table, th, td {
	border-bottom: 1px solid #ddd;
	padding-top: 5px;
	font-size: 115%%;
}
.halign {
	text-align: center;
}
.header {
	font-style: italic;
}
</style>
<body>
%(entries)s
</body>
</html>
"""

def mk_page(email, d, volunteering):
	o = """
			<div style="text-align: center; font-size: 275%%">
				<h1><b>%(email)s %(npers)sp</b></h1>
			</div>
			<div class="halign">
				<h1>Welkom op Fri3dcamp!</h1>
				<h3>Dit is een overzicht van je bestelling.</h3>
			</div>
			%(tickets)s
			<br>
			%(others)s
			<br>
			%(vol)s
			<br>
			<div class="footer">
			<p>Nuttige tips:</p>
			<ul>
			<li>De openingsceremonie neemt <b>zaterdag</b> om <b>11:00</b> plaats.</li>
			<li>De officiele communicatiebron is de <b>infodesk</b>. Daarnaast zitten al vele kampeerders op onze <b>Slack</b>, je kan jezelf toevoegen en meepraten op <u>http://slack.fri3d.be/</u>.</li>
			<li>Je kan <b>vrijdag</b> en <b>zaterdag</b> tot <b>15:00</b> brood en croissants bestellen aan de <b>infodesk</b>. Je kan je bestelling de volgende ochtend om  <b>9:00</b> ophalen aan de infodesk.</li>
			<li>Vragen? Kijk even in de FAQ <u>http://fri3d.be/faq</u>, of kom langs de infodesk!</li>
			</ul>
			</div>
			<div><pdf:nextpage /></div>
		"""
	tickets = [ p for p in d if 'ticket' in p['product'] ]
	others = [ p for p in d if 'ticket' not in p['product'] ]
	volunteers = [ p for p in tickets if p['person_id'] in volunteering ]

	if len(volunteers):
		vol_html = """
		<div id="volunteering">
			<p><b>Volunteering</b>:</p>
			<table>
				<tr class="header">
					<td>Naam</td>
					<td>Wanneer</td>
					<td>Wat</td>
				</tr>"""
		for v in volunteers:
			i = v['person_id']
			for e in volunteering[i]:
				vol_html += """
					<tr>
						<td>{0}</td>
						<td>{1}</td>
						<td>{2}</td>
					</tr>""".format(v['name'], e['when']['name'], e['what']['name'])
		vol_html += "</table></div>"
	else:
		vol_html = ""

	tickets_html = """
	<div id="tickets">
		<p><b>Tickets</b>:</p>
		<table>
			<tr class="header">
				<td>Naam</td>
				<td>Ticket</td>
				<td>Volunteer</td>
				<td>Volunteer opkuis</td>
			</tr>"""
	for t in tickets:
		tickets_html += """
			<tr>
				<td>{0}</td>
				<td>{1}</td>
				<td>{2}</td>
				<td>{3}</td>
			</tr>""".format(t['name'], t['what'],
				"ja" if t['volunteer_during'] else "", 
				"ja" if t['volunteer_after'] else "")
	tickets_html += "</table></div>"
	if len(others):
		others_html = """
		<div id="andere">
			<p><b>Andere</b>:</p>
			<table>
				<tr class="header">
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
		'npers' : len(tickets),
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
				if person not in sched_by_person:
					sched_by_person[person] = []
				sched_by_person[person].append({ 'when' : when[time], 'what' : what[post] })

	entries = []
	for email in sorted([ str(e) for e in purchases_all.keys()], key=str.lower):
		for p in purchases_all[email]:
			for k, v in p.iteritems():
				if type(v) in [ unicode, str ]:
					p[k] = v.encode('ascii', 'replace')
		entries.append(mk_page(email, purchases_all[email], sched_by_person))
	pdf = pisa.CreatePDF(t % { 'entries' : "".join(entries) }, file('purchases.pdf', 'wb'))
	g.db_commit = True
	setup.wrapup_db(None)

