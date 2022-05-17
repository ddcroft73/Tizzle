# message.py

from re import findall
from tabulate import tabulate
from providers import PROVIDERS
from smtplib import SMTP_SSL
from ssl import create_default_context
from subprocess import run, Popen, DEVNULL, PIPE
from time import sleep
from os import remove as os_remove, startfile   
from os.path import exists as os_exists
from sys import executable 

# data\utility functions:
from utility import (
    format_expression,
    write_data,
    load_data,
    get_time_date,
    wrap_quotes,
    warn_or_continue,
    contact_exists,
    group_exists,
    get_scheduled_tasks,
    get_unique_id,
    format_expression,
    insert_breaks_and_sep,
    get_scheduled_tasks,
    create_batch_path_command,
    create_batch_file,
    get_living_batch_files,
    validate_time_date, 
    valid_schedule_time,
    print_report,
    clean_message,
    get_digit,
    get_actual_frequency,
    get_end_timedate,
    trunc_message,
    trunc_all_messages,
    calculate_end_time,
    validate_duration,
    eval_date,
    get_credentials,
    search_ID,
    messages_header
)
# shared all between message.py and contacts.py
from constants import *

from mod_message import(
    create_command_list_validate,
    display_message_changes,
    edit_batchfile,
    edit_WTS,
    get_message_from_disk
)

# TODO
# Add support for login pword  for use on machines without admin rights..
# Create a GUI wrapper that will visually accept the options and call this program.
# add Oauth support to handle the changes put forth by Gmail
# Maybe look into a small SMTP server to send the texts from your computer. Not sure about security 
# issues. Will still need IMAP support to use the Responder.

class Message:
    

    def __init__(self):
        if os_exists(DB):            
            self.__check_and_update_status()   
        else:
            print(f'\nUnable to locate {BLUET}{DB}{ENDC}. \n{YELLIT}Rebuild now or recover from backup{ENDC}.') 
            exit()   
        
    def new(self, args: object) -> None:
        """ The main focus of the entire application:

        Creates a new message task, and thereby calls all other routines needed to create a new message 
        and get it scheduled. 
        
        - Sets up and validates the user input.
        - Creates a unique Id for the Message.
        - Initializes a batch file and command.
        - Schedules the task to send the message with WTS.
        - Adds the message to the DB.
        - Creates the batch file that calls this application when launced via WTS.
        - Displays a detailed report.
        """
        _msg:               str = args.message
        _time_to_text:      str = args.time
        _destination :      str = args.destination
        _dest_type:    int|None = args.dest_type
        _date_to_text: str|None = args.date 
        _frequency:    str|None = args.freq
        _mo:           str|None = args.mo
        _duration:     str|None = args.duration
        _dow:          str|None = args.dow 
        _dom:          str|None = args.dom 
        _end_date:     str|None = args.ed
        
        bat_path: str
        bat_command: str
        contacts_info: list[list[str]] = load_data(CONTACTS_DB)             
        
        # Support the use of short dates no year required. 
        _date_to_text, _end_date = eval_date(_date_to_text, _end_date)
       
        # set defaults
        if (_date_to_text is None): 
            _date_to_text = get_time_date("todays_date")           
        if (_frequency is None):    
            _frequency = "once"             

        # Certain options dont jive, and others have special needs.    
        bad_options: bool = self.__check_args(
            _frequency, 
            _duration, 
            _mo, 
            _dow, 
            _dom,
            _end_date,
            _date_to_text
        )          
        if (bad_options): return

        _frequency = self.__set_for_hour_minute(_frequency, _mo)          

        end_time_date: str = self.__get_end_time_date(
            _frequency, 
            _time_to_text, 
            _date_to_text, 
            _end_date,
            _duration
        )                

        _destination = self.__validate_and_format_destination(
            contacts_info,
            _destination, 
            _dest_type
        )
        if (not _destination): return              

        if (validate_time_date(_time_to_text, _date_to_text)):
            if (valid_schedule_time(_time_to_text, _date_to_text)):  

                unique_msg_id: str = get_unique_id()       
                
                if(_dest_type == GROUP):
                    self.__add_msgid_to_contacts_list(unique_msg_id, _destination)    
                
                # create the bat file path and command only so that 
                # WTS has a prog path tho schedule a task for.
                bat_path, bat_command = create_batch_path_command(
                    _msg, 
                    unique_msg_id, 
                    _destination,
                    _frequency,
                    _dest_type
                )                
                
                return_code: int = self.__schedule_task(
                    _time_to_text, 
                    _date_to_text,
                     unique_msg_id, 
                     bat_path, 
                    _frequency_sched=_frequency,
                    _day_of_week_sched=_dow, 
                    _day_of_month_sched=_dom,
                    _end_date=end_time_date.split('\n')[1],
                    _mo=_mo,
                    _duration=_duration
                )                             
                # Since all went well finish up message creation with Db Entry
                # And creation of actual batch file to launch the app and send text.
                if (return_code == SUCCESS): 
                    self.__add_msg_database(
                        unique_msg_id, 
                        insert_breaks_and_sep(_msg),         
                        _destination,
                        _time_to_text + '\n' + _date_to_text, 
                        _frequency.upper(), 
                        end_time_date,
                        _dow,
                        _dom
                    )                   

                    create_batch_file(bat_path, bat_command)       

                    print_report(
                        unique_msg_id,
                        _time_to_text,
                        _destination,
                        _dest_type,
                        _date_to_text, 
                        _frequency,
                        _mo,
                        end_time_date.split('\n')[0],
                        _dow, 
                        _dom, 
                        _end_date
                    )                                    
