#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ts=4:sw=4:noexpandtab
import smtplib
import json
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from celery import Celery
from celery.utils.log import get_task_logger

app = Celery(broker='redis://queue')
l = get_task_logger(__name__)

@app.task(name='fr1ckets.background.tasks.mail', bind=True)
def mail(self, from_addr, to_addrs, subject, msg_html, msg_text, smtp_auth, smtp_location):
	l.info("sending mail to {0} subject {1}".format(to_addrs, subject))
	l.info("foo={0}{1}".format(*smtp_location))
	msg = MIMEMultipart('alternative')
	msg['Subject'] = subject
	msg['From'] = from_addr
	msg['To'] = ", ".join(to_addrs)

	part_text = MIMEText(msg_text.encode('utf-8'), 'plain', 'UTF-8')
	part_html = MIMEText(msg_html.encode('utf-8'), 'html', 'UTF-8')

	msg.attach(part_text)
	msg.attach(part_html)

	try:
		server = smtplib.SMTP(*smtp_location)
		server.ehlo()
		server.starttls()
		server.ehlo()
		server.login(*smtp_auth)
		server.sendmail(from_addr, to_addrs, msg.as_string())
	except Exception as e:
		self.retry(exc=e, countdown=3)


@app.task(name='fr1ckets.background.tasks.notif', bind=True)
def notif(self, url, msg):
	l.info("sending notif")

	payload = {
		'text' : msg,
		'username' : 'ticketshop',
		'icon_emoji' : ':space_invader:'
	}

	r = requests.post(url, data=json.dumps(payload))
	l.info("sending notif ret={0}".format(r.text))
