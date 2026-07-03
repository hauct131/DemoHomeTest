---
title: "Operational Schedule Troubleshooting"
source_url: "https://support.optisigns.com/hc/en-us/articles/48241081473043-Operational-Schedule-Troubleshooting"
article_id: 48241081473043
section_id: 26319502894611
created_at: "2026-01-15T16:38:40Z"
updated_at: "2026-04-20T21:26:17Z"
labels: ["troubleshooting", "Troubleshooting Page", "Hardware Troubleshooting"]
---
# Operational Schedule Troubleshooting

### In this article, we will troubleshoot common issues related to the Operational Schedule feature in OptiSigns.

- [Introduction to Operational Scheduling](#Introduction)
- [Changing Display Settings](#ChangingSettings)
- [How to Test HDMI-CEC / RS-232 Connections](#TestConnections)
- [OptiStick Improperly Powered](#ImproperlyPowered)
- [Operational Schedule Works at Different Times from How It Was Set](#DifferentTimes)
- [Screen Turns Off, But Not Back On](#TurnOff)

Operational Scheduling is a feature which allows you to turn off and on your digital signs on a set schedule, further automating your setup. If you’re looking to set up an Operational Schedule of your own, see our guide on [Creating and Using Operational Schedules](how-to-create-and-use-operational-schedules-hdmi-cec-rs-232.md).

However, many factors and settings may need adjustment in order to get this feature running properly. Here, we go through a few of the most common troubleshooting scenarios our teams face.

---

## **Introduction to Operational Scheduling**

Operational Schedule allows you to schedule when your TV powers on/off and to control the volume and brightness through the device level, HDMI-CEC, or RS-232 connections. HDMI-CEC is a popular feature available on most consumer TVs right now, while RS-232 is useful for commercial-grade displays.

| |
| --- |
| Limitations |
| - You will need the **Pro+ Plan** or above to have access to this HDMI-CEC and RS-232 feature. The HDMI-CEC or RS-232 capabilities allow you to Power On/Off your TV using the Operational Schedule, and change the volume or mute the screen. |
| - If you have the **Free** or **Standard** plan and create an Operational Schedule, the player will display black to save power and device life. Free and Standard plan users will not have access to the "Advanced Scheduling" option: [Image: 50995869008275] |
| - To access Operational Schedule with an HDMI-CEC port, you will need our [**OptiSigns OptiStick**](https://shop.optisigns.com/products/optisigns-android-stick-player-2), [**Pro Signage Player**](https://shop.optisigns.com/products/optisigns-digital-signage-player), or [**ProMax Player**](promax.md). The player will need to be plugged in to an HDMI-CEC port to function. RS-232 functionality can be used with any device which supports it. - Please ensure your OptiStick device is ***powered from an outlet, not the screen's USB port.***If plugged into the USB port, the act of turning off the screen will also power off the device - meaning, it will not be able to turn the screen back on. - Operational Scheduling is not supported on Roku nor Samsung Tizen devices. The option will not be visible. |

**One last important note:**

HDMI-CEC is referred to by numerous names. Depending on the brand of your TV or device, it might be called something else, and may need to be enabled in the device software.

Here is a complete list of [**TV Manufacturer CEC Names**](link). Simply find your device on the list and enable HDMI-CEC, if necessary. This will solve a lot of issues by itself.

---

## Changing Display Settings

In order for Operational Scheduling to work, your TV must actually support it. Operational Scheduling makes use of either:

- **HDMI-CEC** - This is the most common option, and supported by most TVs. See this guide on [HDMI-CEC settings](https://www.helpdesk.nakamichi-usa.com/hdmi-cec-settings) to find your display’s make and model for information on how to set this up to receive signal.
- **RS-232** - This option is most common on commercial displays, and is the most reliable option. ***If you can set up your player to use RS-232, you should, as it is far more reliable than HDMI-CEC***.

| |
| --- |
| **NOTE** |
| Your device will try RS-232 first if available, then HDMI-CEC command to turn off TV/Monitor. Your TV/Monitor model and player needs to support this feature for it to work. Players sold by OptiSigns support HDMI-CEC and RS-232. |

On most displays, HDMI-CEC or RS-232 will need to be enabled before Operational Scheduling will work. How to do this will vary by TV and connection.

| | |
| --- | --- |
| **MORE ON RS-232** | |
| An RS-232 cable should have come with your display. We recommend using this if possible, as there are reportedly issues with certain displays (generally LG) when other RS-232 cables are used. Your RS-232 ports may look different depending on the age of your display: | |
| **OLDER DISPLAYS:** | **NEWER DISPLAYS:** |
| [Image: 48241078964883] | [Image: 48241078965907] |
| A typical RS-232 cable which comes with most new commercial displays: [Image: 48241081463699] | |
| [**Buy USB-A to RS-232 cable for older displays**](link) | - [**Buy USB-A to RS-232 cable for newer displays**](link) - [**Buy USB-A to RS232 Female Adapter**](link) |

---

## How to Test HDMI-CEC / RS-232 Connections

Here is how to test your HDMI-CEC or RS-232 connection to make sure it works as it should.

Go to **Edit Screen → Advanced → More**:

Click the **Arrow** in the right hand corner of the popup, next to the **Save** option. This will bring up several options. Hit **Send HDMI CEC** or **Send RS232**:

[Image: 48241081464467]

This should either turn on or turn off the TV depending on whether the TV is currently on or off. If it does not, keep troubleshooting.

---

## OptiStick Improperly Powered

It is possible to power the OptiStick via a USB port on your display. However, in addition to [the other problems this causes](optistick-troubleshooting-guide.md), powering an OptiStick via USB will cause significant problems with the Operational Schedule feature.

Think about it this way: your OptiStick is tasked with powering down and powering off your display, but it is relying on that display to pull power from. Once the display is off, how is the OptiStick supposed to turn it back on? There is no power reaching it. That’s why it needs its own dedicated power source (i.e. outlet) to use Operational Scheduling properly.

For this reason, if you want to make use of Operational Scheduling with an OptiStick, ***be sure to plug it into a dedicated outlet, not the USB port.***

---

## Operational Schedule Works at Different Times from How It Was Set

This is very common and almost always goes back to the device Time Zone. Your first troubleshooting step for this issue should be to set the time zone.

This can be done either with the device itself, or remotely (if the device is online). To update it remotely, edit the screen, then hit **Advanced**. You should see the below bar, click the **Time Zone** button:

[Image: 48241081465107]

This will open up the **Update Time Zone** screen:

[Image: 48241081468307]

Here, simply select the appropriate Time Zone for your device. This should match the Operational Schedule you’ve set to it. Now, they should be aligned.

---

## Screen Turns Off, But Not Back On

One of the main reasons for this is that the [OptiStick is improperly powered](#ImproperlyPowered). However, another possible reason (regardless of the device being used) is that Operational Scheduling might not be supported on your individual TV, regardless of settings. This is a limitation of the device.

Assuming the OptiStick is plugged into a wall socket and this issue persists, here is what you can try:

- Replace the HDMI-CEC connection with RS232. This issue usually occurs because, for whatever reason, your TV is not able to make use of this feature. Plugging in a [USB-to-RS232 cable](link) usually fixes these issues. For Pro/ProMax users, this [3.5mm-to-RS232 cable](link) will also work.

If you've tried the above, feel free to [reach out to our support team](how-to-contact-optisigns-support.md).

### That’s all!

Still having problems with getting your Operational Schedule to work? Reach out to our support team at [our support team](mailto:our support team) for additional help.