#-------------------------------------------------------------------------------------------------------------------------------------------    
    def send(self, args: object) -> None:
        """Depending on the arguments, instigates the sending of text messages to one or more contacts.
        Args:
            _destination (str): The contact or the group to send to.
                                Contact must be title
                                Group must be all Caps
                                Default must be lower case.
            _msg         (str): The message to be sent

            All the Cases of the destination will be sorted out by the time it reaches here.
        """
        _destination: str = args.destination        
        _msg:         str = args.message#.replace(":", "")   # colons seem to mess up the texts? IDEKW If you are receiving blank messages
                                                             # uncomment the replace method and it should stop. Would love tho know why.
        _msg_id: str|None = args.msg_id.upper() if args.msg_id is not None else None   # Only used by the ID when sending group texts

        settings: dict[str,str|int] = load_data(SETTINGS_FILE)
        contacts: list[list[str]] = load_data(CONTACTS_DB)  
        found: bool = False

        for contact in contacts:
            if (_destination.lower() in ['def', 'default']):  # Default contact
                print(f'Sending text to {YELLT}{contacts[DEFAULT_CONTACT][NAME]}{ENDC}.') 
                self.__send_text(_msg, contacts[DEFAULT_CONTACT], settings)             
                found = True
                break

            elif (_destination.isupper()):                    # Group
                if (contact[GROUP_NAME] == _destination):                    
                    # Check the contacts message list to see if they get this message.
                    if _msg_id in contact[MSG_LIST]:      
                        print(f'Sending text to {YELLT}{contact[NAME]}{ENDC} ' 
                              f'of group[{YELLT}{contact[GROUP_NAME]}{ENDC}].')
                        self.__send_text(_msg, contact, settings)
                    else:
                        print(f'{BLUET}{contact[NAME]}{ENDC}: {YELLIT} has stopped this message{ENDC}.')      

                    found = True
                    sleep(0.5)

            elif (_destination.istitle()):                    # Single Contact
                if (contact[NAME] == _destination):
                   print(f'Sending text to {YELLT}{contact[NAME]}{ENDC}.')
                   self.__send_text(_msg, contact, settings)
                   found = True 
                   break
                
            else:
                found = False

        if (not found):
            print(f'No Contact or Group info found for "{YELLT}{_destination}{ENDC}"'  
                  f'\nAll words in contact names should {BLUET}begin with a capitial letter{ENDC}.'
                  f'\nIf sending to a group make sure the group was entered in {BLUET}ALL CAPS{ENDC}.')  
#-------------------------------------------------------------------------------------------------------------------------------------------
# Enable Tasks
    def enable_task(self, args: object) -> None:
        """will enable a task asociated with a message"""
        
        try:
           _msg_id: str = args.msg_id.upper()
        except:
           _msg_id = args.upper()         
        
        if (_msg_id in get_scheduled_tasks()):
            res: str = self.__get_status(_msg_id)
            if (res == "Disabled"):
                command: str = ["schtasks.exe", "/CHANGE",  "/TN", _msg_id, "/ENABLE"]   

                return_code: int = run(command).returncode      
                if (return_code == SUCCESS):
                    self.__change_message_status(_msg_id, 'Enabled')
                    print(f'\nMessage "{BLUET}{_msg_id}{ENDC}" has been {GRNT}ENABLED{ENDC}.')                    
            else:
                print(f'\nMessage "{BLUET}{_msg_id}{ENDC}" is already {GRNT}ENABLED{ENDC}.')
        else:
            print(f'\nTask: "{BLUET}{_msg_id}{ENDC}" {YELLT}was not found{ENDC}.')            
#-------------------------------------------------------------------------------------------------------------------------------------------
# Disable Tasks
    def disable_task(self, args: object) -> None:
        """will disable a task associated with a message"""
        _msg_id: str = args.msg_id.upper() 
        # only viable if it's a living task.
        # if not don't disable it
        
        if (_msg_id in get_scheduled_tasks()):
            res: str = self.__get_status(_msg_id)
            
            if (res in ["Recurring", "Started", "Ready", "Started(m)", "Ready(m)", "Modified"]):
                command: str = ["schtasks.exe", "/CHANGE",  "/TN", _msg_id, "/DISABLE"]

                return_code: int = run(command).returncode  
                if (return_code == SUCCESS):
                    self.__change_message_status(_msg_id, 'Disabled')
                    print(f'\nMessage "{ENDC}{BLUET}{_msg_id}{ENDC}" has been {REDT}DISABLED{ENDC}.')

            
            elif res in ['Expired', 'Sent']:
                print(f'\nMessage "{BLUET}{_msg_id}{ENDC}" is no longer viable. No need to disable.'
                    f'\nIf you would like to change the message so that it sends again,  '
                    f'\n\nUse: stext mod_msg <message_id> [options]')  

            elif (res == 'not found'):
                print(f'\nMessage: "{YELLT}{_msg_id}{ENDC}" {YELLT}was not found{ENDC}.')
        else:
            print(f'\nTask: "{BLUET}{_msg_id}{ENDC}" {YELLT}was not found{ENDC}.')
#-------------------------------------------------------------------------------------------------------------------------------------------
# Run A set task now   
    def run_task(self, args: object) -> None:
        """will run a task associatd with a message"""
        _msg_id: str = args.msg_id.upper()
       
        if (_msg_id in get_scheduled_tasks()):
           command: str = ["schtasks.exe", "/RUN", "/TN", _msg_id] 
           run(command)
        else:
           print(f'\nTask: "{BLUET}{_msg_id}{ENDC}" {YELLT}was not found{ENDC}.')
