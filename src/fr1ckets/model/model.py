from fr1ckets import app
import string
import random
import datetime
import copy
import MySQLdb

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

	the timezone stuff is ugly, but mysql happily returns 
	"""
	q = "SET @@session.time_zone='+00:00';"
	cursor.execute(q)
	q = """
		select
			id,
			email,
			discount,
			unix_timestamp(available_from) as available_from_unix,
			available_from
		from
			reservation
		where
			email = %(email)s
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
		return res

	q = """
		update
			reservation
		set
			claimed = 1,
			claimed_at = %(now)s
		where
			email = %(email)s
			AND claimed = 0
			AND available_from <= utc_timestamp();
		"""
	qd = {
		'now' : datetime.datetime.utcnow(),
		'email' : email,
	}

	cursor.execute(q, qd)

	return res

def reservation_get(cursor, id=None):
	f = ""
	if id:
		f = " where id=%(id)s"
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
	cursor.execute(q, { 'id' : id })
	return cursor.fetchall()

def reservation_delete(cursor, id):
	q = """
		delete from
			reservation
		where
			id=%(id)s;
		"""
	cursor.execute(q, { 'id' : id })

def reservation_update(cursor, id, values):
	q = """
		update
			reservation
		set
			email=%(email)s,
			discount=%(discount)s,
			available_from=%(available_from)s,
			claimed=%(claimed)s,
			claimed_at=%(claimed_at)s,
			comments=%(comments)s
		where
			id=%(id)s;
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
			%(email)s,
			%(discount)s,
			%(available_from)s,
			%(claimed)s,
			%(claimed_at)s,
			%(comments)s
		);
		"""
	cursor.execute(q, values)

def generate_payment_code(date):
	"""
	generate a payment code "mDDxxxxxxxcc", prettyfied as
	"+++WWx/xxxx/xxxcc+++", with;
		WW = week in year
		xxxxxxxx = random
		cc = checksum
	"gestructureerde mededeling"-compliant
	"""
	first = date.isocalendar()[1] * 10
	first *= 1000000000

	last = random.randint(0, 99999999) * 100
	
	total = first + last
	check = (total / 100) % 97
	check = check if check else 97
	total += check
	return "{0:012d}".format(total)

def purchase_create(cursor, email, products, billing_info, queued):
	"""
	"""
	now = datetime.datetime.utcnow()
	nonce = random_string(16)

	# get the reservation for this email
	reservation = reservation_claim(cursor, email)

	payment_code = generate_payment_code(now)

	# the purchase proper
	q = """
		insert into purchase (
			email, nonce, reservation_id, created_at, queued,
			business_name, business_address, business_vat,
			payment_code)
		values
			(%s, %s, %s, %s, %s, %s, %s, %s, %s);
		"""
	n_tries = 20
	while True:
		"""
		we have randomness in the payment code, should it ever clash, retry
		up to n_tries before finally bugging out (could be another issue)
		"""
		try:
			payment_code = generate_payment_code(now)
			cursor.execute(q, (email, nonce, reservation['id'], now, queued,
				billing_info['name'], billing_info['address'], billing_info['vat'],
				payment_code))
		except MySQLdb.IntegrityError as e:
			n_tries -= 1
			if n_tries == 0:
				raise e
			else:
				continue
		finally:
			break

	purchase_id = cursor.lastrowid

	# add the products
	q = """
		insert into purchase_items (
			purchase_id, product_id, n, person_name, person_dob,
			person_volunteers_during, person_volunteers_after, person_food_vegitarian)
		values
			(%(purchase_id)s, %(product_id)s, %(n)s, %(person_name)s, %(person_dob)s,
			%(person_volunteers_during)s, %(person_volunteers_after)s, %(person_food_vegitarian)s);
		"""
	for p in products:
		p['purchase_id'] = purchase_id
		cursor.execute(q, p)

	out = {}
	out['nonce'] = nonce
	out['payment_code'] = payment_code
	out['id'] = purchase_id

	return out

def purchase_get(cursor, nonce=None, id=None):
	qf = []
	if nonce:
		qf.append("nonce=%(nonce)s")
	if id:
		qf.append("id=%(id)s")

	q = """
		select
			id,
			email,
			reservation_id,
			created_at,
			dequeued_at,
			billed_at,
			queued,
			once_queued,
			business_name,
			business_address,
			business_vat,
			payment_code,
			nonce
		from
			purchase
		where
			""" + " AND ".join(qf) + """;
		"""
	cursor.execute(q, { 'nonce' : nonce, 'id' : id })
	return cursor.fetchone()

def purchase_items_get(cursor, id):
	q = """
		select
			pr.display as product,
			pr.billable as billable,
			pui.n as n,
			case
				when
					pui.person_volunteers_during
				then
					pr.volunteering_price
				else
					pr.price
			end as price_single,
			pui.n * (case
				when
					pui.person_volunteers_during
				then
					pr.volunteering_price
				else
					pr.price
			end) as price_total,
			pui.person_volunteers_during as volunteers_during,
			pui.person_volunteers_after as volunteers_after,
			pui.person_name as person_name,
			pui.person_dob as person_dob,
			pui.person_food_vegitarian as person_vegitarian
		from
			purchase_items pui
			inner join product pr on pui.product_id = pr.id
		where
			pui.purchase_id = %s;
		"""
	cursor.execute(q, (id,))
	return cursor.fetchall()

