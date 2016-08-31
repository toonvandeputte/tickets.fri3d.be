FROM debian:jessie-backports

RUN apt-get -y update
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y	\
	python-flask		\
	python-pysqlite2	\
	python-flaskext.wtf	\
	sqlite3				\
	python-celery		\
	python-redis		\
	redis-server		\
	mysql-server		\
	uwsgi				\
	uwsgi-core			\
	uwsgi-plugin-python	\
	python-mysqldb		\
	nginx-full			\
	supervisor			\
	python-requests		\
	python-pisa			\
	make

EXPOSE 8080

WORKDIR /usr/share/fr1ckets
