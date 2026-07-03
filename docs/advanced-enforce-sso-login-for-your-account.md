---
title: "Advanced: Enforce SSO login for your account"
source_url: "https://support.optisigns.com/hc/en-us/articles/360061576673-Advanced-Enforce-SSO-login-for-your-account"
article_id: 360061576673
section_id: 26319169224851
created_at: "2021-01-04T16:38:24Z"
updated_at: "2025-09-02T20:14:28Z"
labels: []
---
# Advanced: Enforce SSO login for your account

### In this article, we'll explain how to enforce SSO logins for your OptiSigns account.

- [Setting Up Basic SSO Enforcement (Microsoft, Facebook, Google)](#BasicSSO)
- [Setting Up SAML SSO Enforcement (MS Entra ID, Okta, OneLogin, Google Workspace)](#SAML)

By default, OptiSigns allows the use of Google, Facebook, or Microsoft accounts to access the OptiSigns portal:

[Image: optisigns sso options]

However, some organizations have requirements to enforce SSO login for two-factor authentication and password protection purposes. OptiSigns supports this through Microsoft Entra ID and Google GSuite, as well as various SAML options requiring custom branding.

---

## Setting Up Basic SSO Enforcement

To set up basic SSO enforcement, go to the **Preferences** page in your OptiSigns portal:

[Image: optisigns preferences tab]

You'll find the **Enforce Account SSO** option under the "General" section, right at the top of the page.

[Image: optisigns enforce sso option]

Clicking on this will display several drop down options:

[Image: optisigns enforce sso dropdown options]

Selecting either option will require any users logging on to OptiSigns to do so with their Google or Microsoft account. If a user tries to log in in any other way, they'll receive this error:

[Image: optisigns failed login error example]

For more information, see our guide on **[User Management](advanced-security-managing-user-roles.md)**.

**Notes:** You will have to use the official <https://app.optisigns.com/> to log in to enforce SSO. You cannot use a custom domain with Enforce SSO, as the custom domain URL does not have an SSO login.

---

## Setting Up SAML SSO Enforcement (MS Entra ID, Okta, OneLogin, Google Workspace)

| |
| --- |
| **NOTE:**  This feature is available to **Pro Plus**, **Engage**, and **Enterprise** plan users. |

Setting up SAML SSO enforcement requires setting up a subdomain, then configuring your settings on your client of choice.

We have numerous articles covering this process, as well as general best practices:

- [**SAML Integration Strategy and Best Practices**](saml-integration-strategies-best-practices.md)
- [**Microsoft Entra ID SAML 2.0 SSO Setup**](how-to-set-up-saml-2-0-with-optisigns-and-ms-entra-id-formerly-azure-ad.md)
- [**Okta SAML 2.0 SSO Setup**](how-to-set-up-saml-2-0-with-optisigns-and-okta.md)
- [**OneLogin SAML 2.0 SSO Setup**](how-to-set-up-saml-2-0-with-optisigns-and-onelogin.md)
- [**Google Workspace SAML 2.0 SSO Setup**](how-to-set-up-saml-2-0-with-optisigns-and-google-workspace.md)

Please follow one of these guides to set up SSO via SAML.

###