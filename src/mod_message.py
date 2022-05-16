# modify.py

from tabulate import tabulate
from constants import(
    SETTINGS_FILE,
    ID,
    DB,
    CONTACT,
    GROUP,
    DEFAULT_CONTACT,
    NAME,
    CONTACTS_DB,
    CREATED,
    MESSAGE,
    DESTINATION,
    SEND_TIME_DATE,
    END_DATE,
    FREQUENCY,
    STATUS,
    ENDC,
    BLUET,
    YELLIT,
    YELLT
)
from utility import(
    contact_exists,
    group_exists,
    load_data,
    insert_breaks_and_sep,
    messages_header,
    valid_time,
    valid_future_date,
    get_default_contact,
    clean_message,
    create_batch_path_command,
    create_batch_file,
    validate_duration,
    calculate_end_time,
    get_digit,
    get_duration,
    get_credentials
)
# What Can be modified:
# ----------------------------------------------------------------------
#  Destination
#  Message
#  Start Date
#  End Date
#  Start time
#
#  Message Types that can be modified and how:
#
# Can modify Message and destiation in the same command as well as:
#
#  HOURLY MINUTE:
#    User can modify one of the following, one at a time:
#       Duration
#       Start_date
#       Start_time
#       END_Date
#
#  All Others:
#  [weekly, daily, monthly, once] 
#  (Once can also be considered hourly or minute, HOUR Or MINUTE Taks presedence over ONCE)
#  can be modifed all at once in the same command
#       Start_date
#       Start_time
#       END_Date
#    
#   
# Modify sends the command line Args to create_command_list_validate(). 
# The options are all validated.
# Args are added to a dict to be represent the arguments chosen and 
# A list is compiled from the dict to be used to represent the modified message.
# Display_message_changes() calls the eval functions to create a "Modified"
# message to be displayed in the terminal, along side the original message for approval.
# If it is acceptable the the batch file is rewritten (if needed)
# THe WTS is edited (if needed)
# the changes are written.
# and a command list to send the WTS is created from the Args
# 
#----------------------------------------------------------------------
# Message.modify() 
#     | 
#     |-> create_command_list_validate() 
#     |              |
#     |              |-> validate_destination()
#     |                  validate_time_options()
#     |
#     |-> display_message_changes()
#     |            |
#     |            |-> eval_message_text_changes()
#     |                eval_destination_changes()
##    |                eval_sendtime_date()  
#     |                eval_endtime_date() 
#     |                       |
#     |                       |-> display_for_approval()
#     |-> warn_or_continue()
#               |
#               |-> edit_batchfile()
#               |
#               |-> edit_WTS()
#               |
#               |-> write_data()


