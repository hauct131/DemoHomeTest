---
title: "Advanced: How to assign security for users to only edit certain zones of the screens"
source_url: "https://support.optisigns.com/hc/en-us/articles/1500002047642-Advanced-How-to-assign-security-for-users-to-only-edit-certain-zones-of-the-screens"
article_id: 1500002047642
section_id: 26503214488979
created_at: "2021-01-25T20:46:11Z"
updated_at: "2025-09-02T19:14:05Z"
labels: []
---
# Advanced: How to assign security for users to only edit certain zones of the screens

This article will guide you through how to assign security for users to only edit certain zones of the screens.
Use Case: a Company with 2 departments, Department A and Department B, each will have a section/zone of the screen that they can update freely, but they cannot change the zone belong to other departments. Administrators can edit modify the whole screen.

[Image: mceclip0.png]

To do this we will need to:

1) You need to add the users to the Account Member. Please set them as a User. Here is a related [article](multi-users-invite-your-team-members-to-your-account.md).

[Image: mceclip22.png]

2) Create Files/Assets folders for Department A & Department B

[Image: mceclip23.png]

3) Create 2 playlists: Department A & Department B

[Image: mceclip13.png]

4) Create a SplitScreen & Assign playlist

[Image: mceclip4.png]

5) Set up security for Screens, Files/Assets, Playlist folders

For the screen: You can edit the "Change Permission" in the folder. You can set **Admin Only**.

Put your screens in this folder so only Admins can edit & change assignment for the screens.

[Image: mceclip5.png]

[Image: mceclip21.png]

For the Department A folder in Files/Assets: You can edit the "Change Permission" in the folder. You can set it to **DepartmentA User**.

[Image: mceclip10.png]

For the Department B folder in Files/Assets: You can edit the "Change Permission" in the folder. You can set it to **DepartmentB User**.

[Image: mceclip11.png]

For the Department A Playlist folder in Playlist: You can edit the "Change Permission" in the folder. You can set it to **DepartmentA User**.

[Image: mceclip14.png]

For the Department B Playlist folder in Playlist: You can edit the "Change Permission" in the folder. You can set it to **DepartmentB User**.

[Image: mceclip19.png]

Now we have: 
Admin can see:

- Administration folder in the Screen.
- Department A and Department B folder in the Files/Assets
- Department A and Department B folder in the Playlist

DepartmentA User can see the

- Department A folder in the Files/Assets
- Department A Playlist Folder in the Playlist

DepartmentB User can see the

- Department B folder in the Files/Assets
- Department B Playlist Folder in the Playlist