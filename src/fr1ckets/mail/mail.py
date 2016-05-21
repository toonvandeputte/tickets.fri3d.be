# -*- coding: utf-8 -*-
# vim: ts=4:sw=4:noexpandtab
from fr1ckets import app
from fr1ckets.background.tasks import mail

def send_mail(from_addr, to_addrs, subject, msg_html, msg_text):
	app.logger.debug(mail)
	app.logger.debug(mail.name)
	mail.delay(from_addr, to_addrs, subject, msg_html, msg_text,
			(app.config['SMTP_USERNAME'], app.config['SMTP_PASSWORD']),
			(app.config['SMTP_SERVER'], app.config['SMTP_PORT']))
