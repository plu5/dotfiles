--[[
local utils = require 'mp.utils'
-- from autoload.lua
local function add_files(files)
    local oldcount = mp.get_property_number("playlist-count", 1)
    for i = 1, #files do
        mp.commandv("loadfile", files[i][1], "append")
        mp.commandv("playlist-move", oldcount + i - 1, files[i][2])
    end
end

local function parent_dir(path)
    path = path:gsub("[/\\]+$", "")
    local parent = utils.split_path(path)
    return parent
end
--]]

-- https://github.com/mpv-player/mpv/issues/9767
-- mp.set_property('sub-file-paths', 'sub/' . mp.get_property('filename/no-ext') .. '.srt')
local msg = require 'mp.msg'
mp.add_hook('on_load', 10, function ()
    mp.set_property('sub-file-paths', 'sub')
    --msg.info(mp.get_property('sub-file-paths'))
    --msg.info("hello?")

    --local path = mp.get_property("path", "")
    --msg.info(parent_dir(parent_dir(path)))
    --add_files(parent_dir(parent_dir(path)))
    --mp.commandv("loadfile", parent_dir(parent_dir(path)), "append")
end)

-- ach-raf https://github.com/mpv-player/mpv/issues/2595
-- remove files with blacklisted extensions from playlist
local blacklist = {'rar'}

local temp = {}
for _, ext in pairs(blacklist) do
    temp[ext] = true
end
blacklist = temp

function removeBlacklistedFiles()
    local playlist = mp.get_property_native('playlist')
    for i = #playlist, 1, -1 do
        if blacklist[playlist[i].filename:lower():match('%.(%w+)$')] then
            mp.commandv('playlist-remove', i-1)
        end
    end
end

mp.register_event('start-file', removeBlacklistedFiles)

mp.observe_property('playlist-count', 'native', function (_, count)
    if count == 1 then
        removeBlacklistedFiles()  -- Call the function when there's only one file in the playlist
        return
    end
end)