#!/usr/bin/env bash
# Gracefully close open windows and associated applications
# 2025-01-19 04:49
#
# Dependencies:
# - wmctrl
# - rofi

MAX_WAIT=5  # seconds/10 to wait before giving up (per application)
DRY_RUN=false  # set to something other than false to not really close windows
# Strings so that it's easy to translate if needed ;-)
T_WAITINGON="En attente de fermeture :"
T_BLOCKING="Applications bloquantes :"

declare -A pid_to_title  # associative array

# Populate array of window IDs
mapfile -t WIN_IDS < <(wmctrl -l | awk '{print $1}')

# Get PID and title for each window and close it (if not dry run)
PIDS=()
for win_id in "${WIN_IDS[@]}"; do
    pid=$(xprop -id "$win_id" _NET_WM_PID 2>/dev/null | awk '{print $3}')
    title=$(xprop -id "$win_id" WM_NAME 2>/dev/null | sed -E 's/^.* = "//; s/"$//')
    if [ -n "$pid" ]; then
        [ "$DRY_RUN" = false ] && wmctrl -ic "$win_id"
        PIDS+=("$pid")
        pid_to_title["$pid"]="$title"
    fi
done

# Check if the applications really closed
BLOCKING_PIDS=()
for pid in "${PIDS[@]}"; do
    if ! ps -p "$pid" > /dev/null 2>&1; then
        continue
    fi
    echo "$T_WAITINGON ${pid_to_title[$pid]} (PID $pid)"
    for ((i=0; i<MAX_WAIT; i++)); do
        sleep 0.1
        if ! ps -p "$pid" > /dev/null 2>&1; then
            break
        fi
    done
    # Still alive after waiting
    if ps -p "$pid" > /dev/null 2>&1; then
        BLOCKING_PIDS+=("$pid")
    fi
done

# If some applications are still blocking, notify and give up
if (( ${#BLOCKING_PIDS[@]} > 0 )); then
    MSG="${T_BLOCKING}\n"
    for pid in "${BLOCKING_PIDS[@]}"; do
        MSG+="${pid_to_title[$pid]} (PID $pid)\n"
    done
    echo -e "$MSG"
    rofi -e "$(printf "$MSG")"
    exit 1
fi

exit 0
