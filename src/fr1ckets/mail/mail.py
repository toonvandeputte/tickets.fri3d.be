# -*- coding: utf-8 -*-
# vim: ts=4:sw=4:noexpandtab
from fr1ckets import app
from fr1ckets.background.tasks import mail
from fr1ckets.background.tasks import notif

def send_mail(from_addr, to_addrs, subject, msg_html, msg_text):
	mail.delay(from_addr, to_addrs, subject, msg_html, msg_text,
			(app.config['SMTP_USERNAME'], app.config['SMTP_PASSWORD']),
			(app.config['SMTP_SERVER'], app.config['SMTP_PORT']))

def send_notif(msg):
	notif.delay(app.config['NOTIF_URL'], msg)
