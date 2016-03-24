from flask import request, jsonify
from fr1ckets import app
import pprint
import string
import time
import json
import random
import sqlite3
import datetime

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

def purchase_create(cursor, email):
	"""
	"""
	now = datetime.datetime.utcnow()
	nonce = random_string(16)

	reservation = reservation_claim(cursor, email)
	# the purchase proper
	cursor.execute('INSERT INTO purchase (email, nonce, reservation_id, created_at) VALUES (?, ?, ?, ?);',
		(email, nonce, reservation['id'], now))
	purchase_id = cursor.lastrowid

def purchase_add(cursor, purchase_id, product_name, n, personal_details=None):
	"""
	add a product (specified by product_name) to a purchase (specified by id),
	if personal_details is present this should contain the following (which is
	saved next to the purchase_item):
	{
		'name' : person's name,
		'dob' : person's dob,
		'volunteers_after' : bool,
		'volunteers_during' : bool,
		'food_vegitarian' : bool
	}
	returns affected rows (0 == error)
	"""
	# the purchased items
	q = """
		INSERT INTO
			purchase_items (purchase_id, product_id, n, person_name, person_dob,
				person_volunteers_during, person_volunteers_after, person_food_vegitarian)
		SELECT
			:purchase_id, product.id, :n, :name, :dob, :vol_during, :vol_after, :food_veggy
		FROM
			product
		WHERE
			product.name = :what"""
	qd = { 'purchase_id' : purchase_id, 'n' : n, 'what' : product_name }
	qd.extend(personal_details if personal_details else { '', '', False, False, False })
	cursor.execute(q, qd)

	return cursor.rowcount


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

def purchase_set_business_details(cursor, nonce, name, address, vat):
	q = """
		UPDATE
			purchase
		SET
			business_name = :name,
			business_address = :address,
			business_vat = :vat
		WHERE
			nonce = :nonce;
		"""
	qd = {
		'nonce' : nonce,
		'name' : name,
		'address' : address,
		'vat' : vat,
	}
	cursor.execute(q, qd)

def get_purchase_total(cursor, nonce, product_filter='%'):
	"""
	get total cost of order id'd by nonce
	"""
	q = """
		select
			sum(purchase_items.n * product.price) as total
		from
			purchase_items
			inner join product on purchase_items.product_id = product.id
			inner join purchase on purchase_items.purchase_id = purchase.id
		where
			purchase.nonce = :nonce
			and product.name like :filter;
		"""
	qd = {
		'nonce' : nonce,
		'filter' : product_filter,
	}
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
