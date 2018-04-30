#!/bin/sh

OUT=`date --iso-8601=seconds`.sql
DDIR=`dirname $0`/../

. $DDIR/env

docker-compose exec fr1ckets /src/reservations_from_csv.py /csv/$1
