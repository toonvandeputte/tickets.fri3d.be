output = output
version = $(shell git log -1 --format=%ct-%h)
project = fr1ckets
db = /var/lib/fr1ckets.sqlite

all: populate

output:
	mkdir -p $(output)/src
	mkdir -p $(output)/conf
	mkdir -p $(output)/ssl

populate: output
	cp -R src/* $(output)/src/
	cp -R conf/* $(output)/conf/
	#cp -R ssl/* $(output)/ssl/

$(db):
	@echo "couldn't find $(db), generating..."
	sqlite3 $(db) < db/fr1ckets_db.sql

test:
	cp docker/fr1ckets /etc/nginx/sites-enabled
	cp docker/fr1ckets.ini /etc/uwsgi/apps-enabled
	/etc/init.d/nginx start
	/etc/init.d/mysql start
	-/etc/init.d/uwsgi start
	mysql -u root --execute "\. /fr1ckets/db/fr1ckets_db.sql"
	mysql -u root -Dfr1ckets --execute "update reservation set available_from=utc_timestamp();"

deb: all
	./mkdeb.sh $(project) $(version) $(output)

docker:
	docker run -it -p 8080:8080 -v $$PWD:/fr1ckets fr1ckets bash

docker-build:
	docker build -t fr1ckets docker/

clean:
	rm -rf $(output) *.deb
	find src/ -name '*.pyc' | xargs rm || true

.PHONY: clean serve docker test
