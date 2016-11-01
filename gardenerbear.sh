#!/bin/sh
if ps -ef | grep -v grep | grep gardenerbear_full.py ; then
        exit 0
else
        wget -N https://raw.githubusercontent.com/bromptonista/gardenerbear/master/gardenerbear_full.py /home/gardenerbear/gardenerbear_full.py
        sudo python /home/gardenerbear/gardenerbear_full.py &
        #Write note to Logfile
        echo "[`date`]: gardenerbear_full.py was not running... Restarted" >> gardenerbear.log
        exit 0
fi
