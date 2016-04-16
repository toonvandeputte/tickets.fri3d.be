from flask import request, jsonify
from fr1ckets import app
import pprint
import string
import time
import json
import random
import sqlite3
import datetime
import copy

D = app.logger.debug
def random_string(length=32):
	return ''.join(
		[ random.SystemRandom().choice(
				string.ascii_lowercase +
				string.ascii_uppercase + string.digits)
			for _ in range(length)
		])

def reservation_find(cursor, email):
	"""
	find any unclaimed reservation for this email, if none is found we return
	the default reservation
	"""
	q = """
		select
			id,
			email,
			discount,
			available_from
		from
			reservation
		where
			email = :email
			and claimed = 0;
		"""
	qd = { 'email' : email }
	
	cursor.execute(q, qd)
	rs = cursor.fetchall()

	if len(rs) != 1 and email != 'default':
		return reservation_find(cursor, 'default')

	return rs[0]

def reservation_claim(cursor, email):
	res = reservation_find(cursor, email)
	if res['email'] == 'default':
		return res['id']

	q = """
		update
			reservation
		set
			claimed = 1,
			claimed_at = :now
		where
			email = :email
			AND claimed = 0
			AND available_from <= datetime('now');
		"""
	qd = {
		'now' : datetime.datetime.utcnow(),
		'email' : email,
	}

	cursor.execute(q, qd)
	D("last_row_id={0}, rowcount={1}".format(cursor.lastrowid, cursor.rowcount))

	return res

def reservation_get(cursor, id=None):
	f = ""
	if id:
		f = " where id=:id"
	q = """
		select
			id,
			email,
			discount,
			available_from,
			claimed,
			claimed_at,
			comments
		from
			reservation
		""" + f + ";"
	app.logger.debug("q={0}".format(q))
	cursor.execute(q, { 'id' : id })
	return cursor.fetchall()

def reservation_delete(cursor, id):
	q = """
		delete from
			reservation
		where
			id=:id;
		"""
	cursor.execute(q, { 'id' : id })

def reservation_update(cursor, id, values):
	q = """
		update
			reservation
		set
			email=:email,
			discount=:discount,
			available_from=:available_from,
			claimed=:claimed,
			claimed_at=:claimed_at,
			comments=:comments
		where
			id=:id;
		"""
	qd = copy.deepcopy(values)
	qd['id'] = id
	cursor.execute(q, qd)

def reservation_create(cursor, values):
	q = """
		insert into
			reservation (
				email,
				discount,
				available_from,
				claimed,
				claimed_at,
				comments
			)
		values (
			:email,
			:discount,
			:available_from,
			:claimed,
			:claimed_at,
			:comments
		);
		"""
	cursor.execute(q, values)

def purchase_create(cursor, email, products, billing_info):
	"""
	"""
	now = datetime.datetime.utcnow()
	nonce = random_string(16)

	# get the reservation for this email
	reservation = reservation_claim(cursor, email)

	# the purchase proper
	q = """
		insert into purchase (
			email, nonce, reservation_id, created_at,
			business_name, business_address, business_vat )
		values
			(?, ?, ?, ?, ?, ?, ?);
		"""
	cursor.execute(q, (email, nonce, reservation['id'], now,
		billing_info['name'], billing_info['address'], billing_info['vat']))

	purchase_id = cursor.lastrowid

	# add the products
	q = """
		insert into purchase_items (
			purchase_id, product_id, n, person_name, person_dob,
			person_volunteers_during, person_volunteers_after, person_food_vegitarian)
		values
			(:purchase_id, :product_id, :n, :person_name, :person_dob,
			:person_volunteers_during, :person_volunteers_after, :person_food_vegitarian);
		"""
	for p in products:
		p['purchase_id'] = purchase_id
		D("p={0!r}".format(p))
		cursor.execute(q, p)
	#cursor.executemany(q, products)

	return nonce


def products_get(cursor):
	q = """
		select
			id,
			name,
			display,
			price,
			volunteering_price,
			max_dob,
			billable
		from
			product;
		"""
	cursor.execute(q)
	return cursor.fetchall()

def get_purchase_discount(cursor, nonce):
	q = """
		select
			reservation.discount as discount
		from
			purchase
			inner join reservation on purchase.reservation_id = reservation.id
		where
			purchase.nonce = :nonce;
		"""
	qd = { 'nonce' : nonce }
	cursor.execute(q, qd)
	rs = cursor.fetchone()
	return rs['discount'] or 0

