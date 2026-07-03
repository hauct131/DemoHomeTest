---
title: "How To Connect To WiFi For Raspberry Pi"
source_url: "https://support.optisigns.com/hc/en-us/articles/360056627833-How-To-Connect-To-WiFi-For-Raspberry-Pi"
article_id: 360056627833
section_id: 26319645952019
created_at: "2020-09-30T06:04:06Z"
updated_at: "2025-09-02T19:22:01Z"
labels: []
---
# How To Connect To WiFi For Raspberry Pi

In this guide, we will walk you through end to end process to connect to WiFi on your Raspberry Pi.

If you haven't set up a Raspberry Pi OS on your device, you can check [here](raspberry-pi.md).

After you set up a Raspberry Pi device, it's common requirement to set up a WiFi connection.

Let's dive in.

**1. Optisign app shows "Internet Connection is required for first time"**

[Image: RPi\_Wifi\_connection-1.png]

**2. Click the WiFi connection button.**

[Image: RPi\_Wifi\_connection-2.png]

**3. Select your WiFi's name**

[Image: RPi\_Wifi\_connection-2.png]

**4. Enter your Wifi's password**

[Image: RPi\_Wifi\_connection-3.png]

**5.  Click OK**

[Image: RPi\_Wifi\_connection-5.png]

**6. Take a few seconds to connect your WiFi**

You may need to restart the device for WiFi config to set in.

[Image: RPi\_Wifi\_connection-5.png]

**7. OptiSigns app shows pair code on your screen**

[Image: RPi\_Wifi\_connection-7.png]

When your screen shows a paring code, your Raspberry Pi has an internet connection.

You're ready to go.

Then you can enter this pairing code on your web portal. If you want to learn more, you can click [here](set-up-add-a-screen.md).

### **Advanced: if you need to connect RPi to WPA-Enterprise network (usually for large organization, universities) the default WiFi manager of Raspberry Pi OS may not be enough.**

You can follow this guide to configure wpa\_supplicant.conf file:

<https://iceburn.medium.com/raspberry-pi-connected-to-wifi-of-wpa2-enterprise-ddd5a40c0b07>

OR:

Follow this guide for a more GUI approach:

<https://raspberrypi.stackexchange.com/a/119653>