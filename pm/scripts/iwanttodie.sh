CHOICE=$(echo -e "switch to tty 2 (C-M-f1 to get back)\nrofi combi\nsysmontask\nrestart psmouse\nkill sxhkd\nstart sxhkd\nrestart polybar\nkill x gracefully\nshutdown\nreboot" | rofi -dmenu -p "i want to die") && case $CHOICE in
    'switch to tty 2'*)
        sudo chvt 2;;
    'rofi combi')
        rofi -show combi;;
    "sysmontask") sysmontask;;
    'restart psmouse')
        sudo modprobe -r psmouse && sudo modprobe psmouse;;
    'kill x gracefully')
        . ~/pm/scripts/xlogout.sh;;
    'kill sxhkd')
        pkill -x sxhkd;;
    'start sxhkd')
        sxhkd&;;
    shutdown)
        systemctl poweroff;;
    reboot)
        systemctl reboot;;
    'restart polybar')
        pkill -x polybar;
        polybar&
        xdo lower $(xwininfo -name polybar-example_eDP-1 | grep xwininfo | cut -d' ' -f4)
        ;;
esac
