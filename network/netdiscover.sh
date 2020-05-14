#!/bin/bash

_term() { 
	# own handler to get rid of children as well
	exit 0
}

trap _term SIGINT SIGTERM

DATABASE="/home/leo/helper/netdiscover.sqlite3"

RANGES=(10.17.76.0/24 10.17.64.0/24)

for RANGE in ${RANGES[@]}; do
	/usr/bin/sqlite3 $DATABASE "create table IF not exists 'range${RANGE}' (ip text primary key, status integer, lastonline integer, mac text)"
done

while true; do
	for RANGE in ${RANGES[@]}; do
		for IP in $(/usr/bin/prips ${RANGE} | /bin/sed '1d' | /bin/sed '$d'); do
			MAC=$(/usr/sbin/arping -i ens3 -c1 -w1 -r ${IP} 2>/dev/null)
			[[ $? -eq 0 ]] && {
				# get rid of linebreak in case of duplicate IPs
				MAC=$(echo $MAC | tr '\0' ' ')
				/usr/bin/sqlite3 ${DATABASE} "insert or replace into 'range${RANGE}' values('${IP}', 1, $(date +%s), '${MAC:-na}')"
			} || {
				LAST=$(/usr/bin/sqlite3 ${DATABASE} "select lastonline from 'range${RANGE}' where ip='${IP}'")
				/usr/bin/sqlite3 ${DATABASE} "insert or replace into 'range${RANGE}' values('${IP}', 0, ${LAST:-0}, '')"
			}
		done
	done
done