#-------------------------------------------------------------------------------------------------------------------------------------------    
    def modify(self, args: object) -> None:
        """ 
        Modifies an existing message in place.  
        Any message may be modified several ways. startdate, enddate, endtime,
        message, or desination. Cannot modify the frequency of how it is sent.
        Useful for correcting mistakes, or to revive a deceased message task.
        """         
        messages: list[list[str]]  = load_data(DB)
        validated:            bool = True
        edit_batch:           bool = False
        arg_d:  dict[str, str|int] = {}       # dictionary that will organize all the args
        command:     list[str|int]            # the argument list to send to schtasks.exe
        _msg_id:               str = args.msg_id.upper() 
        start_date:            str
        end_date:              str

        # support short Dates:
        start_date, end_date = eval_date(args.start_date, args.end_date)
        
        if (not search_ID(_msg_id)): return

        # If the message is disabled, check to enable it first.
        if (self.__check_enable(_msg_id)): return
        
        # Evaluate all the mods the user requested and create a command to make
        # the changes. Decide if it is needed to edit the batch file or not
        # and validate any necessary arguments
        validated, edit_batch, arg_d, command = \
        create_command_list_validate(
            _msg_id,
            args.start_time,
            args.message,
            args.destination,
            args.dest_type,
            start_date,
            end_date,
            args.duration,
            args.userid,
            args.pword
        )       
                
        if (validated):   
            # find the message being modified and present the user with the changes
            # to be approved.
            for msg in messages:
                if msg[ID] == _msg_id:                 
                    
                    msg = display_message_changes(
                        msg,
                        _msg_id, 
                        arg_d
                    )   
                    break          

            if warn_or_continue(
                   f"\n{BLUET}Would you like to commit these changes{ENDC}?", warn=False
                ): 

                # Is this a group message? If so add it back to the group members lists
                if args.dest_type == GROUP or self.__is_group_message(_msg_id):
                    self.__add_msgid_to_contacts_list(_msg_id, args.destination)                

                if edit_batch: 
                   edit_batchfile(args.message, _msg_id, args.destination, args.dest_type)

                # may need to only edit the batch file if the dest, dest_type, and msg changed only.
                # no reason to mess with the WTS if so.
                if edit_WTS(arg_d):
                    return_code: int = run(command).returncode            
                    if return_code == SUCCESS:
                         write_data(messages, DB)  
                else:           
                    write_data(messages, DB)    
                    
                print(f'\n"{BLUET}{_msg_id}{ENDC}" succesfully modified.')    
#-------------------------------------------------------------------------------------------------------------------------------------------   
    def delete(self, args: object) -> None:
        """ Handles the choices for deletion of items in database json, scheduler, batch files. """
        # REWRITE THIS TO USE A MORE TRADITIONAL MENU SYSTEM WITH A LOOP, hell, it works fine. 

        #Convert the ID\s into a list to be processed,
        # even if a single item. This allows me to Delete one, or more instead
        # of just one, or all.
        if len(args.msg_id) == 1:
            _msg_id: str = [args.msg_id[0].upper()]
        else:
           _msg_id = [_id.upper() for _id in args.msg_id]   

        # only show option 3, and 4 if "all" was entered. 
        # Option 3 is only really viable if an ALL action is eneterd so 
        # Adjust the menu and match case accordingly.
        print(f'\n{BLUET}How do you want to proceed for{ENDC} "{", ".join(_msg_id)}"?')
        print(f'\n{BLUET}1{ENDC}. Delete only from database.')
        print(f'{BLUET}2{ENDC}. Delete from database and from scheduler.')
        if _msg_id[0] =='ALL':
            print(f'{BLUET}3{ENDC}. Delete sent\expired messages.')
            print(f'{BLUET}4{ENDC}. Purge batch directory of all files.')        
            print(f'{BLUET}5{ENDC}. Exit')
        else:          
            print(f'{BLUET}3{ENDC}. Exit')

        choice = input('\nChoice: ')
        match choice: 
            case "1":
                self.__delete_from_database(_msg_id)      
                # eidt any group list entries.
                self.__edit_group_members_lists(_msg_id)
            case "2":
                self.__delete_from_database(_msg_id)                
                self.__delete_from_task_scheduler(_msg_id)
                # eidt any group list entries.
                self.__edit_group_members_lists(_msg_id)
            case "3":
                if _msg_id[0] == 'ALL': self.__delete_executed_messages()
                else: print('Good-Bye')    
            case "4":
                if _msg_id[0] == 'ALL': self.__purge_batch_directory()       
                else: print('Good-Bye')
            case "5":
                if _msg_id[0] == 'ALL': print('Good-Bye') 
                else: print(f'{YELLT}Invalid Choice.{ENDC}')                                   
            case _:
                print(f'{YELLT}Invalid Choice.{ENDC}')
#-------------------------------------------------------------------------------------------------------------------------------------------           
    def view(self, args: object) -> None:
        """Prints out the info in the json about the messages one at a time, or all. """
 
        truncate: bool = False
        # enables this method to be called with a value from inside the application
        # and not just from the command line.      
        try:
           _msg_id: str = args.msg_id
           if args.truncate: truncate = True
        except:
            _msg_id = args 

        found:    bool = False
        messages: list[list[str]] = load_data(DB) 

        if len(messages) < 1: 
            print(f'\n{YELLT}No messages to view{ENDC}.')
            return

        if _msg_id.lower() == 'all':
            if truncate:
                messages = trunc_all_messages(messages)    

            messages_header.extend(messages)
            print('\n'+tabulate(messages_header, headers='firstrow'))
        else:
            for msg in messages:
                if _msg_id.upper() == msg[ID]:
                    if truncate:
                        msg = trunc_message(msg)

                    messages_header.append(msg)
                    print('\n'+tabulate(messages_header, headers='firstrow'))
                    found = True
            if not found: 
                print(f"\n{YELLT}{wrap_quotes(_msg_id.upper())}{ENDC} does not exist.")
#-------------------------------------------------------------------------------------------------------------------------------------------
    def recover_tasks(self, args: object) -> None:
        """ 
        In case any, or all tasks have been deleted form the task scheduler this method will recover them and
        reschedule with WTS. There must still be a message_db.json file to work from.
        User may recover one message, more than one message, or all messages.

        _msg_ids: str -- The message(s) to be recovered. If _msg_ids[0] == ALL then all will be recovered.
        """
        _msg_ids:           list[str] = [msg.upper() for msg in args.msg_id]

        messages:     list[list[str]] = load_data(DB)
        recover_messages:   list[str] = []
        living_batch_files: list[str] = get_living_batch_files()

        if _msg_ids[0]  == 'ALL':
            recover_messages = messages[:]
        else:
            recover_messages = [msg for msg in messages if msg[ID] in _msg_ids]                  

        for msg in recover_messages:
            print(f'{YELLIT}Recovering Message{ENDC}: {BLUET}{msg[ID]}{ENDC}')
            self.__recover_task(msg, living_batch_files)
            # take some time not sure how it will work balls out.
            sleep(1.5)
