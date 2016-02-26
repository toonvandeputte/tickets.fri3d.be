from fr1ckets import app

try:
	app.config.from_pyfile('fr1ckets_priv.conf')
except IOError:
	for i in range(5):
		print "YOU ARE RUNNING THE STOCK CONFIG, which is not in git, smtp passwords and so on, ask jef for fr1ckets_priv.conf"
	app.config.from_pyfile('fr1ckets.conf')


if __name__ == '__main__':
	app.secret_key = "dev"
	app.run(host='0.0.0.0', debug=True)
