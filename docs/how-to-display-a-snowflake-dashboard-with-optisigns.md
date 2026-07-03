---
title: "How to Display a Snowflake Dashboard with OptiSigns"
source_url: "https://support.optisigns.com/hc/en-us/articles/53028011485715-How-to-Display-a-Snowflake-Dashboard-with-OptiSigns"
article_id: 53028011485715
section_id: 26588648205715
created_at: "2026-06-29T22:30:18Z"
updated_at: "2026-07-01T21:59:22Z"
labels: []
---
# How to Display a Snowflake Dashboard with OptiSigns

If you want to display a Snowflake Dashboard, this can be accomplished with the dedicated Snowflake app within OptiSigns. This article will show how to set that up.

| |
| --- |
| **IMPORTANT NOTE** |
| The Snowflake app only works with ***internal reports*** made using Snowsight, or Streamlit with Snowflake Authentication. Other applications of Snowflake will not work using OptiSigns. |

---

## What You'll Need

- An OptiSigns account - [**Pro Plus Plan or higher**](https://www.optisigns.com/pricing)
- Access to Snowflake - specifically internal reports like Snowsight and Streamlit, with Snowflake Authentication
- An [OptiSigns-enabled device](what-hardware-and-devices-are-supported.md)
- A screen, [set up and paired with OptiSigns](optisigns-getting-started-guide.md)

---

## Create a Snowflake App

At the risk of repeating ourselves, don't forget that this is **specifically for internal reports** - Snowsight or Streamlit with Snowflake Authentication. Other applications of Snowflake will not work with OptiSigns.

To set up a Snowflake app, go to the **Files/Assets** tab, then click **Apps** on the left side of the screen:

[Image: 53052248552467]

Find and click on **Snowflake**.

[Image: 53027988862227]

Enter the details for your Snowflake site.

[Image: 53027988863635]

- **Name -** This is the name of your asset. It is for internal OptiSigns use and will not display on your screens.
- **URL -** The URL of your Snowflake Report. Please note that this ***must be*** a Snowsight or Streamlit report with Snowflake authentication.
- **Update Interval -** How often, in seconds, the dashboard reloads. This is useful if you choose to display the Snowflake asset by itself. When placed in a Playlist, the Snowflake asset will automatically update. Note that setting the number to "0" will have it reload only upon first load.
- **Sign In**
 - **Master Password -** When checked, this will prompt you to enter a Master Password for use on OptiSigns.
 - While your password is encrypted with OptiSigns, this adds an extra layer of encryption. This way, even OptiSigns cannot decrypt your password. More detail in [the FAQ section](#Encryption).
 - **Username / Email** - The Username or Email associated with the Snowflake report.
 - **Password** - The password associated with the Snowflake report.
 - **Secret 2FA** - This is the Secret Key. Only needed if your login requires 2FA. We go over how to obtain this in [the FAQ section](#2FA).
 - **Recorded 2FA Code** - If your login requires 2FA, this is where you input the code you received. Paired with the Secret Key, this keeps your 2FA channel open for this asset to use repeatedly.[Image: 53027988864403]
- **Delay Execute 2FA JavaScript -** Delays execution of JavaScript elements on the 2FA element by a set amount of time, measured in seconds.
- **Delay Execute JavaScript -** Delays execution of JavaScript elements on the Snowflake report by a set amount of time, measured in seconds.

---

## Deploying a Snowflake App

You can deploy your new Snowflake app as an individual asset, or as part of a [Split Screen](how-to-create-and-use-the-split-screen-app.md).

To get your new Snowflake asset to a screen, go to the **Screens** tab, then click the screen you want to assign it to.

[Image: 53028011480979]

This brings us to the **Edit Screen** tab:

[Image: 53027988865171]

Here, select **Asset** under Content type. If you already have an Asset, Playlist, or Schedule selected, you can hit **Change**.

Then, select your created Snowflake Asset:

[Image: 53027988866707]

Now hit **Save**. Your Snowflake asset will now display on screen.

You can also deploy it as part of a split screen, allowing you to show other assets at the same time. See how in our [Split Screen app article.](how-to-create-and-use-the-split-screen-app.md) It can also be displayed in a Playlist or Schedule.

---

## Frequently Asked Questions

#### **How does the encryption of my password work at OptiSigns? If I input it, will I be at risk?**

Here's how the encryption flow works:

[[Image: 53052194976659]](https://support.optisigns.com/hc/article_attachments/53052194976659)

When you input your Username and Password into the OptiSigns Snowflake app, it is being utilized as a [Web Script](how-to-use-the-web-scripting-app.md). This script is encrypted at your browser, and transferred securely using HTTPS/SSL during transits and stored on our servers.

It is then sent via the same method to devices, and decrypted at device level before executing on the target website. In this case, that's Snowflake.

If you want to add additional security by utilizing a Master Password and our Zero Knowledge Encryption framework, you will have to enter your Master Password when:

- Creating/editing assets
- One time on each device, so it will know how to decrypt

The Master Password can be input on OptiSigns devices under the **Advanced Options** menu under **Master Password**.

[[Image: 53052210787603]](https://support.optisigns.com/hc/article_attachments/53052210787603)

The Master Password can then be input. It will need to match the Master Password field input on your assets.

[**[Image: 53052210788371]**](https://support.optisigns.com/hc/article_attachments/53052210788371)

This will ensure no one, not even OptiSigns, can decrypt your password under any circumstance.

#### **How do I obtain my Snowflake 2FA information?**

If 2FA is enabled on your login, you'll need to obtain a **Secret Key**.

To get this, click the "I Can't Scan the QR Code" button on your authenticator.

It will provide you with a Secret Key.

Copy this Secret Key for use later, then finish the 2FA process.

Now, record the script as described in [the above step](how-to-use-the-web-scripting-app.md).

After this step, you should have:

- 2FA Secret Key
- 2FA Code

Now your Snowflake asset can be displayed securely.

###