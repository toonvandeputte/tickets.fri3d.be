# -*- coding: utf-8 -*-
# vim: ts=4:sw=4:noexpandtab
from flask import request, jsonify, session, render_template, redirect, url_for, g, abort, Response
from flask_wtf import Form
from wtforms import StringField, validators
from wtforms import SelectField, BooleanField, IntegerField
from wtforms.fields.html5 import EmailField
from fr1ckets import app
from fr1ckets.texts import texts
from fr1ckets.model import model
from fr1ckets.mail import mail
from functools import wraps
import pprint
import time
import json
import datetime

def check_auth_basic(u, p):
	return u == app.config['TEMP_SHIELDING_USERNAME'] and p == app.config['TEMP_SHIELDING_PASSWORD']

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

	ticket_normal = IntegerField('ticket_normal', validators=[
		validators.NumberRange(min=0, max=10),
		])
	ticket_billable = IntegerField('ticket_billable', validators=[
		validators.NumberRange(min=0, max=10),
		])

	terms_payment = BooleanField('', default=False,
		validators=[
			validators.DataRequired(message="did not agree to terms")
		])
	terms_supervision = BooleanField('', default=False,
		validators=[
			validators.DataRequired(message="did not agree to terms")
		])

def make_form_billable_tickets(n_tickets):
	class BillableTicketForm(Form):
		pass

	if (n_tickets_billable > 0):
		for e in [ 'name', 'address', 'vat' ]:
			name = 'ticket_billable_{0}'.format(e)
			setattr(BillableTicketForm, name, StringField(name, validators=[ validators.DataRequired() ]))

	for i in range(n_tickets_billable):
		fmt = "ticket_billable_visitors_{0}".format(i)
		name = fmt + '_name'
		setattr(BillableTicketForm, name, StringField(name, validators=[ validators.DataRequired() ]))

		for field in [ '_dob_year', '_dob_month', '_dob_day' ]:
			name = fmt + field
			setattr(BillableTicketForm, name, IntegerField(name, validators=[ validators.NumberRange() ]))

		fmt += "_options"
		for field in [ '_volunteering_toggle', '_cleanup_toggle', '_veggy_toggle' ]:
			name = fmt + field
			setattr(BillableTicketForm, name, BooleanField(name))

	return BillableTicketForm

def make_form_individual_tickets(n_tickets_normal, n_tickets_billable):
	class IndividualTicketForm(Form):
		pass

	for i in range(n_tickets_normal):
		fmt = "ticket_normal_visitors_{0}".format(i)
		name = fmt + '_name'
		setattr(IndividualTicketForm, name, StringField(name, validators=[ validators.DataRequired() ]))

		for field in [ '_dob_year', '_dob_month', '_dob_day' ]:
			name = fmt + field
			setattr(IndividualTicketForm, name, IntegerField(name, validators=[ validators.NumberRange() ]))

		fmt += "_options"
		for field in [ '_premium_toggle', '_cleanup_toggle', '_veggy_toggle' ]:
			name = fmt + field
			setattr(IndividualTicketForm, name, BooleanField(name))

	for i in range(n_tickets_billable):
		fmt = "ticket_billable_visitors_{0}".format(i)
		name = fmt + '_name'
		setattr(IndividualTicketForm, name, StringField(name, validators=[ validators.DataRequired() ]))

		for field in [ '_dob_year', '_dob_month', '_dob_day' ]:
			name = fmt + field
			setattr(IndividualTicketForm, name, IntegerField(name, validators=[ validators.NumberRange() ]))

		fmt += "_options"
		for field in [ '_volunteering_toggle', '_cleanup_toggle', '_veggy_toggle' ]:
			name = fmt + field
			setattr(IndividualTicketForm, name, BooleanField(name))

	if (n_tickets_billable > 0):
		for e in [ 'name', 'address', 'vat' ]:
			name = 'ticket_billable_{0}'.format(e)
			setattr(IndividualTicketForm, name, StringField(name, validators=[ validators.DataRequired() ]))

	return IndividualTicketForm

def find_form_individual_tickets(form, n_tickets_normal, n_tickets_billable):

	out = []

	for i in range(n_tickets_normal):
		fmt = 'ticket_normal_visitors_{0}'.format(i)
		this = {
			'dob' : datetime.date(getattr(form, fmt + '_dob_year').data,
				getattr(form, fmt + '_dob_month').data,
				getattr(form, fmt + '_dob_day').data),
			'name' : getattr(form, fmt + '_name').data,
			'volunteers_during' : not getattr(form, fmt + '_options_premium_toggle').data,
			'volunteers_after' : getattr(form, fmt + '_options_cleanup_toggle').data,
			'food_vegitarian' : getattr(form, fmt + '_options_cleanup_toggle').data,
		}
		out.append(this)
	
	for i in range(n_tickets_billable):
		fmt = 'ticket_billable_visitors_{0}'.format(i)
		this = {
			'dob' : datetime.date(getattr(form, fmt + '_dob_year').data,
				getattr(form, fmt + '_dob_month').data,
				getattr(form, fmt + '_dob_day').data),
			'name' : getattr(form, fmt + '_name').data,
			'volunteers_during' : getattr(form, fmt + '_options_volunteering_toggle').data,
			'volunteers_after' : getattr(form, fmt + '_options_cleanup_toggle').data,
			'food_vegitarian' : getattr(form, fmt + '_options_cleanup_toggle').data,
		}
		out.append(this)
	
	return out

