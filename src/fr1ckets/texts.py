# -*- coding: utf-8 -*-
# vim: ts=4:sw=4:noexpandtab
texts = {}

# mail sent when visitor makes a purchase, and it's OK
texts['MAIL_TICKETS_ORDERED_OK_SUBJECT'] = u"Fri3d Camp 2016 bestelling ontvangen!"
texts['MAIL_TICKETS_ORDERED_OK_HTML'] = u"""<html>
<body>
<p>Beste,</p>
<p>Bedankt voor je aankoop op de Fri3d Camp 2016 ticketshop!</p>
<p>Gelieve binnen de {days_max} dagen het bedrag van <b>€{amount}</b> over te maken op rekening {payment_account}, met als vermelding "{payment_code}".</p>
<p>We sturen je een bevestigingsmail op {email} als de betaling ontvangen is.</p>
<p>Als we je betaling niet binnen de 14 dagen ontvangen hebben, worden je tickets opnieuw vrijgegeven voor verkoop.</p>
<p>We zien je graag op het kamp!</p>
<p>Met vriendelijke groeten,</p>
<p>De Fri3d Camp organisatie.</p>
<p><small>Dit is een automatische mail. Heb je nog vragen? Mail dan naar <a mailto="tickets@fri3d.be">tickets@fri3d.be</a>.</small></p>
</body>
</html>"""

texts['MAIL_TICKETS_ORDERED_OK_TEXT'] = u"""Beste,

Bedankt voor je aankoop op de Fri3d Camp 2016 ticketshop!

Gelieve binnen de {days_max} dagen het bedrag van €{amount} over te maken op rekening {payment_account}, met als vermelding "{payment_code}".

We sturen je een bevestigingsmail op {email} als de betaling ontvangen is.

Als we je betaling niet binnen de 14 dagen ontvangen hebben, worden je tickets opnieuw vrijgegeven voor verkoop.

We zien je graag op het kamp!

Met vriendelijke groeten,

De Fri3d Camp organisatie.

Dit is een automatische mail. Heb je nog vragen? Mail dan naar tickets@fri3d.be."""

# mail sent when visitor makes a purchase, but it's queued
texts['MAIL_TICKETS_ORDERED_QUEUE_SUBJECT'] = u"Fri3d Camp 2016 registratie ontvangen!"
texts['MAIL_TICKETS_ORDERED_QUEUE_HTML'] = u"""<html>
<body>
<p>Beste,</p>
<p>Bedankt voor je registratie op de Fri3d Camp 2016 ticketshop!</p>
<p>Helaas zijn alle beschikbare plaatsen volzet. Je bestelling is dus niet kunnen doorgaan. We hebben je bestelling onthouden en contacteren je wanneer er voldoende plaatsen zijn vrijgekomen. We hanteren een first-come first-served principe.</p>
<p>Heb je ondertussen andere plannen, en wil je je bestelling afzeggen? Laat dat dan snel weten via <a mailto="tickets@fri3d.be">tickets@fri3d.be</a>. Zo maak je anderen erg blij!</p>
<p>Met vriendelijke groeten,</p>
<p>De Fri3d Camp organisatie.</p>
<p><small>Dit is een automatische mail. Heb je nog vragen? Mail dan naar <a mailto="tickets@fri3d.be">tickets@fri3d.be</a>.</small></p>
</body>
</html>"""

texts['MAIL_TICKETS_ORDERED_QUEUE_TEXT'] = u"""Beste,

Bedankt voor je aankoop op de Fri3d Camp 2016 ticketshop!

Helaas zijn alle beschikbare plaatsen volzet. Je bestelling is dus niet kunnen doorgaan. We hebben je bestelling onthouden en contacteren je wanneer er voldoende plaatsen zijn vrijgekomen. We hanteren een first-come first-served principe.

Heb je ondertussen andere plannen, en wil je je bestelling afzeggen? Laat dat dan snel weten via tickets@fri3d.be. Zo maak je anderen erg blij!

Met vriendelijke groeten,

De Fri3d Camp organisatie.

Dit is een automatische mail. Heb je nog vragen? Mail dan naar tickets@fri3d.be."""

# mail sent when purchase has been unqueued
texts['MAIL_UNQUEUED_SUBJECT'] = u"Fri3d Camp 2016 plaatsen vrijgekomen!"
texts['MAIL_UNQUEUED_HTML'] = u"""<html>
<body>
<p>Beste,</p>
<p>Goed nieuws! Er zijn nieuwe plaatsen vrijgekomen voor Fri3d Camp 2016. Toen je recent een bestelling plaatste op de ticketsite van Fri3d Camp 2016 waren er niet genoeg vrije plaatsen meer. Maar omdat er opnieuw plaatsen zijn, kan je bestelling alsnog doorgaan!</p>
<p>Gelieve binnen de {days_max} dagen het bedrag van <b>€{amount}</b> over te maken op rekening {payment_account}, met als vermelding "{payment_code}".</p>
<p>We sturen je een bevestigingsmail op dit adres als de betaling ontvangen is.</p>
<p>Als we je betaling niet binnen de {days_max} dagen ontvangen hebben, worden je tickets opnieuw vrijgegeven voor verkoop.</p>
<p>Heb je ondertussen andere plannen, en wil je je bestelling afzeggen? Laat dat dan snel weten via <a mailto="tickets@fri3d.be">tickets@fri3d.be</a>. Zo maak je anderen die op tickets zitten te wachten erg blij!</p>
<p>We zien je graag op het kamp!</p>
<p>Met vriendelijke groeten,</p>
<p>De Fri3d Camp organisatie.</p>
<p><small>Dit is een automatische mail. Heb je nog vragen? Mail dan naar <a mailto="tickets@fri3d.be">tickets@fri3d.be</a>.</small></p>
</body>
</html>"""

