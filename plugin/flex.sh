#!/bin/sh
URL_FM="http://sgcpm.com/radio/fmstations"
URL_WEB="http://sgcpm.com/radio/webstations"
URL_INTER="http://sgcpm.com/radio/interstations"

if wget -q -O /tmp/fmstations $URL_FM && wget -q -O /tmp/webstations $URL_WEB && wget -q -O /tmp/interstations $URL_INTER

then
mv /tmp/fmstations $1
mv /tmp/webstations $1
mv /tmp/interstations $1
echo "stations updated successfully"
else
echo "error downloading stations"
fi
echo
