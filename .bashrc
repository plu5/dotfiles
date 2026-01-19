#
# ~/.bashrc
#

# If not running interactively, don't do anything
[[ $- != *i* ]] && return

alias ls='ls --color=auto'
alias grep='grep --color=auto'
PS1='[\u@\h \W]\$ '

alias sgfeed='while true; do python /media/pnotes/py/sgfeed.py; sleep $((60*60*5)); done'
alias qmacs='sudo emacs -nw -q'
#alias em='SUDO_EDITOR="emacsclient -nw" sudo -e'
alias krita='krita --nosplash --template /usr/share/krita/templates/texture/.source/Texture1024x10248bitsrgb.kra'
alias cddev='cd /media/Windows/Users/pm/dev/'
alias cdpy='cd /media/Windows/Users/pm/Dropbox/Apps/py/'
alias asf='~/Applications/ASF/ArchiSteamFarm'
alias sshiph='ssh -p 22 root@192.168.1.11'
alias connectapms='sudo systemctl start bluetooth && sleep 1 && bluetoothctl connect 08:FF:44:1E:52:CA'
alias connecthotspot='sudo systemctl start usbmuxd'
alias archupgrade='sudo pacman -Syyu 2>&1 | tee ~/OneDrive/Documents/archupgrade.txt'
alias restartmouse='sudo modprobe -r psmouse && sudo modprobe psmouse'
alias doentrycount='ls "/media/pnotes/Day One/Journal.dayone/entries/" | grep -c "^[A-Z0-9]*\.doentry$"'

# ls avec date de modification et création, trié par ce dernier
alias lshorodatage='shopt -s dotglob && stat * --format "%.16w %.16y %n" | sort -n'
# seulement date de modification, trié par ce dernier
alias lshorodatagem='shopt -s dotglob && stat * --format "%.16y %n" | sort -n'
# lshorodatage avec date de création ntfs
alias lshorodatagen='for f in *; do echo $(ntfsbirth "$f" "%F %H:%M") $(date -r "$f" "+%F %H:%M") $f; done | sort -n'
# version recursive
alias rlshorodatagen='find . | while read f; do echo $(ntfsbirth "$f" "%F %H:%M") $(date -r "$f" "+%F %H:%M") $f; done | sort -n'

# >:-(
PROMPT_COMMAND='history -a'

# afficher birthtime d'un fichier ntfs avec `ntfsbirth 'path'`
ntfsbirth() {
    [ -z "$1" ] && echo "usage: ntfsbirth <file> [date-format]" && return
    format="%Y-%m-%d %H:%M:%S"
    [ ! -z "$2" ] && format="$2"
    getfattr --only-values -n system.ntfs_crtime_be --absolute-names "$1" | perl -MPOSIX -0777 -ne "\$t = unpack(\"Q>\"); print strftime(\"$format\n\", localtime(\$t/10000000-11644473600))"
}
