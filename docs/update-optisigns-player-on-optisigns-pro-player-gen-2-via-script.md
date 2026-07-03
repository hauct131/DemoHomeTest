---
title: "Update OptiSigns player on OptiSigns Pro Player (Gen 2) via script"
source_url: "https://support.optisigns.com/hc/en-us/articles/21449362442003-Update-OptiSigns-player-on-OptiSigns-Pro-Player-Gen-2-via-script"
article_id: 21449362442003
section_id: 26319495746195
created_at: "2023-10-03T16:00:44Z"
updated_at: "2025-09-02T20:33:55Z"
labels: []
---
# Update OptiSigns player on OptiSigns Pro Player (Gen 2) via script

If your Pro Player looks like the image below, read on. If it does not, read on [**Remote Commands for the OptiSigns Pro Player (Gen 3)**](how-to-use-remote-command-execution-windows-linux.md).

[Image: Pro Player.png]

## OptiSigns Pro Player Gen 2 Commands

You can install/update OptiSigns player on your OptiSigns Pro Player with 1 command line script:

```
 ~/bin/manual_update.sh
```

This script will download latest version of OptiSigns AppImage and run it.

You can use our Remote Access feature to access the OptiSigns Pro Player, go to this article & copy the command line and run on the Pi to update. It will save time vs. manually clicking & downloading methods.

Other command line scripts:

- If your TV has color saturation issues, run this command to fix it:

 ```
 wget -O- https://download.optisignsapp.com/pro-player/change-color-profile.sh | bash 
 ```
- Overwrite the automatic security updates timing

 ```
 bash~/bin/override_upgrade_schedule.sh 23:30
 ```
- To lock the USB port, if you want to lock the device to prevent tampering fully.

 ```
 ~/bin/optisigns-lockusb.sh
 ```
- To unlock the USB port.

 ```
 ~/bin/optisigns-unlockusb.sh
 ```