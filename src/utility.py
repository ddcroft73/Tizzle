
from datetime import datetime, timedelta
from sys import executable 
from shutil import copyfile
import webbrowser
from  win32com.client import Dispatch
from random import randint
from json import (
    load as json_load,
    dump as json_dump
)
from os.path import exists as os_exists
from constants import *
from os import (
    listdir as os_listdir, 
    remove as os_remove,
    rename as os_rename
)    

# So when printing the table, the header is a different color
contacts_header: list[str] = [
            [
                f"{YELLT}Name:",
                "Phone Number:",
                "Provider:",
                f"Group:{ENDC}"
            ]    
        ]    

messages_header: list[str] = [
            [
                f"{YELLT}ID:",
                "Message:", 
                "Destination:",
                "Send T&D:", 
                "End Date:", 
                "Created:",
                "Frequency:",
                f"Status:{ENDC}"
            ]
        ]     
        
#-------------------------------------------------------------------------------------------------------------------------------------------
def load_data(_fname: str) -> dict or list:
    """
       Opens JSon amd loads the data into a list of lists
       or a dictionary. Used to access 2 different JSon files. 
    """
    try:
        with open(_fname, "r") as file:
            data: list = json_load(file)
    except FileNotFoundError as er:
        print(f'The DataBase:'
              f'\n{YELLT}{_fname.upper()}{ENDC} could not be found.'
              f'\nUse: {GRYT}python{ENDC} {GRNT}stext{ENDC} {TURT}rebuild{ENDC} '
              f'<{VIT}messages{ENDC}|{VIT}contatcs{ENDC}|{VIT}all{ENDC}> to create a new one.')
        exit()
    return data
#-------------------------------------------------------------------------------------------------------------------------------------------
def write_data(_data: list, database: str) -> None:
    """Writes a list of data to a json file Serves as a DataBase.] """
    with open(database, "w") as file:
       json_dump(_data, file, indent=4)
#-------------------------------------------------------------------------------------------------------------------------------------------
def get_unique_id() -> str:
    """
    [Checks the ids already created in the message DB then creates a
    unique message identifier. Ids are nothing more than a means to 
    single out messages. The ID itself means nothing and is completly
    random preceeded by M, for message. ex. M069, M420 etc...]
    
    GOOD FOR 999 messages
    Returns:
        str: [The unique ID]
    """    
    def pad_number(_num: str) -> str:
        """
           pad out string with a 0 to the left.        
        """
        res: str
        if len(_num) == 2:
            res = "0" + _num
        return res
        
    messages: list[list[str]] = load_data(DB)     
    curr_ids: list            = [message[ID] for message in messages]       
    id_exists: bool = True     
    rnd: str
    uid: str

    # loop while creating the unique id in case it encounters one
    # that is already being used. Repeat the process till UID found. 
    while (id_exists): 
        rnd = str(randint(1,999))
        if int(rnd) < 99: 
            uid = "M" + pad_number(rnd) 
        else: 
            uid = "M" + rnd    
        if not uid in curr_ids: 
            id_exists = False

    return uid        

#-------------------------------------------------------------------------------------------------------------------------------------------
def get_time_date(_when: str) -> str:
    """Returns the current time, date or both in string format """
    todays_date_time: datetime = datetime.now()
    res: str 
    match _when:
        case 'time_now':
            #HH:MM:SS
            res = todays_date_time.strftime("%m/%d/%Y %H:%M:%S").split()[1]            
        case 'todays_date':
            #MM/DD/YYYY
            res = todays_date_time.strftime("%m/%d/%Y %H:%M:%S").split()[0]
        case 'time_date':
            res = todays_date_time.strftime("%m/%d/%Y %H:%M:%S")    
        case 'time_date_break':
            # Reurns the time date formatted to fit in the table
            #MM/DD/YYYY
            #     HH:MM
            res = todays_date_time.strftime("%m/%d/%Y\n     %H:%M")
        case 'tomorrows_date':
            # adds a day to the object and returns a string representing that mug
            tom: datetime = todays_date_time + timedelta(days=1)
            res = tom.strftime("%m/%d/%Y %H:%M:%S").split()[0]
                

    return res
    
#-------------------------------------------------------------------------------------------------------------------------------------------
def get_credentials(_user: str, _pass: str) -> list[str]:
    """
        Decides how to get the user credentials for modifications and returns a list extension
        if found.
    """
    settings: dict[str,str|int] = load_data(SETTINGS_FILE)
    ext: list[str] = []

    if _user is None and _pass is None:
        # predefined
        if settings['user'] is not None and settings['pword'] is not None:
            ext = ['/RU', settings['user'], '/RP', settings['pword']]
        else:
            # adding at execution
            pass    
    else:
        # as arguments
        ext = ['/RU', _user, '/RP', _pass]
    return ext
