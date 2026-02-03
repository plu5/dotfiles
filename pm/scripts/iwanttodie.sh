#!/usr/bin/env bash
# Emergency commands in a rofi interface
# 2025-11-21 19:38
#
# Dependencies:
# - rofi
# - sysmontask
# - sxhkd
# - polybar
# - xwininfo
# - ~/pm/scripts/xlogout.sh
# - systemd (systemctl)

CHOICES=(
    "switch to tty 2 (C-M-f1 to get back)"
    "rofi combi"
    "sysmontask"
    "restart psmouse"
    "kill sxhkd"
    "start sxhkd"
    "restart polybar"
    "kill x gracefully"
    "shutdown"
    "reboot"
)

# Guss https://stackoverflow.com/a/53050617/18396947
CHOICE=$(echo "$(IFS="⁋"; echo "${CHOICES[*]}" | sed "s,⁋,\n,g")" |
             rofi -dmenu -p "i want to die") && case $CHOICE in
    "${CHOICES[0]}") sudo chvt 2;;
    "${CHOICES[1]}") rofi -show combi;;
    "${CHOICES[2]}") sysmontask;;
    "${CHOICES[3]}") sudo modprobe -r psmouse && sudo modprobe psmouse;;
    "${CHOICES[4]}") pkill -x sxhkd;;
    "${CHOICES[5]}") sxhkd&;;
    "${CHOICES[6]}")
        pkill -x polybar;
        polybar&
        xdo lower $(xwininfo -name polybar-example_eDP-1 | grep xwininfo |
                        cut -d' ' -f4)
        ;;
    "${CHOICES[7]}") . ~/pm/scripts/xlogout.sh;;
    "${CHOICES[8]}") systemctl poweroff;;
    "${CHOICES[9]}") systemctl reboot;;
esac
