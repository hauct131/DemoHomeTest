---
title: "Pagination"
source_url: "https://support.optisigns.com/hc/en-us/articles/4414558369811-Pagination"
article_id: 4414558369811
section_id: 4414558217235
created_at: "2022-01-06T16:32:50Z"
updated_at: "2025-09-04T16:16:44Z"
labels: []
---
# Pagination

GraphQL enables you to fetch only the fields you need. This helps keep network responses small and fast. However, GraphQL doesn't automatically guarantee small responses. If the result list contains a lot of elements, it could cause an enormous response. You will need to do pagination in this situation.

Our GraphQL API implemented cursor-based pagination. There are 4 parameters used to traverse through the elements.

- after: Paginate after opaque cursor
- before: Paginate before opaque cursor
- first: Paginate first x elements
- last: Paginate last x elements

In the query, you can request the pageInfo and pageData object, which will provide all the needed data for pagination. Below is an example to paginate on devices response. It requests the first element after the specified cursor.

```
query{
 devices (query : {},first:1,after:"YXJyYXljb25uZWN0aW9uOjQ=") {
 page{
 edges{
 cursor,
 node{
 _id,
 deviceName,
 UUID,
 pairingCode,
 currentType,
 currentAssetId,
 currentPlaylistId,
 localAppVersion,
 },
 },
 pageInfo{
 hasNextPage,
 startCursor,
 endCursor
 }
 },
 pageData{
 limit,
 offset
 }
 }
}
```

[Image: 36564421486483]

**Previous Article - [Tutorial: Creating Schedules and Adding Schedule Items Using GraphQL](tutorial-creating-schedules-and-adding-schedule-items-using-graphql.md)**

**Next Article - [Error Handling](error-handling.md)**