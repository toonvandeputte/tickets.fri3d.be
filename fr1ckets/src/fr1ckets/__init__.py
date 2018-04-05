from flask import Flask

app = Flask(__name__)

try:
	app.config.from_pyfile('fr1ckets_priv.conf')
	app.secret_key = app.config['SECRET_KEY']
	app.debug = True
except IOError:
	for i in range(5):
		print "YOU ARE RUNNING THE STOCK CONFIG, which is not in git, smtp passwords and so on, ask jef for fr1ckets_priv.conf"
	app.config.from_pyfile('fr1ckets.conf')

import fr1ckets.views
import fr1ckets.model.setup
