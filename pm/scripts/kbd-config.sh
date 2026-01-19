#!/bin/sh

for i in $(seq 10); do
    if lsusb | grep -q -e 'SONIX\|Huntsman'; then
        sleep 3
        break
    fi
    sleep 1
done

/home/pm/pm/scripts/toggle_internal_kbd.sh disable