def purchase_history_append(cursor, id, creator='SYSTEM', msg=None):
	q = """
		insert into purchase_history (
			purchase_id,
			created_at,
			creator,
			event
		)
		values (
			%(purchase_id)s,
			%(created_at)s,
			%(creator)s,
			%(event)s
		);
		"""
	qd = {
		'purchase_id' : id,
		'created_at' : datetime.datetime.utcnow(),
		'creator' : creator,
		'event' : msg,
	}
	cursor.execute(q, qd)

def purchase_history_get(cursor, id):
	q = """
		select
			created_at,
			creator,
			event
		from
			purchase_history
		where
			purchase_id=%s;
		"""
	cursor.execute(q, (id,))
	return cursor.fetchall()

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
			purchase.nonce = %(nonce)s;
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
			truncate(sum(purchase_items.n * (case
				when
					purchase_items.person_volunteers_during
				then
					product.volunteering_price
				else
					product.price
				end)
			), 2)
			as total
		from
			purchase_items
			inner join product on purchase_items.product_id = product.id
			inner join purchase on purchase_items.purchase_id = purchase.id
		where
			purchase.nonce = %(nonce)s {0};
		""".format(f)
	qd = { 'nonce' : nonce }
	cursor.execute(q, qd)
	rs = cursor.fetchone()
	return rs['total'] or 0

def tickets_actual_total(cursor):
	"""
	get the number of tickets we actually expect to attend, meaning
	every ticket not removed or queued
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
			purchase.removed = 0 and
			purchase.queued = 0;
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
			pu.payment_code as payment_code,
			pu.paid as paid,
			pu.removed as removed,
			pu.queued as queued,
			pu.once_queued as once_queued,
			pu.billed as billed,
			pu.dequeued_at as dequeued_at,
			pu.billed_at as billed_at,
			sum(pui.n * (
				case
				when (pui.person_volunteers_during)
				then pr.volunteering_price
				else pr.price
				end)
			) - res.discount as total_price,
			sum(
				case
				when pr.name like 'ticket%'
				then pui.n
				else 0
				end
			) as n_tickets,
			sum(
				case
				when pr.name like 'token%'
				then pui.n
				else 0
				end
			) as n_tokens,
			sum(
				case
				when pr.name like 'tshirt%'
				then pui.n
				else 0
				end
			) as n_tshirts,
			sum(
				case
				when pr.billable
				then 1
				else 0
				end
			) as n_billable
		from
			purchase_items pui
			inner join purchase pu on pui.purchase_id = pu.id
			inner join product pr on pui.product_id = pr.id
			inner join reservation res on pu.reservation_id = res.id
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

def get_overview_tokens(cursor):
	return get_overview_something(cursor, 'token')

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


def purchase_mark_paid(cursor, purchase_id, paid):
	"""mark a purchase as being paid"""
	q = "update purchase set paid = %(paid)s, paid_at = %(now)s where id = %(purchase_id)s;"
	cursor.execute(q, { 'purchase_id' : purchase_id, 'now' : datetime.datetime.utcnow(), 'paid' : paid })

def purchase_mark_billed(cursor, purchase_id, billed):
	"""mark a purchase as being billed"""
	q = "update purchase set billed = %(billed)s, billed_at = %(now)s where id = %(purchase_id)s;"
	cursor.execute(q, { 'purchase_id' : purchase_id, 'now' : datetime.datetime.utcnow(), 'billed' : billed })

def purchase_mark_removed(cursor, purchase_id, removed):
	"""mark a purchase as being removed"""
	q = "update purchase set removed=%(removed)s, removed_at=%(now)s where id = %(purchase_id)s;"
	cursor.execute(q, { 'purchase_id' : purchase_id, 'now' : datetime.datetime.utcnow(), 'removed' : removed })

def purchase_mark_dequeued(cursor, purchase_id):
	"""mark a purchase as being removed"""
	q = "update purchase set queued=0, once_queued=1, dequeued_at=%(now)s where id = %(purchase_id)s;"
	cursor.execute(q, { 'purchase_id' : purchase_id, 'now' : datetime.datetime.utcnow() })

def get_stats_tickets(cursor, removed=0, queued=0):
	q = """
		select
			pr.name as type,
			sum(pui.n) as n_total,
			sum(case
				when pui.person_dob >= %(cutoff)s
				then 0
				else pui.person_volunteers_during
				end
			) as n_volunteers_during,
			sum(case
				when pui.person_dob >= %(cutoff)s
				then 0
				else pui.person_volunteers_after
				end
			) as n_volunteers_after,
			sum(case
				when pui.person_food_vegitarian
				then 1
				else 0
				end
			) as n_vegetarian
		from
			purchase_items pui
			inner join purchase pu on pui.purchase_id = pu.id
			inner join product pr on pui.product_id = pr.id
		where
			pr.name like 'ticket%%'
			and pu.removed = %(removed)s
			and pu.queued = %(queued)s
		group by
			pr.name;
		"""
	qd = {
		'removed' : removed,
		'queued' : queued,
		'cutoff' : app.config['VOLUNTEERING_CUTOFF_DATE'],
	}

	cursor.execute(q, qd)
	return cursor.fetchall()

def get_stats_tshirts(cursor, removed=0, queued=0):
	q = """
		select
			pr.name as type,
			sum(pui.n) as n_total
		from
			purchase_items pui
			inner join purchase pu on pui.purchase_id = pu.id
			inner join product pr on pui.product_id = pr.id
		where
			pr.name like 'tshirt%%'
			and pu.removed = %(removed)s
			and pu.queued = %(queued)s
		group by
			pr.name;
		"""
	qd = {
		'removed' : removed,
		'queued' : queued,
	}

	cursor.execute(q, qd)
	return cursor.fetchall()