#-------------------------------------------------------------------------------------------------------------------------------------------
def wrap_quotes(_text: str) -> str:
    """wraps text in quotes"""    
    return "\"" + _text + "\""
#-------------------------------------------------------------------------------------------------------------------------------------------
def rebuild_database(args: object) -> None:
    """
    Rebuilds the json format with header info in-case it gets corrupted or is deleted.
    Will delete any data base already populated.
    
    These function(s) are useful for recovering a database from backup if you lost the 
    .json file, and for deleting all the data before a commit.
    """    
    _db: str = args.db.lower()

    db_list: list[str] = []
    all_dbs: list[str] = [
        CONTACTS_DB,
        DB,
        SETTINGS_FILE
    ]

    def strip_filenames_from_list(path: list[str]) -> str:
        '''
        given a list of paths, pulls out the file names and formats them for display,
        '''
        def get_fname(path: list[str]) -> str:
            #Just get the filename only
            return path.split('\\')[-1]

        fname_list: list[str] = []
        for item in path:
            fname_list.append(get_fname(item) ) 
        return f'{YELLT}[ {ENDC}' + f'{BLUET}, {ENDC}'.join(fname_list) + f'{YELLT} ]{ENDC}'

    if _db == 'all':
        db_list = all_dbs[:]
    elif _db == 'contacts':
        db_list.append(CONTACTS_DB)
    elif _db == 'messages':
        db_list.append(DB)
    elif _db == 'settings':
        db_list.append(SETTINGS_FILE)

    if (warn_or_continue(
            f"{YELLT}This command will erase ALL data from{ENDC}: \n" 
            f"{strip_filenames_from_list(db_list)} {YELLIT}if any exists{ENDC}.")
        ):
        try:
            for db in db_list:
                with open(db,'w') as _:
                    write_data([], db)
                print(f"\nNew Database Created in:" f"\n{BLUET}{db}{ENDC}" )    

        except Exception as er:
            print(f"{er}\n{REDT}Error creating {strip_filenames_from_list(db_list)}.{ENDC}")
    else:
        print(f"{YELLT}Rebuild Aborted{ENDC}: {BLUET}{strip_filenames_from_list(db_list)}{ENDC}.")
#-------------------------------------------------------------------------------------------------------------------------------------------
def backup_databases(args: object) -> None:
    """Backs up the databases"""    
    _db: str = args.db.lower()
    s: str = "s" if _db == 'all' else ""

    def generate_backup_path(src_path: str) -> str:
        """replace the extension with .bck"""
        return "".join(src_path.split('.')[0]) + '.bck'

    src_list: list[str] = [
        CONTACTS_DB, 
        DB,
        SETTINGS_FILE
    ]    
    dest_list: list[str] = [
        generate_backup_path(CONTACTS_DB),  
        generate_backup_path(DB), 
        generate_backup_path(SETTINGS_FILE)
    ]
    try:        
        match _db:
            case 'all':
                if _db == 'all':                
                    for index in range(3):
                        copyfile(src_list[index], dest_list[index])   
            case 'contacts':
                copyfile(src_list[0], dest_list[0])                
            case 'messages':
                copyfile(src_list[1], dest_list[1])      
            case 'settings':
                copyfile(src_list[2], dest_list[2])  
            case _:
                print(f'{YELLT}Invalid input{ENDC}.')       
                return

    except Exception as er:
        print(er, f'\n')

    print(f'{YELLT}{_db.title()}{ENDC} {BLUET}database{s} backed up{ENDC}.')        
#-------------------------------------------------------------------------------------------------------------------------------------------
def recover_database(args: object) -> None:
    """ 
    replace the current database(s) with the backups.
    learning with nested functions.
    """
    db: str = args.db.lower()
    found: bool = False
    db_path: str

    dbs_to_recover: list[str] = []
    db_list: list[str] = [
        DB, 
        CONTACTS_DB,
        SETTINGS_FILE
    ]

    def get_fname_only(_path: str) -> str:
        """return the filename and ext from the absolute path"""
        return ''.join(_path.split('\\')[-1])

    def generate_backup_path(_src_path: str) -> str:
        """replace the extension with .bck"""
        return "".join(_src_path.split('.')[0]) + '.bck'
    
    def recover(_db_path: str) -> None:
        """Rename db.bck to db.json only if both exist."""
        if os_exists(_db_path):
            if os_exists(generate_backup_path(_db_path)):
                os_remove(_db_path)
                os_rename(generate_backup_path(_db_path), _db_path)
                return True, _db_path
            else:
                return False, _db_path
        else:
            # Need to rebuild the json and then make the restoration.
            return False, _db_path

    if db == 'all':        
        dbs_to_recover = db_list[:]    
    elif db == 'messages':
        dbs_to_recover.append(db_list[0])    
    elif db == 'contacts':
        dbs_to_recover.append(db_list[1])     
    elif db == 'settings':
        dbs_to_recover.append(db_list[2])      

    # fix one, two , or all
    for this_db in dbs_to_recover:
        found, db_path = recover(this_db)   

        if found:     
            print(f'{YELLIT}{get_fname_only(db_path)}{ENDC} {BLUET}recovered{ENDC}.')
        if not found: 
            print(f'{YELLIT}{get_fname_only(db_path)}{ENDC} {BLUET}not found{ENDC}.') 
            print(f'Rebuild {db_path} using:\n'
                  f'{GRNT}tizz{ENDC} {TURT}rebuild{ENDC} <{VIT}Database{ENDC}> and then run this command again.')       
