#!/bin/bash

BASEDIR=`dirname ${0}`
BASEDIR=`readlink -f ${BASEDIR}`

# permissions
cd ${BASEDIR}
find tmp -type d | xargs chmod 777
