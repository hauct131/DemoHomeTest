---
title: "Display Salesforce Dashboards with MFA using Web Scripting"
source_url: "https://support.optisigns.com/hc/en-us/articles/32839794222099-Display-Salesforce-Dashboards-with-MFA-using-Web-Scripting"
article_id: 32839794222099
section_id: 26318933920019
created_at: "2024-08-28T21:16:42Z"
updated_at: "2025-09-02T20:45:08Z"
labels: []
---
# Display Salesforce Dashboards with MFA using Web Scripting

#### Displaying Salesforce Dashboards on your digital screens is crucial to getting real-time data directly to who needs it. Let's go through how to set up your MFA-protected Salesforce Dashboard by using our Web Scripting app!

Things You'll Need:

- [Salesforce Dashboard](https://www.salesforce.com/)
- [Burp Suite Navigation Recorder](link)
- Authenticator App (ex., Google Authenticator)

---

## Setting Up MFA

| |
| --- |
| *If you don't already have MFA set up for your Salesforce account, please visit their support article: **[Multi-Factor Authentication for Salesforce Orgs.](https://help.salesforce.com/s/articleView?id=sf.security_overview_2fa.htm&type=5)*** |

Next, go to your account settings > My Personal Information > Advanced User Details

From there, click **"Connect"** on "**App Registration: One-Time Password Authenticator**"

[Image: Salesforce account settings and setting up authenticator app]

When Salesforce prompts you to connect an Authenticator App, **DO NOT** immediately scan the QR code.

Click "**I Can't Scan the QR Code**".

[Image: Salesforce setting up authenticator app. Select 'I can't scan the QR code']

**Copy and paste the alphanumeric string** displayed underneath "Key". **Save this key** somewhere secure, like the Notepad app.

- This is ***necessary*** for the web scripting process later.

Next, enter that setup key in your authenticator app, then enter the verification code into Salesforce, and connect!

[Image: Save the setup key that Salesforce provides you.]

**Your MFA is now set up!**

---

## Record & Set Up Your Web Scripting App

| |
| --- |
| *You can refer to our **[How to use the Web Scripting App article](how-to-use-the-web-scripting-app.md)** on how to download Burp Suite Navigation Recorder and record your script.* |

During the recording process, **write down the exact verification code** you inputted to log in to your account.

- This is ***necessary*** when setting up the Web Scripting app.

Once your script is recorded, Burp Suite should automatically copy it to your clipboard. You can also copy it to your clipboard by opening Burp Suite in the extension manager:

[Image: Click 'Copy to clipboard' on Burp Suite Navigation extension to copy the script again.]

Log in to your OptiSigns account and open the Files/Assets page to create your asset. Click on **"Apps"** You need to:

1. Paste your script into the "**Recorded Script**" box
2. Paste the alphanumeric setup key you saved from Salesforce into "**Secret 2FA**"
3. Input the *exact* verification code you used during the login process while recording into the "**Recorded 2FA Code**" box.

[Image: Web scripting in OptiSigns and pasting the script, setup key, and 2fa code in their respective boxes.]

Click **Save!**

---

Now you can [push this app to your screen,](push-contents-to-your-screens.md) [add it to a split screen app](how-to-create-and-use-the-split-screen-app.md), and more!

[Image: A salesforce dashboard displayed on a split screen app to show the dashboard, weather, and important news on your TV.]