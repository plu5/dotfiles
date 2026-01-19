To set up these services that run something when you connect a device, I followed [ArchWiki: Graphics tablet](https://wiki.archlinux.org/title/Graphics_tablet).
Other than the service files and the scripts associated, you need to add udev rules:
```sh
# /etc/udev/rules.d/99-wacom.rules
ACTION=="add", SUBSYSTEM=="usb", ATTRS{idVendor}=="056a", TAG+="systemd", ENV{SYSTEMD_USER_WANTS}+="wacom.service"
```

```sh
# /etc/udev/rules.d/99-sonixkbd.rules
ACTION=="add", SUBSYSTEM=="usb", ATTRS{idVendor}=="320f", TAG+="systemd", ENV{SYSTEMD_USER_WANTS}+="sonixkbd.service"
ACTION=="add", SUBSYSTEM=="usb", ATTRS{idVendor}=="1532", TAG+="systemd", ENV{SYSTEMD_USER_WANTS}+="sonixkbd.service"
```
Each line is a separate rule.

Find `idVendor` for a device with `lsusb | grep Wacom` (for example) (in its output it's `ID idVendor:idProduct`)

Reload rules with `sudo udevadm control --reload-rules`. That's all, it should work after that. You can watch it with `journalctl -f` to check if reconnecting device is indeed triggering the service.
