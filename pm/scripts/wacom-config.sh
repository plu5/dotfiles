#!/usr/bin/env sh
# Wacom tablet configuration script for a systemd service
# 2025-05-20 00:56

for i in $(seq 10); do
    if xsetwacom list devices | grep -q Wacom; then
        break
    fi
    sleep 1
done

list=$(xsetwacom list devices)
pad=$(echo "${list}" | awk '/pad/{print $8}')
stylus=$(echo "${list}" | xsetwacom list devices | awk '/stylus/{print $8}')
touch=$(echo "${list}" | xsetwacom list devices | awk '/touch/{print $8}')

if [ -z "${pad}" ]; then
    exit 0
fi

xsetwacom set "${stylus}" Area 0 0 44704 25146

# inkscape
xsetwacom set "${pad}" Button 2 "key s"
xsetwacom set "${pad}" Button 3 "key c"
xsetwacom set "${pad}" Button 8 "key +shift e -shift"
xsetwacom set "${pad}" Button 9 "key +ctrl z -ctrl"
xsetwacom set "${pad}" Button 1 "key d"
xsetwacom set "${pad}" Button 10 "key ctrl"
xsetwacom set "${pad}" Button 11 "key shift"
xsetwacom set "${pad}" Button 12 "key d"
xsetwacom set "${pad}" Button 13 "key space"

# krita
xsetwacom set "${pad}" Button 2 "key grave"
xsetwacom set "${pad}" Button 3 "key /"
xsetwacom set "${pad}" Button 8 "key ctrl"
xsetwacom set "${pad}" Button 9 "key +ctrl z -ctrl"
xsetwacom set "${pad}" Button 1 "key b"
xsetwacom set "${pad}" Button 10 "key a"
xsetwacom set "${pad}" Button 11 "key +ctrl t -ctrl"
xsetwacom set "${pad}" Button 12 "key +ctrl left -ctrl"
xsetwacom set "${pad}" Button 13 "key +ctrl right -ctrl"

xsetwacom set "${touch}" Touch off
