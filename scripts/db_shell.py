#!/bin/sh

DDIR=`dirname $0`/../

. $DDIR/env
docker-compose -f $DDIR/docker-compose.yml exec db mysql -uroot -p$MYSQL_ROOT_PASSWORD -D$MYSQL_DATABASE
