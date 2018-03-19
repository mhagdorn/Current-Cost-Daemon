#!/bin/bash

case $1 in
   config)
	cat <<'EOM'
graph_title Power Usage
graph_vlabel power (watt)
graph_category sensors
EOM
	for i in $(seq 1 $(tail -n 1 /home/mhagdorn/CurrentCost/currentcost.data | awk '{print NF-3}')); do
	    echo p$i.label power s$i
	done

	exit 0;;
esac

tail -n 1 /home/mhagdorn/CurrentCost/currentcost.data | awk '{for (i=4;i<=NF;i++) printf("p%d.value %s\n",i-3,$i)}'
