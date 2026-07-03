---
title: "How to display content inside websites that require login?"
source_url: "https://support.optisigns.com/hc/en-us/articles/360037391854-How-to-display-content-inside-websites-that-require-login"
article_id: 360037391854
section_id: 26319219055891
created_at: "2019-10-24T17:26:23Z"
updated_at: "2026-06-25T12:33:44Z"
labels: []
---
# How to display content inside websites that require login?

Sometimes you have content behind a website that requires log-in, such as your project schedule in Atlassian's JIRA, Trello, dashboard behind Tableau, Salesforces, etc.

It can either be a Browser Popup or a Gated Website (like below)

[Image: mceclip0.png]

The solution is simple, you just need to:

- Copy the link to the page, and dashboard you need to display.
- Put it in the Website app in OptiSigns
- Then put the asset on your screen or in the playlist as an asset
- When it shows up on your device, just use your mouse & keyboard to enter in username and password (remember to save credentials, for Fire TV, you may need a [Bluetooth mouse & keyboard](link) to pair and type this information in).
- If you don't have a Bluetooth mouse & keyboard, you can use a [USB HUB adaptor](how-to-use-usb-hub-adaptor-connect-to-your-fire-stick.md) to connect with your mouse & keyboard.

, the credential will be saved, and every time OptiSigns plays the link, it will show the secured information inside the website.

[Image: mceclip0.png]

Enter the Website URL:

[Image: mceclip1.png]

Note: Browser Popup kind of password is not supported for Android, FireStick player. Only Windows, Linux, MacOS, Raspberry Pi, and ChromeOS are supported. The app will pop up a window for you to enter password:

[Image: mceclip2.png]

You can also prefill a password in your URL for the Browser Popup case such as: <https://guest:guest@jigsaw.w3.org/HTTP/Basic/>