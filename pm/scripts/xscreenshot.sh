case $1 in
    clipboard)
      maim --select --tolerance 10 --nokeyboard --format png /dev/stdout | xclip -selection clipboard -t image/png -i
      echo "Saved screenshot to clipboard"
      ;;
    *)
      path=~/pm/r/screen/$(date +%y%m%d%H%M%S).png
      maim --select --tolerance 10 --nokeyboard --hidecursor $path
      echo "Saved screenshot to '${path}'"
      ;;
esac
