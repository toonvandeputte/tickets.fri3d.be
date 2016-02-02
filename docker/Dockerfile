FROM debian:jessie

RUN apt-get -y update
RUN apt-get install -y	\
	python-flask		\
	python-pysqlite2	\
	python-flaskext.wtf	\
	sqlite3				\
	make

EXPOSE 5000

WORKDIR /fr1ckets
