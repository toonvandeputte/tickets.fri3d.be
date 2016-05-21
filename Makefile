output = output
version = $(shell git log -1 --format=%ct-%h)
project = fr1ckets
db = /var/lib/fr1ckets.sqlite

all: populate

output:
	mkdir -p $(output)/src
	mkdir -p $(output)/conf
	mkdir -p $(output)/ssl
	mkdir -p $(output)/db

populate: output
	cp -R src/* $(output)/src/
	cp -R conf/* $(output)/conf/
	#cp -R ssl/* $(output)/ssl/
	cp -R db/* $(output)/db/
	chmod -R a+r $(output)/src/fr1ckets/static

deb: all
	./mkdeb.sh $(project) $(version) $(output)

docker-test:
	@echo "=== installing config ==="
	cp conf/fr1ckets /etc/nginx/sites-available
	ln -s /etc/nginx/sites-available/fr1ckets /etc/nginx/sites-enabled/fr1ckets
	cp conf/fr1ckets.ini /etc/uwsgi/apps-available
	ln -s /etc/uwsgi/apps-available/fr1ckets.ini /etc/uwsgi/apps-enabled/fr1ckets.ini
	cp conf/celeryd.conf /etc/supervisor/conf.d
	mkdir -p /var/log/celery/
	@echo "=== restarting daemons ==="
	/etc/init.d/nginx restart
	/etc/init.d/redis-server restart
	/etc/init.d/mysql restart
	/etc/init.d/supervisor restart
	-/etc/init.d/uwsgi restart
	@echo "=== reloading database ==="
	mysql -u root --execute "\. /usr/share/fr1ckets/db/fr1ckets_db.sql"
	mysql -u root -Dfr1ckets --execute "update reservation set available_from=utc_timestamp();"

docker-run:
	docker run -it -p 8080:8080 -v $$PWD:/usr/share/fr1ckets fr1ckets bash

docker-build:
	docker build -t fr1ckets docker/

clean:
	rm -rf $(output) *.deb
	-find src/ -name '*.pyc' | xargs rm || true

.PHONY: clean serve docker docker-test
