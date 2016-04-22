#!/usr/bin/env bash
set -e

[ $# != 3 ] && echo "usage: `basename $0` version" && exit 1

NAME=$1
VERSION=$2
SRC=$3

DST=/usr/share/fr1ckets

DEB=`mktemp -d`

# copy over the contents
mkdir -p $DEB/$DST
cp -R $SRC/* $DEB/$DST

# debian-specific
mkdir $DEB/DEBIAN
cat > $DEB/DEBIAN/control <<REDHERRING
Package: $NAME
Version: $VERSION
Section: misc
Priority: optional
Architecture: all
Depends: nginx, uwsgi-plugin-python, python-flask, python-pysqlite2, sqlite3, python-flaskext.wtf, redis-server, python-redis, mysql-server, python-mysqldb
Maintainer: Jef Van den broeck <jef@codewerken.be>
Description: fr1ckets, the Fri3d Camp ticketing system
REDHERRING

fakeroot dpkg-deb --build $DEB
mv $DEB.deb $NAME"-"$VERSION.deb

rm -rf $DST
