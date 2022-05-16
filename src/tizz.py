 
from argparse import (
        HelpFormatter,
        ArgumentParser
)        
from contacts import Contacts
from message import Message

from constants import PROG_NAME
#PROG_NAME = PROG_NAME.split('.')[0]

from utility import (
        backup_databases, 
        rebuild_database, 
        backup_databases, 
        recover_database,
        lookup_number,
        YELLT,
        BLUET,
        GRNT,
        TURT,
        VIT,
        GRYT,
        YELLIT,
        ENDC
)

## Parses all arguments. THis is a very confusing looking module. I used a lot of color coding and custom formatting to 
# make the help as useful as possible. 


class SmartFormatter(HelpFormatter):

    def _split_lines(self, text, width):
        if text.startswith('R|'):
            return text[2:].splitlines()  
        # this is the RawTextHelpFormatter._split_lines
        return HelpFormatter._split_lines(self, text, width)


def get_parser():
    parser = ArgumentParser(formatter_class=SmartFormatter,
    description=f''
        f'- {YELLIT}Tizzle{ENDC} - {BLUET}Send text messages now or schedule them to be sent '
        f'anytime in the future{ENDC}.') 

    subparsers = parser.add_subparsers(description=f"{TURT}Below is detatiled help on how to use each command."
                                                   f" More detailed help available for each command.{ENDC}", 
    help="R|\n\n\n\n"
        f'{YELLIT}For General help on setting up the application and what all you need to \n'
        f'schedule   and  send free text  messages  from  the  command  line, see \n'
        f'{BLUET}gettingstarted.md{ENDC}. {YELLIT}Additional help is also available in {ENDC}{BLUET}readme.md{ENDC}. \n\n' 
         f'Sub Command Help Color Key:\n'
         '--------------------------------------------\n'
         f'Program Name:          {GRNT}Light green{ENDC}\n'
         f'Sub Commands:          {TURT}Turquoise{ENDC}\n'
         f'Positional Arguments:  {VIT}Purple{ENDC}\n'
         f'Optional Arguments:    {YELLIT}Yellow Italic{ENDC}\n'
         f'Place holder/Options:  {BLUET}Dark Blue {ENDC}\n'

         'Detailed info:         White\n\n\n'
    )
    

    # ---------------------------------------------------------------------------------------
    # Parser for "Contacts" sub commands
    #----------------------------------------------------------------------------------------
    # ADD CONTACT
    parser_new = subparsers.add_parser(
            'add_contact',  
            help='R|'
            'Add a new contact.\n\n'
            f'{GRYT}python{ENDC} {GRNT}{PROG_NAME}{ENDC} {TURT}add_contact{ENDC} <{VIT}name{ENDC}> <{VIT}phone{ENDC}> <{VIT}provider{ENDC}> '
            f'[{YELLIT}-g{ENDC}|{YELLIT}--group{ENDC}] <{BLUET}group_name{ENDC}>\n\n'
            f'The add-contact arguments are all {YELLIT}case insensitive{ENDC}.\n' 
            f'Case of Names, Providers, and Groups will all be adjusted by the \napplication.\n'
            'To add a contact to a group\n\n',
             description=f'{YELLIT}Adds a new contact to the contacts database{ENDC}.', formatter_class=SmartFormatter)

    parser_new.add_argument(
            '-g', "--group", 
            required=False, dest="group",
            help=f"R|{BLUET}Optional GROUP to add the contact to on creation{ENDC}.\n"
                 f'If omitted the GROUP will be initialized as {BLUET}None{ENDC}'
    )
    parser_new.add_argument('name', help=f"R|{VIT}Contact name{ENDC}.")
    parser_new.add_argument('phone', help=f"R|{VIT}Contact phone number{ENDC}.")   
    parser_new.add_argument('provider', help=f"R|{VIT}Provider for contacts cell service{ENDC}.")     
    parser_new.set_defaults(func=contacts.add_new)

    # DELETE contact:------------------------------------------------------------------------
    parser_new = subparsers.add_parser(
            'del_contact',  
            help='R|Delete one or more contacts.\n'
            f'{GRYT}python{ENDC} {GRNT}{PROG_NAME}{ENDC} {TURT}del_contact{ENDC} <{VIT}contact{ENDC}|{VIT}all{ENDC}> \n\n',

             description=f'{YELLIT}Delete one or all contacts from the database{ENDC}.', formatter_class=SmartFormatter)

    parser_new.add_argument('name',
               help=f"R|{VIT}Enter contact name to be removed from database{ENDC}.\n"
                    f'Or enter {YELLIT}all{ENDC} to remove all contacts.')
    parser_new.set_defaults(func=contacts.del_contact)

    ##MODIFY Contact: -----------------------------------------------------------------------   
    parser_new = subparsers.add_parser(
            'mod_contact',  help='R|Modify a contacts information.\n\n'
                                 f'{GRYT}python{ENDC} {GRNT}{PROG_NAME}{ENDC} {TURT}mod_contact{ENDC} <{VIT}contact name{ENDC}> \n'
                                 f'[{YELLIT}-n{ENDC}|{YELLIT}--name{ENDC}] <{BLUET}new name{ENDC}>\n'
                                 '  This is the name to use if you are changing the name.\n'
                                 f'[{YELLIT}-ph{ENDC}|{YELLIT}--phone{ENDC}] <{BLUET}new phone{ENDC}>\n'
                                 '  The new phone number.\n'
                                 f'[{YELLIT}-pr{ENDC}|{YELLIT}--provider{ENDC}] <{BLUET}new provider{ENDC}>\n'
                                 '  The new provider name.\n'
                                 f'[{YELLIT}-g{ENDC}|{YELLIT}--group{ENDC}] <{BLUET}new group name{ENDC}>\n'
                                 '  The new GROUP name.\n\n'
                                 '------------------------------------------------------------------------------------------\n'
                                f'{BLUET}Examples{ENDC}:\n\n' 
                                ' Change a contact named "John Smiths" provider:\n'
                                f'  {GRNT}{PROG_NAME} {TURT}mod_contact{ENDC} {VIT}"john Smith"{ENDC} {YELLIT}-pr{ENDC} {BLUET}verizon{ENDC}\n\n'
                                ' Change "John Smiths" name to "Jon Smith:"\n'
                                f'  {GRNT}{PROG_NAME} {TURT}mod_contact{ENDC} {VIT}"john Smith"{ENDC} {YELLIT}-n{ENDC} {BLUET}"jon Smith"{ENDC}\n\n'
                                ' Change every element of the contact:\n'
                                f'  {GRNT}{PROG_NAME} {TURT}mod_contact{ENDC} {VIT}"john Smith"{ENDC} {YELLIT}-n{ENDC} {BLUET}"JaCk RiPpEr"{ENDC} '
                                f'{YELLIT}-ph{ENDC} {BLUET}8567894561{ENDC} {YELLIT}-pr{ENDC} {BLUET}VeRIzon{ENDC} {YELLIT}-g{ENDC} {BLUET}"some Group"{ENDC}\n\n'
                                f' Modifying  groups and names of contacts is {YELLIT}Case Insensitive.{ENDC} It really\n'
                                 " doesn't matter how you in put the names for this routine. The only thing that \n"
                                 ' matters is that you include the current name the contact is saved under as.\n'
                                 ' as a positioinal argument.\n\n'
                                 ,
                                 
             description=f'{YELLIT}Modify existing contact info{ENDC}.', formatter_class=SmartFormatter)

    parser_new.add_argument(
            '-n', "--name", 
            required=False, dest="name",
            help=f"R|{BLUET}The new contact name{ENDC}.\n\n"
    )
    parser_new.add_argument(
            '-ph', "--phone", 
            required=False, dest="phone_number",
            help=f"R|{BLUET}The new contact phone number{ENDC}.\n\n"
    )
    parser_new.add_argument(
            '-pr', "--provider", 
            required=False, dest="provider",
            help=f"R|{BLUET}The new contact provider name{ENDC}.\n\n"
    )
    parser_new.add_argument(
            '-g', "--group", 
            required=False, dest="group",
            help=f"R|{BLUET}The new contact group name{ENDC}.\n\n"
    )    
    parser_new.add_argument('contact_id',help=f"R|{VIT}The current name of the contact you wish to modify{ENDC}.")
    parser_new.set_defaults(func=contacts.mod_contact)
    
    ## VIEW Contact(s) -------------------------------------------------------------------
    parser_new = subparsers.add_parser(
            'view_contact',  
            help='R|View the information of one or all contacts.\n'
                f'{GRYT}python{ENDC} {GRNT}{PROG_NAME}{ENDC} {TURT}view_contact{ENDC} <{VIT}contact name{ENDC}|{VIT}all{ENDC}> \n\n' ,
            
            description=f"{YELLIT}View an existing contacts info, or all contacts{ENDC}.", formatter_class=SmartFormatter)   

    parser_new.add_argument('name',help=f"R|{VIT}Enter contact name to be modified, or all for all.{ENDC}.")  
    parser_new.set_defaults(func=contacts.view_contact)

    #set DEFAULT Contact -----------------------------------------------------------------   
    parser_new = subparsers.add_parser(
            'set_def_contact',  
             help='R|Sets the default contact.\n'
                  f'{GRYT}python{ENDC} {GRNT}{PROG_NAME}{ENDC} {TURT}set_def_contact{ENDC} <{VIT}contact name{ENDC}> \n\n' 
                   f'\n'
                  '------------------------------------------------------------------------------------------\n\n'
                  f'{YELLIT}DATABASE METHODS{ENDC}\n\n',

             description=f'{YELLIT}Sets an existiing contact as the "default" contact{ENDC}.', formatter_class=SmartFormatter)   

    parser_new.add_argument('name',help=f"R|{VIT}Enter contact name to be default{ENDC}.")  
    parser_new.set_defaults(func=contacts.set_default_contact)

    # REBUILD Contacts database: ---------------------------------------------------------
    parser_new = subparsers.add_parser(
            'rebuild',  
             help='R|Rebuilds one or all databases in case they were deleted or corrupted.\n'
                  f'{GRYT}python{ENDC} {GRNT}{PROG_NAME}{ENDC} {TURT}rebuild{ENDC} <{VIT}contacts{ENDC}|{VIT}messages{ENDC}|{VIT}all{ENDC}> \n\n'
                  ,
             description=f'{YELLIT}Rebuilds a database incase corrupted, or missing{ENDC}.', formatter_class=SmartFormatter)   

    parser_new.add_argument('db', choices=['contacts', 'messages', 'settings', 'all'],
                            help=f"R|{VIT}Enter database to rebuild{ENDC}.\n"
                                      f'<{VIT}messages{ENDC}|{VIT}contatcs{ENDC}|{VIT}settings{ENDC}|{VIT}all{ENDC}>\n' )  
    parser_new.set_defaults(func=rebuild_database)

    # RECOVER  databases: ---------------------------------------------------------
    parser_new = subparsers.add_parser(
            'recover_db',  
             help='R|Recovers one or all databases from the associated .bck backup files.\n'
                  f'{GRYT}python{ENDC} {GRNT}{PROG_NAME}{ENDC} {TURT}recover_db{ENDC} <{VIT}contacts{ENDC}|{VIT}messages{ENDC}|{VIT}all{ENDC}> \n\n'
                  ,
             description=f'{YELLIT}Recovers one or both databases from the associated .bck backup files{ENDC}.', formatter_class=SmartFormatter)   

    parser_new.add_argument('db', choices=['contacts', 'messages', 'settings', 'all'],
                            help=f"R|{VIT}Enter database to recover{ENDC}.\n"
                                      f'<{VIT}messages{ENDC}|{VIT}contatcs{ENDC}|{VIT}settings{ENDC}|{VIT}all{ENDC}>\n' )  
    parser_new.set_defaults(func=recover_database)

    #BACKUP databases: -------------------------------------------------------------------
    parser_new = subparsers.add_parser(
            'backup',  
            help='R|Backup one or all databases. (including settings)\n'
                 f'{GRYT}python{ENDC} {GRNT}{PROG_NAME}{ENDC} {TURT}backup{ENDC} <{VIT}contacts{ENDC}|{VIT}messages{ENDC}|{VIT}settings{ENDC}|{VIT}all{ENDC}> \n\n'
                 ,

             description=f'{YELLIT}backs-up databases{ENDC}.', formatter_class=SmartFormatter)  
                
    parser_new.add_argument('db', choices=['contacts', 'messages', 'settings', 'all'],
                            help=f"R|{VIT}Enter database to backup{ENDC}.")  
    parser_new.set_defaults(func=backup_databases)

    #Lookup Number provider: --------------------------------------------------------------
    parser_new = subparsers.add_parser(
            'lookup',  
            help='R|Opens a webbrowser and loads url to lookup a cell number for the provider.\n'
                 f'{GRYT}python{ENDC} {GRNT}{PROG_NAME}{ENDC} {TURT}lookup{ENDC} \n\n'
                 f'\n'
                  '------------------------------------------------------------------------------------------\n\n'
                  f'{YELLIT}GROUP METHODS{ENDC}\n\n',
            description=f'{BLUET}Gives info to lookup a numbers provide{ENDC}r.')     
    parser_new.set_defaults(func=lookup_number)

    #---------------------------------------------------------------------------------------
    # groups sub commands  
    #---------------------------------------------------------------------------------------
    # MAKE GROUP
    parser_new = subparsers.add_parser(
            'make_group',  
            help='R|Create a new GROUP.\n\n'
                 f'{GRYT}python{ENDC} {GRNT}{PROG_NAME}{ENDC} {TURT}make_group{ENDC} <{VIT}GROUP{ENDC}> <{VIT}contact1{ENDC}> <{VIT}contact2{ENDC}> <{VIT}...{ENDC}>\n'
                 'There must be at least 2 contacts to create a group.\n\n',

            description=f'{YELLIT}Creates a group with two or more contacts{ENDC}.', formatter_class=SmartFormatter)
                 
    parser_new.add_argument('group_name', help=f"R|{VIT}Group name to create{ENDC}.")     
    parser_new.add_argument('contacts',  nargs='*', help=f"R|{VIT}Contacts to add to the group{ENDC}.") 
    parser_new.set_defaults(func=contacts.groups.make_group)
    
    
    ## add to Group: ------------------------------------------------------------------------------------------------
    parser_new = subparsers.add_parser(
            'add2group',  
             help='R|Add one or more contacts to a GROUP.\n'
                  f'{GRYT}python{ENDC} {GRNT}stext{ENDC} {TURT}add2group{ENDC} <{VIT}GROUP{ENDC}> <{VIT}contact1{ENDC}> <{VIT}contact2{ENDC}> <{VIT}...{ENDC}>\n\n'
             ,
             description=f'{YELLIT}Adds one or more contacts to an existing group{ENDC}.', formatter_class=SmartFormatter)
    
    parser_new.add_argument('group', help=f"{VIT}Group name add to{ENDC}.") 
    parser_new.add_argument('contacts', nargs='*', help=f"|{VIT}Contacts to be aded to the group{ENDC}.")
    parser_new.set_defaults(func=contacts.groups.add2group)

    ## Remove Group: ------------------------------------------------------------------------------------------------
    parser_new = subparsers.add_parser(
            'remove_from_group', 
             help='R|Removes one or more contacts from a GROUP.\n'
                  f'{GRYT}python{ENDC} {GRNT}{PROG_NAME}{ENDC} {TURT}remove_from_group{ENDC} <{VIT}GROUP{ENDC}> <{VIT}contact1{ENDC}> <{VIT}contact2{ENDC}> <{VIT}...{ENDC}>\n\n'
                  ,
             description=f'{YELLIT}Removes one or more contacts from an existing group{ENDC}.', formatter_class=SmartFormatter)
 # Need to go back to otional so arguments are enteded in correct order   
    parser_new.add_argument('group', help=f"{VIT}Group removing contacts from{ENDC}.") 
    parser_new.add_argument('contacts', nargs='*', help=f"{VIT}Contact(s) to be removed{ENDC}.")
    parser_new.set_defaults(func=contacts.groups.remove_from_group)

    ## Change Group: ------------------------------------------------------------------------------------------------
    parser_new = subparsers.add_parser(
            'change_group',  
             help='R|Changes the name of an existing GROUP.\n'
                  f'{GRYT}python{ENDC} {GRNT}{PROG_NAME}{ENDC} {TURT}change_group{ENDC} <{VIT}"CURRENT GROUP NAME"{ENDC}> <{VIT}"NEW GROUP NAME"{ENDC}>\n\n'
                 
                 ,
             description=f'{YELLIT}Changes the name of an existing group{ENDC}.', formatter_class=SmartFormatter)
    
    parser_new.add_argument('old_group', help=f"{VIT}Old group name{ENDC}.") 
    parser_new.add_argument('new_group', help=f"{VIT}New group name{ENDC}.") 
    parser_new.set_defaults(func=contacts.groups.change_group)

    ## Wipe Groups: --------------------------------------------------------------------------------------------------
    parser_new = subparsers.add_parser(
            'wipe_groups',  
             help='R|Wipes all conacts of all groups.\n'
                  f'{GRYT}python{ENDC} {GRNT}{PROG_NAME}{ENDC} {TURT}wipe_groups{ENDC}\n\n'
                 ,
             description=f'{YELLIT}Deletes all groups from all contacts.{ENDC}', formatter_class=SmartFormatter)
    parser_new.set_defaults(func=contacts.groups.wipe_groups)

    ## Assimilate groups: --------------------------------------------------------------------------------------------
    parser_new = subparsers.add_parser(
            'ass_groups', 
             help='R|Wipes all conacts of all groups.\n'
                  f'{GRYT}python{ENDC} {GRNT}{PROG_NAME}{ENDC} {TURT}ass_groups{ENDC} <{VIT}"GROUP"{ENDC}>\n\n'
                 ,
             description=f'{YELLIT}Changes all group names to the name specified{ENDC}.', formatter_class=SmartFormatter)
             
    parser_new.add_argument('group', help=f'{VIT}Group name to create.{ENDC}')
    parser_new.set_defaults(func=contacts.groups.ass_groups)        

    ## View by Group -------------------------------------------------------------------------
    parser_new = subparsers.add_parser(
            'view_group',  
            help='R|View the members of a given group.\n'
                  f'{GRYT}python{ENDC} {GRNT}{PROG_NAME}{ENDC} {TURT}view_group{ENDC} <{VIT}"GROUP"{ENDC}>\n\n'
                  f'\n'
                  '------------------------------------------------------------------------------------------\n\n'
                  f'{YELLIT}MESSAGE METHODS{ENDC}\n\n',
             description=f'{YELLIT}View the contacts that belong to a group. {ENDC}', formatter_class=SmartFormatter)

    parser_new.add_argument('group_name', help='{VIT}Group to view.{ENDC}')     
    parser_new.set_defaults(func=contacts.groups.view_by_group)

    #-------------------------------------------------------
    # parser for "new" message task sub command:
    #-------------------------------------------------------    
    # no -dtype = send to default, no matter what -dest is set to
    # -dtype will overide destination if set to 0 period.
    # but if you use -dest, you must specify -dtype with either contact, 1, or group, 2
    parser_new = subparsers.add_parser(
            'new_msg', help='R|Create a new message to be sent in the future to a contact, or a group of contacts.\n'
                            'Messages can be sent once,  a hourly, every so many minutes, daily, weekly,or monthly \n' 
                            'and can be set to expire after the desired cycles.\n\n'
                            f'{GRYT}python{ENDC} {GRNT}{PROG_NAME}{ENDC} {TURT}new_msg{ENDC} '
                            f'<{VIT}"message"{ENDC}> '
                            f'<{VIT}time HH:MM{ENDC}>  [-Options] \n\n'
                            f'Options and descriptions:\n'
                            f'[{YELLIT}-dest{ENDC}|{YELLIT}--destination{ENDC}] <{BLUET}destination{ENDC}> \n'
                            f'  If using -dest(contact name or group name), you must also use {YELLIT}--dtype{ENDC}|{YELLIT}-dt{ENDC}\n'
                            '  Do not set for default contact.\n\n'  
                            f'[{YELLIT}-dt{ENDC}|{YELLIT}--dtype{ENDC}] <{BLUET}1|2{ENDC}>\n'
                            '  Will send to default contact if omitted, no matter what is specified with -dest.\n'
                            '  Set to 1 to specify contact, 2 for group.\n\n'
                            f'[{YELLIT}-sd{ENDC}|{YELLIT}--send_date{ENDC}] <{BLUET}mm/dd/yyyy{ENDC}>\n'
                            '  Date the message should start. Default is same day.\n'
                            f'[{YELLIT}-ed{ENDC}|{YELLIT}--end_date{ENDC}] <{BLUET}mm/dd/yyyy{ENDC}>\n'
                            '  Date the message should stop, if daily, weekly, monthly, will not end if omitted.\n'
                            
                            f'[{YELLIT}-du{ENDC}|{YELLIT}--duration{ENDC}] <{BLUET}HH:MM{ENDC}>\n' 
                            '  Only used on MINUTE or HOURLY schedule. How long to send messages.\n'
                            '  Use if you want to limit when to stop a task on that day.\n\n'
                            f'[{YELLIT}-f{ENDC}|{YELLIT}--frequency{ENDC}] <{BLUET}frequency{ENDC}>\n'
                            '  [hour, minute, daily, weekly, monthly, once]\n'
                            f'[{YELLIT}-mo{ENDC}|{YELLIT}--modifier{ENDC}] <{BLUET}1-1439{ENDC}|<{BLUET}1-12{ENDC}>\n'
                            '  Only used for hourly and minute. Send a message 1-1439 times a day, or 1-12 hours a day.\n'                            
                            f'[{YELLIT}-dow{ENDC}|{YELLIT}--day_week{ENDC}] <{BLUET}day{ENDC}>\n'
                            '  [sun, mon, tue, wed, thur, fri, sat, sun]\n'
                            f'[{YELLIT}-dom{ENDC}|{YELLIT}--day_month{ENDC}] <{BLUET}1-31{ENDC}>\n' 
                            '  The day of the moth to send a message on. 1=1st, 2=2nd, etc.\n\n'
                            f'{BLUET}Examples{ENDC}:\n'
                            '------------------------------------------------------------------------------------------\n'
                             ' Send a message at 3:00pm to a contact named John Smith on 04/16/2021:\n'
                            f'  {GRNT}{PROG_NAME} {TURT}new_msg{ENDC} {VIT}"Message" 15:00{ENDC} {YELLIT}-dest{ENDC} {BLUET}"John Smith"{ENDC}'
                            f' {YELLIT}-dt{ENDC} {BLUET}1{ENDC} {YELLIT}-sd{ENDC} {BLUET}04/16/2021{ENDC}\n\n'
                            f' Send a message to the default contact, today:\n'
                            f'  {GRNT}{PROG_NAME}{ENDC} {TURT}new_msg{ENDC} {VIT}"Message" 15:00{ENDC}\n\n'                            

                             ' Send the same mesage to the default contact on a certain day in the future:\n'
                            f'  {GRNT}{PROG_NAME}{ENDC} {TURT}new_msg{ENDC} {VIT}"Message" 15:00{ENDC} {YELLIT}-sd{ENDC} {BLUET}04/16/2021{ENDC}\n\n'  

                            ' Send a message to default and repeat it once every 5 minutes for 15 minutes:\n'
                            f'  {GRNT}{PROG_NAME}{ENDC} {TURT}new_msg{ENDC} {VIT}"Message" 15:00{ENDC} {YELLIT}-f{ENDC} '
                            f'{BLUET}minute{ENDC} {YELLIT}-du{ENDC} {BLUET}00:15{ENDC}\n\n'
                            f' The duration and the amount of messages you can sent is limited. You can use this \n'
                            ' Option for HOUR or MINUTE one time messages. \n'
                            '   HOUR: \n'
                            '       Once an hour for up to six hours.\n'
                            '   MINUTE:\n'
                            '       Once every [5,10,15,20] minutes for up to 00:60 minutes.\n'
                            '       And the intervals have been crippled.'
                           ' Example:\n'
                            '       Once every 5 for up to 00:60.\n'
                            '       Once every 10 for up to 00:60.\n'
                            '       Once every 20 for up to 00:60.\n'
                            "       You can't itereate any message > 6 times.\n\n"
                            f' {BLUET}NOT INTENDED TO SPAM SOME POOR SOB EVERY MINUTE FOR THE REST OF THEIR LIVES{ENDC}!\n'
                             ' These time increments and max time limit will give you more than you need to\n'
                             ' get the2point across. Messages can also be cancelled by the user via text reply.\n\n'
                           
                            f' Send a message to a GROUP, today:\n'
                            f'  {GRNT}{PROG_NAME}{ENDC} {TURT}new_msg{ENDC} {VIT}"Message" 15:00{ENDC} {YELLIT}-dest{ENDC} {BLUET}"group name"{ENDC}'
                            f' {YELLIT}-dt{ENDC} {BLUET}2{ENDC}\n\n' 
                            f' Send a message to default contact at 1:00pm, and repeat every 10 minutes\n' 
                             ' for 1 hour, then end:\n'
                            f'   {GRNT}{PROG_NAME}{ENDC} {TURT}new_msg{ENDC} {VIT}"Message" 13:00{ENDC} {YELLIT}-f {BLUET}minute{ENDC}' 
                            f' {YELLIT}-mo{ENDC} {BLUET}10{ENDC} {YELLIT}-et{ENDC} {BLUET}14:00{ENDC}\n\n' 
                             ' Send a message to a contact every friday at 5:00pm, if Friday is the 3rd:\n'
                            f'  {GRNT}{PROG_NAME}{ENDC} {TURT}new_msg{ENDC} {VIT}"Message" 17:00{ENDC} {YELLIT}-dest{ENDC} {BLUET}"contact name"'
                            f'{ENDC} {YELLIT}-dt{ENDC} {BLUET}1{ENDC} {YELLIT}-sd{ENDC} {BLUET}08/03/2021{ENDC} {YELLIT}-f{ENDC} {BLUET}weekly {ENDC}\n\n'
                            ' Send a message at 3:00pm everyday for one week to a Group of contacts: \n'
                            f'  {GRNT}{PROG_NAME}{ENDC} {TURT}new_msg{ENDC} {VIT}"Message" 15:00{ENDC} {YELLIT}-dest{ENDC} {BLUET}"GROUP NAME"'
                            f'{ENDC} {YELLIT}-dt{ENDC} {BLUET}2{ENDC} {YELLIT}-sd{ENDC} {BLUET}08/03/2021{ENDC} {YELLIT}-f{ENDC} '
                            f'{BLUET}daily {ENDC}{YELLIT}-ed{ENDC} {BLUET}03/11/2021{ENDC}\n\n\n' 

                            
                            ' All end_dates end on midnight of the chosen day so if the message needs to\n'
                            f' run after midnght you need to schedule an extra day. The arguments for this sub \n'
                            f' command are all {YELLT}Case {ENDC}in{YELLIT}sensitive{ENDC}. The case will be adjusted by the application. \n'
                            ' In fact all are case insensitive accept where specifically indicated.\n\n'  
                            ' "Tizzle" uses the schtasks API to schedule the texts. More info can be found at:\n'
                            ' https://docs.microsoft.com/en-us/windows-server/administration/windows-commands/schtasks \n'
                            " This is in no way all of the functionality available. It's just all I wanted to add.\n"
                            ' The functionality i have implemented is likely way more than anyone will need and\n'
                            ' there is room to do even more with this API, however I feel it can become too \n'
                            ' confusing, as it really got out of hand.' 
                            

                            '\n\n ', formatter_class=SmartFormatter)

    # Optional arguments:
    parser_new.add_argument(
            '-dest', "--destination", 
            required=False, dest="destination",
            help=f'R|The destination to send to, Contact name, or group name. If left blank\n'
                  'Will be sent to the default contact. Default contact is always the first\n' 
                  'contact in the contacts DB.\n\n'
                  f'If using {YELLIT}-dest{ENDC} you must also use {YELLIT}-dt{ENDC} to specify Contact, {BLUET}1{ENDC} or Group, {BLUET}2{ENDC}.\n\n'

    )
    parser_new.add_argument(  
            f'-dt', f'--dtype', 
            dest='dest_type', 
            required=False,
            default=0, 
            type=int,
            help=f"R|{YELLIT}The Type of destination. {BLUET}1{ENDC} for Contacts, {BLUET}2{ENDC} for Groups.\n{ENDC} " 
                 f'This optiion will default to 0 to send to the default contact.\n\n'
    )    
    parser_new.add_argument(
            '-sd', "--send_date",  
            required=False, 
            dest='date',
            help=f'R|{YELLIT}Date to send message.{ENDC} Same day if not specified. {BLUET}MM/DD/YYYY{ENDC}\n\n'
    )  
    parser_new.add_argument(
            '-ed', "--end_date", 
            required=False, dest="ed",
            help=f"R|{YELLIT}The expiration date for the message{ENDC}. If you only want it to repeat a\n"
                  "set number of times. All ending dates will terminate at midnight on the\n"
                  f"day of ending. Unless {YELLIT}--end_time{ENDC}|{YELLIT}-et{ENDC} is also used. Not applicable for {BLUET}ONCE{ENDC},\n"
                  'if not specified for recurring messsages, texts will not end, until you\n'
                  "disable or delete them.\n\n"
    )    
    """parser_new.add_argument(
            '-et', "--end_time",  
            required=False, 
            dest='end_time',
            help=f'R|{YELLIT}Specifies the time to end a task.{ENDC} Coincides with {YELLIT}--end_date{ENDC}|{YELLIT}-ed{ENDC}. \n'
                  f'This would be the time to end a task if {YELLIT}--end_date{ENDC}|{YELLIT}-ed{ENDC} is not \n'
                  'used, it will end the same day. \n\n'
                  f'End a message at 3:00pm that is set to start at 1:00pm and execute every 20 minutes.\n'
                  f'... {YELLIT}-st{ENDC} {VIT}13:00{ENDC} {YELLIT}-f{ENDC} {BLUET}minute{ENDC} '
                  f'{YELLIT}-mo{ENDC} {BLUET}20{ENDC} {YELLIT}-et{ENDC} {VIT}15:00{ENDC} ...\n\n'
    )"""  
    parser_new.add_argument(
            '-du', "--duration",  
            required=False, 
            dest='duration',
            help=f'R|{YELLIT}Specifies the duration the message will live.{ENDC} Coincides with {YELLIT}--modifier{ENDC}|{YELLIT}-mo{ENDC}. \n'
                  f'This for how long the message will be sent on its current frequency. {YELLIT}--frequency{ENDC}|{YELLIT}-f{ENDC}  \n'
                  f'\n'
                  f'Send a message 3 times on 5 minute intervals:\n'
                  f'...{YELLIT}-st{ENDC} {VIT}13:00{ENDC} {YELLIT}-f{ENDC} {BLUET}minute{ENDC} '
                  f'{YELLIT}-mo{ENDC} {BLUET}5{ENDC} {YELLIT}-du{ENDC} {VIT}00:15{ENDC} ...\n\n'
                  f' You can only use {YELLIT}--duration{ENDC}|{YELLIT}-du{ENDC} on MINUTE and HOURLY messages. These\n'
                  ' are the only frequencies that have a frequency limit. There should \n'
                  ' be no reason to message anybody a reminder, more than every\n'
                  ' 5 minutes, 3 times.\n\n' +
                  " Don't be a stalker, or a spammer!!\n\n".upper()
    )
    parser_new.add_argument(
            '-f', "--frequency", 
            required=False, dest="freq",
            choices=['once', 'minute', 'hourly','daily', 'weekly','monthly'],
            help=f"R|{YELLIT}If not specified text will be sent only once.{ENDC}\n\n"
    )
    parser_new.add_argument(
            '-mo', "--modifier",  
            required=False, 
            dest='mo',
            help=f'R|{YELLIT}Hour and minute modifier.{ENDC} Only applicable if scheduling a message \n'
                  'to repeat N times an hour or every N minutes. \n\n'
                  f'{YELLIT}-f{ENDC} {BLUET}minute{ENDC} {YELLIT}-mo{ENDC} {BLUET}10{ENDC} = Send every 10 minutes.\n'
                  f'{YELLIT}-f{ENDC} {BLUET}hourly{ENDC} {YELLIT}-mo{ENDC} {BLUET}1{ENDC} = equals send once an hour.\n\n'
    )      
    
    parser_new.add_argument(
            '-dow', '--day_week', metavar="Day", 
            required=False, dest="dow",  
            choices=['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'],
            help=f"R|{YELLIT}The day of the week to repeat the text if{ENDC} {BLUET}WEEKLY{ENDC} is specified{ENDC}.\n\n"
    )
    parser_new.add_argument(
            '-dom', '--day_month', metavar='1-31', 
            required=False, dest="dom", 
            help=f"R|{YELLIT}The day of the month to repeat if{ENDC} {BLUET}MONTHLY{ENDC} is specified.\n\n"
    )
        
    parser_new.add_argument(f'message', help=f"{VIT}The message to be sent.{ENDC} Must wrap in quotes if message is more than one word.")
    parser_new.add_argument(f'time', help=f"{VIT}The time to send the message{ENDC}. Format: {BLUET}HH:MM{ENDC}")     
    parser_new.set_defaults(func=msg.new)    

    # "Modify" message sub command ---------------------------------------------------------
    parser_new = subparsers.add_parser(
            'mod_msg',
             help='R|Modify an existing message. \n\n'
                f'{GRYT}python{ENDC} {GRNT}{PROG_NAME}{ENDC} {TURT}mod_msg{ENDC} <{VIT}messageID{ENDC}> [-Options]\n\n'
                f'You may modify:\n'
                f'------------------------------\n'
                f'Message     [{YELLIT}-m{ENDC}|{YELLIT}--message{ENDC}] <{BLUET}"message"{ENDC}>\n'
                f'Start Time  [{YELLIT}-st{ENDC}|{YELLIT}--start_time{ENDC}] <{BLUET}HH:MM{ENDC}>\n'
                f'Destination [{YELLIT}-dest{ENDC}|{YELLIT}--destination{ENDC}]<{BLUET}"Contact Name" or group{ENDC}>\n'
                f'Dest Type   [{YELLIT}-dt{ENDC}|{YELLIT}--dtype{ENDC}] <{BLUET}1,2{ENDC}>\n'
                f'Start Date  [{YELLIT}-sd{ENDC}|{YELLIT}--start_date{ENDC}] <{BLUET}mm/dd/yyyy{ENDC}>\n'
                f'End Date    [{YELLIT}-ed{ENDC}|{YELLIT}--end_date{ENDC}] <{BLUET}mm/dd/yyyy{ENDC}>\n'
                f'Duration    [{YELLIT}-et{ENDC}|{YELLIT}--duration{ENDC}] <{BLUET}HH:MM{ENDC}>\n'
                f'User ID     [{YELLIT}-ru{ENDC}|{YELLIT}--user{ENDC}] <{BLUET}userid{ENDC}>\n'
                f'Pword       [{YELLIT}-rp{ENDC}|{YELLIT}--pword{ENDC}] <{BLUET}pword{ENDC}>\n'
                '\n\n'

                f'You can enter you User Id and password into the settings.json file\n'
                'if you would like to not be prompted at modification. Enter "null" \n'
                'for each one if you wish to use them at command line. Or at the time\n'
                'of modification.'
                '\n\n', 

             description=f'{YELLIT}Modifies any live message. (Message that has not been deleted form the Task Scheduler.){ENDC}', formatter_class=SmartFormatter)
    
    parser_new.add_argument(
            '-st', "--start_time", 
            required=False, 
            dest="start_time",
            help=f'R|The time the messsage is sent.\n\n'

    )
    parser_new.add_argument(
            '-m', "--message", 
            required=False, 
            dest="message",
            help=f'R|The The actual text message.\n\n'

    )
    parser_new.add_argument(
            '-f', "--frequency", 
            required=False,
            dest="freq",
            choices=['once', 'minute', 'hourly','daily', 'weekly','monthly'],
            help=f"R|{YELLIT}Used to change how often the message will repeat.{ENDC}\n\n"
    )    
    parser_new.add_argument(
            '-mo', "--modifier",  
            required=False, 
            dest='mo',
            help=f'R|{YELLIT}Hour and minute modifier.{ENDC} Only applicable if scheduling a message \n'
                  'to repeat N times an hour or every N minutes. \n\n'
                  f'{YELLIT}-f{ENDC} {BLUET}minute{ENDC} {YELLIT}-mo{ENDC} {BLUET}10{ENDC} = Send every 10 minutes.\n'
                  f'{YELLIT}-f{ENDC} {BLUET}hourly{ENDC} {YELLIT}-mo{ENDC} {BLUET}1{ENDC} = equals send once an hour.\n\n'
    )  
    parser_new.add_argument(
            '-dest', "--destination", 
            required=False, dest="destination",
            help=f'R|The destination to send to, Contact name, or group name. If left blank\n'
                  'Will be sent to the default contact. Default contact is always the first\n' 
                  'contact in the contacts DB.\n\n'
                  f'If using {YELLIT}-dest{ENDC} you must also use {YELLIT}-dt{ENDC} to specify Contact, {BLUET}1{ENDC} or Group, {BLUET}2{ENDC}.\n\n'

    )
    parser_new.add_argument(  
            f'-dt', f'--dtype', 
            dest='dest_type', 
            required=False,
            default=0, 
            type=int,
            help=f"R|{YELLIT}The Type of destination. {BLUET}1{ENDC} for Contacts, {BLUET}2{ENDC} for Groups.\n{ENDC} " 
                 f'This optiion will default to 0 to send to the default contact.\n\n'
    )    
    parser_new.add_argument(
            '-sd', "--start_date",  
            required=False, 
            dest='start_date',
            help=f'R|{YELLIT}Date to send message.{ENDC} Same day if not specified. {BLUET}MM/DD/YYYY{ENDC}\n\n'
    )  
    parser_new.add_argument(
            '-ed', "--end_date", 
            required=False, dest="end_date",
            help=f"R|{YELLIT}The expiration date for the message{ENDC}. If you want it to end on this date. a\n"
                  " All ending dates will terminate at midnight on the day of ending. Unless \n"
                  f"{YELLIT}--end_time{ENDC}|{YELLIT}-et{ENDC} is also used.\n\n" 
                  f" Not applicable for {BLUET}ONCE{ENDC}, if not specified for recurring messsages, texts\n"
                  " will not end, until you disable or delete them.\n\n"
    )    
    parser_new.add_argument(
            '-du', "--duration",  
            required=False, 
            dest='duration',
            help=f'R|{YELLIT}Specifies the duration the message will live.{ENDC} Coincides with {YELLIT}--modifier{ENDC}|{YELLIT}-mo{ENDC}. \n'
                  f'This for how long the message will be sent on its current frequency. {YELLIT}--frequency{ENDC}|{YELLIT}-f{ENDC}  \n'
                  f'\n'
                  f'Send a message 3 times on 5 minute intervals:\n'
                  f'...{YELLIT}-st{ENDC} {VIT}13:00{ENDC} {YELLIT}-f{ENDC} {BLUET}minute{ENDC} '
                  f'{YELLIT}-mo{ENDC} {BLUET}5{ENDC} {YELLIT}-du{ENDC} {VIT}00:15{ENDC} ...\n\n'
                  f' You can only use {YELLIT}--duration{ENDC}|{YELLIT}-du{ENDC} on MINUTE and HOURLY messages. These\n'
                  ' are the only frequencies that have a frequency limit. There should \n'
                  ' be no reason to message anybody a reminder, more than every\n'
                  ' 5 minutes, 3 times.\n\n' +
                  " Don't be a stalker, or a spammer!!\n\n".upper()
    )
    parser_new.add_argument(
            '-dow', '--day_week', metavar="Day", 
            required=False, dest="dow",  
            choices=['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'],
            help=f"R|{YELLIT}The day of the week to repeat the text if{ENDC} {BLUET}WEEKLY{ENDC} is specified{ENDC}.\n\n"
    )
    parser_new.add_argument(
            '-dom', '--day_month', metavar='1-31', 
            required=False, dest="dom", 
            help=f"R|{YELLIT}The day of the month to repeat if{ENDC} {BLUET}MONTHLY{ENDC} is specified.\n\n"
    )
    parser_new.add_argument(
            '-ru', '--userid', metavar='userID', 
            required=False, dest="userid", 
            help=f"R|{YELLIT}Your User ID for this computer {ENDC}. USe if you don't want to\n "
                  "keep in the setttings file, or be prompted at modification.\n\n"
    )
    parser_new.add_argument(
            '-rp', '--pword', metavar='pword', 
            required=False, dest="pword", 
            help=f"R|{YELLIT}Your password for this computer.{ENDC}. USe if you don't want to\n "
                  "keep in the setttings file, or be prompted at modification.\n\n"
    )

    parser_new.add_argument('msg_id', help=f"R|{VIT}The message to be modified{ENDC}.\n\n" )            
    parser_new.set_defaults(func=msg.modify)



    # "Delete" message sub command ---------------------------------------------------------
    parser_new = subparsers.add_parser(
            'del_msg', 
             help='R|Delete one or more messages\n\n'
             f'{GRYT}python{ENDC} {GRNT}{PROG_NAME}{ENDC} {TURT}del_msg{ENDC} <{VIT}messageID{ENDC}> <{VIT}messageID{ENDC}> <{VIT}messageID{ENDC}> | <{VIT}all{ENDC}>\n\n'
             'When you enter this sub command you will be presented with a menu to\n'
             'To select how to proceed. The removal of messages takes place in three\n'
             'areas. Database, Scheduler, and the batch files that call the app with\n'
             'message to be sent. You can remove these just from the database, or from\n'
             'databse, Scheduler, and the batch files.\n\n',

             description=f'{YELLIT}Deletes an existing message, or all messages{ENDC}.', formatter_class=SmartFormatter)

    parser_new.add_argument('msg_id',nargs='*',
                           help=f"R|{VIT}The message to be deleted{ENDC}.\n"
                                f'To delete all messages enter {YELLIT}all{ENDC}.')

    parser_new.set_defaults(func=msg.delete)

    # "View" message(s) sub command --------------------------------------------------------
    parser_new = subparsers.add_parser(
            'view_msg',  
            help='R|View one or more messages and all associated information.\n\n'
                f'{GRYT}python{ENDC} {GRNT}{PROG_NAME}{ENDC} {TURT}view_msg{ENDC} <{VIT}messageID{ENDC}|{VIT}all{ENDC}> [{YELLIT}--truncate{ENDC}|{YELLIT}-t{ENDC}]\n\n',
            description=f'{YELLIT}View an existing message, or all messages.{ENDC}', formatter_class=SmartFormatter)

    parser_new.add_argument(
            '-t', '--truncate', action='store_true',
            required=False, dest="truncate", 
            help=f"R|{YELLIT}Truncate the message text.{ENDC}. Will shorten the text to 35 characters.\n\n"
    )
    parser_new.add_argument('msg_id', 
                          help=f"R|{VIT}The message(s) to be viewed.{ENDC}\n"
                                f'To delete all messages enter {YELLIT}all{ENDC}.')
   
    parser_new.set_defaults(func=msg.view)

    # "Send" message(s) sub command --------------------------------------------------------
    parser_new = subparsers.add_parser(
            'send',  
            help='R|Send a text message right now.\n\n'
            f'{GRYT}python{ENDC} {GRNT}{PROG_NAME}{ENDC} {TURT}send{ENDC} <{VIT}Contact Name{ENDC}|{VIT}GROUP NAME{ENDC}> <{VIT}message{ENDC}>\n\n'
            'This method is used by the application to send the messages. When/If you\n'
            'use it directly you must pay atention to the case of the group or contact.\n\n'
            
            f'This routine is {YELLIT}Case Sensitive{ENDC} on the destination.\n'
            f'{VIT}Contact Names{ENDC} are passed in with each word capitilaized, and {VIT}GROUPS{ENDC} are all caps.\n\n',
            description=f'{YELLIT}Send a text message right now{ENDC}.', formatter_class=SmartFormatter)   

    parser_new.add_argument('destination', help=f"R|{VIT}Enter the contact, or group to send the message to.{ENDC}\n"
                                                f'{BLUET}Contact Names{ENDC} are Capitilazed, and {BLUET}GROUPS{ENDC} are all caps.\n\n')
