## Plugins
- [PluginDevTools](https://github.com/KnowZero/Krita-PythonPluginDeveloperTools) by KnowZero
- † [KanvasBuddy](https://github.com/Kapyia/KanvasBuddy)
- † [LazyTextTool](https://github.com/KnowZero/Krita-LazyTextTool-Prototype) by KnowZero
- ★ visuallayeractions  
  layer actions like moving up and down, displacing them, merging, ... which does the usual action then flashes visibility and selection so that you can work without the layers panel open and get visual feedback when performing layer actions to know what has happened and which layer you are now on. had many issues with getting it to not break when you spam actions, but it can still break sometimes, and it also pollutes your history because each time it selects and deselects it creates history entries.
- ★ hidenews  
  simple custom plugin to remove widgets from the main page so that recent files takes up the whole space.

† : modified so i committed my version  
★ : custom

## Settings
I made the decision not to commit kritarc because it has a lot of garbage, the list of recent files, and changes every time you open and relaunch. So instead will try to keep here a list of settings I set:
- AutoSaveInterval=0  
  (disables autosave)
- ShowOutlineWhilePainting=false
- compressLayersInKra=true  
  (smaller project files at a cost of slightly longer to load/save)
- newCursorStyle=6  
  (Icône de curseur de brosse : Triangle gauchers)
- numFavoritePresets=999  
  (these are the presets that show up in the right click "contextual palette". in the settings dialog the highest you can set is 45, but you can increase it further in kritarc. this change will be reverted if you change any settings in the dialog and save)
- tabletPressureCurve=0,0;0.106843,0.261044;0.324129,0.433735;0.606242,0.871486;1,1;
- useRightMiddleTabletButtonWorkaround=true  
  (necessary for input mapper 2 emulated mouse clicks to work)

I launch Krita like `krita --nosplash --template /usr/share/krita/templates/texture/.source/Texture1024x10248bitsrgb.kra` (I have this in desktop file exec) in order for it to launch immediately into a new file. It launches in about 2 seconds, which is faster than gimp, slightly slower than inkscape.

## libpng patch
Krita patches the libpng that it uses in order to increase its limits, notably `USER_CHUNK_MALLOC_MAX` which is set by default to 8000000 bytes (8 MB). Unless you use the appimage you are subjected to these limits, unless the distribution you use patches libpng to increase these limits also. This causes some brushes not to load, see Draneria/Metallics-by-Draneria_Krita-Brushes#4.

I prefer to use my distribution-provided stable version of Krita, so I patch libpng. The patch in [../../../libpng.patch](../../../libpng.patch) increases the limit to 8000000000 bytes (8 GB).

Patching using the AUR helper `yay`:
1. Save the patch to a file (e.g. `~/libpng.patch`)
2. `yay --editmenu --editor=nano -S libpng-git`
3. When yay asks "PKGBUILDs to edit?" enter A
4. In the PKGBUILD in the function `build()` the first line is `cd "code"`, add a line after it with `patch -p1 < ~/libpng.patch` (or wherever you placed the patch). save and exit.
5. Let the build continue, and when yay asks "libpng-git and libpng are in conflict. Remove libpng?" enter y
