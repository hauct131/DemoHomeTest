---
title: "Using an Enterprise Network (802.1x) with OptiSigns"
source_url: "https://support.optisigns.com/hc/en-us/articles/44890229616403-Using-an-Enterprise-Network-802-1x-with-OptiSigns"
article_id: 44890229616403
section_id: 26319359505427
created_at: "2025-09-19T21:49:13Z"
updated_at: "2026-05-20T18:11:11Z"
labels: ["enterprise", "wifi", "network", "802.1x"]
---
# Using an Enterprise Network (802.1x) with OptiSigns

### In this article, we'll cover how to get OptiSigns working on an Enterprise-level security network, either over WiFi or Ethernet.

- [Supported Devices](#SupportedDevices)
- [Setting Up 802.1x Enterprise WiFi on a Pro or ProMax Player](#SettingUp)
 - [On Initial Setup](#OnInitialSetup)
 - [Changing From Another Network Source](#Changingfrom)
- [Setting Up a Wired Ethernet 802.1x Enterprise Network](#WiredEthernet)

If your organization uses an 802.1x Enterprise Network, many devices will not be compatible with OptiSigns. Here, we'll let you know which ones are, and how to connect to it on OptiSigns devices.

---

## Supported Devices

- OptiSigns [Pro Player](https://www.optisigns.com/product/hardware/pro-digital-signage-player) or [ProMax Player](https://www.optisigns.com/product/hardware/promax-digital-signage-player)
- Windows
- Linux

Note that this does not include the OptiStick, nor other devices such as Raspberry Pi. These do not support Enterprise networks at this time.

The scope of this article will limit itself to getting OptiSigns to work on OptiSigns devices. For Windows and Linux, connect the device to your network as normal and be sure OptiSigns has been [**whitelisted through your organization's firewall**](whitelist-optisigns-ip-addresses-ports.md)**.**

| |
| --- |
| **IMPORTANT** |
| You'll need to know whether or not you're using **PEAP** or **EAP-TTLS** for your network security protocol. This will determine what sort of certificate to set up on the OptiSigns device. |

---

## Setting Up 802.1x Enterprise WiFi on a Pro or ProMax Player

Setting up Enterprise WiFi on a Pro or ProMax Player can be done during initial setup, or it can be switched to from a different WiFi source.

### On Initial Setup

You can set your Enterprise WiFi network as See our article on [Setting Up WiFi on the Pro or ProMax Player](proplayer.md) for more information on that.

You'll be on the **Device Wi-Fi Settings** menu. Under **Security**, select **WPA2-Enterprise**.

[Image: device wifi settings wpa2-enterprise]

Several more options will open up.

[Image: wpa2-enterprise login options]

You'll need to enter a **Username** and **Password**, and upload a certificate depending on the needs of your security network. Simply locate this certificate, place it on a USB or MicroSD card, attach it to the Pro Player, and select it here. The certificate will automatically be downloaded to the appropriate location.

This should connect your Pro or ProMax player to your Enterprise WiFi network.

### Changing from Another Network Source

If you've already performed your initial setup, you can still change to an Enterprise WiFi network.

To do this, open up the **Side Menu**, then navigate to **About:**

[Image: pro player side menu about option]

On the **About** menu, hit **WiFi Setup**.

[Image: about menu wifi settings option]

From here, it's the same process as above. You'll be on the **Device Wi-Fi Settings** menu. Under **Security**, select **WPA2-Enterprise**.

[Image: wpa2-enterprise login options img2]

Several more options will open up.

[Image: device wifi settings wpa2-enterprise img2]

You'll need to enter a **Username** and **Password**, and upload a certificate depending on the needs of your security network. Simply locate this certificate, place it on a USB or MicroSD card, attach it to the Pro Player, and select it here. The certificate will automatically be downloaded to the appropriate location.

This should connect your Pro or ProMax player to your Enterprise WiFi network.

---

## Setting Up a Wired Ethernet 802.1x Enterprise Network

To set up an 802.1x Enterprise Ethernet connection on an OptiSigns Pro or ProMax player, you'll need to attach an Ethernet cable to your player first.

Then, open the **Side Menu**, then go to **About**.

[Image: side menu about]

On the **About** menu, go to **Advanced Settings:**

[Image: pro player side menu advanced settings]

Next, click the **802.1x Ethernet** switch to enable it. Several additional options will become available:

[Image: 802.1x ethernet login options]

You'll need to enter a **Username** and **Password**, and upload a certificate depending on the needs of your security network. Simply locate this certificate, place it on a USB or MicroSD card, attach it to the Pro Player, and select it here. The certificate will automatically be downloaded to the appropriate location.

###