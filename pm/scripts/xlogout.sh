#!/usr/bin/env sh
# Logout gracefully (close all applications first)
# 2025-01-19 05:07
#
# Dependencies:
# - ~/pm/scripts/close_windows.sh
# - bspwm
# - rofi

T_CANCEL="Annuler"
T_FORCE="Forcer le logout"
T_PROMPT="Certaines apps bloquent. Que faire ?"

if bash ~/pm/scripts/close_windows.sh; then
    bspc quit
else
    CHOICE=$(echo -e "$T_CANCEL\n$T_FORCE" | rofi -dmenu -p "$T_PROMPT")
    if [ "$CHOICE" == "$T_FORCE" ]; then
        bspc quit
    fi
fi