#-------------------------------------------------------------------------------------------------------------------------------------------
    def rerun_message(self, args: object) -> None:
        '''
        GIven a messgage id, If the task has previously expired, set the -sd to equal to the next day
        or the date given.
        '''
        start_date: str
        msg_id: str = args.msg_id.upper()

        # see what date they are going with and allow short date 
        if args.date: 
            start_date = eval_date(args.date)
        else:
            start_date = get_time_date("tomorrows_date")
        
        self.__rerun_message(msg_id, start_date)

    
#-------------------------------------------------------------------------------------------------------------------------------------------
    def control_responder(self, args: object) -> None:
        '''
        Launches the sister application that monitors emails to be stopped
        Or sends a command to kill the process
        '''
        command: str = [executable, RESPONDER]

        def run_responder():
            # Kind of uncharted territory for me but this seems to work.
            # Have to assume its a running and just say it is.
            print(f"\n{BLUET}Responder launched... Do not close the command prompt until you wish to stop the application.{ENDC}.\n"
                   'You can continue using this terminal as usual.')
            startfile(RESPONDER)            

        if args.stop :
            self.__stop_responder(RESPONDER_LOG, args.debug)

        if args.start:
            run_responder()
            



##================================================================================================================================
# PRIVATE METHODS 
#=================================================================================================================================

#-------------------------------------------------------------------------------------------------------------------------------------------
    def __check_enable(self, _msg_id: str) -> bool:
        '''
        Message may be disabled. Check the DB to see, and if it is promptbefore enabling.
        '''
        status: str = get_message_from_disk(_msg_id)[STATUS]
        if status == 'Disabled':
            if warn_or_continue(
                f'\n{YELLT}MESSAGE{ENDC}: "{BLUET}{_msg_id}{ENDC}" is {YELLT}Disabled{ENDC}. \nEnable it before modification?'
                '',
                warn=False
            ):
                self.enable_task(_msg_id)
                
#-------------------------------------------------------------------------------------------------------------------------------------------
    def __is_group_message(self, _msg_id: str) -> bool:
        '''
        True if this message is a group message.
        Reads the contents of its batch file to see where its going
        based on the size of the instructions.
        '''
        bat_file: str = os_join(MAIN_DIR, BAT_DIR, _msg_id+'.bat')

        with open(bat_file, 'r') as file:
            file_data: str  = file.readline()
        
        file_data: list[str] = file_data.split()
        
        if len(file_data) == 8: return True

        return False
        
#-------------------------------------------------------------------------------------------------------------------------------------------
    def __stop_responder(self, log_: str, debug=False) -> None:
        '''
        Stops the responder by killing the process.
        '''
        pid: str = self.__extract_pid(log_)
        if pid:
           if not debug:  
                Popen(f'taskkill /F /PID {pid}', shell=False, stdout=PIPE, stderr=DEVNULL)
                # Assume success...
                print(f'{YELLT}SUCCESS{ENDC}: The process with PID {BLUET}{pid}{ENDC} was terminated.')
           else:
                #Let the procedure show its output
                Popen(f'taskkill /F /PID {pid}')           

#-------------------------------------------------------------------------------------------------------------------------------------------
    def __extract_pid(self, log_: str) -> str|None:
        '''
        Opens the responder log and pulls out the PID
        '''
        target: str = r'(PID: \d*)'

        if os_exists(log_):
            with open(log_, 'r') as f:
              lines: list[str] = f.readlines()

            # current PID will always be the last one
            pid: str = findall(target, ''.join(lines))[-1]  
            # Get just the number
            pid = pid.split()[1]
            return pid  
        else:
            print(f'{YELLT}Unable to locate{ENDC} {BLUET}{log_}{ENDC}.')
        return 

#-------------------------------------------------------------------------------------------------------------------------------------------
    def __rerun_message(self, 
        _msg_id: str, 
        _start_date: str,
        _user_id: str=None,
        _pword: str=None) -> None:
        '''
        Sets the curent message task to the new start date.    
        '''

        # search for the ID to make sure it exists.
        if not search_ID(_msg_id) : return

        messages: list[list[str]] = load_data(DB)
        command: list[str|int] = [
            'schtasks.exe', 
            '/CHANGE', 
            '/TN', 
            _msg_id
        ]       
        # See if the user has credintials in settings
        ext = get_credentials(_user_id, _pword) 
        if ext: command.extend(ext) 
       
        command.extend(['/sd', _start_date])     
        return_code: int = run(command).returncode                    
        if return_code == SUCCESS:
            # update this message for the DB
            for msg in messages:
                if msg[ID] == _msg_id:
                   msg[SEND_TIME_DATE] = msg[SEND_TIME_DATE].split('\n')[0] + '\n' + _start_date
                   msg[END_DATE] = msg[END_DATE].split('\n')[0] + '\n' + _start_date
                   msg[STATUS] = 'Rewind'
                   
                   write_data(messages, DB)  
                   print(f'{YELLT}Message{ENDC}: "{BLUET}{_msg_id}{ENDC}" set to rerun on {BLUET}{_start_date}{ENDC}.')
                   # show results
                   self.view(_msg_id)