@app.route('/tickets', methods=[ 'GET', 'POST' ])
@req_auth_basic
def tickets():
	form = TicketForm()
	#tickets_available = app.config['TICKETS_MAX'] - model.get_total_tickets(g.db_cursor)

	if form.validate_on_submit():
		n_tickets_normal = form.ticket_normal.data
		n_tickets_billable = form.ticket_billable.data
		n_tickets = n_tickets_normal + n_tickets_billable
		app.logger.debug("n_tickets={0}".format(n_tickets))

		individual_form = make_form_individual_tickets(n_tickets_normal, n_tickets_billable)()

		if individual_form.validate_on_submit():
			app.logger.debug(repr(find_form_individual_tickets(individual_form, n_tickets_normal, n_tickets_billable)))
			raise YEEHAA

		if (billable_form.validate_on_submit() and normal_form.validate_on_submit()):
			normal_tickets = find_form_normal_tickets(normal_form, form.ticket_normal.data)
			billable_tickets = find_form_billable_tickets(normal_form, form.ticket_normal.data)
			app.logger.debug(repr(find_form_normal_tickets(normal_form, form.ticket_normal.data)))
			app.logger.debug("SMASHING!")
		raise foo

	else:
		return render_template('tickets.html', tickets_available=10, form=form)

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

		mail_data = {
			'amount' : model.get_purchase_total(g.db_cursor, nonce),
			'days_max' : app.config['DAYS_MAX'],
			'email' : form.email.data
		}
		mail.send_mail(
			from_addr=app.config['MAIL_MY_ADDR'],
			to_addrs=[ form.email.data, app.config['MAIL_CC_ADDR'] ],
			subject=texts['MAIL_TICKETS_SUBJECT'],
			msg_html=texts['MAIL_TICKETS_HTML'].format(**mail_data),
			msg_text=texts['MAIL_TICKETS_TEXT'].format(**mail_data))

		return redirect(url_for('confirm', nonce=nonce))
	else:
		prices = { p[0] : p[1] for p in model.get_prices(g.db_cursor) }
		return render_template('tickets.html', form=form, tickets_available=tickets_available, prices=prices)


@app.route('/confirm/<nonce>', methods=[ 'GET', 'POST' ])
@req_auth_basic
def confirm(nonce=None):
	form = BusinessAdressForm()
	amount = model.get_purchase_total(g.db_cursor, nonce)
	amount_business = model.get_purchase_total(g.db_cursor, nonce, product_filter='%business%')
	if form.validate_on_submit():
		model.set_business_details(g.db_cursor, nonce,
			form.name.data,
			form.address.data,
			form.vat.data)
		return render_template('confirm.html',
			amount=amount,
			amount_business=amount_business,
			days_max=app.config['DAYS_MAX'],
			page_opts = { 'business_details_have' : True })
	else:
		return render_template('confirm.html',
			form=form,
			amount=amount,
			amount_business=amount_business,
			days_max=app.config['DAYS_MAX'],
			nonce=nonce,
			page_opts = { 'business_details_need' : bool(amount_business) })
	

@app.route('/payments', methods=[ 'GET' ])
@req_auth_basic
def payments():
	now = datetime.datetime.utcnow()
	time_delta = datetime.timedelta(days=app.config['DAYS_MAX'])

	p = map(dict, model.get_purchases(g.db_cursor, strip_removed=False))
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

@app.route('/api/purchase_mark_paid/<int:purchase_id>/<int:paid>', methods=[ 'GET' ])
@req_auth_basic
def api_purchase_mark_paid(purchase_id, paid):
	model.purchase_mark_paid(g.db_cursor, purchase_id)
	return "ok", 200

@app.route('/api/purchase_remove/<int:purchase_id>', methods=[ 'GET' ])
@req_auth_basic
def api_purchase_remove(purchase_id):
	model.purchase_remove(g.db_cursor, purchase_id)
	return "ok", 200

@app.route('/api/get_prices', methods=[ 'GET' ])
@req_auth_basic
def api_get_prices():
	prices = { p[0] : p[1] for p in model.get_prices(g.db_cursor) }
	return json.dumps(prices), 200

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
