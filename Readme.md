# Tizzle -  Send text messages now or schedule for anytime in the future for free.

## Purpose:
I always respond better to a text message. When I hear that familiar chime, I know someone in my life (80% chance anyway) is trying to reach me and it could be more important, than an email. There for I am more apt to check it and see whats up. I made this application to send myself reminders about important dates, meetings, and to remind me when largish bills are due. "It's your last chance to get the trash on the curb!". Or even to send a reminder to a friend. "I'll text you in the morning to remind you about the meeting." Schedule a text now while its fresh to be sent to them at a certain time the next day, and forget it. This has proven just a useful as reminding myself. 

I was never going to put this application out there but it's literally so convenient I thought maybe someone else would find it useful. I made the on board help as thorough and colorful as I could to facilitate an intuitive program.  I'm also planning a GUI wrapper as another project. 

## Features: 

- 100% FREE Text messages. No API needed.
- Send or schedule FREE text messages, for one or more contacts, now or anytime in the future from the command line.
- Don't try to remember to send that text tomorrow, Schedule it now and it's done. 
- For really important tasks. Schedule a text to repeat every few minutes or once an hour.
- Designate a particular contact as "default" so messages can be scheduled with minimal command line arguments.
- Complete and thorough help with examples from the command line.
- Create and maintain contacts and groups of contacts from the terminal.
- Backup the databases.
- Recover the databases.
- Rebuild the databases.
- Recover message tasks from the message database or the backup in case the tasks were deleted.
- Make modifications to a message that has expired or is still active.  Change the message or any of the times and dates.
- Tracks and monitor the status of all messages.
 

## Requirements:
 - Python 3.10
 - Windows 10+
 - tabulate

## Upcoming changes:
On May 30th 
Google will no longer support the use of third-party apps or devices which ask you to sign in to your Google Account using only your user name and password. Instead, you’ll need to sign in using Sign in with Google or other more secure technologies, like OAuth 2.0. [Learn more](https://accounts.google.com/AccountChooser?Email=ddc.dev.python@gmail.com&continue=https://support.google.com/accounts/answer/6010255?rfn%3D1646361360139%26anexp%3Dnret-fa)
I plan to find a work around for this if necessary and will likely implement Oauth .2.0. May be an answer [here](https://localcoder.org/python-smtplib-is-sending-mail-via-gmail-using-oauth2-possible).

## ## TODO:
- Add support for oauth authentication (Adapt to Gmails new policy)
- Add a GUI wrapper.
- Full documentation.
- Add support to schedule tasks on remote machines. 
- Add User and password support for using on machines that you don't have admin rights.
- Anti-Spam measures.
  - Crippled the hourly and minute tasks so a user cannot send them indefinitely.
    - Limits were imposed. 
      - Hourly: 1 per hour for max 6 hours.
      - Minute: no more than 1 every 5, 10, 15, or 20 minutes.
  - Still need to do something to the contacts and\or Groups.
      - maybe make it only support groups up tp 5.
- App is being totally re-written using OOD.
  - Change the makeshift Json database to use a more traditional DB.   
  - Interaction with the Task Scheduler seems to be a bit sluggish. Likely it's my programming not being optimized. But the pauses during deletions and scheduling are normal. 
<br>
<br>



## Troubleshooting:
The only real problem I've see with this application is the inability to get the Task scheduler to execute the task. It works flawlessly on my desktop but for some ungodly reason WTS will not launch any task whatsoever on my laptop. I don't get it. When you check the task history it is clearly not executing the tasks, and if you have this problem, IDK what to tell you. I can't get cron to work on my laptop either through WSL2 or through a dual boot Ubuntu distro. But If you are having problems a few steps you can take are:

 - Open cmd Prompt with elevated privileges and run:
  ```
  $ sfc /scannow <ENTER>
  ````
 - Open cmd prompt with elevated privileges and run:
 ```
 $ net start task scheduler <ENTER>
 ```
 - Once again at the cmd prompt:
 ```
 $ SC config schedule start=auto <ENTER>
 ```
 


## What I did not intend:
I did not make this to be used for sending spam. Or to annoy the hell out of your friends. I cant guarantee that it will work in this respect, and I'm going to implement a way to stop certain spam type behavior. It will do what I've said to help you keep up with your life, and to send reminders to others about future happenings. NO OTHER USE IS SUGGESTED OR INFERRED.