#-------------------------------------------------------------------------------------------------------------------------------------------
    def __recover_task(self, _msg: list[str], all_bat_files: list[str])-> None:
        """ 
        Will recover one message that was deleted form the WTS.

        This method relies on the message_db.json  file to exist in order to recover deleted schedules.
        If message_db.json was deleted as well the backup may be used once it has been reinstated. 
        The associated batch file does not have to exist, it will be respawned from the information 
        found in the the messsage db if it does not exist.
        """
        batch_dir:       str = os_join(MAIN_DIR, BAT_DIR)
        create_batch:   bool = False
        this_batch_file: str = os_join(batch_dir, _msg[ID]+'.bat')
        send_time:       str = _msg[SEND_TIME_DATE].split('\n')[0]
        send_date:       str = _msg[SEND_TIME_DATE].split('\n')[1]
        msg_id:          str = _msg[ID]

        bat_path: str
        bat_command: str
        frequency: str
        day: str
        end_date: str
        end_time: str
      
        mo: str = get_digit(_msg[FREQUENCY], 'EVERY')  
        frequency, day = get_actual_frequency(_msg[FREQUENCY])      
        end_time, end_date = get_end_timedate(_msg[END_DATE])

        # will not need an end_time if its once, if you use and end_time with once it makes the task fire on 10m intervals.
        if frequency == 'once': end_time = None 
        if end_time == '00:00': end_time = None # false End_time, used for terminal display ONly, Do not schedule.        
        
        if this_batch_file not in all_bat_files: 
            # batch wasn't found
            bat_path, bat_command = create_batch_path_command( 
                clean_message(_msg[MESSAGE]),
                _msg[ID],
                _msg[DESTINATION]
            )            
            create_batch = True
        
        # schedule the task  
        return_code: int = self.__schedule_task(
            send_time,
            send_date,
            msg_id,
            this_batch_file,
            end_date,
            _frequency_sched=frequency,
            _day_of_week_sched=day,
            _day_of_month_sched=day,
            _mo=mo,
            _end_time=end_time
        )
        
        if return_code == SUCCESS:
            if create_batch:
                create_batch_file(bat_path, bat_command)

#-------------------------------------------------------------------------------------------------------------------------------------------
    def __add_msgid_to_contacts_list(self, _msg_id: str, _destination: str) -> None:
        '''
        adds the message ID to the list of every contact in the group /destinatiin.
        '''        
        destination: str

        contacts_info: list[list[str|list[str]]] = load_data(CONTACTS_DB)
        if _destination is None:
            destination = get_message_from_disk(_msg_id)[DESTINATION]
        else:
            destination = _destination

        for contact in contacts_info:
            if contact[GROUP_NAME] == destination.upper():
                contact[MSG_LIST].append(_msg_id)
                write_data(contacts_info, CONTACTS_DB)        


#-------------------------------------------------------------------------------------------------------------------------------------------
    def __set_for_hour_minute(self, _freq: str, _mo: str) -> str:
        """ evaluate _frequency and format output for HOUR Minute"""
        format_interval: str = ""
        if _freq in ['hourly', 'minute']:
            if (_freq == 'hourly'):
                format_interval =  'EVERY ' +_mo + " HOURS"  
            if (_freq == 'minute'):                         
                format_interval = 'EVERY ' + _mo + ' MINS'
        else:
            format_interval = _freq  
          
        return format_interval
#-------------------------------------------------------------------------------------------------------------------------------------------
    def __check_args(self, 
        _freq: str, 
        _duration: str|None, 
        _mo: str|None, 
        _dow: str|None, 
        _dom: str|None,
        _end_date: str|None,
        _start_date: str|None
        ) -> bool:
        """ try to catch anything that dont jive with what is expected by schtasks 
            The function will report on all bad options
        """
        res: bool = False

        if _freq in ['hourly', 'minute'] and _duration is None:
            print(f'The option {YELLT}-du{ENDC} | {YELLT}--duration{ENDC} must be in the time format. <HH:MM>')
            res = True

        # Make sure duration is in the correct time format and it follows the rules
        if _duration is not None and _freq is not None:
            if not validate_duration(_duration, _freq, _mo, _start_date, _end_date): 
                res = True           

        # not hour minute with duration        
        if _freq not in ['hourly', 'minute'] and _duration is not None:
            print(f'You can only use the option {YELLT}-du{ENDC} with {BLUET}HOURLY{ENDC} or {BLUET}MINUTE{ENDC}.')
            res = True
        #Hour minute without a modifier
        if _freq in ['hourly', 'minute'] and _mo is  None:
            print(f'You must use option {YELLT}-mo{ENDC} with {BLUET}HOURLY{ENDC} or {BLUET}MINUTE{ENDC}.')
            res = True   
        # no specified day when using weekly
        if _freq == 'weekly' and _dow is None:
            print(f'You must use option {YELLT}-dow{ENDC} with {BLUET}WEEKLY{ENDC}.')
            res = True
        # no specified day of month with monthly
        if _freq == 'monthly' and _dom is None:
            print(f'You must use option {YELLT}-dom{ENDC} with {BLUET}MONTHLY{ENDC}.')
            res = True

        return res
#-------------------------------------------------------------------------------------------------------------------------------------------
    def __send_text(self, message_: str, dest_: list, settings_) -> None:
        """ Sends a text message to one contact. Only MMS is used because
            SMS will create a new text after 61 chars. 
        Arguments:
            message -- Message
            dest -- The destination
            settings -- The destinations credintials, phone number and ptovider info.
        """
        sender_email: str
        email_password: str
        message_gateway: str = "mms"

        # replace "break instruction" with '\n' so there is an actual line break after the message
        # and distinguish it from the stop message. CANNOT  use inline breaks in abatch file, this 
        # Does the trick.
        message_ = message_.replace(LINE_BREAK, '\n')
        
        # decide if this provider supports mms, or if the mms and sms are
        # under the same value. 
        if (not PROVIDERS.get(dest_[PROVIDER]).get('mms_support')):
            message_gateway = "sms" 

        sender_email, email_password = settings_["sender_credentials"]
        #If the mms gateway and sms are the same, default to the sms gateway.
        receiver_email: str = f'{dest_[PHONE_NUMBER]}@{PROVIDERS.get(dest_[PROVIDER]).get(message_gateway, PROVIDERS.get(dest_[PROVIDER]).get("sms"))}'
       
        with SMTP_SSL(settings_["smtp_server"], settings_["smtp_port"], context=create_default_context()) as email:
           email.login(sender_email, email_password)
           email.sendmail(sender_email, receiver_email, message_)
