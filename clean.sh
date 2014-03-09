#!/bin/bash

find -type d -name "__pycache__" | xargs rm -rf
find -type f -name "*.pyc" | xargs rm -f
rm -rf tmp/mako
