---
title: "Error Handling"
source_url: "https://support.optisigns.com/hc/en-us/articles/4414564078995-Error-Handling"
article_id: 4414564078995
section_id: 4414558217235
created_at: "2022-01-06T16:31:58Z"
updated_at: "2025-09-11T14:10:24Z"
labels: []
---
# Error Handling

Whenever our server encounters errors while processing a GraphQL operation, it will include an error object in the response. The error object has an error array that contains each error occured. Each error in the array has a message field that contains the error message, and an extensions field that provides additional useful information, including an error code.

When calling the GraphQL API, you will need to check the response for errors instead of the HTTP status. Below are some examples of an error.

[Image: 36565574448659]

[Image: 36565574450579]

**Previous Article -** [**Pagination**](pagination.md)

**Next Article - [Subscription Function in GraphQL](subscription-function-in-graphql.md)**