#-------------------------------------------------------------------------------------------------------------------------------------------
# Get Message Status
    def __get_status(self, _msg_id: str) -> str:
        """Checks the message dB and gets the status of the message
        Arguments:
            _msg_id -- The message in question
        Returns:
            Message status if a message is alive, "not found" if not.
        """
        messages: list[list[str]] = load_data(DB)
        found: bool = False
        res: str 

        for msg in messages:
            if msg[ID] == _msg_id:
               found = True
               res = msg[STATUS] 

        if not found:
            res = 'not found'

        return res     
#-------------------------------------------------------------------------------------------------------------------------------------------
# CHANGE MESSAGE STATUS
    def __change_message_status(self, _msg_id: str, _status: str) -> None:
        """Changes the status of a message used by disable, enable"""
        messages: list[list[str]] = load_data(DB)
        for msg in messages:
            if msg[ID] == _msg_id:
                msg[STATUS] = _status

        write_data(messages, DB)
#------------------------------------------------------------------------------------------------------------------------------------------- 
    def __check_and_update_status(self) -> None:
        """Checks the send time in the database of each message to determine if it has been
           sent. And checks the End Date to see if a recurring message has ended. Updates
           The message status accordingly.
        """        
        messages: list[list[str]] = load_data(DB)

        if (len(messages) != 0):
            for msg in messages:
                # check if the status has been altered by Disable|Enable
                # if it says Enable, check the end_date and reset
                # if it says Disabled, break the loop to maintain it.
                if (msg[STATUS] == "Disabled"):
                    continue

                elif msg[STATUS] == "Enabled" :
                    if ( msg[END_DATE] == "Recurring" ):
                        msg[STATUS] = "Started"
                    else:
                        msg[STATUS] = "Ready"    

                start_time: str = msg[SEND_TIME_DATE].split("\n")[0]
                start_date: str = msg[SEND_TIME_DATE].split("\n")[1]
                     
                if (msg[END_DATE] != "Recurring" ):
                    end_time: str = msg[END_DATE].split("\n")[0]
                    end_date: str = msg[END_DATE].split("\n")[1]  

                # started?   
                if (not valid_schedule_time(start_time, start_date, output=False)):  
                    # if its not ONCE it has started.

                    if (msg[FREQUENCY] == 'ONCE'):
                        msg[STATUS] = "Sent"    
                    else:
                        # was this a modified message?
                        if msg[STATUS] == "Started(m)":
                            msg[STATUS] = "Started(m)"
                        else:    
                            msg[STATUS] = "Started"

                    if(
                        'EVERY' in msg[FREQUENCY] or 
                        'HOUR'  in msg[FREQUENCY]   
                      ):   
                        msg[STATUS] = "Started"     
                      
                # ended?
                if (not valid_schedule_time(end_time, end_date, output=False) and msg[STATUS] != 'Disabled'): 
                     if msg[STATUS] in ["Started", 'Started(m)', 'Rewind', 'Modified'] :
                        msg[STATUS] = "Expired"

                     if msg[FREQUENCY] in ['DAILY', "WEEKLY", 'MONTHLY']:
                         msg[STATUS] == 'Expired'
                     
                     # If this message is associated with  group and it has expired, 
                     # remove it from all members lists
                     self.__edit_group_members_lists(msg[ID])

            write_data(messages,DB)

#------------------------------------------------------------------------------------------------------------------------------------------- 
    
    def __edit_group_members_lists(self, _msg_id: str) -> None:
        '''
        if the msg is apart of a group list then delete the msgID from all lists
        it has expired.
        '''
        contact_info: list[list[str]] = load_data(CONTACTS_DB)
        #This message id will only be used once, there for should be deleted from any lists its on.
        for contact in contact_info:
            if _msg_id in contact[MSG_LIST]:
                contact[MSG_LIST].remove(_msg_id)
                write_data(contact_info,CONTACTS_DB)

#------------------------------------------------------------------------------------------------------------------------------------------- 
        
##===================================================================================================
# new_msg HELPER MEthods  
##===================================================================================================

    def __add_msg_database(self,  
         msg_id: str, 
         msg: str,
         destination: str,  
         time_date: str,
         frequency: str,
         end_date: str,
         dow: str=None,
         dom: str=None
        ) -> None:

        """Adds a new message and all its details to the json dataBase.

        Arguments:
            msg_id --      Message Identifier.
            msg --         Message.
            destination -- To Whom it is being sent.
            time_date --   The time and date to send.
            frequency --   How often it will occur.
            end_date --    When the messages will end.
        """
        status: str = "Ready"                                      # New message is always ready
        time_task_created: str = get_time_date('time_date_break')  # Created on:   
        messages: list[list[str]] = load_data(DB)                  # Current messages
        
        # do we need to append the day for the frequency?
        if dow is not None:
            frequency = frequency + '\n' + dow.upper()
        if dom is not None:
            frequency = frequency + '\n' + dom.upper()    

        # set up lists to save the data     
        new_msg: list[str] = [
            msg_id, 
            msg, 
            destination,
            time_date, 
            end_date, 
            time_task_created, 
            frequency, 
            status
        ]        
        messages.append(new_msg)   
        write_data(messages, DB)
