---
title: "How to Use OptiSigns with Microsoft Teams Rooms"
source_url: "https://support.optisigns.com/hc/en-us/articles/36911639377683-How-to-Use-OptiSigns-with-Microsoft-Teams-Rooms"
article_id: 36911639377683
section_id: 26324023523603
created_at: "2024-12-31T20:28:22Z"
updated_at: "2025-09-04T18:42:32Z"
labels: []
---
# How to Use OptiSigns with Microsoft Teams Rooms

### In this article, we will explain how to set up OptiSigns for use with Microsoft Teams Rooms’ new Digital Signage option.

- [Prerequisites](#Prerequisites)
- [Configure the Source within Teams Rooms Pro Management Portal and OptiSigns Web Player](#Configure)
- [Send to a Teams Rooms Device](#Send)
- [Set Up the Virtual Screen App (ALTERNATE METHOD)](#SetUp)

Microsoft has released a new Digital Signage option for their [Microsoft Teams Rooms](https://www.microsoft.com/en-us/microsoft-teams/microsoft-teams-rooms) application, which allows digital signage to be displayed on a Microsoft Teams Rooms device. This will cause Teams Rooms screens and devices to display digital signage content when idle.

[Image: teams rooms using digital signage]

---

## Prerequisites

Before getting started, you’ll need:

- Microsoft Teams Rooms Pro on Windows 5.1 or later
- A configured Microsoft Teams Rooms device
- An active OptiSigns subscription

Once this is accomplished, we can move on to the next step.

---

## Configure the Source within Teams Rooms Pro Management Portal and OptiSigns Web Player

Navigate to your Teams Rooms Pro Management Portal. On the left toolbar, expand the **Settings** section then click **Digital signage**.

[Image: teams rooms pro manager digital signage setting]

On this screen, ensure the Digital signage switch is **On** (it should be by default), then click **Add Source**.

[Image: teams rooms digital signage screen steps]

This screen will appear:

[Image: teams rooms add digital signage source]

The **Name and Description** sections are purely for MS Teams Rooms - provide a name and description which will help you identify your signs in case you want to make several. Once inputted, hit **Next**.

Now you’ll need to Select source. We recommend using the OptiSigns Web Player for this. It allows frequent updates and is extremely easy to set up. Simply input the following URL as your Custom Source:

```
https://webplayer.optisigns.com/
```

[Image: custom source ms teams rooms optisigns web player]

The last screen is a Review screen. If everything looks good, hit Finish.

Last, you'll need to input your pairing code:

[Image: optisigns web player + pairing code]

See our article on [Setting Up and Adding Screens](set-up-add-a-screen.md) for more information.

---

## Send to a Teams Rooms Device

Whichever method you've used, you'll need to send your Source to a Teams Rooms device. To begin, click **Assign to rooms**.

[Image: teams rooms assign to rooms choice]

Choose the Source you made in the last step, then hit **Next**.

[Image: teams rooms assign to rooms select source]

Now you’ll be reviewing your preferences for how to display signage on your Rooms app.

[Image: teams rooms assign to rooms review preferences]

There are several parts to take note of here:

- **Show Teams Rooms banner** - Displays Room information over top of your digital signage when selected. Remove if you do not want this overlay.
- **Display Period** - These settings allow you to configure how quickly your display changes from Teams Rooms settings to your signage.
- **Allow screen timeout when device is idle** - When selected, this will keep your default screen settings for timing it out. Deselect this if you want your signage to continuously display.

Once you’ve tweaked these settings to your liking, hit **Next**. You’ll be taken to the Assign rooms screen.

[Image: teams rooms assign rooms]

Here, simply choose the Room you want the signage to display it. Hit **Next**.

[Image: teams rooms assign rooms select schedule]

These options change when these changes will be applied. Pick one, then hit **Next**.

Now you’ll review all these changes. Simply hit **Submit**, and you’re done.

---

## Set Up the Virtual Screen App (ALTERNATE METHOD)

Set up a [Virtual Screen app](how-to-create-and-use-virtual-screen-app.md) as an alternative to the OptiSigns Web Player. This app will provide an alternate URL to use as a Source in our Microsoft Teams Rooms Portal to set up digital signage.

To get started, click **Files/Assets** within the OptiSigns app and navigate to **Apps**.

[Image: optisigns portal files assets app]

Search for **Virtual Screen App**, then select it.

[Image: virtual screen app optisigns]

You’ll see a screen similar to this:

[Image: virtual screen app config optisigns]

You’ll need to fill in the information on the side.

[Image: virtual screen app information filled in]

For this, there are a couple things to note.

First, the **Screen** you select will be what displays on your Microsoft Teams Rooms display. This screen should be configured with the digital signage you want to display there.

Second, the **Share Type** should be set to **URL Link**. It is this URL you will input into the Teams Rooms Professional Portal in the next step.

Now, hit **Save**. Your asset/playlist will show on the right side of the screen, and you’ll receive the URL you need.

[Image: virtual screen app completely configured]

This Virtual Room app will now be saved as an Asset on OptiSigns. By clicking on it, you will be able to access the URL anytime. You'll want to enter this into your Custom source within the Teams Rooms Pro Management portal.

[Image: teams rooms digital signage select source]

---

### That’s all!