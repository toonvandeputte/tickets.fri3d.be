# -*- coding: utf-8 -*-
# vim: ts=4:sw=4:noexpandtab
from flask import request, jsonify, session, render_template, redirect, url_for, g, abort, Response
from flask_wtf import Form
from wtforms import StringField, validators
from wtforms import SelectField, BooleanField, IntegerField
from wtforms.fields.html5 import EmailField
from fr1ckets import app
from fr1ckets.model import model
from functools import wraps
import pprint
import time
import json
import datetime

TICKETS_MAX = 32
DAYS_MAX = 14

def check_auth_basic(u, p):
	return u == 'hello' and p == 'world'

def auth_basic():
	return Response('No', 401, { 'WWW-Authenticate' : 'Basic realm="Login Required"' })

def req_auth_basic(f):
	@wraps(f)
	def fn(*args, **kwargs):
		auth = request.authorization
		if not auth or not check_auth_basic(auth.username, auth.password):
			return auth_basic()
		return f(*args, **kwargs)
	return fn

def generate_tickets():
	return [ 'ticket_{0}'.format(t) for t in [ 'business', 'supporter', 'premium', 'padawan' ] ]

def generate_tshirts():
	tshirts = []
	for color in [ 'red', 'yellow', 'green' ]:
		for size in [ 's', 'm', 'l', 'xl' ]:
			tshirts.append('tshirt_{0}_{1}'.format(color, size))
	return tshirts

class TicketForm(Form):
	email = EmailField('email', validators=[
		validators.Email(message="Really an email?"),
		])
	handle = StringField('handle', validators=[
		validators.DataRequired()
		])

	for ticket in generate_tickets():
		vars()[ticket] = IntegerField()
	for tshirt in generate_tshirts():
		vars()[tshirt] = IntegerField()

	terms_payment = BooleanField('I agree to pay', default=False,
		validators=[
			validators.DataRequired(message="HEEELA")
		])

@app.route('/tickets', methods=[ 'GET', 'POST' ])
@req_auth_basic
def tickets():
	form = TicketForm()
	tickets_available = TICKETS_MAX - model.get_total_tickets(g.db_cursor)

	if form.validate_on_submit():
		products = {}
		n_tickets = 0
		for ticket in generate_tickets():
			products[ticket] = getattr(form, ticket).data or 0
			n_tickets += products[ticket]
		tshirts = {}
		for tshirt in generate_tshirts():
			products[tshirt] = getattr(form, tshirt).data or 0

		if tickets_available < n_tickets:
			return render_template("tickets_retry.html",
				tickets_available=tickets_available,
				tickets_ordered=n_tickets)
	
		nonce = model.create(g.db_cursor,
			form.email.data,
			form.handle.data,
			products
		)
		return render_template('confirm.html',
			amount=model.get_purchase_total(g.db_cursor, nonce),
			days_max=DAYS_MAX)
	else:
		return render_template('tickets.html', form=form, tickets_available=tickets_available)

@app.route('/payments', methods=[ 'GET' ])
@req_auth_basic
def payments():
	now = datetime.datetime.utcnow()
	time_delta = datetime.timedelta(days=DAYS_MAX)

	p = map(dict, model.get_purchases(g.db_cursor, strip_removed=True))
	for x in p:
		created_at = datetime.datetime.strptime(x['created_at'], '%Y-%m-%d %H:%M:%S.%f')
		if not x['paid'] and (created_at + time_delta) < now:
			x['overtime'] = True
		else:
			x['overtime'] = False

	return render_template('payments.html', purchases=p, page_opts={ 'internal' : True })

@app.route('/overview', methods=[ 'GET' ])
@req_auth_basic
def overview():
	overview_tickets = model.get_overview_tickets(g.db_cursor)
	overview_tshirts = model.get_overview_tshirts(g.db_cursor)
	return render_template('overview.html',
		overview_tickets=overview_tickets,
		overview_tshirts=overview_tshirts,
		page_opts={
			'charting' : True,
			'internal' : True})

@app.route('/api/purchase_mark_paid/<int:purchase_id>', methods=[ 'GET' ])
@req_auth_basic
def api_purchase_mark_paid(purchase_id):
	model.purchase_mark_paid(g.db_cursor, purchase_id)
	return "ok", 200

@app.route('/api/purchase_remove/<int:purchase_id>', methods=[ 'GET' ])
@req_auth_basic
def api_purchase_remove(purchase_id):
	model.purchase_remove(g.db_cursor, purchase_id)
	return "ok", 200

@app.route('/api/get_timeline_tickets')
@req_auth_basic
def api_get_timeline_tickets():
	timeline_tickets = map(dict, model.get_timeline_tickets(g.db_cursor))

	sum = 0
	for t in timeline_tickets:
		at = datetime.datetime.strptime(t['at'], '%Y-%m-%d %H:%M:%S.%f')
		epoch = datetime.datetime(1970, 1, 1)
		when = (at - epoch).total_seconds()
		t['at'] = int(when)

		sum += t['n']
		t['n'] = sum

	return json.dumps({
		'at' : [ t['at'] for t in timeline_tickets ],
		'n' : [ t['n'] for t in timeline_tickets ]})

@app.route("/")
@req_auth_basic
def index():
	return render_template("index.html")
