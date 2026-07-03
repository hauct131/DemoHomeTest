---
title: "Set OptiSigns as ScreenSaver on Windows"
source_url: "https://support.optisigns.com/hc/en-us/articles/360053211594-Set-OptiSigns-as-ScreenSaver-on-Windows"
article_id: 360053211594
section_id: 26318906819091
created_at: "2020-09-08T16:16:53Z"
updated_at: "2025-08-29T20:39:30Z"
labels: []
---
# Set OptiSigns as ScreenSaver on Windows

Sometimes, you would want to set OptiSigns to run if the PC is idle for some time.
This is a good use case for Kiosk and Public use computers.

In this guide, we will walk you through end to end process to set OptiSigns app as Screen Saver on Windows.

### How to Set OptiSigns as Screen Saver on Windows.

First open OptiSigns side menu, click Advanced, and turn on "Screen Saver Mode".

When this mode is on, OptiSigns will be closed on any mouse move, click, or keyboard pressed.

[Image: mceclip0.png]

Then use Window's task scheduler to run OptiSigns when the PC is idle.

Here's the steps, on Windows click Start, search for "Task Scheduler" & open it.

Task Scheduler -> Create Task -> "Trigger" tab -> New -> "Begin the task:" -> "On Idle"

Next, go to the "Actions" tab and set the action to whatever it is you want to run.

- Search for "**Task Scheduler**" & open it

[Image: Task\_Scheduel\_1.png]

- **Create Task** in your Task Scheduler

[Image: Task\_Scheduel\_2.png]

- Set **Configure** for your device

[Image: Task\_Scheduel\_3.png]

- Go to **Triggers** tap, and click "**New ...**"

[Image: Task\_Scheduel\_4.png]

- Set Begin the task: "**On idle**"

[Image: Task\_Scheduel\_5.png]

- Go to **Actions** tap, and click "**New ...**"

[Image: Task\_Scheduel\_6.png]

- Set Action: "**Start a program**", and "**Browse**" OptiSigns app's location.

[Image: Task\_Scheduel\_7.png]

- Go to **Condition** tap, and set the condition for your computer.

[Image: Task\_Scheduel\_8.png]

- Go to **Setting** tap, and set "**Run a new instance in parallel**" (The Task Scheduler service will run the new instance of the task in parallel with the instance that is already running.)

[Image: Task\_Scheduel\_9.png]

- After that, you finish your task setting. You can click "**Run**" to start this task.

[Image: Task\_Scheduel\_10.png]

- Your status of task will show "**Running**".

[Image: Task\_Scheduel\_11.png]

- Close OptisSigns app

Once the computer is idle, your screen will run OptiSigns app.

You're ready to go.

**IMPORTANT:**

Because OptiSigns is closed on any mouse move, click or key press when Screen Saver mode is turned on.

If you want to control OptiSigns again, press Ctrl + Alt + A or Ctrl + Alt + S, this will turn off Screen Saver mode, and you can interact with OptiSigns.

If you have feedback on how to make the how-to guides better, please let us know at: [our support team](mailto:our support team)