#------------------------------------------------------------------------------------------------------------------------------------------- 
def lookup_number(args: object) -> None:
    """directs user to site to lookup their Number and find a provider."""

    url: str = 'https://freecarrierlookup.com/'    
    if warn_or_continue(
            f"\n{BLUET}This link will take you to {url} to " 
            f"look up a provider for a given cell number.\nWould " 
            f"you like to open a browser? {ENDC}", False
        ):
        webbrowser.open(url)
#-------------------------------------------------------------------------------------------------------------------------------------------
def warn_or_continue(msg: str, warn: bool=True) -> bool:
    """ 
       much cleaner way to warn user and get input to continue
       or just ask a question.
    """
    warning: str = f'\n{REDT}WARNING{ENDC}: '
    choice: str = f'\n\nContinue ({YELLT}y{ENDC},{YELLT}n{ENDC}) '
    
    res = input(warning + msg + choice) if warn else input(msg + choice)    
    print()
    if res in ['y', 'yes']:
        return True
    else:
        return False                    
#-------------------------------------------------------------------------------------------------------------------------------------------
def contact_exists(_contact_info: list[list[str]], _name: str) -> bool:
    """True if a contact exists."""
    found: bool = False

    for contact in _contact_info:
        if contact[NAME] == _name.title():
            found = True         
            break    

    return found  
#-------------------------------------------------------------------------------------------------------------------------------------------
def phone_exists(_contact_info: list[list[str]], _phone: str) -> bool:
    """True if a phone # is in use."""
    found: bool = False

    for contact in _contact_info:
        if contact[PHONE_NUMBER] == _phone:
            found = True         
            break    

    return found  

#-------------------------------------------------------------------------------------------------------------------------------------------
def get_contact(_contacts: list[list[str]], _contact_name: str) -> list[str] | None:    
    '''
    gets a contacts info or returns None if doesnt exist.
    '''
    for contact in _contacts:
        if contact[NAME] == _contact_name:
            return contact
    return  
#-------------------------------------------------------------------------------------------------------------------------------------------
def group_exists(
    _contact_info: list[list[str]], 
    _group: str, 
    output: bool=True) -> bool:
    """Checks to see if a a group has any contacts already, if so appends to a list and reports
    Or simply checks the existence of a group and returns true or false if output is False"""
    exists:             bool = False
    group_members: list[str] = []  
    
    # check all the group items in the contacts for this group
    for contact in _contact_info:
        if contact[GROUP_NAME] == _group.upper():
            group_members.append(contact[NAME] + '\n')
            exists = True   

    if exists and output:
        print(f"\nThe group {BLUET}{_group.upper()}{ENDC} already exits" 
                f" with The following contacts:")
        print(f'\n{BLUET}{"".join(group_members)}{ENDC}') 
        
    return exists       
#-------------------------------------------------------------------------------------------------------------------------------------------
def get_scheduled_tasks() -> list[str]:
    """Gets a list of all scheduled tasks that concern this app"""
    scheduler = Dispatch('Schedule.Service')
    scheduler.Connect()

    folders: list[str] = [scheduler.GetFolder('\\')]
    folder: str = folders.pop(0)
    tasks: list[str] = list(folder.GetTasks(0))
    task_list: list[str] = [task.Path.replace('\\', '') for task in tasks]
    
    return [
        task for task in task_list 
            if len(task) == 4 
            and task.startswith('M') 
            and task[1:].isdigit()
    ]    
#-------------------------------------------------------------------------------------------------------------------------------------------
def get_default_contact()-> list[str]:
    """Returns the info for the default contact"""
    contacts: list[list[str]] = load_data(CONTACTS_DB) 
    return contacts[DEFAULT_CONTACT]
