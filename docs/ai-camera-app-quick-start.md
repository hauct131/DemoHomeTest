---
title: "AI Camera App - Quick Start"
source_url: "https://support.optisigns.com/hc/en-us/articles/27690296225555-AI-Camera-App-Quick-Start"
article_id: 27690296225555
section_id: 26323817773843
created_at: "2024-03-22T16:43:29Z"
updated_at: "2026-06-29T19:26:02Z"
labels: []
---
# AI Camera App - Quick Start

OptiSigns AI Camera app that allows you to use any camera, plug into the device playing OptiSigns Digital Signage player to:

1. Detect and collect data about passing by foot traffic to analyze impressions and exposure of your Digital Sign.

2. Responsively display different content based on demographic of viewers standing in front of your screens.

This feature is supported on [Linux](linux.md), [Windows](windows.md), and [Android Device](link).

**Quick start guide to use OptiSigns AI Camera:**

In this guide, we will:

1. Set up the AI Camera to display suit sales when a male person is detected and yoga wear sales when a female person is detected.

[[Image: 27855243843091]](https://support.optisigns.com/hc/article_attachments/27855243843091)

2. Review the data collected by the app on the portal's reporting page.

Ex:

[Image: Screenshot 2024-03-22 141025.png]

From there, you can modify the set-up to fit your needs.

**1.) Preparation:**

If you haven't paired a device yet, follow this guide [for Windows](windows.md), or this guide [for Linux](linux.md) or [Raspberry Pi](raspberry-pi.md) to install and run OptiSigns Digital Signage Player first.

**You must have the OptiSigns' Engage Subscription or Trial to access the AI Camera feature.**

Each account is entitled to use the AI Camera feature on **ONE FREE** screen. If you would like to add the AI Camera feature to more than 1 screen, you will need to purchase the Engage subscription.

This screen is the only one that will ever have Engage enabled, and it is a one-time assignment. If you remove the Engage feature from that screen, you will not be able to add it to another.

Here is a link to the [subscription page](link).

Get a USB Camera and plug into your device:

We recommend the Logitech Webcams like the [C270](link).

If you are running on your Windows Laptop, you can use the built-in camera; no additional camera is needed.

**2.) Review & configure AI Camera:**

Go to the **Engage** Tab at the top of the screen.

**[Image: annotely\_image (19).jpeg]**

Click New App on the top right corner:

**[Image: annotely\_image (20).jpeg]**

First, click the "**AI Camera**" tab on the left side. Then, click the "**Build**" button in the bottom right corner.

**[Image: annotely\_image (21).jpeg]**

You will then be directed to the AI Camera Build page.

[Image: Screenshot 2024-03-22 101159.png]

[Image: Screenshot 2024-03-22 101449.png]

You can view how the asset is configured

**Play Settings:**

- Play for at least: when detected, the app will play the content corresponding to detection rule for at least X seconds. (Default is 3s)
- Rest for: the device will wait for at least X seconds (Default: 3s) before triggering additional content if multiple rules are detected.

We recommend to keep Play for at least and Rest for at 3s, to give smooth feeling experience when in crowded place like mall, or an airport with many people walking by very quickly.

**Play Rules:**

- Effective Time: This refers to the time frame during which the feature is active and the specific days it applies to.
- If Detected: This describes how the AI camera determines when to trigger a change.
- Play Content: This pertains to the asset assigned to play when a specific gender is detected.

After completing the previous steps, you will be directed to the "Assign to Screen" page. Here, you will assign the AI camera to the specific screen on which you want the camera to trigger.

[Image: Screenshot 2024-03-28 112724.png]

**3.) Assign the AI Camera app to your Screen:**

1. Go to the **Screen** tab and click **Edit**.

2. Click **Advanced**.

[Image: annotely\_image (22).jpeg]

3. Click **More**.

[Image: 27974903303571]

4.  **Activate** the AI Add-on.

[Image: 27974903309715]

If you want the device to send data for Analytics purposes, please leave the Send AI Data box checked as well. You can learn more about what data we collect [here](audience-intelligence-ai-camera-faqs.md).

[Image: 27974888673171]

5. Change the **AI Add-on** and it will bring you to the select Asset Page.

6. Click **Engage**

[Image: annotely\_image (25).jpeg]

7. Choose your **AI App** and then save.

[Image: annotely\_image (26).jpeg]

**4**.) **Set up camera & app on your device**

If you are using Linux or Raspberry Pi, the AI Camera will be automatically install when you click AI Camera Activate in the step above. You may need to restart your device. If you need instruction on how to manually activate, run AI Camera for Linux, you can follow [this guide](how-to-manually-install-activate-optisigns-ai-add-on-on-linux-or-raspberry-pi.md).

For Android, you'll need to go to the app permission settings and grant camera access.

If you are using Windows just download & run [optisigns-ai-detection.exe.](https://links.optisigns.com/ai-add-on-win) If you want OptiSigns AI Detection to run on system start up just follow these [steps here](how-to-run-optisigns-ai-add-on-on-start-up-in-windows.md).

The app will log events it detected like below.

[[Image: 27805047501843]](https://support.optisigns.com/hc/article_attachments/27805047501843)

Once OptiSigns AI detection is running, you'll notice it's using the camera to detect and send events to the OptiSigns Player to change content as appropriate. In this case, if a male person is in front of the camera, the Suit Sales ad will be displayed. If a female person is in front of the camera, the Yoga ad will be displayed.

If you leave "Send AI data" on, you can view the analytics report here:

[Image: Screenshot 2024-03-22 141025.png]

Please let us know if you have any questions or feedback.