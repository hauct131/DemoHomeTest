---
title: "How to Set Up a Power BI Service Principal for Use in OptiSigns"
source_url: "https://support.optisigns.com/hc/en-us/articles/32860569148819-How-to-Set-Up-a-Power-BI-Service-Principal-for-Use-in-OptiSigns"
article_id: 32860569148819
section_id: 26319305433875
created_at: "2024-08-29T14:32:01Z"
updated_at: "2026-03-17T22:32:17Z"
labels: ["power bi", "powerbi"]
---
# How to Set Up a Power BI Service Principal for Use in OptiSigns

### In this article, we will walk you through the process of setting up a service principal for Power BI in Microsoft Azure, and connecting it to OptiSigns.

- [Creating an Entra App in Microsoft Azure](#Create)
- [Enable Power BI Service Admin Settings](#Enable)
 - [Add the Service Principal to a Workspace](#Add)
- [Authenticating OptiSigns via Service Principal](#Auth)
- [Getting Power BI onto a Screen](#Get)

Using a Power BI service principal with app registration is a preferred option for companies with strict information security rules that don't want to use individual user accounts for Power BI integration.

This reduces headaches in situations when:

- There is a position or permission change of a user and authentication needs to be performed again by a different user.
- A prolonged authentication token period cannot be set for individual users, and you will need to reauthorize and refresh the token every couple of months.

Using a Power BI service principal, the authentication tokens are associated with a registered app instead of a user. This allows you to set a longer validity time for the authentication token and avoids more frequent re-authorization. Using service principal with App registration for Power BI integration is supported well with OptiSigns.

| |
| --- |
| **NOTE:** This feature is only available to customers on an **Enterprise** plan. |

---

## Create an Entra App in Microsoft Azure

An Entra app will be responsible for handling identity and access management for your service principal. In order to create one, you’ll need to login to Microsoft Azure with a viable Microsoft account.

Once at the Azure portal, search for **“app registrations,”** then select **App Registrations** from the list that appears:

[Image: app registration instructions in microsoft azure]

Create a **New Registration**.

[Image: how to create a new registration in microsoft azure]

On this screen, type a name for the app, then leave the other settings as default. These can be changed or altered at any time.

[Image: instructions on registering an application in microsoft azure]

Once done, hit **Register.**

---

## Enable Power BI Service Admin Settings

Follow this link to the [PowerBI Admin Portal](https://app.powerbi.com/admin-portal/capacities?experience=power-bi).

Once there, click **Tenant Settings**. Then, scroll down to **Developer Settings**.

[Image: finding developer settings in tenant settings within powerbi admin portal]

Enable the **Embed Content in Apps Settings**, as below:

[Image: how to enable embed content in apps]

In this example, we’ve set this embed to apply permissions to the entire organization. However, you can restrict access to specific security groups based on your needs. These security settings can be changed as per your requirements.

Next, **Enable Service principals can create workspaces, connections, and deployment pipelines** and **Enable Service Principals can call Fabric public APIs**, as below:

[Image: image (28)(1).png]

Like before, we’ve applied these to the entire organization. Just like the last step, you can restrict access to specific security groups based on your needs.

### Add the Service Principal to a Workspace

Now we need to assign service principal access to the workspaces you want to show in your PowerBI reports.

In the admin portal, click **Workspaces**. You’ll want to go to the workspace you want to assign service principal access to. Click the workspace, then hit **Access**.

[Image: how to grant service principal access powerbi]

Add the service principal you created in the last step as a member of the workspace.

[Image: how to add service principal as a member of powerbi workspace]

---

## Authenticating OptiSigns via Service Principal

In order to authenticate your Power BI on OptiSigns via service principal, you’ll need four pieces of information:

1. Name of the service principal
2. Application (client) ID
3. Directory (tenant) ID
4. Application (client) secret

Since we’ve already created an Entra app in Azure, we already have access to the first three pieces of information. These can be found under **App Registrations** back in Azure.

[Image: where to find app registration information in microsoft azure]

In this example, the values have been blurred, but on your Azure portal, these should be visible.

The only piece of information you won’t have is the client secret. To get that, click **Manage → Certificates & Secrets → Client Secrets → New Client Secret**

**[Image: how to create new client secret in microsoft azure]**

Next, set the **Description** and **Expiry**, then click **Add**.

[Image: how to add a client secret]

The **Value** present is the last piece of information you need.

Now, head into the OptiSigns app. Click your **Profile name → More → Integrations.**

[Image: where to find integrations tab in optisigns]

A screen like the one below will appear. Click **Add Azure Service Principal.**

[Image: how to add service principal in optisigns]

When the popup appears, collect the information mentioned above from Microsoft Azure and input it into OptiSigns. The values match up like this:

[Image: inputting all the powerbi service principal information into optisigns]

Once all the information is input correctly, hit **Save**. Now your Service Principal is saved to the OptiSigns portal.

---

## Getting Power BI onto a Screen

Now we’ll need to configure your Power BI asset in OptiSigns for use with your screens.

In the OptiSigns portal, go to **Files/Assets → Apps → Power BI**

**[Image: how to find powerbi app in optisigns]**

Check **Use Service Principal** and select the service principal you set up in the last step, or whichever service principal you want to use.

| |
| --- |
| **NOTE:** Using a service principal, the Power BI Dashboard URL link needs to include the actual **workspace (group)** ID instead of me. |

**[Image: powerbi app information in optisigns]**

Finally, input the URL of whatever report you want to share. Name the app whatever you like, then hit **Preview** to view your report.

**[Image: preview of powerbi app running in optisigns]**

Hit **Save**, then this Power BI app will exist as an asset. It can be pushed to any of your screens individually, scheduled, or added to a Playlist.

### **That’s all!**