def create_command_list_validate(
    _msg_id:  str,
    _start_time: str= None,
    _msg: str=None,
    _destination: str=None,
    _dest_type: int=None, 
    _date_to_text: str=None, 
    _end_date: str=None, 
    _duration: str=None,
    _user_id: str=None,
    _pword: str=None 
) -> tuple[bool, bool, dict[int, str|int], str]:
    """
        given the command line args, create a list of commands to carry out the task modification.
    """    
    freq: str = get_message_from_disk(_msg_id)[FREQUENCY].split('\n')[0] # will always be the first even if nothing to split
    mod: str = get_digit(freq, 'EVERY')

    edit_batch: bool = False
    resume: bool = True
    command: list[str|int] = [
        'schtasks.exe', 
        '/CHANGE', 
        '/TN', 
        _msg_id
    ]
    ext: list[str]
    # used to record the options user wishes to modify
    arg_d: dict[str, str|int] = {}
    arg_d['_msg']          = insert_breaks_and_sep(_msg) if _msg is not None else None
    arg_d["_destination"]  = _destination
    arg_d["_dest_type"]    = _dest_type 
    arg_d["_start_time"]   = _start_time
    arg_d['_date_to_text'] = _date_to_text
    arg_d['_end_date']     = _end_date
    arg_d['_duration']     = _duration
    arg_d['_stop_time']    = None # THis cannot be changed directly, but will need to be altered later
    
    ext = get_credentials(_user_id, _pword) 
    if ext: command.extend(ext) 

    if (not changes_made(arg_d)):
        print(f'{YELLIT}No modifications detected{ENDC}.')
        resume = False        
    
    # Need to validate if the users choices are legal or not. that will stop a lot of chaos down the line.
    # So much validation, should probably have done it all at once?

    if (_msg is not None):
        edit_batch = True 
    
    if (_destination is not None):
        resume, arg_d["_destination"] = validate_destination(_destination, _dest_type)
        edit_batch = True    

    # Refactor all this because I should not be validating like this in two spots
    if not resume: return (resume, edit_batch, arg_d, command)

    resume = validate_time_options(_start_time, _date_to_text, _duration, _end_date, freq, mod)     
    # Decide what is being modified, If its an hourly or minute message
    # it will be handled differetly than the others.
    # If HOUR then only duration, start or end may be edited at once.
    # All others can alter sd, st, and ed at the same time

    if (resume):
        if ('EVERY' in freq): 
            # if doing hour and shit only let them change one at a time
            # duration
            if (_duration is not None):            
                ext = ['/du', _duration]
                command.extend(ext) 

            # start time    
            elif (_start_time is not None):
                ext = ['/st', _start_time]
                command.extend(ext)
               # arg_d['_date_to_text'] = get_message_from_disk(_msg_id)[SEND_TIME_DATE].split('\n')[1] 
                
            # start date     
            elif (_date_to_text is not None):
                ext = ['/sd', _date_to_text]
                command.extend(ext)

               # arg_d['_start_time'] = get_message_from_disk(_msg_id)[SEND_TIME_DATE].split('\n')[0]                    
        else:    
            # Can be one or all of start time, start date, and or enddate
            # date does not change. start time does          
            if (_start_time is not None and _date_to_text is None):               
                ext = ['/st', _start_time]
                command.extend(ext)
                #arg_d['_date_to_text'] = get_message_from_disk(_msg_id)[SEND_TIME_DATE].split('\n')[1]            
        
            # date changes, start time does not
            if (_start_time is None and _date_to_text is not None): 
                ext = ['/sd', _date_to_text]
                command.extend(ext)
               # arg_d['_start_time'] = get_message_from_disk(_msg_id)[SEND_TIME_DATE].split('\n')[0]
                
            #Changed Both Start and date         
            if (_start_time is not None and _date_to_text is not None) :
                # make sure the date is in the future, Time cant really police.        
                ext = ['/st', _start_time, '/sd', _date_to_text]
                command.extend(ext)

            # changing only end time
            if (_end_date is not None ):
                ext = ['/ed', _end_date]   
                command.extend(ext)
                 
    return (resume, edit_batch, arg_d, command)
#-------------------------------------------------------------------------------------------------------------------------------------------
def validate_time_options(_start_time: str ,_start_date: str, _duration: str, _end_date: str, _freq: str, _mod: str) -> bool:
    """  
        validates all times and dates and makes sure the otions entered 
        are valid together.
    """
    res: bool = True    

    only_one: list[str] = [_start_time, _start_date, _duration, _end_date]
    None_cnt: int = 0

    # if you cahnge the start time on a reeating hour or minute then the end time needs to be reflected as well.
    # only let the modification proceed if all the options jive.
    if 'EVERY' in _freq: 
        # only can modify duration, start date, or start time at once with 
        # Hour Minute 
        for el in only_one:
            if el is not None:
                None_cnt += 1

        if None_cnt > 1:
            print(f"\nYou can only modify one option at a time when modifying an {BLUET}HOUR{ENDC} or {BLUET}MINUTE{ENDC} message task.\n"
                  f"\n {YELLIT}Pick one of the following only{ENDC}:\n" 
                  f' <{BLUET}start time{ENDC}> {YELLT}-st{ENDC}|{YELLT}--start_time{ENDC}, '
                  f'<{BLUET}start date{ENDC}> {YELLT}-sd{ENDC}|{YELLT}--start_date{ENDC}, '
                  f'or <{BLUET}duration{ENDC}> {YELLT}-du{ENDC}|{YELLT}--duration{ENDC}.') 
            return False          

        if _end_date is not None:
            print(f"{YELLIT}Can't alter the end_date on a minute or hourly task as of yet WIll\n"
                  f'add hourly and minute tasks that will span days in future versions{ENDC}.')
            return False
        

    # can modify, st, sd, or ed    
    elif _freq == 'ONCE':
        # make sure not messing with duration
        if (_duration is not None): 
            print(f"\nThere is no duration option on a single task thats not {BLUET}HOUR{ENDC} or {BLUET}MINUTE{ENDC}.")
            return False

    # can modify st, sd, and  ed     
    elif _freq in ['DAILY', 'WEEKLY', 'MONTHLY']:
        if _duration is not None:
            print(f"Can't modify duration on a {BLUET}DAILY{ENDC}, {BLUET}WEEKLY{ENDC}, or {BLUET}MONTHLY{ENDC} message task.")
            return False        
    
    #Validate the times that are truthy make sure they are in the future and properly formatted.
    if _start_time is not None:
        if not valid_time(_start_time):
            print(f'\n{YELLIT}Invalid start time{ENDC} Check your time formatting <HH:MM> 24Hr.')
            res = False
    
    #Validate the duration to make sure its accepatable
    if _duration is not None:
        if not validate_duration(_duration, _freq, _mod):
            res = False
            
    if _end_date is not None:
        if not valid_future_date(_end_date):        
            print(f'\n{YELLIT}Invalid end date{ENDC}.')
            res = False        

    if _start_date is not None:
        if not valid_future_date(_start_date):
            print(f'\n{YELLIT}Invalid start date{ENDC}.')
            res = False
    
    return res

