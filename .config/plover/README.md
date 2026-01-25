# plu5's Plover configuration
## Dictionary stack
- `user.json` : in this repository
- [`fr_spelling.json`](https://forge.gresille.org/stl/plover-french-extended-stenotype/-/blob/main/french_extended_stenotype/dictionaries/fr_spelling.json) : [stl's French Extended Stenotype](https://forge.gresille.org/stl/plover-french-extended-stenotype/)
- [`orthofr.json`](https://forge.gresille.org/stl/plover-french-extended-stenotype/-/blob/main/dictionaries/orthofr.json) : [stl's French Extended Stenotype](https://forge.gresille.org/stl/plover-french-extended-stenotype/)
- [`tao_la_salle_simple.json`](https://github.com/Vermoot/Pluvier/blob/main/resources/tao_la_salle_simple.json) : [Vermoot's Pluvier](https://github.com/Vermoot/Pluvier)
- [`pluvier_dicofr.json`](https://github.com/Vermoot/Pluvier/blob/main/resources/dicofr.json) : [Vermoot's Pluvier](https://github.com/Vermoot/Pluvier)
- [`pluvier_verbs.json`](https://github.com/Vermoot/Pluvier/blob/main/resources/verbs.json) : [Vermoot's Pluvier](https://github.com/Vermoot/Pluvier)
- `dicofrbysyll.json` : [Vermoot's Pluvier](https://github.com/Vermoot/Pluvier)
- commands.json : default
- main.json : default

## Approach
I started by "fingerspelling", i.e. typing letters one by one like normal typing to spell out words. In that way at least you have the ability to type anything, albeit slowly. I made a hotkey to be able to painlessly toggle it whenever I feel like using it rather than forcing myself to slow down all the time; you still progress little by little typing with it whenever you feel like. Then use the suggestions panel, I use a [plugin I made](https://github.com/plu5/pyhuntsman/tree/main/plover_huntsman_plugin) to toggle it easily, as well as experiment / rgrep your dictionaries because (some?) briefs don't show up in suggestions for some reason, slowly integrating into your typing the most common words you type. Not forcing yourself to learn the outlines for everything straight away, just integrating one-two easy ones at a time.

> [!WARNING]
> Careful what keyboard shortcut you set to toggle Plover; if it includes a key on the main part of the keyboard, it could break Plover if the key is still depressed when it output is toggled. In my testing <kbd>Shift-Super-space</kbd> would sometimes break it, whereas <kbd>Scroll_Lock</kbd> works fine.

    STPH FPLTD
    SKWR RBGSZ
      AO EU

1. a:`A*` b:`PW*` c:`KR*` d:`TK*` e:`E*` f:`TP*` g:`TPKW*` h:`H*` i:`EU*` j:`SKWR*` k:`KW*` l:`HR*` m:`PH*` n:`TPH*` o:`O*` p:`P*` q:`KW*` w:`W*` r:`R*` s:`S*` t:`T*` u:`U*` v:`SR*` w:`W*` x:`KP*` y:`KWR*` z:`STPKW*`
2. à:`A*RB` ç:`KR*R` é:`*ER` è:`*ERB` ù:`*URB` ô:`RO*` ê:`R*E`
3. .:`-FPLT` ,:`-RBGS`
4. .:`P-P`,:`W-B` ':`-PBT` :`:KHR-PB`  >:`A*EPBG` -:`H-B`

1 : fingerspelling même que par défaut. pour capitaliser les lettres ajoute -P.  
2 : lettres accentuées que j'avais ajouté dans user.json  
3 : ponctuation qui va être suivi par une espace  
4 : ponctuation sans espace

- `R-R` :: newline
- `S-P` :: space (important for word boundary when fingerspelling words, real spacebar will not be detected as a new word by the suggestions)
- `TK-LS` :: suppress space. should be inputted every time you are on a new line / input, and don't need a space at the start.

Ctrl still works while steno is active and while it is depressed steno keys do not output strokes. With the hands in the steno keyboard position it's relatively easy to lower the left hand palm to depress Ctrl to be able to input emacs hotkeys the usual way without having to have outlines for them. Alt works also but it's pretty hard to press. For the outlines approach to it, see [excalamus' plover-emacs](https://excalamus.github.io/plover-emacs/).

Personally I just toggle a lot, treating it like vim insertion/navigation mode.

TODO:
- mode toggle caps
- mode for having output display strokes (press SKWR for example and have it output SKWR instead of je)
- capitalise next (KPA doesn't work with Pluvier)
- R-R sometimes broken like after typing WEU, vie, typing R-R turns it into virer, but what if we want to have vie at the end of a line?

## Shortcuts
For toggling Plover you can use the binary that comes with it, `plover_send_command`. I have my keyboard set to emit Scroll Lock upon inputting <kbd>Fn-Altgr</kbd>. sxhkd bindings:
```
Scroll_Lock
     plover_send_command toggle
ctrl + Scroll_Lock
     plover_send_command focus
```
so it's
- <kbd>Fn-Altgr</kbd> to toggle Plover on/off
- <kbd>Ctrl-Fn-Altgr</kbd> to focus Plover.

then when focused can:
- quit with <kbd>Ctrl-q</kbd>
- open configuration with <kbd>Ctrl-,</kbd>
- load/reload dictionary with <kbd>Ctrl-o</kbd>, down arrow, <kbd>Enter</kbd>, type dictionary file name (user.json normalement), <kbd>Enter</kbd>

For adding translations I edit the json file directly rather than the dialog.

[I made a plugin](https://github.com/plu5/pyhuntsman/tree/main/plover_huntsman_plugin) to toggle NKRO on my keyboard, and to have easier shortcuts when Plover is activated. <kbd>-</kbd> to toggle the lookup dialog, <kbd>=</kbd> to toggle and position the suggestions dialog, <kbd>]</kbd> to deactivate Plover.

## Problems
### Emacs
Plover uses <kbd>C-S-u</kbd> in linux to insert unicode characters (y compris un caractère aussi simple que 'é'), which is not supported by default in Emacs. [This hack by Post Self](https://emacs.stackexchange.com/a/80061/15886) gets around the issue. With this addition to your configuration Emacs actually handles it better than Qt (don't need to have anything running in the background, no problem with speed of insertion).

```elisp
;;; + unicode C-S-u insertion hack necessary for linux and plover
;; by Post Self https://emacs.stackexchange.com/a/80061/15886
(setq lexical-binding t)
(defun my/insert-unicode-char ()
  (interactive)
  (let* ((digits (named-let gather-hex-digits ((digits nil))
                   (let ((digit (read-char)))
                     (if (not (or (<= ?0 digit ?9)
                                  (<= ?a digit ?f)
                                  (<= ?A digit ?F)))
                         digits
                       (gather-hex-digits (cons digit digits))))))
         (code (string-to-number
                (apply 'string (reverse digits))
                16)))
    (insert-char code)))
(define-key global-map (kbd "C-S-u") 'my/insert-unicode-char)
```

## Qt
For unicode insertion to work in Qt applications, including Plover's own Qt-based GUI, you must have ibus or fcitx running in the background.

Unicode insertion is broken in Qt when it is inserted too fast. I have 3ms input delay in the configuration to deal with this issue. Even then if you spam unicode characters too fast, it breaks.

## Non-exhaustive list of arch packages to install to get Plover working locally without tox
AUR:
- `python-plover_stroke`
- `python-rtf_tokenize`

Not 100% required, only for the plugin manager:

Pacman:
- `python-requests-futures`
- `python-pkginfo`
- `python-readme-renderer`

AUR:
- `python-requests-cache`
