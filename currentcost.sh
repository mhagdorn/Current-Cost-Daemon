#!/bin/bash

case $1 in
   config)
        cat <<'EOM'
graph_title Power Usage
graph_vlabel power (watt)
graph_category sensors
power.label power
EOM
        exit 0;;
esac

echo -n "power.value "
tail -n 1 /home/magi/CurrentCost/currentcost.data | cut -d' ' -f4