#-------------------------------------------------------------------------------------------------------------------------------------------
def validate_destination(_dest: str, _dest_type: int) -> tuple:
    """ 
    Validates the destination
    """
    dest_value: str
    resume: bool = True
    
    if (_dest_type == CONTACT):
        dest_value = _dest.title()
        if (not contact_exists(load_data(CONTACTS_DB), _dest.title())):
            print(f'{YELLIT}There is no Contact by the name{ENDC}: {BLUET}{_dest.title()}{ENDC}.')
            resume = False
    elif (_dest_type == GROUP):
        dest_value = _dest.upper()
        if ( not group_exists(load_data(CONTACTS_DB), _dest.upper(), output=False) ):
            print(f'{YELLIT}There is no GROUP by the name{ENDC}: {BLUET}{_dest.upper()}{ENDC}.')
            resume = False        
    # if destination is not def then they must choose dtype
    elif(_dest not in ['def', 'default'] and  _dest_type == DEFAULT_CONTACT ) :
        print(f"\nIf the destination is changed and its not {YELLIT}'def'{ENDC} or "
                f"{YELLIT}'default'\n{ENDC}then a destination type {YELLIT}-dt{ENDC} must be provided as 1 for Contact \nand 2 for GROUP.")
        resume = False            
        dest_value = ""
    else:
        dest_value = get_default_contact()[NAME]
       

    return resume, dest_value
#-------------------------------------------------------------------------------------------------------------------------------------------

def edit_WTS(d: dict[str, int|str]) -> bool:
    """
        Checks the dict to see if any changes are being made to the task scheduler.
    """
    res: bool = False
    for k,v in d.items():
        if k not in ['_msg', '_destination', '_dest_type']:
            if v is not None:
                res = True
    return res
#-------------------------------------------------------------------------------------------------------------------------------------------
def display_message_changes( 
    _msg: list[str],
    _msg_id: str, 
    _arg_d: dict[str, str|int]
    )-> list[str]:
    """
    Makes a list of all the changes that need to be shown in the table acording to 
    the command line args saved in _arg_d. Also need to maintain the ones that dont change   
    Arguments:
        _msg --THe message being modfied.
                        
        _msg_id -- THe ID of the Message being modified
        _arg_d -- THe dictionary of command line args

    Returns:
        a copy of the message with changes made.
    """
    # THIS CODE NEEDS TO BE REFACTORED:
    # The main problem is with the below functions eval_send and eval_end in particular. 
    # I need to rethink how I do the visual reprensentain of the modified message.
    changes: list[str] = []    
    
    # THe message being modded.
    changes.append(_msg[ID])   

    # the 7 elements of each message in the messages database
    eval_message_text_changes(_arg_d, _msg, changes)
    eval_destination_changes(_arg_d, _msg, changes)
    eval_sendtime_date(_arg_d, _msg, changes)  
    eval_endtime_date(_arg_d, _msg, changes)    
    
    # Maintain these 2
    changes.append(_msg[CREATED])     
    changes.append(_msg[FREQUENCY])

    # status adjusted if needed.
    _msg[STATUS] = get_new_status(_arg_d, _msg)   
    changes.append(_msg[STATUS]) 
    
    display_for_approval(_msg_id, changes)       

    return _msg 
