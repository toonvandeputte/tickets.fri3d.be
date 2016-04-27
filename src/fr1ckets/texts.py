# -*- coding: utf-8 -*-
# vim: ts=4:sw=4:noexpandtab
texts = {}

# mail sent when visitor makes a purchase, and it's OK
texts['MAIL_TICKETS_ORDERED_OK_SUBJECT'] = u"Fri3dcamp 2016 order ontvangen!"
texts['MAIL_TICKETS_ORDERED_OK_HTML'] = u"""<html>
<body>
<p>Beste,</p>
<p>Bedankt voor je aankoop op de Fri3dcamp 2016 ticket page!</p>
<p>Gelieve binnen {days_max} dagen het bedrag van <b>€{amount}</b> over te maken op rekening {payment_account}, met als vermelding "{payment_code}".</p>
<p>We sturen je een bevestigingsmailtje op dit adres als de betaling ontvangen is.</p>
<p>We zien je graag op het kamp!</p>
<p>Met vriendelijke groeten,</p>
<p>de Fri3d orga.</p>
<p><small>Dit is een automatische mail. Bij vragen of opmerkingen, gelieve te mailen naar <a mailto="tickets@fri3d.be">tickets@fri3d.be</a>.</small></p>
</body>
</html>"""

texts['MAIL_TICKETS_ORDERED_OK_TEXT'] = u"""Beste,

Bedankt voor je aankoop op de Fri3dcamp 2016 ticket page!

Gelieve binnen {days_max} dagen het bedrag van €{amount} over te maken op rekening {payment_account}, met als vermelding "{payment_code}".

We sturen je een bevestigingsmailtje op dit adres als de betaling ontvangen is. We zien je graag op het kamp!

Met vriendelijke groeten,

de Fri3d orga.

Dit is een automatische mail. Bij vragen of opmerkingen, gelieve te mailen naar tickets@fri3d.be."""

# mail sent when visitor makes a purchase, but it's queued
texts['MAIL_TICKETS_ORDERED_QUEUE_SUBJECT'] = u"Fri3dcamp 2016 registratie ontvangen!"
texts['MAIL_TICKETS_ORDERED_QUEUE_HTML'] = u"""<html>
<body>
<p>Beste,</p>
<p>Bedankt voor je registratie op de Fri3dcamp 2016 ticket page!</p>
<p>Helaas zijn alle beschikbare plaatsen volzet. We hebben je bestelling onthouden en contacteren je ééns er genoeg plaatsen zijn vrijgekomen, ook hierin hanteren we een first-come first-served principe.</p>
<p>Met vriendelijke groeten,</p>
<p>de Fri3d orga.</p>
<p><small>Dit is een automatische mail. Bij vragen of opmerkingen, gelieve te mailen naar <a mailto="tickets@fri3d.be">tickets@fri3d.be</a>.</small></p>
</body>
</html>"""

texts['MAIL_TICKETS_ORDERED_QUEUE_TEXT'] = u"""Beste,

Bedankt voor je aankoop op de Fri3dcamp 2016 ticket page!

Helaas zijn alle beschikbare plaatsen volzet. We hebben je bestelling onthouden en contacteren je ééns er genoeg plaatsen zijn vrijgekomen, ook hierin hanteren we een first-come first-served principe.

Met vriendelijke groeten,

de Fri3d orga.

Dit is een automatische mail. Bij vragen of opmerkingen, gelieve te mailen naar tickets@fri3d.be."""

# mail sent when purchase has been unqueued
texts['MAIL_UNQUEUED_SUBJECT'] = u"Fri3dcamp 2016 plaatsen vrijgekomen!"
texts['MAIL_UNQUEUED_HTML'] = u"""<html>
<body>
<p>Beste,</p>
<p>Goed nieuws! Toen u recent een bestelling plaatste op de ticket-site van Fri3dcamp 2016 waren er niet genoeg vrije plaatsen meer. Maar omdat er ondertussen terug plaatsen zijn vrijgekomen kan uw bestelling als nog doorgaan!</p>
<p>Gelieve binnen {days_max} dagen het bedrag van <b>€{amount}</b> over te maken op rekening {payment_account}, met als vermelding "{payment_code}".</p>
<p>We sturen je een bevestigingsmailtje op dit adres als de betaling ontvangen is.</p>
<p>We zien je graag op het kamp!</p>
<p>Met vriendelijke groeten,</p>
<p>de Fri3d orga.</p>
<p><small>Dit is een automatische mail. Bij vragen of opmerkingen, gelieve te mailen naar <a mailto="tickets@fri3d.be">tickets@fri3d.be</a>.</small></p>
</body>
</html>"""

texts['MAIL_UNQUEUED_TEXT'] = u"""Beste,

Goed nieuws! Toen u recent een bestelling plaatste op de ticket-site van Fri3dcamp 2016 waren er niet genoeg vrije plaatsen meer. Maar omdat er ondertussen terug plaatsen zijn vrijgekomen kan uw bestelling als nog doorgaan!

Gelieve binnen {days_max} dagen het bedrag van <b>€{amount}</b> over te maken op rekening {payment_account}, met als vermelding "{payment_code}".

We sturen je een bevestigingsmailtje op dit adres als de betaling ontvangen is.

Met vriendelijke groeten,

de Fri3d orga.

Dit is een automatische mail. Bij vragen of opmerkingen, gelieve te mailen naar tickets@fri3d.be."""

# mail sent when payment has been received
texts['MAIL_PAYMENT_RECEIVED_SUBJECT'] = u"Uw Fri3dcamp 2016 betaling is binnen!"
texts['MAIL_PAYMENT_RECEIVED_HTML'] = u"""<html>
<body>
<p>Beste,</p>
<p>Uw betaling is binnengekomen, alles zal klaarliggen op het kamp. Tot dan!</p>
<p>Met vriendelijke groeten,</p>
<p>de Fri3d orga.</p>
<p><small>Dit is een automatische mail. Bij vragen of opmerkingen, gelieve te mailen naar <a mailto="tickets@fri3d.be">tickets@fri3d.be</a>.</small></p>
</body>
</html>"""

texts['MAIL_PAYMENT_RECEIVED_TEXT'] = u"""Beste,

Uw betaling is binnengekomen, alles zal klaarliggen op het kamp. Tot dan!

Met vriendelijke groeten,

de Fri3d orga.

Dit is een automatische mail. Bij vragen of opmerkingen, gelieve te mailen naar tickets@fri3d.be."""
