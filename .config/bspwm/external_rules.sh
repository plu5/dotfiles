#! /bin/sh
# cf log 2025-11-22

window_id=$1
window_class=$2
window_instance=$3
consequences=$4
if  [[ "$window_class" = "firefox" ]] then sleep 0.7; fi
window_title="$(xwininfo -id "$window_id" | sed -nE 's/^xwininfo.{1,}"(.*)"$/\1/p')"

if  [[ "$window_class" = "firefox" ]]
then
    case "$window_title" in
        'ChatGPT — Mozilla Firefox')
            echo "desktop=4"
            exit
            ;;
        'google translate - Recherche Google — Mozilla Firefox')
            echo "desktop=3"
            exit
            ;;
        *' WordReference.com — Mozilla Firefox')
            echo "desktop=3"
            exit
            ;;
        *'bilibili — Mozilla Firefox')
            echo "desktop=9"
            exit
            ;;
    esac
fi

if [[ -f "/tmp/profidesireddesktop" ]]; then
    d=$(cat /tmp/profidesireddesktop)
    if [[ -n "$d" ]]; then
        desktop=$(echo "$d" | grep -oE '[^[:space:]]+$')
        # the bspwm desktop numbers are one higher, i.e. 0→1, 1→2. but 10→0.
        ((desktop++))
        [[ "$desktop" == "10" ]] && desktop=0
        program=$(echo "$d" | grep -oP '(?<=/)[^/ ]+(?=\s|$)|^(\w+)' | head -n 1)
        class=$(echo "$window_class" | awk '{print tolower($0)}')
        # notify-send "$d // $program // $class"  # debug
        if [[ "$class" == "$program" ]]; then
            echo "desktop=$desktop"
            exit
        fi
        # echo "" > /tmp/profidesireddesktop  # unnecessary and breaks in some cases where several windows open like krita
    fi
fi
