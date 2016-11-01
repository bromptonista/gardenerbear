#!/bin/sh
if ps -ef | grep -v grep | grep gardenerbear_full.py ; then
        exit 0
else
        cd "${0%/*}"
        wget -N https://raw.githubusercontent.com/bromptonista/gardenerbear/master/gardenerbear_full.py gardenerbear_full.py
        sudo python gardenerbear_full.py &
        #Write note to Logfile
        echo "[`date`]: gardenerbear_full.py was not running... Restarted" >> gardenerbear.log
        exit 0
fi
