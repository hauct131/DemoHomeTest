---
title: "How to Set Up an Outlook Calendar App with Shared Permissions"
source_url: "https://support.optisigns.com/hc/en-us/articles/45619214182803-How-to-Set-Up-an-Outlook-Calendar-App-with-Shared-Permissions"
article_id: 45619214182803
section_id: 26319441450131
created_at: "2025-10-14T22:08:58Z"
updated_at: "2025-10-17T16:01:18Z"
labels: ["microsoft 365", "outlook", "calendar", "rooms", "resource"]
---
# How to Set Up an Outlook Calendar App with Shared Permissions

### In this article, we'll go over how to set up Shared Permissions to show Room or Equipment Resources on an Outlook Calendar with OptiSigns.

- [What You'll Need](#WhatYouNeed)
- [Step 1: Granting the Proper Resource Permissions to a User Account](#Step1)
- [Step 2: Displaying the Resource in the User's Outlook Calendar](#Step2)

When using Outlook calendar in an organization, you are often granted access to various calendars. These may be for other individuals, or they may show the availability of certain shared resources, such as Rooms or Equipment.

While OptiSigns currently does not support showing multiple user calendars at once (see our [**Calendar Mix**](how-to-use-calendar-mix-app.md) app for doing that), it is possible to show those Resources. However, specific permissions will need to be granted via your Microsoft Admin account in order to do this.

Let's get started.

---

## What You'll Need

To set up Resource permissions and display them on OptiSigns, you'll need:

- Administrator Access to a Microsoft Business Account
- A Room or Equipment Resource to display
- An OptiSigns[**Standard Plan or higher**](https://www.optisigns.com/pricing)

---

## Step 1: Granting the Proper Resource Permissions to a User Account

To get started, we'll need to open up the [**Microsoft Exchange Admin center**](https://admin.exchange.microsoft.com/#/resources). This is where permissions of this type are handled.

Navigate through the sidebar to the **Resources** tab. Here, select either **Add a Room Resource, Add an Equipment Resource,** or an already made Resource.

[Image: exchange admin center resource example]

You'll see that the **Type** displays what type of resource it is, whether Room or Equipment. These resources are distinct from Users, and have different permissions.

Click the Display Name of the resource you want to change the permissions of to continue:

[Image: microsoft room 1]

Next, navigate to the **Delegation** tab, then hit **Edit** under the "Read and manage" section:

[Image: microsoft room permissions delegation]

On the Manage delegates screen, click **Add Member:**

[Image: 45619197981459]

This will open up the "Add read and manage permissions tab." Here, select the Display Name of the user you want to set up OptiSigns with.

[Image: microsoft exchange admin read manage permissions]

Hit **Save**. Now we need to make sure the Resource calendar is set up in Outlook.

---

## Step 2: Displaying the Resource in the User's Outlook Calendar

Log in to Outlook with the user you wish to display OptiSigns on. Hit **Add Calendar**:

[Image: microsoft outlook add calendar]

Next, click **Add from Directory**, then **Select an Account**.

[Image: microsoft outlook add calendar directory]

You'll choose your User account here:

[Image: add from directory choose email]

You'll be asked to Select a person, group, or resource from your organization's directory. Find the desired Resource's **email address**. This can be found on your Resources page in your Exchange Admin portal:

[Image: use room email][Image: select room from email]

Once it has been found and entered, it will appear on the list:

[Image: room resource on list]

When you try and exit, you'll be asked to Save changes. Do so.

[Image: save changes to outlook calendar]

Now the Resource's calendar will populate on this User's calendar display.

From here, follow the normal instructions on [Setting Up a Microsoft Outlook Calendar with OptiSigns](how-to-use-microsoft-outlook-calendar-with-optisigns.md) to get your Calendar up and running.

###