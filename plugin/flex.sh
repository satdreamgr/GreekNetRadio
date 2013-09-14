#!/bin/sh
cd /
echo -------------------------------------------------------------------------
echo $1
echo -------------------------------------------------------------------------
case $1 in
#########update epg ###############
"stations")
URLL="http://sgcpm.com/radio/fmstations"
URL="http://sgcpm.com/radio/webstations"
                                 if wget -q -O /tmp/fmstations $URLL && wget -q -O /tmp/webstations $URL

then
                                 mv /tmp/fmstations /usr/lib/enigma2/python/Plugins/Extensions/GreekNetRadio
                                 mv /tmp/webstations /usr/lib/enigma2/python/Plugins/Extensions/GreekNetRadio
				 else
				 echo "error!"
fi
;;

*)
echo "error"
;;

esac
