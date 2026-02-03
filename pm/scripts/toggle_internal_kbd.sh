#!/usr/bin/env sh
# Toggle internal keyboard
# 2024-12-25 19:12
#
# Turn off internal keyboard and apply Xmodmap.

# use `xinput list` to check your keyboard name. this one is for laptop internal keyboard
deviceName="AT Translated Set 2"
builtInId=$(xinput list | grep "$deviceName" | sed 's/^.*id=//' | sed 's/\t.*//')

case $1 in
    disable)
      xinput disable $builtInId
      echo "Keyboard '${deviceName}' disabled"
      ;;
    enable)
      xinput enable $builtInId
      echo "Keyboard '${deviceName}' enabled"
      ;;
    *)
      echo "Toggle keyboard '${deviceName}' (id ${builtInId})"
      echo "Invalid options"
      echo "Syntax: $0 enable/disable"
      exit
      ;;
esac

# if you have an xmodmap config you need to reapply it
xmodmap -e "keycode  66 = Caps_Lock NoSymbol Caps_Lock"
xmodmap ~/.Xmodmap

# cf 2025-07-25 log
xmodmap -e "add Mod3 = Hyper_L"
