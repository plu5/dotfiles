#!/usr/bin/env sh
# Screenshot to clipboard or path
# 2025-01-19 06:02
#
# Dependencies:
# - maim
# - xclip
#
# Options explanation:
# * --select : interactive selection mode to select a window or region
# * --tolerance 10 : prevents selecting a tiny region by accident
#   when you actually intended to click on a window
# * --nokeyboard : doesn't block the keyboard. enables me to select using
#   keyboard-controlled mouse emulation instead of a real mouse.
# * --hidecursor : to not have the mouse cursor appear in screenshots

SAVETO="~/pm/r/screen"

case $1 in
    clipboard)
        maim --select --tolerance 10 --nokeyboard --format png /dev/stdout |
            xclip -selection clipboard -t image/png -i
        echo "Saved screenshot to clipboard"
        ;;
    *)
        path="${SAVETO}/"$(date +%y%m%d%H%M%S).png
        maim --select --tolerance 10 --nokeyboard --hidecursor $path
        echo "Saved screenshot to '${path}'"
        ;;
esac
