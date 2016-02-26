# -*- coding: utf-8 -*-
# vim: ts=4:sw=4:noexpandtab
texts = {}

texts['MAIL_TICKETS_SUBJECT'] = u"Fri3dcamp 2016 order ontvangen!"
texts['MAIL_TICKETS_HTML'] = u"""<html>
<body>
<p>Beste,</p>
<p>Bedankt voor je aankoop op de Fri3dcamp 2016 ticket page!</p>
<p>Gelieve binnen {days_max} dagen het bedrag van <b>€{amount}</b> over te maken op rekening BE 0123456789, met als vermelding "{email}".</p>
<p>We sturen je een bevestigingsmailtje op dit adres als de betaling ontvangen is.</p>
<p>We zien je graag op het kamp!</p>
<p>Met vriendelijke groeten,</p>
<p>de Fri3d orga.</p>
<p><small>Dit is een automatische mail. Bij vragen of opmerkingen, gelieve te mailen naar <a mailto="tickets@fri3d.be">tickets@fri3d.be</a>.</small></p>
</body>
</html>"""

texts['MAIL_TICKETS_TEXT'] = u"""Beste,

Bedankt voor je aankoop op de Fri3dcamp 2016 ticket page!

Gelieve binnen {days_max} dagen het bedrag van €{amount} over te maken op rekening BE 0123456789, met als vermelding "{email}".

We sturen je een bevestigingsmailtje op dit adres als de betaling ontvangen is. We zien je graag op het kamp!

Met vriendelijke groeten,

de Fri3d orga.

Dit is een automatische mail. Bij vragen of opmerkingen, gelieve te mailen naar tickets@fri3d.be."""
