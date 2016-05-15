#!/usr/bin/env python
import requests
from lxml import html
import pprint
import sys
import random
import string
import time
import datetime

def D(*args, **kwargs):
	print("{0} {1}".format(pprint.pformat(*args), pprint.pformat(kwargs) if kwargs else ''))

auth=('hello', 'world')
url=sys.argv[1]

class Form(object):
	tshirt_choices = [ 'tshirt_adult_m_' + size for size in [ 's', 'm', 'l', 'xl' ] ]
	tshirt_choices.extend([ 'tshirt_adult_f_' + size for size in [ 's', 'm', 'l', 'xl' ] ])
	tshirt_choices.extend([ 'tshirt_kid_' + size for size in [ 's', 'm', 'l', 'xl' ] ])
	token_choices = [ 0, 5, 10, 15, 20, 30, 40, 50, 100 ]

	def __init__(self):
		print self.tshirt_choices
		self.data = {}
		self.n_tickets = 0
		for k in [ 'payment', 'supervision', 'excellent' ]:
			self.data['terms_'+k] = 'on'
		for t in self.tshirt_choices:
			self.data[t] = 0
		self.data['n_tickets'] = self.n_tickets

	def set_static(self, email, token):
		self.data['email'] = email
		self.data['csrf_token'] = token

	def set_tokens(self, n):
		if n in self.token_choices:
			self.data['token'] = n
		else:
			print "not a valid token amount, this {0}".format(n)
	
	def set_tshirt(self, which, n):
		if which in self.tshirt_choices:
			self.data[which] = n
		else:
			print "not a valid tshirt, this {0}".format(which)

	def add_ticket(self, name, dob, billable, volunteers_during, volunteers_after, veggy):
		t = 'tickets_{0}_'.format(self.n_tickets)
		self.n_tickets += 1
		self.data['n_tickets'] = self.n_tickets
		self.data.update({
			t+'name' : name,
			t+'dob_year' : dob.year,
			t+'dob_month' : dob.month,
			t+'dob_day' : dob.day,
		})
		# yes, browers don't show these when not checked
		if billable:
			self.data[t+'billable'] = 'on'
		if volunteers_during:
			self.data[t+'options_volunteers_during'] = 'on'
		if volunteers_after:
			self.data[t+'options_volunteers_after'] = 'on'
		if veggy:
			self.data[t+'options_vegitarian'] = 'on'

	def set_business_info(self, name, address, vat):
		self.data.update({
			'business_name' : name,
			'business_address' : address,
			'business_vat' : vat,
		})

	def need_business_info(self):
		return len([ self.data[k] for k in self.data if '_billable' in k and self.data[k] == 'on'])

	def __str__(self):
		return pprint.pformat(self.data)

class RandomForm(Form):

	def __init__(self):
		Form.__init__(self)

	def fill(self, n_tickets, token):
		base = ''.join([ random.choice(string.ascii_letters) for _ in range(5) ])
		age_min = int(time.time())
		age_max = 0

		self.set_static('{0}@{0}.notreal'.format(base), token)
		self.set_tokens(random.choice(self.token_choices))

		for t in range(n_tickets):
			ext = ''.join([ random.choice(string.ascii_letters) for _ in range(4) ])
			name = '{0} {1}'.format(ext, base)
			dob = datetime.datetime.fromtimestamp(random.randrange(age_max, age_min))
			self.add_ticket(name, dob, not bool(random.randint(0, 8)),
				*(bool(random.randint(0, 1)) for _ in range(3) ))
			self.set_tshirt(random.choice(self.tshirt_choices), 1)

		if self.need_business_info():
			self.set_business_info(
					base + 'corp NV',
					base + 'street 1\n' + base + 'ville\n' + base + 'land',
					'BTW 111.111.4444')

s = requests.session()

ts = time.time()

r = s.get(url+'/tickets', auth=auth)

timing_page = time.time() - ts

page = html.fromstring(r.text)
csrf_token = page.forms[0].fields['csrf_token']
r = RandomForm()
r.fill(random.randrange(1, 5), csrf_token)

ts = time.time()
x = s.get(url+'/api/get_reservation/' + r.data['email'], auth=auth)
timing_email = time.time() - ts

ts = time.time()
o = s.post(url+'/api/tickets_register', auth=auth, data=r.data)
timing_post = time.time() - ts
import json
do = json.loads(o.text)
if 'redirect' in do:
	ts = time.time()
	o = s.get(url+do['redirect'])
	timing_confirm = time.time() - ts
else:
	timing_confirm = 0

print "timing: page={0} email={3} post={1} confirm={2} total={4}".format(timing_page, timing_post, timing_confirm, timing_email, timing_page+timing_post+timing_confirm+timing_email)
