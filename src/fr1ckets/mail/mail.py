# -*- coding: utf-8 -*-
# vim: ts=4:sw=4:noexpandtab
import smtplib
from fr1ckets import app
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_mail(from_addr, to_addrs, subject, msg_html, msg_text):
	msg = MIMEMultipart('alternative')
	msg['Subject'] = subject
	msg['From'] = from_addr
	msg['To'] = ", ".join(to_addrs)

	part_text = MIMEText(msg_text.encode('utf-8'), 'plain', 'UTF-8')
	part_html = MIMEText(msg_html.encode('utf-8'), 'html', 'UTF-8')

	msg.attach(part_text)
	msg.attach(part_html)

	try:
		server = smtplib.SMTP(app.config['SMTP_SERVER'], app.config['SMTP_PORT'])
		server.ehlo()
		server.starttls()
		server.ehlo()
		server.login(app.config['SMTP_USERNAME'], app.config['SMTP_PASSWORD'])
		server.sendmail(from_addr, to_addrs, msg.as_string())
	except Exception as e:
		app.logger.error("failed sending mail from \"{0}\" to \"{1}\" subj \"{2}\" reason \"{3!r}\"".format(
			from_addr, to_addrs, subject, e))
