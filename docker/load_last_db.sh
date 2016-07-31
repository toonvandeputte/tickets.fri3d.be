#!/usr/bin/env bash

set -ue -o pipefail

LAST_DUMP=`ls db_dump*sql | tail -n 1`

[ -z $LAST_DUMP ] && echo "no dump found" && exit 1
echo "loading from $LAST_DUMP"
mysql -u root -p --execute="\. $LAST_DUMP"
mysql -u root -p -D fr1ckets --execute="update purchase set email = concat(email, '.notreal');"