#-------------------------------------------------------------------------------------------------------------------------------------------
    def __schedule_task(self,
          _start_time: str, 
          _start_date: str,  
          _uid: str,
          _bat_path: str,
          _end_date: str,
          _frequency_sched: str=None,
          _day_of_week_sched: str=None,
          _day_of_month_sched: str=None,
          _mo: str=None,
          _duration: str=None,
          _end_time: str=None
          ) -> None:
        """
            Schedules a new task with Windows Task Scheduler. 
        """

        #adjust _frequency_sched for hourly or minute 
        if 'hour' in _frequency_sched.lower():
            _frequency_sched = 'hourly'
        if 'mins' in _frequency_sched.lower():
           _frequency_sched = 'minute'
        
        # all necesart commands
        command: list[str]= [
            "schtasks.exe", 
            "/CREATE", 
            "/SC", _frequency_sched, 
            "/TN", _uid, 
            "/TR", _bat_path, 
            "/ST", _start_time, 
            "/SD", _start_date
        ]    

        extension: list[str] 

        #Extend the command list according to options. 
        if (_duration):
            # should i allow user to pick up after stopping on one day?
            # /K will let it start up again on another day after it stopped the previous day'/K
            # only allow the user to extend the frequency for 3 days...
            # check to make sure -ed is not more than 3 days in the future
            # Need to code the days tester and then apply it here.
            # Nope.. this is likely just too much

            # business as usual
            extension = ['/DU', _duration]
            command.extend(extension)                    

        if (_mo):
            extension = ['/MO', _mo]
            command.extend(extension)        
        
        if ( 
            _end_date != "Recurring" and 
            _frequency_sched.lower() != 'once' and 
            _end_date is not None and _duration is None
           ):              
            extension = ['/ED', _end_date]
            command.extend(extension)

        if( _frequency_sched.lower() == 'weekly'):
            extension = ['/D', _day_of_week_sched]
            command.extend(extension)

        if (_frequency_sched.lower() == 'monthly'):
            extension = ['/D', _day_of_month_sched]
            command.extend(extension)
        
        return_code = run(command).returncode                
        if (return_code == SUCCESS):
           self.__set_WakeToRun(_uid)

        return return_code
#-------------------------------------------------------------------------------------------------------------------------------------------
    def __set_WakeToRun(self, task_name: str) -> None:
        """
        generates and runs a powershell script to set the WakeToRun Setting to true. Cannot access this
        setting using schtasks.exe, and accesing These 2 PS functions was problematic. So I just run a script instead.
        I know there is a way to pass the data from a variable once set by the first cmdlet to the call to the next.
        But I get PS errors saying that $settings is null, so this works well enough.
        """
        
        code: list[str] = [
            '$settings = New-ScheduledTaskSettingsSet -WakeToRun\n',
            'Set-ScheduledTask -TaskName ',
             task_name, 
            ' -Settings $settings | Out-Null'
            ]            

        script_path: str  = os_join(MAIN_DIR, task_name+'.ps1')

        command: list[str] = [
            'powershell.exe',
            '-ExecutionPolicy',
            'Unrestricted',
             script_path 
            ]

        with open(script_path, 'w') as script:
            script.write("".join(code))

        return_code: int = run(command).returncode   

        if return_code == SUCCESS:     
            try:
                os_remove(script_path)
            except Exception as er:        
                print(f'{YELLT}ERROR:{ENDC} in __setWakeToRun\n', er)
#-------------------------------------------------------------------------------------------------------------------------------------------
    def __get_end_time_date(self,
        _frequency: str, 
        _time_to_text: str, 
        _date_to_text: str, 
        _end_date: str,
        _duration: str|None
        )-> str:

        end_time_date: str
        # Add the duration to the starting time
        # Only need end_time if usinfg duration
        
        """Calculates the the time the messages will be stopped on. This is promarily
        done for the information to be displayed from the database.

        Arguments:
            _frequency -- The fequency at which a message is to be sent
            _time_to_text -- THe time a message is set for
            _date_to_text -- The date to send
            _end_date -- The date to end            

        Returns:
            Returns a formatted time and date string of when the message terminates.
        """
        #Monthly daily weekly
        # will still be ONCE even if its minute or hour
        if _frequency == "once" : 
            # end_time_date is after execution same date
            end_time_date = _time_to_text + '\n' + _date_to_text

        # Not ONCE and did not specify a date to end
        if _frequency != "once" and _end_date is None:
            end_time_date = "\nRecurring"    
        
        #no end date, but there is a duration. add the calculated end_time

        # daily, weeekly, monthly
        """if _frequency != "once" and _end_date is None and _duration is  None:
            end_time: str = calculate_end_time(_date_to_text, _time_to_text, _duration)
            end_time_date = end_time + '\n' + _date_to_text  """
            
        # end on endDate only, to 00:00
        # This does not need to be displaed since the scheduler will default to 00:00
        # Im just doing this to have a time placeholder for terminal viewing
        if _frequency != "once" and _end_date is not None:
            end_time_date = '00:00\n' + _end_date

        if 'HOUR' in _frequency and _duration is not None and _end_date is None:
             end_time: str = calculate_end_time(_date_to_text, _time_to_text, _duration)
             end_time_date = end_time + '\n' + _date_to_text

        if 'MIN' in _frequency and _duration is not None and _end_date is None:
             end_time: str = calculate_end_time(_date_to_text, _time_to_text, _duration)
             end_time_date = end_time + '\n' + _date_to_text

        return end_time_date
#-------------------------------------------------------------------------------------------------------------------------------------------
    def __validate_and_format_destination(self, 
        _contacts: list[list[str]], 
        _destination: str|bool, 
        _dest_type: int
        )-> bool | str:

        """"
        Checks to make sure a Contact or GROUP exists and returns them 
        formattted accordingly or returns False if not.
        """
        # Given the _dest_type, decide how to format the destinaion to be saved and later ran by send.  
        if _dest_type == DEFAULT_CONTACT:   
            _destination = _contacts[DEFAULT_CONTACT][NAME]

        elif _dest_type == CONTACT:  
            if contact_exists(_contacts, _destination):
                _destination = _destination.title()
            else:
                print(f"Contact: {BLUET}{_destination}{ENDC}{YELLT} does not exist.{ENDC}")    
                _destination = False

        elif _dest_type == GROUP: 
            if group_exists(_contacts, _destination,output=False):
                _destination = _destination.upper()
            else:
                print(f"Group: {BLUET}{_destination}{ENDC}{YELLT} does not exist.{ENDC}")    
                _destination = False

        return _destination
##===================================================================================================
# END  new_msg HELPER MEthods  
##===================================================================================================


