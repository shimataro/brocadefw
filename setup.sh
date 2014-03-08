#!/bin/bash

BASEDIR=`dirname ${0}`
BASEDIR=`readlink -f ${BASEDIR}`

# permissions
cd ${BASEDIR}
find tmp -type d | xargs chmod 777

# libraries
cd ${BASEDIR}/modules/libs
ln -fns __archives/Mako-0.9.1/mako .
