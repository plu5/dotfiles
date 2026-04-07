
Settings I have changed:

Editor Settings:
- Interface → Editor → Display Scale → 100%  
  (The default is 75% which is too small to read on my screen)
- Run → Bottom Panel → Action on Play → Do Nothing  
  (It annoys me that the output panel pops up on play and has to be collapsed manually. If I want to open it I will do so myself.)
- Text Editor → External → Exec Path → emacsclient
- Text Editor → External → Exec Path → `+{line}:{col} {file}`
  + by default it set itself to `emacs +{line}:{col} {file}` which had the effect of opening a new buffer called emacs
- Text Editor → External → Exec Path → Use External Editor → On
- Text Editor → Behavior → Indent → Type → Spaces

Emacs:
- M-x package-install gdscript-mode