#-------------------------------------------------------------------------------------------------------------------------------------------
def format_expression(lst: list[str]) -> tuple[str, str]:
    """Not really necessary, but..."""
    if len(lst) > 1:
        s = 's'; verb = 'were'
    else: 
        s = ''; verb = 'was'             
    return (s, verb)    
#-------------------------------------------------------------------------------------------------------------------------------------------
def clean_message(_msg: str) -> str:
    """Removes the line breaks and footer used for displaying in the table in Terminal"""
    footer: str = '\n'+('-'*27)    
    clean_msg: str = _msg.replace(footer, "")
    return clean_msg.replace('\n', '')
#-------------------------------------------------------------------------------------------------------------------------------------------
def insert_breaks_and_sep(_text: str) -> str:
    """ 
        Simple word wrap Inserts a (Line break) into the text message so that when viewed in the terminal
        the entire message can be viewed multiline rather than one line that over extends the table. 
    """
    # inserts a bit of a divider at the end to make it easier to dicern between messages
    # when viewing in terminal    
    
    footer: str = '\n'+('-'*27) 
    cnt: int = 0
    str_list: list[str] = [ch for ch in _text]        
    for index, char in enumerate(str_list):
        cnt+=1
        if cnt >= 20: # was just >
            if char == " ":
                cnt = 0
                str_list.insert(index+1,"\n")    

    str_list.extend(footer)

    return "".join(str_list)        
#-------------------------------------------------------------------------------------------------------------------------------------------
def get_digit(_text: str, _target: str) -> str:
    """ 
    picks out any digits in a string 
    Used in __recover_task() to pull out the hour or minute modifier
    """
    res: str = None
    if _target in _text:
        text_list: list[str] = _text.split()
        for item in text_list:
           if item.isdigit():
               res = item
    return res
#-------------------------------------------------------------------------------------------------------------------------------------------
def get_actual_frequency(_text: str) -> str:
    """ 
    Given a string will pull out the frequency as it needs to be
    fed to the WTS for recovery purposes and the day if it is there.
    """
    freq: str = _text.split('\n')[0].lower()
    # Try to get the dom, or dow if avaialble.
    try:
       day: str =  _text.split('\n')[1].lower()
    except:
        day = None

    if 'every' in freq and 'hour' in freq:
        freq = 'hourly'
    elif 'every' in freq and 'mins' in freq:    
        freq = 'minute'
    elif freq in ['daily', 'weekly', 'monthly']:
        freq = freq
    else:
        freq = 'once'

    return freq, day
#-------------------------------------------------------------------------------------------------------------------------------------------
def get_end_timedate(_time_date: str) -> tuple[str|None, str|None]:
    """ 
        Decide how to return the end_time and End_date
    """
    end_date: str
    end_time: str

    if _time_date == '\nRecurring':
        end_date = None
        end_time = None
    else:
        end_date = _time_date.split('\n')[1]  
        end_time = _time_date.split('\n')[0]
    return end_time, end_date
#-------------------------------------------------------------------------------------------------------------------------------------------
def get_living_batch_files() -> list[str]:
    """gets the names\path of all the batch files currently in the batch directory"""
    batch_dir: str = os_join(MAIN_DIR, BAT_DIR)
    return [os_join(MAIN_DIR, BAT_DIR, file) for file in  os_listdir(batch_dir)]
#-------------------------------------------------------------------------------------------------------------------------------------------
def create_batch_path_command(_msg: str, 
    _msg_id: str, 
    _destination: str, 
    _frequency: str|None=None,
    _dest_type: int|None=None
    ) -> tuple[str, str]:
    """Creates a batch file with 'send' as argument, and the message as an argument. 
        This is how the program is launched via the WTS and the message is delivered.
        All commands written in a batch file MUST be wrapped in quotes with attention
        to  maintaining whitespace. 
    Returns:
        The path of the generated .bat file.
        And the command to write to it
    """    
    def eval_for_stop_message(msg_id_: str, _msg: str, freq_: str) -> str:
        '''Decides if a message needs to be flagged with a stop message and appends if needed.'''
        # This will not show up in DB. only in the text message
        break_message: str = f"BREAKBREAKReply 'Stop {msg_id_}' to stop." 
        if ('EVERY' in freq_.upper() or 
            freq_.upper() in ['DAILY', 'WEEKLY', 'MONTHLY']):
            new_message: str = _msg + break_message
        else:
            new_message = _msg  
        return new_message
    
    clean_msg: str = clean_message(_msg)
    python_path: str = wrap_quotes(executable) + " "    
    this_path: str = wrap_quotes(os_join(MAIN_DIR, SRC_DIR, PROG_NAME))
    _destination = wrap_quotes(_destination) + " "
    arg_send: str = ' "send" '        
    
    message: str = wrap_quotes(eval_for_stop_message(_msg_id, clean_msg, _frequency)) 
    # Need to know if this is a group text, if so need to add the msgid as an argument so the send function
    # can assees if the mesage is still alive for each contact in the group.
    if _dest_type == GROUP:
        arg_msgID: str = ' "--msg_id" '
        msg_id = wrap_quotes(_msg_id)
        command: str = python_path + this_path  + arg_send + _destination + message + arg_msgID + msg_id
    else:
        command: str = python_path + this_path  + arg_send + _destination + message

    bat_path: str = os_join(MAIN_DIR, BAT_DIR, _msg_id+".bat")   
    
    return (bat_path, command)

