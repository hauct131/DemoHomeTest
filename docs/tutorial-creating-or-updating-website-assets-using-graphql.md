---
title: "Tutorial: Creating or Updating Website Assets Using GraphQL"
source_url: "https://support.optisigns.com/hc/en-us/articles/36562094987795-Tutorial-Creating-or-Updating-Website-Assets-Using-GraphQL"
article_id: 36562094987795
section_id: 4414558217235
created_at: "2024-12-18T19:32:16Z"
updated_at: "2025-09-04T18:54:21Z"
labels: []
---
# Tutorial: Creating or Updating Website Assets Using GraphQL

Using GraphQL, it is possible to create a website asset on OptiSigns.

| |
| --- |
| **NOTE** |
| At this time, this Mutation is primarily used to create or update Website assets. |

**1. Creating a New Website Asset**

To do this, we’ll need to create a specific Mutation:

```
mutation saveAsset ($payload: AssetInput!, $teamId: String)
{saveAsset (payload:$payload,teamId:$teamId){
 _id
 originalFileName
 webLink
 webType
 fileType
 }
}
```

**Variables:**

```
{
 "payload": {
 "originalFileName": "",
 "webLink": "",
 "webType": "",
 "fileType": ""
 }
}
```

[Image: 36562094972435]

This Mutation, once run, will create a new asset:

[Image: 36562091083539]

This asset can now be assigned to a device, queried for additional information, or added to a playlist or schedule.

**2. Updating Assets**

Updating assets is as simple as running the same Mutation while providing an \_id field. This can be done for any asset type, not just website assets, but we will be using a website asset as an example.

**Variables:**

```
{
 "payload": {
   "_id": "",
 "originalFileName": "",
 "webLink": "",
 "webType": "",
 "fileType": ""
 }
}
```

[Image: 36562091085843]

**Previous Article - [Tutorial: Create, Update, Add, Remove Items from Playlists](tutorial-create-update-add-remove-items-from-playlists.md)**

**Next Article - [Tutorial: Creating Schedules and Adding Schedule Items Using GraphQL](tutorial-creating-schedules-and-adding-schedule-items-using-graphql.md)**