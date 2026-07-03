---
title: "How to Use the Website App and Display URLs on OptiSigns"
source_url: "https://support.optisigns.com/hc/en-us/articles/360016382473-How-to-Use-the-Website-App-and-Display-URLs-on-OptiSigns"
article_id: 360016382473
section_id: 26324169707283
created_at: "2019-01-28T18:24:08Z"
updated_at: "2026-02-03T18:12:07Z"
labels: []
---
# How to Use the Website App and Display URLs on OptiSigns

### In this article, we'll show you how to set up the Website app to display basic websites on your digital signs.

- [What You'll Need](#WhatYouNeed)
- [Setting Up a Website App](#SettingUp)
- [Deploying a Website App](#Deploying)

To display Websites on your digital signs, you can use the **Website app**. Here is how to set one up.

---

## What You'll Need

- An OptiSigns account - [**Free Plan or higher**](https://www.optisigns.com/pricing)
- A Website URL
- An [OptiSigns-enabled device](what-hardware-and-devices-are-supported.md) - if on Free plan, one of [these devices](what-do-i-get-with-an-optisigns-free-plan.md)
- A screen, [set up and paired with OptiSigns](optisigns-getting-started-guide.md)

---

## Setting Up a Website App

On the OptiSigns portal, go to **Assets → Add Asset → Apps.**

[Image: optisigns add asset]

Select **Website**:

[Image: optisigns website app selection]

Fill in the name and the link (URL) of the site you want to use.
You can also specify refresh interval if you want the player to automatically refresh the link at certain interval.

[Image: optisigns website app interface]

- **Name** - The Name of your Website within OptiSigns. This is for organizational purposes within the OptiSigns portal, and will NOT be displayed on your signs.
- **URL** - The URL of the website you wish to display.

| |
| --- |
| **NOTE** |
| Every website is different - many will not allow Embedding, or others have specific security requirements. Even if it does not display in the Preview pane on the right, we recommend attempting to push this to your screen to be sure it will display properly. If not, you may need to use the [**Advanced Website** app](how-to-use-advanced-website-app.md), or [**Web Scripting** app](how-to-use-the-web-scripting-app.md) if your website requires login or authentication. |

- **Update Interval** - Choose how often to refresh the website to provide up-to-date data. By default, this is set to 600 seconds (10 minutes). Note that, if a Website app is used as part of a Playlist, it will always automatically refresh when it is brought up.
 - **Load only first time (no refresh)** - When toggled, will only load the website when it is first displayed on the sign. Choose this if you notice interrupted playback when trying to load a website (usually caused by latency or network issues).

---

## Deploying a Website App

You can deploy your new Website app as an individual asset, or as part of a [Split Screen](how-to-create-and-use-the-split-screen-app.md).

To get your new Website asset to a screen, go to the **Screens** tab, then click the screen you want to assign it to.

[Image: optisigns screens]

This brings up the **Edit Screen** tab:

[Image: optisigns edit screen select asset]

Here, select **Asset** under Content type, then hit **Select Asset**.

Then, select your created Website Asset:

[Image: optisigns select asset]

Now hit **Save**. Your Website asset will now display on screen.

You can also deploy it as part of a split screen, allowing you to show other assets at the same time. See how in our [Split Screen app article.](how-to-create-and-use-the-split-screen-app.md)

In order to display multiple web pages, you can create individual Website assets, then place them in a [Playlist](how-to-create-use-playlists.md). The asset or playlist can also be placed in a [Schedule](creating-and-using-schedules-with-optisigns.md).

###