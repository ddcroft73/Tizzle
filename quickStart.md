
# Quick Start

## To use Tizzle you need to first do a few things:
- Install python 3.10+ if you dont already have it installed. More information [Here](https://www.python.org/downloads/).
- Make sure you have admin rights on the computer you are using. If you are the sole user then you're probably already Administrator.
- Make sure Windows Task Scheduler is running. [How to check](https://www.minitool.com/news/fix-task-scheduler-not-running-windows-10.html).
- Enter the settings information into the settings.json file.
- Have an email address that you can log into and use from a 3rd party aspect. Google 3rd party app help [here](https://support.google.com/accounts/answer/185833?hl=en).
- Install [tabulate](https://pypi.org/project/tabulate/).
- Make sure you are set up for 3rd party access to a [Gmail](www.gmail.com) account. I recommend you set up an account specifically for this. Gmail  is changing their policy on May 30th and I am currently working on a workaround in case tis directly effects the use of this application. 
___
### Install tabulate:
```
$ python pip install tabulate
```

### Edit settings.json
```
    "sender_credentials": ["user@email_addy.com","password"],
    "smtp_server": "smtp.gateway.com",
    "smtp_port": 465,
    "pword": "your_computer_pword",
    "user": "User_ID"
```    

The bottom credentials are used when you want to modify a message Task in place. You can alternatively enter these at the time of modification, or as command line arguments.
<br>
<br>

### To get help at the command line:
 ```
 :\>python tizz -h
 ```
 
Before you can use the application you need to set up the environment, that is add some contacts. sText will not send a text to anyone that is not a contact, or apart of a contact GROUP.  Once you have at least one contact setup you can start to schedule or send texts to this person.
<br>
<br>

 ### To create a contact:
```
:\>python tizz add_contact <contact_name> <phone_number> <provider> -g <GROUP>
```
Only certain providers are supported (most of the common ones) and All info will be validated. You can access a free provider lookup site that can be launched from the terminal. And help is issued for provider trouble. The group should be avoided until you have more than 2 contacts and would like to add new contacts to an existing group on contact creation.
### Provider Lookup:
```
:\>python tizz.py lookup
```
### Set the default contact:
```
:\>python tizz.py set_def_contact <contact_name>
```
The first contact will always be the default. 

<br>

 ## Schedule your first text:
 ### 
 ```
 :\>python tizz.py new_msg "Message" <send_time> 
 ```
 This will send a text to the default contact at the time specified. Of course you can get a lot more specific than this, Thats just the way I set it up so i could send myself fast reminders.
 ### Send a message at 3:00pm to a contact named John Smith on 04/16/2021:
 ```
 :\>python tizz.py new_msg "Message" 15:00 -dest "John Smith" -dt 1 -sd 04/16/2021
 ```

You can get a LOT more specific but these are just a couple of the ways the application can be used to remind yourself and the people in your circle about the things you don't want to forget. For more detailed help use the on board help.

There is a lot more you can do to maintain and use the messages. You can `modify` messages that have already been sent. Or you can `modify` messages that have expired if you just want to change them to be active again. The application will `backup` both databases, and you can even recover all the messages if for some reason you delete all the tasks from the scheduler. (It happens) 
<br>
<br>
<br>
___

## Upcoming changes:
On May 30th 
Google will no longer support the use of third-party apps or devices which ask you to sign in to your Google Account using only your user name and password. Instead, you’ll need to sign in using Sign in with Google or other more secure technologies, like OAuth 2.0. [Learn more](https://accounts.google.com/AccountChooser?Email=ddc.dev.python@gmail.com&continue=https://support.google.com/accounts/answer/6010255?rfn%3D1646361360139%26anexp%3Dnret-fa)
I plan to find a work around for this if necessary and will likely implement Oauth .2.0. May be an answer [here](https://localcoder.org/python-smtplib-is-sending-mail-via-gmail-using-oauth2-possible). I plan to find an easy fix for this because I do use this app often.
<br>
<br>
## Disclaimer:
As I'm sure you have realized this application could be used in nefarious ways. I do not intend for you to use this to annoy the hell out of your friends or badger your enemies. It is nothing more than a convenient way to remind yourself, and maybe some other people in your life about important events. If Anyone has any good ideas of how to implement any anti-spam measures please submit a pull request and do so. I am not totally done with sText but I ave other pressing issues, that I need to attend to and I've spent a too much time on it already.

{ [email](gen.disarray@outlook.com) - [/uHobblingCobbler](https://www.reddit.com/user/HobblingCobbler/) }