#-------------------------------------------------------------------------------------------------------------------------------------------
def get_new_status(_arg_d: dict, _msg: list[str]) -> str:
    new_status: str = "Ready(m)"

    if (_arg_d['_start_time'] is not None or         
        _arg_d['_duration'] is not None or 
        _arg_d['_end_date'] is not None or 
        _arg_d['_date_to_text'] is not None
       ):
        new_status = "Modified" 

    if _arg_d['_destination'] is not None:
        new_status = "Modified" 
    
    if _arg_d['_msg'] is not None:
        new_status = "Modified"     

    if _msg[STATUS] == 'Started': 
        new_status = "Started(m)"
        
    return new_status
#------------------------------------------------------------------------------------------------------------------------------------------- 
def changes_made( d: dict[str, str|int]) -> bool:
    """
    Evaluates dict to see if any changes were requested.
    """
    None_size: int = len(d)-1
    None_cnt: int = 0        
    for v in d.values():
        if (v == None):
            None_cnt+=1

    if (None_cnt == None_size and d['_dest_type'] == 0):
        return False
    return True  
#-------------------------------------------------------------------------------------------------------------------------------------------
def eval_message_text_changes( d: dict, msg: list, lst: list) -> None:
    """make changes to message in memory and collect them for viewing later.

    Arguments:
        d -- the dict with all user changes
        msg -- a copy of the message from the DB that is being modified
        lst -- change list that is populated and used to display the changes.
    """
    # If the user did not make changes
    if d['_msg'] is not None:
        lst.append(d['_msg'])
        msg[MESSAGE] = d['_msg']
    else:
        lst.append(msg[MESSAGE])
#-------------------------------------------------------------------------------------------------------------------------------------------
def eval_destination_changes(d: dict, msg: list, lst: list)-> None:
    """make changes to message in memory and collect them for viewing later.

    Arguments:
        d -- the dict with all user changes
        msg -- a copy of the message from the DB that is being modified
        lst -- change list that is populated and used to display the changes.
    """
    if(d['_destination'] is not None):
        lst.append(d['_destination']) 
        msg[DESTINATION] = d['_destination']
    else:
        lst.append(msg[DESTINATION])
#-------------------------------------------------------------------------------------------------------------------------------------------
def eval_sendtime_date(d: dict, msg: list, lst: list) -> None:
    """make changes to message in memory and collect them for viewing later.

    Arguments:
        d -- the dict with all user changes
        msg -- a copy of the message from the DB that is being modified
        lst -- change list that is populated and used to display the changes.
    """
    if 'EVERY' in msg[FREQUENCY]:
        # Only worry about 
        old_start_time: str =  get_message_from_disk(msg[ID])[SEND_TIME_DATE].split('\n')[0] #msg[SEND_TIME_DATE].split('\n')[0] #
        old_start_date: str = get_message_from_disk(msg[ID])[SEND_TIME_DATE].split('\n')[1]
        
        # Changed time, not date
        if (d['_start_time']  is not None and 
            d['_date_to_text']  is None ):
            lst.append(d['_start_time'] + '\n' + old_start_date)
            msg[SEND_TIME_DATE] = d['_start_time'] + '\n' + old_start_date
                        
        #changed date not time
        if (d['_start_time']  is None and 
            d['_date_to_text']  is not None ):
            lst.append( old_start_time + '\n' + d['_date_to_text']  )
            msg[SEND_TIME_DATE] = old_start_time + '\n' + d['_date_to_text'] 

        # If both are None:     
        if (d['_start_time']  is None and  d['_date_to_text']  is None):  
           lst.append( old_start_time + '\n' + old_start_date  )
           msg[SEND_TIME_DATE] = old_start_time + '\n' + old_start_date  

    else:
    # if only the time was changed
        if (
            d['_start_time']   is not None and 
            d['_date_to_text'] is None
        ):
            lst.append(d['_start_time'] + '\n' + msg[SEND_TIME_DATE].split('\n')[1].strip())
            msg[SEND_TIME_DATE] = d['_start_time'] + '\n' + msg[SEND_TIME_DATE].split('\n')[1].strip()     
            
        # Only the date changed    
        elif (
            d['_start_time']   is None and 
            d['_date_to_text'] is not None
            ):
            lst.append( msg[SEND_TIME_DATE].split('\n')[0].strip() + '\n' + d['_date_to_text']  )
            msg[SEND_TIME_DATE] = msg[SEND_TIME_DATE].split('\n')[0].strip() + '\n' + d['_date_to_text']         
        #both changed:
        elif (
            d['_start_time']   is not None and 
            d['_date_to_text'] is not None
            ):    
            lst.append(d['_start_time'] + '\n' + d['_date_to_text']  )
            msg[SEND_TIME_DATE] = d['_start_time'] + '\n' + d['_date_to_text']             
        # Neither one changed: 
        elif (
            d['_start_time']   is None  and 
            d['_date_to_text'] is None
            ):
            lst.append(msg[SEND_TIME_DATE])


