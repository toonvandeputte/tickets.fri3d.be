import sqlite3
from flask import g
from fr1ckets import app

@app.before_request
def setup_db():
	g.db_con = sqlite3.connect(app.config['DB_PATH'], detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
	g.db_con.row_factory = sqlite3.Row
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
	else:
		app.logger.error("wrapup_db(error={0}), no db_con?".format(error))
