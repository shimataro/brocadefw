#!/bin/bash
# ./setup.sh [server-user-name]

BASEDIR=`dirname ${0}`
BASEDIR=`readlink -f ${BASEDIR}`

# permissions
ALLOW_USER="www-data"
if [ -n "${1}" ]; then
	ALLOW_USER=${1}
fi

cd ${BASEDIR}
find .                     -type d | xargs setfacl -b
find brocadefw private tmp -type d | xargs setfacl -m u:${ALLOW_USER}:rwx
setfacl -m u:${ALLOW_USER}:rwx .
