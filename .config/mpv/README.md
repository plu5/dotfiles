## Scripts

- [autoload](https://raw.githubusercontent.com/mpv-player/mpv/refs/heads/master/TOOLS/lua/autoload.lua)
  + modified to use directory up a level for autoloading; the folder that contains the folder that contains the video. that way the standard layout of a course that is split into different folders for each part, each containing videos, the whole course in order is loaded into the playlist when you open one of the videos.
- [SimpleHistory](https://github.com/Eisa01/mpv-scripts/blob/master/scripts/SimpleHistory.lua) by Eisa01n
  + modified to make the blacklist into a whitelist and whitelist mpv and youtube. though you should use script-opts for option value changes
- plu5
  + `sub-file-paths` (though you could set this in the config just the same)
  + force remove files with certain extensions from the playlist

## Little reminders
- set video-rotate 270
- show-text ${path}
  + or just open the console bc after it starts playing a new file there is a "playing" message that shows the path to the file
- run with debug messages: add `-v` to launch options
