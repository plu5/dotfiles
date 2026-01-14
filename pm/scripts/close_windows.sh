#!/bin/bash

MAX_WAIT=2  # secondes
declare -A pid_to_title

# Récupère les fenêtres ouvertes (hors panel/bureau)
mapfile -t WIN_IDS < <(wmctrl -l | grep -vwE "Desktop$|xfce4-panel$" | awk '{print $1}')

PIDS=()
for win_id in "${WIN_IDS[@]}"; do
    pid=$(xprop -id "$win_id" _NET_WM_PID 2>/dev/null | awk '{print $3}')
    title=$(xprop -id "$win_id" WM_NAME 2>/dev/null | sed -E 's/^.* = "//; s/"$//')
    if [[ -n "$pid" ]]; then
        # Demander fermeture
        wmctrl -ic "$win_id"
        PIDS+=("$pid")
        pid_to_title["$pid"]="$title"
    fi
done

# Suivi des pids à surveiller
BLOCKING_PIDS=()

for pid in "${PIDS[@]}"; do
    if ! ps -p "$pid" > /dev/null 2>&1; then
        continue
    fi

    echo "En attente de fermeture : ${pid_to_title[$pid]} (PID $pid)"
    for ((i=0; i<MAX_WAIT; i++)); do
        sleep 1
        if ! ps -p "$pid" > /dev/null 2>&1; then
            break
        fi
    done

    # Si toujours vivant après attente
    if ps -p "$pid" > /dev/null 2>&1; then
        BLOCKING_PIDS+=("$pid")
    fi
done

# Si des applis bloquent, notifier et quitter sans logout
if (( ${#BLOCKING_PIDS[@]} > 0 )); then
    echo "Certaines applications n'ont pas fermé proprement :"
    MSG="Applications bloquantes :\n"
    for pid in "${BLOCKING_PIDS[@]}"; do
        MSG+="• ${pid_to_title[$pid]} (PID $pid)\n"
    done

    # Affichage console
    echo -e "$MSG"

    # Notification (choix : notify-send, dmenu, rofi...)
    # notify-send "xlogout bloqué" "$(echo -e "$MSG")"
    echo -e "$MSG" | rofi -dmenu -p "xlogout bloqué"

    # Échouer avec code de retour ≠ 0 pour stopper xlogout.sh
    exit 1
fi

exit 0