#-------------------------------------------------------------------------------------------------------------------------------------------
def search_ID(id_: str) -> bool:
    '''
    True if this message exists.
    '''
    messages: list[list[str]] = load_data(DB)
    for msg in messages:
        if id_ == msg[ID]:
            return True
    print(f'\nMESSAGE{YELLT}:{ENDC} "{BLUET}{id_}{ENDC}" {YELLT}not found{ENDC}.')        
    return False        
#-------------------------------------------------------------------------------------------------------------------------------------------
def create_batch_file(_bat_path: str, _bat_command: str) -> None:
    """creates the actual .bat file used to call the application and send a message"""
    with open(_bat_path, "w") as bat:            
        bat.write(_bat_command)    
#-------------------------------------------------------------------------------------------------------------------------------------------

def trunc_message(_msg: list[str]) -> str:
    """ 
    Truncates a message text down to 35 chars and ...
    """
    cnt: int = 0
    str_list: list[str] = [ch for ch in _msg][MESSAGE]      
    tr_msg: str = ''
    footer: str = '...\n' + "-"*27 
    for _, char in enumerate(str_list):
        cnt+=1
        tr_msg += char
        if cnt >= 35: 
            if char == " ":   
                _msg[MESSAGE] = tr_msg[:-1] + footer  
                # Take out the space    ^
                break
    return _msg
#-------------------------------------------------------------------------------------------------------------------------------------------
def trunc_all_messages(_messages: list[list[str]]) -> list[list[str]]:
    """ 
    Truncates all messages in the database.    
    """    
    for msg in _messages:
        msg = trunc_message(msg) 
    return _messages
#-------------------------------------------------------------------------------------------------------------------------------------------
def valid_time_format(_time: str) -> bool:
    '''
      Tests to see if a time is in the right format only ie hh:mm. 
      However, hours need to go up to 36:00
      But hour cannot be > 36 and min cannot be < 0
    '''
    res: bool = True
    try:
        hour: str = _time.split(":")[0]
        min: str = _time.split(":")[1]
        
        if int(hour) > 36 or int(hour) < 0:
            res = False
        if int(min) >60 or int(min) < 0:
            res = False
    except:
        res = False

    return res

#-------------------------------------------------------------------------------------------------------------------------------------------
def enddate_in_bounds(_sd: str, _ed: str) -> bool:
    '''
    checks to see if the end date is no more than 3 days from the start date.
    ''' 
    res: bool = True
    # this will go 4 days if the user needs to stop it after midnight, othewise it will stop at 00:00 on the 3rd day
    max_days: int = 4
    # get the days out and make sure they do not extend beyond
    """try:
        s_day: str = _sd.split('/')[1]
        e_day: str = _ed.split('/')[1]

        if e_day - s_day <= 4:
            res = False
    except Exception as er:
        print(er)
        res = False   """     
    
    # Let it all pass until implemented
    return res

