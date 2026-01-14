#!/bin/bash

if bash ~/pm/scripts/close_windows.sh; then
    bspc quit
else
    CHOICE=$(echo -e "Annuler\nForcer le logout" | rofi -dmenu -p "Certaines apps bloquent. Que faire ?")
    
    if [[ "$CHOICE" == "Forcer le logout" ]]; then
        bspc quit
    fi
fi
