# Tizzle -  Remind yourself or one or more contacts via free text messages in many different ways.

## Purpose:
I always respond better to a text message. When I hear that familiar chime, I know someone in my life (80% chance anyway) is trying to reach me and it could be more important, than an email. There for I am more apt to check it and see whats up. I made this application to send myself reminders about important dates, meetings, and to remind me when largish bills are due. "It's your last chance to get the trash on the curb!". Or even to send a reminder to a friend. "I'll text you in the morning to remind you about the meeting." Schedule a text now while its fresh to be sent to them at a certain time the next day, and forget it. This has proven just a useful as reminding myself. 

I was never going to put this application out there but it's literally so convenient I thought maybe someone else would find it useful. I made the on board help as thorough and colorful as I could to facilitate an intuitive program.  I'm also planning a GUI wrapper as another project. 

## Features: 

- No cell service, no API, 100% FREE.
- Schedule a reminder, promised, or updated text for you, another person or entire group to be sent on any day in multiple ways and cycles.
- Disable recurring texts from your phone. (Optional sister program, Send reply to the message to stop.)
- Anti-Spam measures to stop abuse.
- Designate yourself as the default contact to take advantage of fast CLI commands.
- Make modifications to current, passed, or future messages, in place.
- Complete maintenance of all databases. Backup, rebuild, restore.
- Failsafe task recovery in case they get deleted or become corrupted.
- Thorough command line help color coded with examples.
- Rerun feature that will reschedule a past reminder.
- Track and monitor the status of messages in real time.


 

## Requirements:
 - Python 3.10
 - Windows 10+
 - tabulate

## Upcoming changes:
On May 30th 
Google will no longer support the use of third-party apps or devices which ask you to sign in to your Google Account using only your user name and password. Instead, you’ll need to sign in using Sign in with Google or other more secure technologies, like OAuth 2.0. [Learn more](https://accounts.google.com/AccountChooser?Email=ddc.dev.python@gmail.com&continue=https://support.google.com/accounts/answer/6010255?rfn%3D1646361360139%26anexp%3Dnret-fa)
I plan to find a work around for this if necessary and will likely implement Oauth .2.0. May be an answer [here](https://localcoder.org/python-smtplib-is-sending-mail-via-gmail-using-oauth2-possible).

Apparently it still works. I am still getting texts from email addresses I'd previously set up, though it may not work with new ones. 

## ## TODO:
- Add support for oauth authentication (Adapt to Gmails new policy)
- Build in a simple SMTP mail server to send texts from computer without need for Email account. Not sure about the security of this. Just an idea.
  - Will still need an account to receive emails to use the Responder application.
- Add a GUI wrapper.
- Full documentation.
- Add support to schedule tasks on remote machines. 
- Add User and password support for using on machines that you don't have admin rights.
- App is being totally re-written using OOD.
  - Change the makeshift Json database to use a more traditional DB.   
  - Interaction with the Task Scheduler seems to be a bit sluggish. Likely it's my programming not being optimized. But the pauses during deletions and scheduling are normal. 
<br>
<br>



## Troubleshooting:
The only real problem I've see with this application is the inability to get the Task scheduler to execute the task. It works flawlessly on my desktop but for some ungodly reason WTS will not launch any task whatsoever on my laptop. The tasks are scheduled as they should be and can be `modified`, `disabled`, etc. and they will `run` manually. But it will not execute any at all. When you check the task history it is clearly not executing the tasks, and if you have this problem, IDK what to tell you. If you are having problems a few steps you can take are:

 - Open cmd Prompt with elevated privileges and run:
 ```
 :\>sfc /scannow <ENTER>
 ```
 - Open cmd prompt with elevated privileges and run:
 ```
 :\>net start task scheduler <ENTER>
 ```
 - Once again at the cmd prompt:
 ```
 :\>SC config schedule start=auto <ENTER>
 ```
 


## What I did not intend:
I did not make this to be used for sending spam. Or to annoy the hell out of your friends. I cant guarantee that it will work in this respect, and I'm going to implement a way to stop certain spam type behavior. It will do what I've said to help you keep up with your life, and to send reminders to others about future happenings. NO OTHER USE IS SUGGESTED OR INFERRED.


