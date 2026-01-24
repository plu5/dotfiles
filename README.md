# plu5's general configuration files and shell scripts
```
    X
  /   \
/_______\
|   _   |  welcome to
|  | |  |  my humble home
```
## Environment
X, bspwm

## Subdirectories in this repository that contain their own README
- [bspwm .config](.config/bspwm)
- [systemd/user .config](.config/systemd/user)
- [Kvantum .config](.config/Kvantum)
- [gtk-3.0 .config](.config/gtk-3.0)
- [mpv .config](.config/mpv)
- [plover .config](.config/plover)
- [ranger .config](.config/ranger)
- [krita .local/share](.local/share/krita)  
  (also contains [an explanation](.local/share/krita/README.md#libpng-patch) as to the purpose of `libpng.patch`)

## Config contained in separate repositories
- [emacs](https://github.com/plu5/emacsd)

## Scripts
in [./pm/scripts](pm/scripts)

1. [**toggle_internal_kbd.sh**](pm/scripts/toggle_internal_kbd.sh) : 2024-12-25 19:12:57  
   turn off or on internal keyboard and apply modmap. ran at launch, when my external keyboard gets connected, and upon clicking the keyboard layout on polybar
2. [**close_windows.sh**](pm/scripts/close_windows.sh) : 2025-01-19 04:49:32 (birth)  
   close all windows gracefully, used in `xlogout.sh` (see below)
3. [**xlogout.sh**](pm/scripts/xlogout.sh) : 2025-01-19 05:07:25  
   kill bspc gracefully (without killing programs brutally which is what happens if you do just `bspc quit`)
4. [**xscreenshot.sh**](pm/scripts/xscreenshot.sh) : 2025-01-19 06:02:30  
   screenshot commands using maim which i bind using sxhkd. <kbd>super-s</kbd> to take a screenshot and save to a particular directory, <kbd>super-S-s</kbd> to save to clipboard (useful to paste in krita or google docs).
5. [**wacom-config.sh**](pm/scripts/wacom-config.sh) : 2025-05-20 00:56:38  
   called by a systemd service. xsetwacom commands to set up the area, buttons, and disables touch when i plug in my drawing tablet.
6. [**kbd-config.sh**](pm/scripts/kbd-config.sh) : 2025-05-20 11:59:55  
   called by a systemd service. calls the script `toggle_internal_kbd.sh` (see above) when i plug in my external keyboard.
7. [**iwanttodie.sh**](pm/scripts/iwanttodie.sh) : 2025-11-21 19:38:24  
   rofi interface for system commands like logging out and shutting down but also other commands i may need in an emergency, like when the keyboard gets stuck. can be triggered with the mouse by right clicking the power button in polybar.
8. [**rappel**](pm/scripts/rappel) : 2025-11-26 13:45:45  
   reminders using dunst notifications. it doesn't have any persistence at the moment (if you restart or otherwise lose your session any reminder you set is gone).
9. [**volume**](pm/scripts/volume) : 2025-11-26 15:35:27  
   script to set the volume of any running audio stream selected via regex of its title. with the option 'b' (for 'boucle') keeps listening to pactl events to keep setting the volume on the matching audio streams so that it continues being the desired volume even after pausing or moving to the next thing in a playlist. it's... imperfect. but does work and is very useful to me.
10. [**t**](pm/scripts/t) : 2025-11-29 01:09:53  
   a script that calls translate-shell with my desired arguments. i call it from rofi (see `profi` below) like `t translate this please` and it translates it to french by default or you can add arguments like `t -t zh translate this please` which would translate it into chinese. because of the way `profi` is set up i can type single quotes without having to escape them nor wrap the string; `t don't break please`.
11. [**g**](pm/scripts/g) : 2025-11-29 17:50:53  
    like `t` (see above) but feeds translate-shell into itself; translates into german and from german into french. useful if you just want to "normalise" text, but i don't use it often. like `t` you can give it other arguments you want to pass to translate-shell.
12. [**dunstaction**](pm/scripts/dunstaction) : 2025-11-30 02:15:31  
    i wanted to be able to copy the contents of dunst notifications and this hacky thing was my first go at it, following [the idea here by yutkat](https://github.com/dunst-project/dunst/issues/669). but the fatal problem with it is that any actions do not work on notifications popped back from history, so i changed to using `copy-dunst-history` (see below).
13. [**copy-dunst-history**](pm/scripts/copy-dunst-history) : 2025-11-30 12:38:55  
    display notifications history from dunstctl rofi interface with ability to copy their summary or pipe them to emacs.
14. [**profi**](pm/scripts/profi) : 2025-12-01 17:57:30  
    my command to launch rofi which has a complex run-command and run-shell-command. i capture the output to display in a notification, so that you're able to see output of commands or scripts you run in rofi. i worked on this a lot and it's still bad, endless issues with escaping quotes. it's also used to save the desktop we are on to `/tmp/profidesireddesktop`, which is then used by bspwm external rules to open the application that was launch on the desktop we were on when launching it, rather than on the current desktop.
15. [**pipe-to-emacs**](pm/scripts/pipe-to-emacs) : 2025-12-03 16:51:44  
    from [this gist by garaud](https://gist.github.com/garaud/06b38554103aa7120337). i modified it to not pop buffer because i find that annoying.
16. [**verify-doentries**](pm/scripts/verify-doentries) : 2025-12-05 04:10:38  
    verifying validity of my doentry files which are xml with markdown; the xml needs to be valid ideally. these are the files i have been using for daily "logs" for over a decade and some old ones are known invalid so i am skipping them in the check. i could fix them but it feels wrong to modify such old files, i can't even open them without mental pain.
17. [**em**](pm/scripts/em) : 2025-12-07 18:34:51  
    [see SE answer i wrote](https://stackoverflow.com/q/79840434). simple script to open a file you need permissions for in emacs tramp in terminal.
18. [**lpr**](pm/scripts/lpr) : 2025-12-17 05:57:16  
    a script for masquerading as the real lpr which is a command to print which is the urxvt terminal does by default if you press <kbd>S-print</kbd>. and that was my usecase, i had a session where i needed to save the output but copying was broken, added the location of the script ahead of path `export PATH="$HOME/pm/scripts:$PATH"` so then the output is written to file instead of printed. for future sessions you can achieve the same thing with `URxvt.print-pipe` in `.Xresources`, which i now have as `URxvt.print-pipe: cat | pipe-to-emacs piped-mode`, but the sad thing is unlike copying it puts in linebreaks where the console wraps.
19. [**pgetimg**](pm/scripts/pgetimg) : 2025-12-21 07:07:33  
    wget command to save an image to images folder faster than using browser dialog. also adds the current timestamp to it (in a rather cryptic format admittedly, yymmddHHMM, but this is what i've come to use for brevity).
20. [**prename**](pm/scripts/prename) : 2025-12-21 09:29:36  
    script to rename a file given to it using a rofi interface. one of the suggestions is filename as is so that you can <kbd>Tab</kbd> completion (i think by default it's maybe something else. `kb-row-select: "Tab";`) to get the path in the input line and modify it. another one is the path prefixed by the birth date of the file in format yymmddHHMM to be able to rename files that don't have their date easily (which is a good habit to get into to have them in the name if you ever intend to move your images elsewhere, because birth dates in linux are immutable). used as a feh action (see `pfeh` below).
21. [**pfeh**](pm/scripts/pfeh) : 2025-12-21 10:30:06  
    command to launch feh in my images directory with actions to rename <kbd>0</kbd> (see `prename` above), see file information and type <kbd>9</kbd>, see stat dates <kbd>8</kbd>, copy file path to clipboard <kbd>7</kbd>, <kbd>1</kbd> to open `fehfavoris` rofi interface (see below), <kbd>2</kbd> to save the image to `fehfavoris`. i don't have one to delete because i don't want to do it by accident. when i need to delete i press 7 to copy the file path, open a terminal with <kbd>C-e</kbd> and enter rm with the path.
22. [**pausepp**](pm/scripts/pausepp) : 2025-12-28 17:54:02  
    it's a simple pomodoro-type thing. just sleeps 25 minutes, plays a sound, sleeps another 5 minutes, plays another sound. simple as that so that i have nothing to fiddle with, can't constantly check how much time there is left. the sounds i used i downloaded from forvo. [une pause pipi](https://forvo.com/word/une_pause_pipi/#fr), [alors on continue](https://forvo.com/word/alors%2C_on_continue_%253F/#fr), both by Pat91.
23. [**fehfavoris**](pm/scripts/fehfavoris) : 2026-01-01 14:03:48  
    a way to save images you want to get back to later in feh, bound to an action in `pfeh` (see above). rofi interface for opening the favourites.
24. [**pnomsacheminsabsolus**](pm/scripts/pnomsacheminsabsolus) : 2026-01-02 16:47:37  
    a mess from when i was trying to deal with paths on a windows smb share where the accents were mixed, for example sometimes é as one character and sometimes two (unicode combined accent character). was trying to get a file with the list of paths to match the real ones without too much manual work, but it took way too long and required manual work anyway. and i thought it was only a windows-paths-on-linux problem, but then encountered same thing when dealing with these paths on windows as well.
25. [**sommeil**](pm/scripts/sommeil) : 2026-01-05 08:13:15  
    lock with xtrlock which prevents input until user types in their password, dim screen automatically and even after you wake up the screen it will go back off in a few seconds, logs timestamp each time someone presses something into a file ~/sommeil.log, then after user types their password to exits out it sends the contents of sommeil.log to an emacs buffer. it's weird but this is what i was doing manually before so better automate but my main motivation for making the script was to prevent the situations where i wake up having to deal with the mess caused by accidentally sleeping on the keyboard. i activate it with <kbd>hyper-]</kbd>
26. [**soncontrol**](pm/scripts/soncontrol) : 2026-01-05 19:37:01  
    controlling mpv processes with audio files playing in the background, start and stop with rofi interface. instead of keeping them running, to pause i just kill them, and since i use mpv with `--save-position-on-quit` starting/stopping is like pausing/unpausing. to keep track of pids they are saved to file. interface is pretty bad, should make it require less keypresses.
27. [**togglepause**](pm/scripts/togglepause) : 2026-01-06 08:04:19  
    pausing/unpausing videos i have in the background. for some you can send a key with xdotool to a window in the background, for others they have to be focused first. but even those you can send the key to, if there are multiple windows, it may send the key to the wrong window, it seems to be sent to the last focused. so as annoying as it is it's more reliable to focus first and then restore focus to previous.
28. [**toggleplover**](pm/scripts/toggleplover) : 2026-01-06 22:39:33  
    wanted to have a simple button, not to use the outline which inserts and then deletes text which is destructive in something like emacs buffers. tried to use xdotool for it but the application ignores commands sent to it when it is not focused so i was focusing it temporarily like i do for `pause`. and `plover -s plover_send_command toggle` is far too slow. `plover_send_command`, if you clone the plover repo, can work separately and send the command to any running instance, and it's fast.
29. [**okularf**](pm/scripts/okularf) : 2026-01-22 01:29
    <br>used in desktop file exec for okular. opens okular with most recent document. courtesy of [kalwardinX](https://www.reddit.com/r/kde/comments/lucqqw/-/i0pfmls/).
30. [**metaf.py**](pm/scripts/metaf.py) : 2026-01-23 19:32
    <br>creates a json file with a list of files under a path (recursive) and their dates of creation and modification.
    <br>would like to add saving also size and checksum.

## TODO
- **add screenshots**  
  desktop, rofi (maybe that one not on here but on .config/rofi). upload the images to a subfolder called 'static'
- **general: increase portability**  
  reduce hard-coded paths, or at least have a centralised source of truth for them.
- **krita: streamline save new file**  
  streamline saving files in krita instead of having to use the dialog, likely a plugin can do this. ideally i press a hotkey and it would save to a defined folder with current timestamp, with maybe ability to later rename via launching something like a rofi interface like my prename script. unsaved file C-s save to a new project in defined directory with current timestamp. if i opened an image (not kra) and press C-s, don't save to the image save to a new project with current timestamp.
- **krita: hide/show easily**  
  krita shortcut toggle hide/show panels (without interface cachée)
- **krita: try using interface cachée anyway**  
  krita shortcut toggle interface cachée
- **bspwm: minimising**  
  bspwm "minimising" windows («changer ces fenêtres en mode floating, petite taille, arrangeés quelque part comme au côté gauche de l'écran, comme ça on voit toujours qu'elles sont là, juste "minimisées", et les faire revenir -- on pourrait avoir 2 raccourcis, un pour restaurer la fenêtre activée, un pour restaurer toutes (comme ça pas besoin de les activer) [idéalement seulement pour celles dans l'espace de travail actuel], et ce que restaurer va faire est les remettre en mode tiled.»)
- **emacs: toggleable files in folder sidebar**  
  emacs toggleable sidebar like imenu-list which I have on C-tab to put on C-S-tab to show files and subfolders in pwd.
- **emacs: markdown-mode C-RET**  
  to when you are in a list item indent the new line so as to be still inside the list item
- **emacs: markdown-mode: fold list items**  
  emacs markdown-mode ability to fold list items like you can in org-mode, see [this effort by Tobias](https://emacs.stackexchange.com/questions/64729/how-to-fold-nested-list-items-in-markdown-mode)
- **emacs: org-mode: align text under list item**  
  advice for org-return that if we're on a list item and the line begins with `"*something:* "` indent a bit extra to align the new line after that.
  ```
  - *something:* item 1,
               item 2
  ```
  whether that is aligned or not depends on whether `*` is hidden but for me it is in org-mode and i do this kind of indentation manually, so better automate it. after item 2 it automatically indents to match so we only need to handle the item 2 situation.
- **XCompose arrow**  
  maybe add another arrow symbol other than →, like ➤ or ➔, because → is barely readable in github readmes, but maybe not all clients would be able to display that. maybe should use just >... -> does not look good either. given that github supports html markup in the markdown it's weird that we can use <> willy nilly
- **org-goto equivalent for any buffer with imenu**  
  i know there is helm-imenu but i hesitate to have to have the whole of helm as a dependency just for that.
- **consolidate doentry and markdown**  
  since doentry mode needs to handle markdown as well might as well make it be able to handle purely markdown files?
- **time spent in application tracker**  
  something, maybe via `profi`, that kind of like steam keeps track of total time spent in x application? maybe a waste of time because who cares, but it would be maybe cool, or maybe mind pollution and better not incentivise existentialism.
- **easier to use interface for soncontrol**  
  less keystrokes. something like [transient](https://github.com/magit/transient) would be nice, but i need it to be standalone. i guess rofi is not the right choice for this and instead need to invoke a small c++ executable or bash/python script that will take the next key pressed

## Logiciels les plus utilisés
- emacs (super-S-e. éditeur)
- urxvt (super-ret. terminal)  
  i have problems with it like some unicode characters breaking on certain font sizes, 1/3 sessions failing to save history on quit (had to begrudgingly add `PROMPT_COMMAND='history -a'` in bashrc to work around it), and reloading configuration once killed my entire X session somehow (i'm now scared every time I run xrdb)
- ranger (super-e. file browser)
- mpv (vidéo et audio)
- feh (images)
- rofi (super-spc. lanceur, commandes shell rapides, interface pour les scripts)
- rofi-calc (super-M-spc. calculatrice)
- warpd (hyper--. émulation de la souris avec le clavier)
- krita (éditeur des images rapide à lancer, bien plus rapide que gimp. je le lance parfois même juste pour coller une image que je veux avoir à côté pour référence car ça lance vite avec `krita --nosplash --template /usr/share/krita/templates/texture/.source/Texture1024x10248bitsrgb.kra`)
- firefox
  <br>extensions:
  + [contextual wiktionary](https://github.com/aesarab/contextual-wiktionary)
  + dark reader
  + firefox color (just to make it black)
  + keygen music play button
  + notifier for github
  + reddit enhancement suite
  + resurrect pages
  + sponsorblock for youtube
  + steamdb
  + treestyletab
  + ublock origin
    <br>([filters](https://gist.github.com/plu5/84c50fd061f844210a7042ed3fc223a1))
  + violentmonkey
    <br>userscripts:
    - [forvo login wall blocker](https://gist.github.com/plu5/c6d54d88b1c0b252b00c081b8cb67db6)
    - [bilibili login wall blocker](https://gist.github.com/plu5/acac697b0bc172d4905179f284bffdf1)
    - [pint login wall blocker](https://gist.github.com/plu5/fd7f2d261b44539402d539cd044e8d4a)
- chromium
  <br>extensions:
  + ublock origin
  + video speed controller
  + proxy switchyomega
    <br>(on a separate profile)
- thunderbird (mais je ne l'aime pas trop)
- anki
- foliate (epub)
- okular (pdf, cbr, cbz)  
  fast, has vertical scrolling, and saves your position. doesn't have the option to restore last session but you can have it open with most recent file with `okular "$(cat .local/share/okular/docdata/"$(ls -ct .local/share/okular/docdata | head -n1)" | grep 'documentInfo url' | cut -d\" -f2)"` (credit [kalwardinX](https://www.reddit.com/r/kde/comments/lucqqw/-/i0pfmls/)).
- inkscape (éditeur svg)
- plover (sténo)
- blender
- godot
- gwenview (images. je préfère feh la plupart de temps mais avec gwenview et kimageformats on peut visionner des fichiers krita)  
  agaçant que ça ne laisse pas dézoomer, seulement zoomer. un contournement est de faire en sorte que la fenêtre soit plus petite (par ouvrir des terminaux autour par exemple) puis appuyer sur le bouton "fit".
- peek (enregistrer des gifs facilement)  
  v useful to be able to share what you're working on, explain, or demonstrates something. it goes on top of what it's recording, kind of like licecap, so it needs to be floating `bspc rule -a 'Peek' state=floating`. restores last used position, and to position it precisely i use a command like `wmctrl -r Peek -e 0,635,339,657,377`
- input remapper 2 (pour avoir plusieurs fonctions avec les 2 boutons de mon stylo wacom)
- fsearch (super-f. j'aimerais passer à un alternatif avec une meilleure navigation clavier)
- sysmontask (C-S-esc. j'aimerais passer à un alternatif avec une meilleure navigation clavier)
- onedrive (utile pour avoir un backup facile en arrière-plan contre la corruption spontanée des fichiers sur lequels on est en train de travailler et qu'on n'a pas encore committé, ce qui m'arrive de temps en temps quand il y a des coupures d'électricité)
- polybar
- nm-applet
- alttab
- dunst
- magnus (magnification. je ne l'aime pas trop)
- xdotool

## Acknowledgements
- [yasnippet docs](https://joaotavora.github.io/yasnippet/snippet-development.html) for the "welcome to my humble home"
