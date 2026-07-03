---
title: "Generate & Manage OptiSigns API Key"
source_url: "https://support.optisigns.com/hc/en-us/articles/4414563797139-Generate-Manage-OptiSigns-API-Key"
article_id: 4414563797139
section_id: 4414558217235
created_at: "2022-01-06T16:17:17Z"
updated_at: "2025-09-04T18:50:38Z"
labels: []
---
# Generate & Manage OptiSigns API Key

In order to use the API, you will need first get an API key. To get an API key, you can either use the link below, or click the **API Keys** button in the side menu of account management on the OptiSigns portal.

<https://app.optisigns.com/app/s/apikeys>

### [Image: 38115363822739]

### Create API Key

1. Click the **New API Key** button
[Image: optisigns new api key button]

2. Enter the API Key name, and select the scopes and permissions for the API key.
[Image: optisigns new api key setup]

3. Save the API key safely, the key will be used the access your account through API.

[Image: optisigns api key token example]

### Use API Key

To use the API key, put it in the HTTP request header following this format.

Authorization: Bearer YOUR\_KEY\_HERE

In the OptiSigns GraphQL playground, you will be able to query your data if the API key is successfully added.

[Image: optisigns graphql playground api key input]

**Previous Article - [Introduction](introduction.md)**

**Next Article - [Get Started](get-started-with-optisigns-api.md)**