texts['MAIL_UNQUEUED_TEXT'] = u"""Beste,

Goed nieuws! Er zijn nieuwe plaatsen vrijgekomen voor Fri3d Camp 2016. Toen je recent een bestelling plaatste op de ticketsite van Fri3d Camp 2016 waren er niet genoeg vrije plaatsen meer. Maar omdat er opnieuw plaatsen zijn, kan je bestelling alsnog doorgaan!

Gelieve binnen de {days_max} dagen het bedrag van <b>€{amount}</b> over te maken op rekening {payment_account}, met als vermelding "{payment_code}".

We sturen je een bevestigingsmail op dit adres als de betaling ontvangen is.

Als we je betaling niet binnen de {days_max} dagen ontvangen hebben, worden je tickets opnieuw vrijgegeven voor verkoop.

Heb je ondertussen andere plannen, en wil je je bestelling afzeggen? Laat dat dan snel weten via tickets@fri3d.be. Zo maak je anderen die op tickets zitten te wachten erg blij!

Met vriendelijke groeten,

De Fri3d Camp organisatie.

Dit is een automatische mail. Heb je nog vragen? Mail dan naar tickets@fri3d.be."""

# mail sent when payment has been received
texts['MAIL_PAYMENT_RECEIVED_SUBJECT'] = u"Uw Fri3d Camp 2016 betaling is binnen!"
texts['MAIL_PAYMENT_RECEIVED_HTML'] = u"""<html>
<body>
<p>Beste,</p>
<p>Je betaling is binnengekomen! Je hoeft verder niets meer te doen. Je tickets en je eventuele extra's, zullen klaarliggen op het kamp. Hou <a href="http://www.fri3d.be">www.fri3d.be</a> in het oog voor updates. Tot dan!</p>
<p>Met vriendelijke groeten,</p>
<p>De Fri3d Camp organisatie.</p>
<p><small>Dit is een automatische mail. Heb je nog vragen? Mail dan naar <a mailto="tickets@fri3d.be">tickets@fri3d.be</a>.</small></p>
</body>
</html>"""

texts['MAIL_PAYMENT_RECEIVED_TEXT'] = u"""Beste,

Je betaling is binnengekomen! Je hoeft verder niets meer te doen. Je tickets en je eventuele extra's, zullen klaarliggen op het kamp. Hou www.fri3d.be in het oog voor updates. Tot dan!

Met vriendelijke groeten,

De Fri3d Camp organisatie.

Dit is een automatische mail. Heb je nog vragen? Mail dan naar tickets@fri3d.be."""

# mail sent when payment has been removed
texts['MAIL_REMOVED_SUBJECT'] = u"Uw Fri3d Camp 2016 bestelling is geschrapt"
texts['MAIL_REMOVED_HTML'] = u"""<html>
<body>
<p>Beste,</p>
<p>We hebben de betaling van je tickets helaas niet binnen de 14 dagen ontvangen. Je bestelling is dan ook geschrapt, en je bestelde tickets en eventuele extra's zijn opnieuw vrijgegeven voor verkoop.</p>
<p>Mocht deze mail je betaling kruisen, dan zullen we het bedrag terugstorten.</p>
<p>Met vriendelijke groeten,</p>
<p>De Fri3d Camp organisatie.</p>
<p><small>Dit is een automatische mail. Heb je nog vragen? Mail dan naar <a mailto="tickets@fri3d.be">tickets@fri3d.be</a>.</small></p>
</body>
</html>"""

texts['MAIL_REMOVED_TEXT'] = u"""Beste,

We hebben de betaling van je tickets helaas niet binnen de 14 dagen ontvangen. Je bestelling is dan ook geschrapt, en je bestelde tickets en eventuele extra's zijn opnieuw vrijgegeven voor verkoop.

Mocht deze mail je betaling kruisen, dan zullen we het bedrag terugstorten.

Met vriendelijke groeten,

De Fri3d Camp organisatie.

Dit is een automatische mail. Heb je nog vragen? Mail dan naar tickets@fri3d.be."""

# mail sent when user commits a volunteering schedule
texts['MAIL_VOLUNTEERING_SCHEDULE_SUBJECT'] = u"Uw Fri3d Camp 2016 vrijwilligers-schema is opgeslagen."
texts['MAIL_VOLUNTEERING_SCHEDULE_HTML'] = u"""<html>
<body>
<p>Beste,</p>
<p>Hier een overzicht van je vrijwilligers-schema dat je hebt ingegeven. Je kan later nog terug naar de pagina gaan om dit aan te passen.</p>
<p>{schedule_html}</p>
<p>Met vriendelijke groeten,</p>
<p>De Fri3d Camp organisatie.</p>
<p><small>Dit is een automatische mail. Heb je nog vragen? Mail dan naar <a mailto="tickets@fri3d.be">tickets@fri3d.be</a>.</small></p>
</body>
</html>"""

texts['MAIL_VOLUNTEERING_SCHEDULE_TEXT'] = u"""Beste,

Hier een overzicht van je vrijwilligers-schema dat je hebt ingegeven. Je kan later nog terug naar de pagina gaan om dit aan te passen.

{schedule_text}

Met vriendelijke groeten,

De Fri3d Camp organisatie.

Dit is een automatische mail. Heb je nog vragen? Mail dan naar tickets@fri3d.be."""
