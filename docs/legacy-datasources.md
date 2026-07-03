---
title: "Legacy DataSources"
source_url: "https://support.optisigns.com/hc/en-us/articles/42915219118739-Legacy-DataSources"
article_id: 42915219118739
section_id: 42924355604627
created_at: "2025-07-11T15:42:48Z"
updated_at: "2025-09-04T16:58:08Z"
labels: ["google sheets", "excel", "ms excel", "spreadsheet", "microsoft 365"]
---
# Legacy DataSources

### In this article, we’ll cover our Legacy DataSources - key-value pair formatting with Google Sheets or Microsoft 365 Excel

- [How it Works and When to Use Legacy DataSources](#HowitWorks)
- [Creating Data Mapping Elements](#Creating)
- [Generating a Google Sheet or Excel Document](#Generating)
- [Modifying the Data](#Modifying)

Using Designer, it’s possible to assign a key value to an element, then map it to a Google Sheet or Microsoft Excel document. This will create a new spreadsheet directly mapped to the individual design. The values on this new spreadsheet can be modified to change what the design displays.

[Image: advanced datasources googlesheet or ms excel 365]

Please note that this is an older form of Data Mapping in OptiSigns. Now, with our new OptiSync feature, exsiting Google Sheets or MS Excell sheets can be directly integrated into a design with a simple drag-and-drop. It is also possible to directly connect APIs, JSON, XML, or custom tables. See our article on [**Dynamic Data Mapping using OptiSync**](how-to-set-up-dynamic-data-mapping-with-optisync.md) for more information.

---

## How it Works and When to Use Legacy DataSources

This form of Data Mapping follows these steps:

1. Mapping data to individual design elements
2. Generating a Google or Excel spreadsheet of these elements
3. Altering the spreadsheet so changes are reflected on the design

Different screens can be mapped to the same design so that, depending on where it’s shown, the values will be different.

Legacy DataSources are particularly useful for pairing with our [**Scrolling Text**](widgets-in-designer.md) and [**Scrolling Vertical** widgets](widgets-in-designer.md), and if you have numerous elements on a single design you wish to be dynamic.

---

## Creating Data Mapping Elements

To get started, you’ll need to create a design. To do this, go to **Files/Assets → Apps → Designer**.

For this example, we’ve used one of our [pre-built Templates](https://canvas.optisigns.com/) as the design. For yours, you can explore our 5000+ template library, or create a design from scratch. See our article on [**Getting Started with Designer**](getting-started-with-designer.md)if you need help.

Now, we’ll need to add a Data Mapping to an element. Click the Element you want to map to your DataSource, then hit the **Settings** button. Then, click **Make Data Mapping**.

[Image: how to make data mapping]

The element will automatically be given an **Element ID.** We also recommend giving it an **Asset Element Name**, which will appear on your generated spreadsheet and can help identify what the value is.

 [Image: data mapping element id and asset element name]

There are also additional options:

- **Hide when data not available:** When no data is present on the sheet, nothing will display
- **Empty Data Handling:** When there is no DataSource element, the default behavior is to use the default value. You can adjust this with the following options:
 - **Use Default Value:** Show default content, which is what your element looks like originally.
 - **Use Blank:** Nothing will display.

For more on the **Advanced Options** here, see [**Property Mapping and Display Format**](how-to-set-up-dynamic-data-mapping-with-optisync.md).

Now, you’ll want to ***repeat this process for every element you wish to be dynamic***. Make sure you do this before you move on to the next step.

---

## Generating a Google Sheet or Excel Document

Once you’ve mapped all the elements you want to be dynamic, it’s time to generate your spreadsheet. To do this, click the **DataSource** button on the Side Menu, then click **Add DataSource**:

[Image: how to add a datasource]

Scroll down in the popup to the **Adv. DataSources** section and choose either **Google Sheets (legacy)** or **MS Excel 365 (legacy)** depending on which you prefer.

[Image: advanced datasources googlesheet or ms excel 365]

Clicking one of these will bring up the option to sign in with your account of choice.

[Image: choose between google sheet or ms excel datasource]

| |
| --- |
| **NOTE** |
| This requires a paid account for Microsoft 365, as the free account does not support this feature. Without a paid MS 365 account, we recommend a Google Sheet. |

Give the Sheet a **Name**, then sign in to your preferred account. You will need to provide certain permissions for this to work. See our [Privacy Policy](https://www.optisigns.com/privacy-policy) for additional information.

Next, you’ll be asked to provide the Folder for where you want your sheet to be saved. Select one, then continue. Your DataSource will be created:

[Image: authorized google sheets datasource example]

| |
| --- |
| **IMPORTANT** |
| Data must be within a table if using Excel Sheets. [Image: excel datasource table example] |

At this point, you can access your spreadsheet to see the elements you’ve mapped by hitting the **Open** button.

[Image: how to open google sheet in optisigns]

The elements you’ve mapped will appear in the sheet.

[Image: 42915219094419]

---

## Modifying the Data

To change the mapping, simply edit the values in the columns, being sure to keep the Asset Element ID and Asset Element Name the same.

For example, say we want the word “SOCIAL” to appear on one screen in one location, but we want it to say “COMMUNAL” in another. To do this, we simply duplicate the Row, then change the “Screen Name” and “Value” cells:

[Image: modified data in datasource]

The “Screen Name” will need to be the same as the name of the screen you’re targeting with the asset. This is equivalent to the **Device Name** under the **Edit Screen** tab:

[Image: device name on edit screen tab]

Some best practices:

- OptiSigns will identify the screens by name and adjust the Value based on what's entered on your spreadsheet.
- If you change your screen's name, be sure to update your spreadsheet at the same time. If updated later, it could cause issues with data mapping on the screen at the next update interval.
- \*\*\*ALL\*\*\* tells OptiSigns that if a screen is not specifically assigned values, it will take value from this row of data. This is equivalent to the "Default Value" mentioned earlier in the article.
 - If a value is detected, it will override the \*\*\*ALL\*\*\* value, like in the example above.

### **That’s all!**