#print(enddate_in_bounds('04'))    
#-------------------------------------------------------------------------------------------------------------------------------------------
def validate_duration(
    _duration: str, 
    _freq: str, 
    _mod: str, 
    _start_date: str=None,
    _end_date: str=None
    ) -> bool:
    ''' 
     True if the string is in the time format HH:MM and all rules are obeyed.
         Rules:
         In order to stop someone from sending some poor SOB a text every minute for the rest of their natural life,
         Some rules are in place.
         Max Hours that may be used: 6
         Max Minutes: 1 every 5, 10 or 15 minutes
         if hourly mod == 1 1 every hour up to 6 hours
         if  minutes mod == [5,10,15], duration == [10|15, 10|30. 15|45]

         A mesage after being stopped on the curent day, nay be started again for up to 3 
         more days.

     This function will report on all errors the user made. 
    '''
    res: bool = True
    hour_mod_only = 1 #['1','2','3', '4', '5', '6']
    min_mod_only = ['5','10','15', '20']
    
    #Must be a time format
    if not valid_time_format(_duration):
        print(f'{YELLT}-du{ENDC}|{YELLT}--duration{ENDC} must be formatted using the time {BLUET}HH:00{ENDC} format.')
        res = False 
 
    try:
        
        # Let the user extend the minute or hourly cycle for up to 3 days
        # FOR NOW ONLY ALLOW end_date on daily, weekly monthly
        if _freq not in ['weekly', 'daily', "monthly"] and _end_date is not None:
           # if not enddate_in_bounds(_start_date, _end_date):
                print('\ncan only use -end_date for daily, weekly, or monthly')
                # print(f'You cannot extend an HOURLY or MINUTE schedules messsage for more than 3 days.')
                res = False            

        if _freq == 'hourly' or 'HOURS' in _freq:
            duration_multi = _duration.split(':')[0]
            # mod must be acceptable
            if _mod != '1':
            #if _mod not in hour_mod_only:
                print(f'\n{YELLT}-mo{ENDC}|{YELLT}--modifier{ENDC} for :{BLUET}HOURLY{ENDC} can only be 1')
                res = False
            if (int(duration_multi) < int(_mod)):
                print(f"\n{BLUET}Duration {YELLT}Can't be less than the modifier{ENDC}.")    
                res = False
            if (int(duration_multi) > 6):
                print(f"\n{BLUET}Duration {YELLT}Can't go over X 6{ENDC}.")
                res = False
            # must be divisible by the mod
            if (int(duration_multi) % int(_mod) != 0):
                print(f'\n{YELLT}The {BLUET}duration {YELLT}must be divisible by the {BLUET}modifier{ENDC}.')
                res = False

        elif _freq == 'minute' or 'MINS' in _freq:
            duration_multi = _duration.split(':')[1]
            # duration must be 2 or 3 x mod
            if _mod not in min_mod_only:
                print(f'\n{YELLT}-mo{ENDC}|{YELLT}--modifier{ENDC} for {BLUET}MINUTE{ENDC} can only be [5, 10, 15, 20].')
                res = False
            # cant go over 60 mins    
            if (int(duration_multi) > 60):
                print(f"\n{BLUET}Duration {YELLT}Can't go over X 3{ENDC}.")
                res =  False

            if (
                int(duration_multi) != int(_mod)*2 and 
                int(duration_multi) != int(_mod)*3
               ):
                print(f'{YELLT}\nDuration must be either 2 or 3 X modifier only. Max 45 minutes total{ENDC}.\n'
                      f'Your duration is {BLUET}{_duration}{ENDC} minutes.\n'
                      f'Your modifier is every {BLUET}{_mod}{ENDC} minutes.')
                res = False
       
        else:
            print(f'Cannot use {YELLT}-f{ENDC}|{YELLT}--frequency{ENDC} with anything except {BLUET}HOUR{ENDC} and {BLUET}MINUTE{ENDC}.')

    #ONly Numbas        
    except:
        res = False

    return res

#-------------------------------------------------------------------------------------------------------------------------------------------
def calculate_end_time(_start_date: str, _start_time: str, _duration: str) -> str:
    ''' 
     Given a time to start and a matter of hours or minutes(duration) returns the 
     addition of both
    '''    
    year: int; month: int;  day: int 
    du_hour: int;  du_minute: int
    st_hour: int; st_minute: int
    
    month, day, year = _start_date.split()[0].split('/')
    st_hour, st_minute = _start_time.split(':')
    du_hour, du_minute = _duration.split(':')
    curr_date_time: datetime = datetime(
        year=int(year), 
        month=int(month), 
        day=int(day),
        hour=int(st_hour),
        minute=int(st_minute)
    )
    
    new_date_time: datetime = curr_date_time + timedelta(hours = int(du_hour), minutes=int(du_minute))
    return new_date_time.strftime("%m/%d/%Y %H:%M").split()[1]

#-------------------------------------------------------------------------------------------------------------------------------------------
def eval_date(*args: tuple) -> list:
    '''
    If a date does not have the year appended, then add it 
    return the altered year or what was passsed in otherwise 
    Will tak in multiple dates if needed and return what was given
    '''
    currentDateTime: datetime = datetime.now()
    date:            datetime = currentDateTime.date()
    curr_year:            str = date.strftime("%Y")
    date_:               list = []
    res:                 list = []

    for arg in args:
        if arg is not None: 
             date_ = arg.split('/')    
             if len(date_) != 3: # ie No year
                date_.append(curr_year)
                res.append('/'.join(date_))
             else:
                res.append('/'.join(date_))
        else:
            res.append(None) # keep None Types in tact and return

    if len(res) == 1: 
        res = res[0]    # return the string not the list
    return res
 
