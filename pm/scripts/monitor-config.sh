#!/usr/bin/env sh
# Second monitor configuration script for a systemd service
# 2026-05-18 15:22
#
# Dependencies:
# - xrandr
# - bspwm

found=

for i in $(seq 5); do
    if xrandr | grep -q "^HDMI-2 connected"; then
        found=true
        break
    fi
    sleep 1
done

update_bspwm() {
    # prevent "stuck in a tile" issue
    # https://github.com/baskerville/bspwm/issues/893
    bspc config right_padding 0
    bspc config bottom_padding 0
    # prevent "Desktop" workspace
    bspc monitor HDMI-2 --remove
    # forcing refresh of polybar workspaces
    bspc monitor -d 1 2 3 4 5 6 7 8 9 0 a
    bspc monitor -d 1 2 3 4 5 6 7 8 9 0
}

[ -z $found ] && {
    xrandr --output eDP-1 --mode 1280x720
    update_bspwm
    exit
}

xrandr --output HDMI-2 --same-as eDP-1 --mode 1280x720 --output eDP-1 --off
update_bspwm
