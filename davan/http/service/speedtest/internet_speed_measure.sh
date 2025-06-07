#!/bin/sh

MSG=`/usr/local/bin/speedtest-cli --simple | perl -pe 's/^(.*): (.*) (.*?)(\/s)?\n/"$1_$3": $2, /m' | cut -d',' -f 1-3`
DATE=`date +\"'%Y%m%d %H:%M'\"`
echo {$MSG, \"Date\": $DATE}>  /home/pi/davanserver/davan/http/service/speedtest/speedtest.txt
