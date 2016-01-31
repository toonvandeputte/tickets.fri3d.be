from flask import request, jsonify
from fr1ckets import app
import pprint
import string
import time
import json
import random
import sqlite3
import datetime

def random_string(length=32):
	return ''.join(
		[ random.SystemRandom().choice(
				string.ascii_lowercase +
				string.ascii_uppercase + string.digits)
			for _ in range(length)
		])
import pprint

def create(cursor, email, handle, products):
	"""
	create a new order for email/handle, products is a dict of
	{ product_name : times_ordered }
	"""
	now = datetime.datetime.utcnow()
	nonce = random_string(16)

	# the purchase proper
	cursor.execute('INSERT INTO purchase (email, handle, nonce, created_at) VALUES (?, ?, ?, ?);',
		(email, handle, nonce, now));
	purchase_id = cursor.lastrowid

	# the purchased items
	q = """
		INSERT INTO
			purchase_items (purchase_id, product_id, n)
		SELECT
			:purchase_id, product.id, :n
		FROM
			product
		WHERE
			product.name = :what"""
	qd = { 'purchase_id' : purchase_id }
	for what, n in products.iteritems():
		if not n:
			continue
		qd['n'] = n
		qd['what'] = what
		cursor.execute(q, qd)

	return nonce

def get_purchase_total(cursor, nonce):
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
			purchase.nonce = :nonce;
		"""
	qd = {
		'nonce' : nonce,
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