#-------------------------------------------------------------------------------------------------------------------------------------------

def get_duration(_stime: str, _etime: str, _sdate: str) -> str:
    '''
    will retuurn in HH:MM format the duration of the current message.
    subtract the start_time from the end_time.
    '''

    year: int; month: int;  day: int
    st_hour: int; st_minute: int
    et_hour: int; et_minute: int    

    # unpack the date
    month, day, year = _sdate.split()[0].split('/')
    st_hour, st_minute = _stime.split(':')
    et_hour, et_minute = _etime.split(':')
    #print(_stime, _etime)

    start_date_time: datetime = datetime(
        year=int(year), 
        month=int(month), 
        day=int(day),
        hour=int(st_hour),
        minute=int(st_minute)
    )
    end_date_time: datetime = datetime(
        year=int(year), 
        month=int(month), 
        day=int(day),
        hour=int(et_hour),
        minute=int(et_minute)
    )
    diff: datetime = end_date_time - start_date_time
    timedelta(0, 32400)

    time_diff_hours: str = str(diff.total_seconds() / 60 / 60)
    time_diff_min: str = str(diff.total_seconds() / 60)

    # If its in the hours then the duration is how ever many hours
    # if the minute one is < 60 its in minutes, else in hours
    if int(float(time_diff_min)) < 60:
        #do mintes
        return '00:' + time_diff_min[:2]
    else:
        #do hours        
        return '0' + time_diff_hours[0] + ':00'

#-------------------------------------------------------------------------------------------------------------------------------------------
def validate_time_date(_time: str, _date: str) -> bool:
    """Validates if input matches requirments""" 
    res: bool = False

    if valid_time(_time):
        res = True
    else:
        print(f"\n({YELLT}Invalid Time.{ENDC})")        
    if valid_date(_date):
        res = True
    else:
        print(f"\n({YELLT}Invalid Date.{ENDC})")         
    return res
#-------------------------------------------------------------------------------------------------------------------------------------------
def valid_schedule_time(_time: str, _date: str, alt_time_date: str=None, output=True) -> bool:
    """Checks to see if the time and date entered are in the future
    Uses the time of day as well as the day of the month to determine if the 
    The time is legal.
    use alt_time_date for an alternate time to base the validation on.
    
    Coded this very early. Before i discovered datetime. Should go back and use datetime 
    objects as i did in later code, will wait and see if bugs arrise.
    Noted
    However, When using the date ad time together its pretty accurate at determining 
    if future. leavng it be.
    """
   
    res: bool = False 
    time_date_now: str
    
    if alt_time_date is None:
        time_date_now = get_time_date('time_date')
    else:
        time_date_now = alt_time_date

    try:
        # scheduled time to validate MM/DD/YYYY 
        sch_hour, sch_min = _time[:2], _time[3:]    
        sch_mth, sch_day, sch_year  = _date[:2],_date[3:5] , _date[6:10]
        # current times
        cur_mth, cur_day, cur_year = time_date_now[:2], time_date_now[3:5], time_date_now[6:10]
        cur_hour, cur_min = time_date_now[11:13], time_date_now[14:16]    
        
        # Start with the year, Month, Day, Hour, min 
        if(sch_year == cur_year):
            if sch_mth > cur_mth: res = True
            if sch_mth == cur_mth and sch_day > cur_day: res = True
            if sch_day == cur_day and sch_hour > cur_hour: res = True
            if sch_hour == cur_hour and sch_min > cur_min: res = True
        elif(sch_year > cur_year):
            res = True

        if not res:
            if output:
                print(f"\n{YELLT}Cannot create{ENDC} a message task for a time that has passed.") 
    except:
        # was not a digit or out of range
        res = False

    return res
#-------------------------------------------------------------------------------------------------------------------------------------------
def valid_future_date(_date: str) -> bool:
    """
      True if date is today or later 
      All I need to know is if this date is today or later, 
      the time of day for my purposes is irrelevant.    
    """ 
    res: bool = False
    now = datetime.today()
    date_format = "%m/%d/%Y"   
    try: 
        # break time date now into a list of yyyy, mm, dd
        now_list = str(now).split()[0].split('-')
        # move the year to the back
        now_list.append(now_list.pop(0))
        # join it with / to match the format of my date
        today_m_d_YYYY_ONLY: str = '/'.join(now_list)

        start = datetime.strptime(_date, date_format)    
        today = datetime.strptime(today_m_d_YYYY_ONLY, date_format)

        if start >= today:
            res = True

    except Exception as e:
        print(e)   
        res = False

    return res        