#-------------------------------------------------------------------------------------------------------------------------------------------
def eval_endtime_date(d: dict, msg: list, lst: list) -> None:
    """make changes to message in memory and collect them for viewing later.

    Arguments:
        d -- the dict with all user changes
        msg -- a copy of the message from the DB that is being modified
        lst -- change list that is populated and used to display the changes.
    """
    # ALL OF THIS NEEDS TO BE REFACTORED, It takes to long to figure out what is going on if a bug is found.

    stop_time:      str = msg[END_DATE].split('\n')[0]
    old_start_time: str = get_message_from_disk(msg[ID])[SEND_TIME_DATE].split('\n')[0] 
    new_start_time: str = msg[SEND_TIME_DATE].split('\n')[0]

    old_start_date: str = get_message_from_disk(msg[ID])[SEND_TIME_DATE].split('\n')[1]
    new_start_date: str = msg[SEND_TIME_DATE].split('\n')[1]

    end_date: str = msg[END_DATE].split('\n')[1]
    

    # Must have different rules for different types of messages
    if 'EVERY' in msg[FREQUENCY]:
        
        if d['_duration'] is not None:
            new_end_time: str = calculate_end_time(
                old_start_date, 
                new_start_time, 
                d['_duration']   
            ) 
            d['_stop_time'] = new_end_time        

        if d['_start_time'] is not None:
            # when the start time changes, need to reflect it on the end time...
            # THere will already be the new start time in the d[] dictionary
            # change the endtime to reflect the new start time + the duration.
            new_end_time: str = calculate_end_time(
                old_start_date, 
                new_start_time, 
                get_duration(old_start_time, stop_time, old_start_date)   
            ) 
            d['_stop_time'] = new_end_time

        if d['_start_time'] is not None and d['_date_to_text'] is None :
            # when the start time changes, need to reflect it on the end time...
            # THere will already be the new start time in the d[] dictionary
            # change the endtime to reflect the new start time + the duration.
            new_end_time: str = calculate_end_time(
                old_start_date, 
                new_start_time, 
                get_duration(old_start_time, stop_time, old_start_date)   
            ) 
            d['_stop_time'] = new_end_time    


        # Start date changed.... reflect in end.
        if d['_date_to_text'] is not None :  
            # make end date be this date
            lst.append(stop_time + '\n' + d['_date_to_text']  )
            msg[END_DATE] = stop_time + '\n' + d['_date_to_text']

        # Date did not change None stopt time untouched
        if d['_date_to_text'] is None and d['_stop_time'] is  None:  
            # make end date be this date
            lst.append(stop_time + '\n' + old_start_date  )
            msg[END_DATE] = stop_time + '\n' + old_start_date
        
        # Stop_Time was effected by eiter duration or stoptime
        if d['_stop_time'] is not None :
            # change the msg to reflect the new stop time and also the terminal
            lst.append(d['_stop_time'] + '\n' + end_date  )
            msg[END_DATE] = d['_stop_time'] + '\n' + end_date

