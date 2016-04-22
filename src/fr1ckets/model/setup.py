import MySQLdb
import MySQLdb.cursors
from flask import g
from fr1ckets import app

@app.before_request
def setup_db():
	g.db_con = MySQLdb.connect(user=app.config['DB_USER'],
			passwd=app.config['DB_PASS'],
			db=app.config['DB_NAME'],
			cursorclass=MySQLdb.cursors.DictCursor)
	g.db_cursor = g.db_con.cursor()

@app.teardown_request
def wrapup_db(error):
	db_con = getattr(g, 'db_con', None)
	db_commit = getattr(g, 'db_commit', None)
	if db_con and db_commit:
		if error:
			app.logger.error("wrapup_db(error={0}), rolling back".format(error))
			db_con.rollback()
		else:
			db_con.commit()
		db_con.close()
