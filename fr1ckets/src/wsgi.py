from fr1ckets import app

if __name__ == '__main__':
	app.secret_key = "dev"
	app.run(host='0.0.0.0', port=8080, debug=True)