# ALl Recurring messsages
    elif  msg[FREQUENCY] != 'ONCE':
        # All others
        if d['_end_date']  is not None:
            # if no endTime, append 00:00
            if stop_time == '': stop_time = '00:00'
            lst.append(stop_time + '\n' + d['_end_date'])
            msg[END_DATE] = stop_time + '\n' + d['_end_date']
            
        elif  d['_end_date'] is None:    
            lst.append(stop_time + '\n' + end_date)
            msg[END_DATE] = stop_time + '\n' + end_date      


    # If its a single message then THe end time must reflect the start time since changing the endtime
    # On a ONCE meddage will not work. There is no endtime option, but it must be represented in the database. 

    elif  msg[FREQUENCY] == 'ONCE':
        # if the start time changed then make end time == start and exit 
        if d['_start_time']   is not None:
            lst.append(d['_start_time'] + '\n' + end_date)
            msg[END_DATE] = d['_start_time'] + '\n' + end_date
            return  # Just catches the start time to make the end reflet it, get iut, now!

        # if the start date change... and not the end date
        # If the start date changed, reflect the end date
        if d['_date_to_text'] is not None and d['_end_date']  is None:  
            # make end date be this date
            lst.append(stop_time + '\n' + d['_date_to_text']  )
            msg[END_DATE] = stop_time + '\n' + d['_date_to_text'] 

        # All others
        if d['_end_date']  is not None:
            # if no endTime, append 00:00
            if stop_time == '': stop_time = '00:00'
            lst.append(stop_time + '\n' + d['_end_date'])
            msg[END_DATE] = stop_time + '\n' + d['_end_date']
            
        elif  d['_end_date'] is None and d['_date_to_text'] is None:    
            lst.append(stop_time + '\n' + end_date)
            msg[END_DATE] = stop_time + '\n' + end_date
    


#-------------------------------------------------------------------------------------------------------------------------------------------
def eval_frequency_changes(d: dict, msg: list, lst: list) -> None:
    """make changes to message in memory and collect them for viewing later.

    Arguments:
        d -- the dict with all user changes
        msg -- a copy of the message from the DB that is being modified
        lst -- change list that is populated and used to display the changes.
    """ 
    if d['_frequency'] is None:
        lst.append(msg[FREQUENCY])  
    elif d['_frequency'] is not None:
        lst.append(d['_frequency'])
        msg[FREQUENCY] = d['_frequency']         
#-------------------------------------------------------------------------------------------------------------------------------------------
def get_message_from_disk(_msg_id: str) -> list[str]:
    """return the entire message represented by _msg_id""" 
    messages: list[list[str]] = load_data(DB)  
    for message in messages:
        if message[ID] == _msg_id: 
            return message
#-------------------------------------------------------------------------------------------------------------------------------------------
def display_for_approval(_msg_id: str, change_list: list[str]) -> None:
    """gets a message from disk, and displays it Above the one to be changed to"""
    
    print(f"\n{BLUET}CURRENT MESSAGE{ENDC}:")
    messages_header.extend( [get_message_from_disk(_msg_id)] )

    print('\n'+tabulate(messages_header, headers='firstrow'))
    del messages_header[1]
    print(f"\n\n{BLUET}MESSAGE AFTER CHANGES{ENDC}:")
    messages_header.extend([change_list])
    print('\n'+tabulate(messages_header, headers='firstrow'))       
#-------------------------------------------------------------------------------------------------------------------------------------------
def edit_batchfile(_message: str, _msg_id: str, _destination: str, _dest_type: int) -> None:
    """Overwrites the current Batch file with either a new Destination and\or Message"""
    # If the _destination is None It stays the same retreive that data
    # It should have a destination and a dtype.
    # If the destination is the same, then we need to retreive that data
    bat_path: str
    command: str
    
    if _destination is None:
        _destination = get_message_from_disk(_msg_id)[DESTINATION]
    elif _destination in ['def', 'default']:
        _destination = get_default_contact()[NAME]    
    if _message is None:
        _message =  clean_message(get_message_from_disk(_msg_id)[MESSAGE]) 
    
    # fullfill the frequency parameter when creating a new batch file
    freq: str = get_message_from_disk(_msg_id)[FREQUENCY]
    bat_path, command = create_batch_path_command(_message, _msg_id, _destination, freq, _dest_type)
    create_batch_file(bat_path, command)

    
    