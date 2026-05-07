#!/usr/bin/env sh
# Screenshot to clipboard or path
# 2025-01-19 06:02
#
# Dependencies:
# - maim
# - xclip
# - (Optional) notify-send (notification with path on success)
#
# Options explanation:
# * --select : interactive selection mode to select a window or region
# * --tolerance 10 : prevents selecting a tiny region by accident
#   when you actually intended to click on a window
# * --nokeyboard : doesn't block the keyboard. enables me to select using
#   keyboard-controlled mouse emulation instead of a real mouse.
# * --hidecursor : to not have the mouse cursor appear in screenshots

SAVETO="$HOME/pm/r/screen"  # Don't use ~, it doesn't expand in quotes

notifysaved() {  # $1 = path
    echo "Saved screenshot to '$1'"
    command -v notify-send >/dev/null 2>&1 &&
        notify-send "Saved screenshot to '$1'"
}

case $1 in
    clipboard)
        maim --select --tolerance 10 --nokeyboard --format png /dev/stdout |
            xclip -selection clipboard -t image/png -i
        [ $? = 0 ] && notifysaved "{clipboard}"
        ;;
    delay)
        path="${SAVETO}/"$(date +%y%m%d%H%M%S).png
        maim --nokeyboard --hidecursor -d 5 "$path"
        [ $? = 0 ] && notifysaved "$path"
        ;;
    *)
        path="${SAVETO}/"$(date +%y%m%d%H%M%S).png
        maim --select --tolerance 10 --nokeyboard --hidecursor "$path"
        [ $? = 0 ] && notifysaved "$path"
        ;;
esac