##=================================================================================================
# TASK AND MESSAGE  MAINTENENCE
##=================================================================================================
    def __purge_batch_directory(self) -> None:
        """Deletes all batch files from the batch directory."""
        bat_files: list = get_living_batch_files()

        if warn_or_continue(
                 'All files will be deleted from: ' 
                f'{YELLT}{os_join(MAIN_DIR, BAT_DIR)}{ENDC}.'
            ):             
            for file in bat_files:
                os_remove(file)
                print(f'\n{YELLT}Removed:{ENDC} {file}.')
        else:
            print(f"\n{YELLT}Delete Aborted.{ENDC}")
#-------------------------------------------------------------------------------------------------------------------------------------------
    def __delete_from_database(self, _msg_ids: list[str]) -> None:
        """
        Deletes messages from the json database only
        """
        messages:  list[list[str]] = load_data(DB)

        all_ids_in_db:   list[str] = [msg[ID].upper() for msg in messages]
        not_found:            list = []
        to_delete:       list[str] = []   
        
        s: str
        verb: str

        _msg_ids = [msg.upper() for msg in _msg_ids]

        if _msg_ids[0]  == 'ALL':
            if warn_or_continue(
                    f'You are about to delete ALL messages from the database.'
                ):
                del messages[:len(messages)]
                print(f'\n{BLUET}Database{ENDC} {YELLT}deleted.{ENDC}')
            else:
                print(f'\n{YELLT}Delete Aborted.{ENDC}')  
                return
        else:   
            for _id in _msg_ids:
                if _id in all_ids_in_db:
                    to_delete.append(_id)
                else:
                    not_found.append(_id)
           
            for message in messages:
                if message[ID] in to_delete:
                   messages.remove(message)             
        
        write_data(messages, DB)

        if to_delete:
            s, verb = format_expression(to_delete) 
            print(f"\nDELETED: {BLUET}{', '.join(to_delete)}{ENDC} message{s} from messages.")

        if not_found:
            s, verb = format_expression(not_found) 
            print(f'Message{s}: {BLUET}{", ".join(not_found)}{ENDC} {verb} {YELLT}not found{ENDC} in messages.\n')             
#-------------------------------------------------------------------------------------------------------------------------------------------
    def __delete_from_task_scheduler(self, _msg_ids: list[str]) -> None:
        '''Deletes one or more messages from the task scheduler, and the .bat
        files associated.
        Method expects a list to be passed in always.'''        
        sched_tasks: list[str] = get_scheduled_tasks()
        not_found_list:   list = []
        deleted:     list[str] = []
        to_delete:   list[str]
        s: str
        verb: str
        
        if (_msg_ids[0]  == 'ALL'):
            # Warn about full delete
            if  warn_or_continue(
                    'You are about to delete all the Tasks to send messages \n' 
                    'from the scheduler, and all the associated batch programs.'
                ):
                to_delete = sched_tasks[:] 
            else:
                print('Delete aborted')    
                return
        else: to_delete = [message.upper() for message in _msg_ids]
           
        for msg_id in to_delete:
            if (msg_id in sched_tasks):
                self.__delete_task_and_batch(msg_id)
                deleted.append(msg_id)                
            else:           
                not_found_list.append(msg_id) 

        if (deleted):
            if  not _msg_ids[0] == 'ALL':
                s, verb = format_expression(deleted)
                pronoun2: str = 'their ' if s else ''
                pronoun: str = "it's" if pronoun2 != 'their ' else 'all' 
                print(f"\nDELETED: {BLUET}{', '.join(deleted)}{ENDC} and {pronoun} {pronoun2}associated batch file{s} from {BLUET}Task Scheduler{ENDC}.")    
            else:
                # rather than displaying each id for all ids, just display 'ALL', common sense approach.
                print(f"\nDELETED: {BLUET}ALL{ENDC} tasks and ALL associated batch files from {BLUET}Task Scheduler{ENDC}.")  

        if (not_found_list):
            s, verb = format_expression(not_found_list)
            print(f'TASK{s.upper()}: {BLUET}{", ".join(not_found_list)}{ENDC} {verb} {YELLT}not found{ENDC} in the scheduled tasks.')
#-------------------------------------------------------------------------------------------------------------------------------------------                          
    def __delete_task_and_batch(self, _msg_id: str)-> None:
        """
        deletes a single task and its associated batch file.
        Opted to use a PS Script instead of the schtasks api 
        Because the API will notify on every action... I just wanted
        To do that myself.
        """ 
               
        command: list[str] = [
            'powershell.exe',
            'Unregister-ScheduledTask -TaskName', 
            _msg_id, 
            '-Confirm:$false'
        ] 
        bat_path: str = os_join(MAIN_DIR, BAT_DIR, _msg_id+'.bat')

        return_code: int = run(command).returncode
        if return_code == SUCCESS:
            if os_exists(bat_path):
                os_remove(bat_path)  
        else:
            print(f'{YELLT}ERROR{ENDC}: Deleting {_msg_id} from the Task Scheduler.\n'
                   'Likely the task does not exist.')        
#-------------------------------------------------------------------------------------------------------------------------------------------
    def __delete_executed_messages(self) -> None:
        """
        Deletes all messages form the scheduler that have been previously executed,
        and the .bat files associated.
        """     
        messages: list[list[str]] = load_data(DB)   
        found: bool = False
        if warn_or_continue(
            f'{YELLT}You are about to delete all the previously sent messages in message_db.json{ENDC}.'
            ):
            for message in messages:
                if message[STATUS] in ['Sent', 'Expired']:
                # These routines expect a list to be pased in.   
                    self.__delete_from_database( [message[ID]] )
                    self.__delete_from_task_scheduler( [message[ID]] )
                    found =  True   

            if not found:            
                print(f"{YELLT}No Expired or Sent messages found{ENDC}.")

    
##=================================================================================================
#  END TASK AND MESSAGE MAINTENENCE 
##=================================================================================================
   