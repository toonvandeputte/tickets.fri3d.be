#!/usr/bin/env python
import pprint
import sqlite3
import random
import os
import string
import datetime

reset_sql_file = "./fr1ckets_db.sql"
db_file = "/var/tmp/fr1ckets.sqlite"

MAX_TICKETS = 192
MAX_AGE_DAYS = 14

print "deleting db file {0}"
try:
	os.remove(db_file)
except OSError:
	pass

print "reloading db file {0} from {1}".format(db_file, reset_sql_file)
db_con = sqlite3.connect(db_file)
db_con.row_factory = sqlite3.Row
db_cur = db_con.cursor()

with open(reset_sql_file, "r") as f:
	db_cur.executescript(f.read())

print "stuffing..."
db_cur.execute("select name, id from product;")
products = { r['name'] : r['id'] for r in db_cur.fetchall() }
pprint.pprint(products)

n_tickets_remaining = MAX_TICKETS
while True:
	n = random.choice(range(1, 4))
	if n > n_tickets_remaining:
		break

	# create an order
	handle = ''.join([ random.choice(string.ascii_lowercase) for x in range(6) ])
	email = handle + '@' + handle + '.nonexistent'
	nonce = ''.join([ random.choice(string.ascii_lowercase) for x in range(6) ])

	offset = datetime.timedelta(days=random.choice(range(1, MAX_AGE_DAYS+1)))

	q = "insert into purchase (email, handle, nonce, created_at) values (?, ?, ?, ?);"
	db_cur.execute(q, (email, handle, nonce, datetime.datetime.utcnow() - offset))
	purchase_id = db_cur.lastrowid

	n_tickets_remaining -= n

	t = random.choice([ p for p in products.keys() if 'ticket' in p ])
	q = """
		insert into
			purchase_items (purchase_id, product_id, n)
		select
			?, product.id, ?
		from
			product
		where
			product.name = ?"""
	db_cur.execute(q, (purchase_id, n, t))

	if 'business' in t:
		q = """
			update purchase
			set business_name=?, business_address=?, business_vat=?
			where nonce=?;"""
		db_cur.execute(q, (handle + ' NV', "{0} street\n{0} ville\nschoten".format(handle), 'BE 4444.333.333', nonce))

	likes_tshirts = random.choice([0, 1])
	n_tshirts = n * 2
	for x in range(n_tshirts):
		t = random.choice([ p for p in products.keys() if 'tshirt' in p ])
		q = """
			insert into
				purchase_items (purchase_id, product_id, n)
			select
				?, product.id, ?
			from
				product
			where
				product.name = ?"""
		db_cur.execute(q, (purchase_id, 1, t))

	bad_payer = random.choice(range(4))
	if not bad_payer:
		offset_payment = datetime.timedelta(seconds=random.choice(range(0, int(offset.total_seconds()))))
		q = "update purchase set paid=1, paid_at=? where id=?;"
		db_cur.execute(q, (datetime.datetime.utcnow() - offset_payment, purchase_id))



db_con.commit()