## %%%%%%%%%%%%%%%%                                                
    parser_new.add_argument(
            '-id', '--msg_id',
            required=False, dest="msg_id", 
            help=f"R|{YELLIT}Required by the app only.{ENDC}. Not to be used.\n\n"
    )
# $$$$$$$$$$$$$$$$$$    
    parser_new.add_argument('message', help=f"R|{VIT}The message to be sent{ENDC}.")    
    parser_new.set_defaults(func=msg.send)
    
    # "Enable Task" sub command ------------------------------------------------------------
    parser_new = subparsers.add_parser(
            'enable',  
            help='R|Enable a previously disabled message task.\n\n'
            f'{GRYT}python{ENDC} {GRNT}{PROG_NAME}{ENDC} {TURT}enable{ENDC} <{VIT}messageID{ENDC}>\n'
            'Can be used to enable a message task that was previously disabled.\n\n',
            description=f'{YELLIT}Enable a task associated with a message{ENDC}.', formatter_class=SmartFormatter)
    
    parser_new.add_argument('msg_id', help=f"R|{VIT}The message to enable{ENDC}.\n"
                                           'Used to enacle a previously disabled message.')
    parser_new.set_defaults(func=msg.enable_task)

    # "Disable Task" sub command ------------------------------------------------------------
    parser_new = subparsers.add_parser(
            'disable',  
            help='R|Disable an active message task.\n\n'
                 f'{GRYT}python{ENDC} {GRNT}{PROG_NAME}{ENDC} {TURT}disable{ENDC} <{VIT}messageID{ENDC}>\n'
                  'Used to disable a message from sending.\n\n',
             description=f'{YELLIT}Disable a task associated with a message{ENDC}.', formatter_class=SmartFormatter)
    
    parser_new.add_argument('msg_id', help=f"R|{VIT}The message you want to enable{ENDC}.")
    parser_new.set_defaults(func=msg.disable_task)

    # "Run Task" sub command ------------------------------------------------------------
    parser_new = subparsers.add_parser(
            'run',  
            help='R|Run any message that is still alive. (Batch file and task still exists.)\n\n' 
                 f'{GRYT}python{ENDC} {GRNT}{PROG_NAME}{ENDC} {TURT}run{ENDC} <{VIT}messageID{ENDC}>\n'
                  'Send a mesage that was previously sent, again or any message still\n'
                  'living in the Task Scheduler\n\n'
                  ,
             description=f'{YELLIT}Run a task associated with a message{ENDC}.', formatter_class=SmartFormatter)
    
    parser_new.add_argument('msg_id', help=f"R|{VIT}The message you wish to run{ENDC}!")
    parser_new.set_defaults(func=msg.run_task)

    # "Recover Task" sub command ------------------------------------------------------------
    parser_new = subparsers.add_parser(
            'recover_tasks',  
            help='R|Recover one or more Tasks that may have been deleted from Windows Task Scheduler. \n'
                 'It can happen.\n\n' 
                 f'{GRYT}python{ENDC} {GRNT}{PROG_NAME}{ENDC} {TURT}recover_task{ENDC} <{VIT}messageID{ENDC}|{VIT}all{ENDC}>\n'
                  'MessageID can be one ID, more than one, or "all" to recover all. '
                  'Either the \nmessage_db.json or message_db.bck file must remain but the batch files will \nbe recreated, as needed. \n\n'
                  ,
             description=f'{YELLIT}Recover one or more tasks that have been deleted form WTS{ENDC}.', formatter_class=SmartFormatter)
    
    parser_new.add_argument('msg_id', nargs='*', help=f"R|{VIT}The message, or messages you wish to recover{ENDC}.\n\n"
                                            'You may enter the Messages ID one by one or all to recover all\n'
                                            'If the associated batch program is not alive it will be created.')
    parser_new.set_defaults(func=msg.recover_tasks)

    # "ReRun Task" sub command ------------------------------------------------------------
    parser_new = subparsers.add_parser(
            'rerun',  
            help='R|Re-run an expired message on the current day or other date.\n\n' 
                 f'{GRYT}python{ENDC} {GRNT}{PROG_NAME}{ENDC} {TURT}rerun{ENDC} <{VIT}messageID{ENDC}> '
                 f'[{YELLIT}--date{ENDC}|{YELLIT}-d{ENDC}] <{BLUET}date{ENDC}> [{YELLIT}-ru{ENDC}|{YELLIT}--user{ENDC}] '
                 f'<{BLUET}userid{ENDC}> [{YELLIT}-rp{ENDC}|{YELLIT}--pword{ENDC}] <{BLUET}pword{ENDC}>\n'
                  f'Will set the start date of an expired messsage to the current day unless \n'
                  f'specified with [{YELLIT}--date{ENDC}|{YELLIT}-d{ENDC}] .\n\n'
                  'User ID and Pword are required to modify a task. You can set these ahead ot \n'
                  'time in settings.json or add them at the command line.\n\n\n',
             description=f'{YELLIT}Rerun an expired task one more time{ENDC}.', formatter_class=SmartFormatter)

    parser_new.add_argument(
            '-d', '--date',
            required=False, dest="date", 
            help=f"R|{YELLIT}The date to set the task on..{ENDC}.If not specified, current date.\n\n"
    )
    parser_new.add_argument(
            '-ru', '--userid', metavar='userID', 
            required=False, dest="userid", 
            help=f"R|{YELLIT}Your User ID for this computer {ENDC}. Use if you don't want to\n "
                  "keep in the setttings file, or be prompted at modification.\n\n"
    )
    parser_new.add_argument(
            '-rp', '--pword', metavar='pword', 
            required=False, dest="pword", 
            help=f"R|{YELLIT}Your password for this computer.{ENDC}. Use if you don't want to\n "
                  "keep in the setttings file, or be prompted at modification.\n\n"
    )
    parser_new.add_argument('msg_id', help=f"R|{VIT}The message you wish to run{ENDC}!")
    parser_new.set_defaults(func=msg.rerun_message)
    
    # "Launch\Kill Responder sub command ------------------------------------------------------------
    parser_new = subparsers.add_parser(
            'responder',  
            help='R|Launches or kills the responder. \n\n'
                 f'{GRYT}python{ENDC} {GRNT}{PROG_NAME}{ENDC} {TURT}responder{ENDC} [{YELLT}-start{ENDC}|{YELLT}-stop{ENDC}]\n'
                  'Launches or kills the responder to listen for Email reponses. Responder is a \n'
                  'Standalone application that will disable any messages that are recurring when it\n'
                  'receives a stop message via Email.\n\n'
                  ,
             description=f'{YELLIT}Launches\kills the responder{ENDC}.', formatter_class=SmartFormatter)

    parser_new.add_argument(
            '-start', '--start', action='store_true',
            required=False, dest="start", 
            help=f"R|{YELLIT}Launch the responder{ENDC}.\n\n"
    )
    parser_new.add_argument(
            '-stop', '--stop',  action='store_true',
            required=False, dest="stop", 
            help=f"R|{YELLIT}Stop the responder{ENDC}.\n\n"
    )
    parser_new.add_argument(
            '-debug', '--debug',  action='store_true',
            required=False, dest="debug", 
            help=f"R|{YELLIT}Debug mode: allows you to get more info from the stop process.{ENDC}.\n\n"
    )
    parser_new.set_defaults(func=msg.control_responder)

    return parser



def main(args: list[str]=None) -> None:
    #try:
        if args is None:
                args = get_parser().parse_args()
                args.func(args) 

        """except AttributeError as er:
            print(er)
            print('This program must be ran with arguments from the command line.'
                  '\nUsage: stext [-h] for help') """     
    
    
if __name__ == "__main__":
    contacts = Contacts()
    msg = Message()
    main()
    