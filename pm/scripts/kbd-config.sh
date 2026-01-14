#!/bin/sh

for i in $(seq 10); do
    if lsusb | grep -q SONIX; then
        sleep 3
        break
    fi
    sleep 1
done

/home/pm/pm/scripts/toggle_internal_kbd.sh disable