#-------------------------------------------------------------------------------------------------------------------------------------------
def valid_date(_date: str) -> bool:
    """True if a string is in the valid date format expected."""
    date_format = "%m/%d/%Y"
    try:
        date_obj = datetime.strptime(_date, date_format)
    except ValueError:
        return False

    return True    
#-------------------------------------------------------------------------------------------------------------------------------------------
def valid_time(_time: str) -> bool:
    """True if a string is in the valid time format expected."""
    time_format = "%H:%M"
    
    try:
        time_obj = datetime.strptime(_time, time_format)
    except ValueError:
        return False
    return True       
    
#-------------------------------------------------------------------------------------------------------------------------------------------
def print_report(
    _id: str, 
    _st: str,
    _destination: str,
    _dest_type: int|None,
    _sd: str|None, 
    _frequency: str|None,
    _mo: str|None,
    _et: str|None,
    _dow: str|None, 
    _dom: str|None, 
    _ed: str|None
) -> None:
    """ Prints out a simple report about the message that was just scheduled."""   
    # message "_id" will be sent on "_sd" to " destinatin or group".
    # The message wil send "_frequency" (if there is a _mo) every Hour or so many minutes.
    # The message will stop at "et" on "ed"\Recurr indefinity 

    if _dest_type ==  DEFAULT_CONTACT or _dest_type ==  CONTACT: _dest_type = "Contact"
    if _dest_type ==  GROUP: _dest_type = "GROUP"

    add_on: str =""
    report: str = f'\nThe message "{YELLIT}{_id}{ENDC}" will be sent on \
{YELLT}{_sd}{ENDC} to {YELLT}{_dest_type}{ENDC} "{BLUET}{_destination}{ENDC}" at {GRNT}{_st}{ENDC}.\n'

    if 'EVERY'  in _frequency or 'hourly' in _frequency:
        if _et is not None:
           add_on = f'It will be sent {GRNT}{_frequency}{ENDC} from {GRNT}{_st}{ENDC} to {GRNT}{_et}{ENDC}.\n'
        if _et is None:
           add_on = f'It will be sent {GRNT}{_frequency}{ENDC} starting at {GRNT}{_st}{ENDC}.\n'
        if _ed is not None:    
           add_on = f'It will be sent {GRNT}{_frequency}{ENDC} starting at {GRNT}{_st}{ENDC} and will end on {YELLT}{_ed}{ENDC}.\n'
        if _ed is not None and _et is not None:  
           add_on = f'It will be sent {GRNT}{_frequency}{ENDC} starting at {GRNT}{_st}{ENDC} to \
{GRNT}{_et}{ENDC} and all messages will end by \nmidnight on {YELLT}{_ed}{ENDC}.\n'

    if 'MIN' in _frequency or 'minute' in _frequency:
        if _et is not None:
            add_on = f'Message will be sent every {GRNT}{_mo} minutes{ENDC} until {GRNT}{_et}{ENDC}.\n'
        if _et is None:    
            add_on = f'Message will be sent every {GRNT}{_mo} minutes{ENDC}.\n'
        if _ed is not None:    
           add_on = f'It will be sent every {GRNT}{_mo} minutes{ENDC} starting at {GRNT}{_st}{ENDC} and will end on {YELLT}{_ed}{ENDC}.\n'
        if _ed is not None and _et is not None:
           add_on = f'It will be sent every {GRNT}{_mo} minutes{ENDC} from {GRNT}{_st}{ENDC} to \
{GRNT}{_et}{ENDC} and all messages will end by \nmidnight on {YELLT}{_ed}{ENDC}.\n'

    if _frequency == 'daily': 
        if _ed is not None: 
            add_on = f'Message will be sent {GRNT}DAILY{ENDC} until {YELLT}{_ed}{ENDC}.\n'   
        if _ed is None: 
            add_on = f'Message will be sent {GRNT}DAILY{ENDC}.\n'

    if _frequency == 'weekly': 
        if _ed is not None: 
            add_on = f'Message will be sent {GRNT}WEEKLY{ENDC} on {YELLT}{_dow}{ENDC} until {YELLT}{_ed}{ENDC}.\n'   
        if _ed is None: 
            add_on = f'Message will be sent {GRNT}WEEKLY{ENDC} on {YELLT}{_dow}{ENDC}.\n'
    
    if _frequency == 'monthly': 
        if _ed is not None: 
            add_on = f'Message will be sent {GRNT}MONTHLY{ENDC} on {YELLT}{_dom}{ENDC} until {YELLT}{_ed}{ENDC}.\n'   
        if _ed is None: 
            add_on = f'Message will be sent {GRNT}MONTHLY{ENDC} on {YELLT}{_dom}{ENDC}.\n'
            
    print(report + add_on)
     