def get_purchase_total(cursor, nonce, only_billable=False):
	"""
	get total cost of order id'd by nonce,
	per item we take volunteering_price if any volunteering is done
	(otherwise we take price), and we deduct any discounts
	"""

	f = ''
	if (only_billable):
		f = 'and product.billable = 1'

	q = """
		select
			sum(purchase_items.n * (case
				when (
					purchase_items.person_volunteers_during or
					purchase_items.person_volunteers_after)
				then
					product.volunteering_price
				else
					product.price
				end)
			)
			as total
		from
			purchase_items
			inner join product on purchase_items.product_id = product.id
			inner join purchase on purchase_items.purchase_id = purchase.id
		where
			purchase.nonce = :nonce {0};
		""".format(f)
	qd = { 'nonce' : nonce }
	cursor.execute(q, qd)
	rs = cursor.fetchone()
	return rs['total'] or 0

def get_total_tickets(cursor):
	"""
	get total number of tickets currently ordered by everyone,
	excluding removed orders
	"""
	q = """
		select
			sum(n) as n_tickets
		from
			purchase_items
			inner join product on purchase_items.product_id = product.id
			inner join purchase on purchase_items.purchase_id = purchase.id
		where
			product.name like 'ticket%' AND
			purchase.removed = 0;
		"""
	cursor.execute(q)
	rs = cursor.fetchone()
	return rs['n_tickets'] or 0

def get_prices(cursor):
	"""
	get all prices in [ { product_name : price } ]
	"""
	q = """select name, price from product;"""
	cursor.execute(q)
	return cursor.fetchall()

def get_purchases(cursor, strip_removed=False):
	"""
	get total overview of all purchases in the system, including all types
	of items, optionally culling the removed ones
	"""
	q = """
		select
			pu.id as id,
			pu.nonce as nonce,
			pu.created_at as created_at,
			pu.email as email,
			pu.handle as handle,
			pu.paid as paid,
			pu.removed as removed,
			sum(pui.n * pr.price) as total_price
		from
			purchase_items pui
			inner join purchase pu on pui.purchase_id = pu.id
			inner join product pr on pui.product_id = pr.id
		{0}
		group by
			pu.id;
		"""
	if strip_removed:
		opt = "where pu.removed = 0"
	else:
		opt = ""
	cursor.execute(q.format(opt))
	rs = cursor.fetchall()
	return rs

def get_overview_something(cursor, what):
	"""
	get an overview of tickets/tshirts/... along with
	how many of them were purchased
	"""
	q = """
		select
			pr.name name,
			sum(pi.n) n
		from
			purchase_items pi
			inner join product pr on pi.product_id = pr.id
			inner join purchase pu on pi.purchase_id = pu.id
		where
			pr.name like '{0}%' and
			pu.removed = 0
		group by pr.name;"""
	cursor.execute(q.format(what))
	return cursor.fetchall()

def get_overview_tickets(cursor):
	return get_overview_something(cursor, 'ticket')

def get_overview_tshirts(cursor):
	return get_overview_something(cursor, 'tshirt')

def get_timeline_something(cursor, what):
	"""
	get a timeline of tickets/tshirts/... on a timeline of
	{ 'at' : timestamp_of_order, 'n' : how_many_ordered }
	"""
	q = """
		select
			pu.created_at at,
			sum(pi.n) n
		from
			purchase pu
			inner join purchase_items pi on pu.id = pi.purchase_id
			inner join product pr on pi.product_id = pr.id
		where
			pu.removed=0 and
			pr.name like '{0}%'
		group by pu.created_at
		order by pu.created_at, pr.name asc;"""
	cursor.execute(q.format(what))
	return cursor.fetchall()

def get_timeline_tickets(cursor):
	return get_timeline_something(cursor, 'ticket')

def get_timeline_tshirts(cursor):
	return get_timeline_something(cursor, 'tshirt')


def purchase_mark_paid(cursor, purchase_id):
	"""mark a purchase as being paid"""
	q = "update purchase set paid = 1, paid_at = :now where id = :purchase_id;"
	cursor.execute(q, { 'purchase_id' : purchase_id, 'now' : datetime.datetime.utcnow() })

def purchase_remove(cursor, purchase_id):
	"""mark a purchase as being removed"""
	q = "update purchase set removed=1, removed_at=:now where id = :purchase_id;"
	cursor.execute(q, { 'purchase_id' : purchase_id, 'now' : datetime.datetime.utcnow() })
