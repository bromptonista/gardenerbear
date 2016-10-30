#!/bin/sh
if ps -ef | grep -v grep | grep gardenerbear_full.py ; then
        exit 0
else
        sudo python gardenerbear_full.py &
        #Write note to Logfile
        echo "[`date`]: gardenerbear_full.py was not running... Restarted" >> gardenerbear.log
        exit 0
fi
