#contacts.py

# data functions
from utility import (
    phone_exists,
    write_data,
    load_data,
    warn_or_continue,
    contact_exists,
    group_exists,
    contacts_header
)

from providers import PROVIDERS
from tabulate import tabulate
from constants import * # shared in entirety between messgae.py and contacts.py 

class Contacts:
    """Contacts Handles all actions related to contacts"""

    def __init__(self):
        # Connect to the Groups class
        self.groups: object = self.Groups()
        
    def add_new(self, args: object ) -> None:
        """ adds a new contact to the contacts database.
        Args:
            name (str): Name
            phone (str): phone number
            provider (str): the cell provider
            group (str, optional): The group if any contact is apart of. 
                                   Can be set at contact creation.
                                   Defaults to None.
        """         
        # Contacts cannot exist witht he same Name or phone number.
        _contact_name:  str = args.name.title() 
        _phone_num:     str = args.phone 
        _provider_name: str = args.provider.title()
        _group:  str | None = args.group.upper() if args.group is not None else None

        contacts_info:  list[list[str]] = load_data(CONTACTS_DB)   

        if (not self.__validate( 
               _phone_num=_phone_num, 
               _provider=_provider_name
               )
           ):
            return
        
        if (contact_exists(contacts_info, _contact_name)):  
            print(f"{YELLT}\nCannot have more than one contact with the same name.{ENDC}")
            return

        # check to see if thes phone # is unique.
        if (phone_exists(contacts_info, _phone_num)):
            print(f"{YELLT}\nCannot have more than one contact with the same phone.{ENDC}")
            return

        if (_group is not None): 
           if (not group_exists(contacts_info, _group, output=False)):
               print(f'GROUP: {BLUET}{_group}{ENDC} does not exist.\n'
                     f'{YELLT}\nA group must contain two or more contacts{ENDC}.')
               return
               
        new_contact: list = [
            _contact_name,
            _phone_num,
            _provider_name,
            _group,
            []     # list used to hold any messages when a contact is in a group
        ]          # list is only utilized if a group message is created so if the user decides to 
                   # stop the message it does not effect the other members. 

        contacts_info.append(new_contact)      
        write_data(contacts_info, CONTACTS_DB) 
        
        print(f'Contact created for: "{BLUET}{_contact_name}{ENDC}"')
#-------------------------------------------------------------------------------------------------------------------------------------------
    def del_contact(self, args: list):
        """Deletes one or all contacts in contacts database""" 
        #TODO: Upgrade this method to take a one OR more contacts
        # as done in the message class.
        _contact_name: str = args.name.title()

        contacts_info: list[list[str]] = load_data(CONTACTS_DB)
        found: bool = False

        if ( not contact_exists(contacts_info, _contact_name) and 
            _contact_name != 'all'
           ):
            print(f'Conact: "{BLUET}{_contact_name}{ENDC}" {YELLT}not found{ENDC}.')
            return

        if warn_or_continue(
                f'You are about to delete {_contact_name} from contacts.'
            ):
            if (_contact_name.lower() == 'all'):
                del contacts_info[:len(contacts_info)] 
                print(f"{YELLT}All Contacts Deleted.{ENDC}")
            else:
                for contact in contacts_info:
                   if _contact_name == contact[NAME]:
                       contacts_info.remove(contact)
                       found = True
                       break
            if (found):
                print(f'"{BLUET}{contact[NAME]}{ENDC}" {YELLT}deleted.{ENDC}')  
            
            write_data(contacts_info, CONTACTS_DB)
        else:
            print(f'{YELLT}Delete Aborted{ENDC}.')        
#-------------------------------------------------------------------------------------------------------------------------------------------
    def mod_contact(self, args: object) -> None:
        """ Change the contact name, Number, provider or group
            contact_id is used to id the contact being modded
            User can also change the contact to a different name      

        """
        #user cannot modify a contact to have the same name or number has another
        # user 

        _contact_name:  str = args.contact_id.title()
        _name:     str|None = args.name.title() if args.name is not None else None
        _number:   str|None = args.phone_number
        _provider: str|None = args.provider.title() if args.provider is not None else None
        _group:    str|None = args.group.upper() if args.group is not None else None
        
        contacts_info: list[list[str]] = load_data(CONTACTS_DB)        
        found: bool
        valid_info: bool

        # make sure user gave me something, anything to work with.
        if (_name is None and 
            _number is None and 
            _provider is None and 
            _group is None
           ):
            print(f'\n{YELLT}You must enter the property of the contact you wish to modify{ENDC},'
                  f'\nName, Provider, Phone and/or Group. ' )          
            return
    
        if (not contact_exists(contacts_info, _contact_name)):
            print(f'\nContact: "{BLUET}{_contact_name}{ENDC}"{YELLT} does not exist.{ENDC}')
            return

        if (_name is not None):
            if (contact_exists(contacts_info, _name)):
                print(f"\n{YELLT}Cannot change to a name that already exists.{ENDC}")
                return                

        if (_number is not None):
            if (phone_exists(contacts_info, _number)):
                print(f"\n{YELLT}Phone numbers are unique to each contact.{ENDC}")
                return      

        found, valid_info, contacts_info = self.__update_contact(
                contacts_info, 
                _contact_name, 
                _name,
                _number, 
                _provider,
                _group
        )       
        if (found and valid_info):
            write_data(contacts_info, CONTACTS_DB)
            print(f'\nUpdated contact info for: {BLUET}{_contact_name}{ENDC}'
                  f'\n\nContact information modifications:')

            # Depending on what the user has modified, name may not be changed  so
            # report using the correct contact info.                
            if (_name is not None):      
                self.view_contact(_name)
            else:
                self.view_contact(_contact_name)

        elif (not found):
            print(f'\nContact info for: "{BLUET}{_contact_name}{ENDC}" {YELLT}not found{ENDC}.') 
        elif (not valid_info):
            print(f'\nFailed to Update Contact info for: "{BLUET}{_contact_name}{ENDC}".') 
#-------------------------------------------------------------------------------------------------------------------------------------------
    def view_contact(self, args: object):
        """View one or all contacts by name. 
        Args:
            args (object): command line arguments
            contact_name (str): The contact to view, or all to view all. 
        """
        # enables this method to be called from inside the application
        try:
           contact_name: str = args.name.title()
        except:
           contact_name = args   
         
        contact_info: list[list[str]] = load_data(CONTACTS_DB)
        found: bool = False

        if (len(contact_info) < 1):
            print(f'\n{YELLT}No contacts to view{ENDC}.')
            return

        if (contact_name.lower() == 'all'):
            # view em all      

            # go through ebery contact and remove the dict
            # so it is not visible
            
            contacts_header.extend(contact_info)
            print('\n'+tabulate(contacts_header, headers='firstrow'))            
        else:
            # view this contact
            for contact in contact_info:                
               if (contact_name == contact[NAME]):                   
                   contacts_header.append(contact) # [:-1]skip the dictionary
                   print('\n'+tabulate(contacts_header, headers='firstrow'))
                   found = True

            if (not found): 
                print(f"\nNo message found for " 
                      f'"{YELLT}{contact_name}{ENDC}".')         
#-------------------------------------------------------------------------------------------------------------------------------------------
    def set_default_contact(self, args: object) -> None:
        """Sets the default contact"""
        _def_contact: str = args.name.title()

        contact_info: list[list[str]] = load_data(CONTACTS_DB)

        if contact_exists(contact_info, _def_contact):
            # if the name is in the contacts, 
            # rewrite the contacts with the name at the top.
            for pos, contact in enumerate(contact_info):    
                if contact[NAME] == _def_contact:
                    contact_info.insert(0, contact_info.pop(pos))  

            write_data(contact_info, CONTACTS_DB)  
            print(f'Contact: "{YELLT}{_def_contact}{ENDC}" is now the default contact.')  
        else:
            print(f'Contact: "{BLUET}{_def_contact}{ENDC}" {YELLT}not found{ENDC}.')
#-------------------------------------------------------------------------------------------------------------------------------------------       
    def __update_contact(self, 
        _contacts_info: list[list[str]], 
        _contact_name: str, _name: str, 
        _number: str, _provider: str,
        _group: str
        ) -> tuple[bool, bool, list[list[str]]]:
        """Updates the contacts_info list according to a users modification prefs. 
        Arguments:
            _contacts_info -- The list of contacts info.
            _contact_name -- The name of the contact being moded.
            _name -- The New Name, if being changed.
            _number -- The new phone if being changed.
            _provider -- The New provider if being changed.
            _group -- The new group if being changed.

        Returns:
             A tuple divided into 3 values:
             list[bool, bool, list[list[str]]] 
             found
             valid_info
             _contacts_info
        """
        found: bool = False
        valid_info: bool = True

        for contact in _contacts_info:
            if contact[NAME] == _contact_name:
                # of all items that are applicable, validate only the ones to be altered
                if (_name is not None):        
                        contact[NAME] = _name 
                if (_number is not None ): 
                    if (self.__validate(_phone_num=_number)):
                        contact[PHONE_NUMBER] = _number 
                    else:
                        valid_info = False    
                if (_provider is not None): 
                    if (self.__validate(_provider=_provider)):
                        contact[PROVIDER] = _provider
                    else:
                        valid_info = False    
                if (_group is not None): 
                        if (group_exists(_contacts_info, _group, output=False)):
                           contact[GROUP_NAME] = _group
                        else:
                           print(f"\nGROUP: {BLUET}{_group}{ENDC}{YELLT} does not exist.{ENDC}")   
                           return 
                found = True        
                break    

        return (found, valid_info, _contacts_info)
#-------------------------------------------------------------------------------------------------------------------------------------------       
    def __validate(self, _phone_num: str=None, _provider: str=None) -> bool:
        """ Checks the contact info for formatting errors and reports any found. """
         #prefix: str = _phone[3:6]
         #line_num: str = _phone[6:]
        
        res: bool = True    
        # cannot be empty strings
        # wrong length 
        if (_phone_num is not None):                                
            area_code: str = _phone_num[:3]
            try:
                # only allow digits
                if (area_code[0] == "1"):
                    print(f"({YELLT}Phone numbers cannot start with 1.{ENDC})")
                    res = False
                    
                if (len(_phone_num) != 10):
                    print(f"({YELLT}Phone number must be 10 digits only.{ENDC})")
                    res = False
                if (int(area_code) < 200 or int(area_code) > 999):
                    print(f"({YELLT}Invalid Phone Number{ENDC}: Area code must be " 
                          f"between 200 and 999.)")
                    res = False
            except ValueError:
                print(f'({YELLT}Phone number may contain only digits.{ENDC})')                
                res = False

        if (_provider is not None):
            accepted_providers: list[str] = [pro for pro in PROVIDERS.keys()]
            provider_list: str            = "".join([pro+'\n' for pro in PROVIDERS.keys()])
            
            if (_provider.title() not in accepted_providers):                
                print(f"{YELLT}Incorrect Provider Name or Provider Not Found.{ENDC}")
                print(f"\n{BLUET}Currently Accepted Providers are{ENDC}: \n\n{provider_list}")
                print(f'\n{YELLT} If your provider is{ENDC} {BLUET}AT&T{ENDC}'
                      f'\n{YELLT} Be sure to wrap it in quotes when creating a contact.{ENDC}')
                res = False

        return res

#-------------------------------------------------------------------------------------------------------------------------------------------
## CLASS GROUPS
#-------------------------------------------------------------------------------------------------------------------------------------------

    class Groups:
        """Groups handles all actions related to Groups
        Groups are ofcourse groups of contacts. The Groups class is 
        instantiated when the contacts class is to tie the 2 together."""
        
        def make_group(self, args: list) -> None:
            """ Creates a group when 2 or more contacts are added
                _group_name       (str): The group to make
                _members    (list[str]): A list of at least 2 conacts to add to the group

            """
            # command line args            
            _group_name: str = args.group_name.upper()
            _group_members: list[str] = [name.title() for name in args.contacts]              
            
            contacts_info: list[list[str]] = load_data(CONTACTS_DB)    
            contact_names: list[str] = [contact[NAME] for contact in contacts_info]   
            false_contacts: bool = False            
            
            # make sure case matches case:
            #_group_members = [name.title() for name in _group_members if name is not None]

            if len(_group_members) < 2:
                print(f"{YELLT}You need at least two contacts to create a group.{ENDC}")
                return                      
                      
            # Make sure that a group were trying to make does not already exists    
            # and make sure that the group members being added to the new group dont already habe a group      
            if (not group_exists(contacts_info, _group_name) and 
                not self.__contacts_have_group(contacts_info, _group_members) 
                ):
                
                for contact in _group_members:
                    if contact.title() not in contact_names:                      
                        print(f'Contact "{BLUET}{contact}{ENDC}" does not exist. {YELLT}Cannot add to group{ENDC}.') 
                        false_contacts = True
                if false_contacts: return

                # edit the group item of the ones in the contacts list
                for contact in contacts_info:
                    if contact[NAME] in _group_members:
                        contact[GROUP_NAME] = _group_name    
                        print(f'Contact: "{BLUET}{contact[NAME]}{ENDC}" added in creation of {BLUET}{_group_name}{ENDC}.') 
                        
                write_data(contacts_info, CONTACTS_DB)
            """else:
                print("Either the group already exists, or a contact being added to the group is already in a group.")"""


#===========================================================================================================================================
## PUBLIC Group Modification Method: 
#===========================================================================================================================================

        def add2group(self, args: object) -> None:
            """ Adds one or more contacts to an existing group"""
            _group_name: str = args.group.upper()
            _contacts: list[str] = [contact.title() for contact in args.contacts] # Make sure the names are capitlized.

            contacts_info: list[list[str]] = load_data(CONTACTS_DB)
            self.__add_contacts2group(contacts_info, _contacts, _group_name)

            write_data(contacts_info, CONTACTS_DB)
#-------------------------------------------------------------------------------------------------------------------------------------------
        def remove_from_group(self, args: object) -> None:
            """ 
            Removes one or more contacts from a group. also deals with the issue
            of leaving one contact in  a group when deleting members from a group
            """
            _group_name: str = args.group.upper()            
            _contact_names: list[str] = [contact.title() for contact in args.contacts]
            
            del_all: bool
            contacts_to_delete: list[str]
            contacts_info:  list[list[str]] = load_data(CONTACTS_DB)
            
            if (not self.__validate_remove_from_group_input(
                    _group_name, 
                    _contact_names, 
                    contacts_info
                  )
               ):
               return            

            # See if this action will leave group with one member.
            del_all, contacts_to_delete = self.__handle_odd_man_out(
                contacts_info,
                _contact_names, 
                _group_name
            )
            # if there was an odd man out, and user wants to delete all contacts
            if del_all == True:
                _contact_names = contacts_to_delete   
                contacts_info = self.__remove_group_contacts(contacts_info, _contact_names, _group_name)
            # Normal delete action. delete members as usual.
            elif del_all == False and contacts_to_delete is None:
                contacts_info = self.__remove_group_contacts(contacts_info, _contact_names, _group_name)
            # Aborted    
            elif del_all is None and contacts_to_delete is None:
                print(f'{YELLT}Contact Removal Aborted{ENDC}.')
                
            write_data(contacts_info, CONTACTS_DB)
#-------------------------------------------------------------------------------------------------------------------------------------------
        def change_group(self, args: object) -> None:
            """ Changes the name of an existing group."""
            _old_group: str = args.group.upper()
            _new_group: str = args.new_group_name.upper()

            contacts_info: list[list[str]] = load_data(CONTACTS_DB)
            contacts_info = self.__change_group(contacts_info, _old_group, _new_group)

            write_data(contacts_info, CONTACTS_DB)
#-------------------------------------------------------------------------------------------------------------------------------------------
        def wipe_groups(self, args: object=None) -> None:
            """ Wipes all contacts of their group. """
            contacts_info: list[list[str]] = load_data(CONTACTS_DB)

            if warn_or_continue(
                    'You are about to wipe all contacts of all groups.'
                 ):
                 for contact in contacts_info:
                     contact[GROUP_NAME] = None

            write_data(contacts_info, CONTACTS_DB)         
            print(f'\n{REDT}Wiped:{ENDC} All contacts of any group.')
#-------------------------------------------------------------------------------------------------------------------------------------------
        def ass_groups(self, args: object) -> None:
            """
            Assimilates all contacts to one group. Group does not have to exist prior.
            In effect will make  a new group. Rules get a bit fuzzy on this so letting this one slide.
            Just makes it faster to use any name for a group rather than following the same rules as normal
            for creating a new group.
            """
            _group_name:       str = args.group.upper()
            contacts_info: list[list[str]] = load_data(CONTACTS_DB)
            
            if warn_or_continue(
                    f'You are about to assimilate all contacts to Group: {BLUET}{_group_name}{ENDC}'
                ):  
                # put in a simple loop and contact[GROUP] = _group_name. 
                for contact in contacts_info:
                    contact[GROUP_NAME] = _group_name

                print(f'\nAssimilated: {YELLT}All{ENDC} contact groups to {BLUET}{_group_name}{ENDC}')
                write_data(contacts_info, CONTACTS_DB)  
            else:
                print('\nDid Nothing.')
#-------------------------------------------------------------------------------------------------------------------------------------------
        def delete(self, args: object):
            """
            Deletes a contacts group.
            """
            _contact_name: str = args[0]            

            contacts: list[list[str]] = load_data(CONTACTS_DB)
            for contact in contacts:            
                if contact[NAME] == _contact_name.title():
                    if contact[GROUP_NAME] == None:
                        print(f'Contact: "{BLUET}{contact[NAME]}{ENDC}" is already void of a group.')
                    else:    
                        print(f'Deleted: "{BLUET}{contact[NAME]}{ENDC}" from ' 
                              f'the {BLUET}{contact[GROUP_NAME]}{ENDC} group.')
                        contact[GROUP_NAME] = None
                        write_data(contacts, CONTACTS_DB)                
#-------------------------------------------------------------------------------------------------------------------------------------------
        def view_by_group(self, args: object):
            """View the contacts in a particular group """
            _group_name: str = args.group_name.upper()
            # gather up the contact information of the contacts in the group
            contacts: list[list[str]] = load_data(CONTACTS_DB)            
            
            group_members: list[str] = [
                contact for contact in contacts 
                if contact[GROUP_NAME] == _group_name.upper()
            ]            
            if len(group_members) < 2:
                print(f'\n{BLUET}{_group_name}{ENDC} {YELLT}does not exist{ENDC}.')
            else:
                contacts_header.extend(group_members)
                print('\n'+tabulate(contacts_header, headers='firstrow')+'\n')

#-------------------------------------------------------------------------------------------------------------------------------------------
## Group PRIVATE METHODS:
#-------------------------------------------------------------------------------------------------------------------------------------------
        def __validate_remove_from_group_input(self, 
            _group_name: str, 
            _contact_names: list[str], 
            _contacts_info: list[list[str]]) -> bool:
            """Makes sure all input is valid for the "remove_from_group method to proceed. """

            if not group_exists(_contacts_info, _group_name, output=False):
                print(f'Group: {BLUET}{_group_name}{ENDC} {YELLT}does not exist{ENDC}.')
                return False

            for contact in _contact_names:            
                if not contact_exists(_contacts_info, contact):
                    print(f"Contact: '{BLUET}{contact}{ENDC}' {YELLT}doesn't exist{ENDC}.")
                    return False
            
            # make sure all contacts being removed are in the same group
            if not self.__contacts_in_same_group(_contacts_info, _group_name, _contact_names):
                print(f'\nNot all the contacts entered belong to Group: {BLUET}{_group_name}{ENDC}.'
                      f"\n{YELLT}Can't remove contacts.{ENDC}")
                return False
            
            # make sure all the contacts in the list of contacts to remove indeed have a group.
            # if one is void, then it could offset the members and possibly leave one.
            for contact in _contacts_info:
                if contact[NAME] in _contact_names:
                 if contact[GROUP_NAME] is None:
                    print(f'"{BLUET}{contact[NAME]}{ENDC}" is already void of a group.'
                          '\nThis action could leave only one member in a group.' 
                          f'\n{YELLT}Aborting...{ENDC}')
                    return False

            return True
#-------------------------------------------------------------------------------------------------------------------------------------------
        def __contacts_in_same_group(self,
            _contacts_info: list[list[str]],
            _group: str, 
            _contacts: list[str]) -> bool:
            """ True if the these contacts belong to THIS group"""
            for contact in _contacts_info:
                if contact[NAME] in _contacts and contact[GROUP_NAME] != _group:
                    return False
            return True        
#-------------------------------------------------------------------------------------------------------------------------------------------
        def __contacts_have_group(self,
            _contact_info: list[list[str]], 
            _group_members: list[str|None],
             verbose: bool=True
             ) -> bool:
            """CHecks a list of contacts to see they already belong to a group
            if verbose is false, then the method will not report the findings"""

            has_group: bool = False
            for contact in _contact_info:
                if contact[NAME] in _group_members and contact[GROUP_NAME] is not None:
                    if verbose:
                        print(f'"{BLUET}{contact[NAME]}{ENDC}" already belongs to {BLUET}{contact[GROUP_NAME]}{ENDC}.')
                    has_group = True               
            return has_group
#------------------------------------------------------------------------------------------------------------------------------------------- 
        def __remove_group_contacts(self, 
            _contacts_info: list[list[str]], 
            _contact_names: list[str], 
            _group_name: str
            ) -> list[list[str]]:
            # deletes the contacts group if it is not none.
            # and if it matches the group name  
            for contact in _contacts_info:                
                if contact[NAME] in _contact_names:
                    if contact[GROUP_NAME] is not None and contact[GROUP_NAME] == _group_name:
                        print(f'Removed: "{BLUET}{contact[NAME]}{ENDC}" from {BLUET}{contact[GROUP_NAME]}{ENDC}') 
                        contact[GROUP_NAME] = None   
                    else:
                        print(f'{BLUET}{contact[NAME]}{ENDC} is already {YELLT}void of a group{ENDC}.')          

            return _contacts_info
#-------------------------------------------------------------------------------------------------------------------------------------------
# TODO Should change this to only add one at at time and loop into it

        def __add_contacts2group(self, 
                 _contacts_info: list[list[str]], 
                 _contact_names: list[str], 
                 _group_name: str) -> list[list[str]]:
            """adds one or more contacts to a group.  """
            
            for contact in _contact_names:
                if not contact_exists(_contacts_info, contact):
                    print(f'{BLUET}{contact}{ENDC} {YELLT}not found{ENDC}.') 
                    return

            # make sure the group exists already.
            for contact in _contacts_info:
                if contact[NAME] in _contact_names:                    
                    if group_exists(_contacts_info, _group_name, output=False):
                        contact[GROUP_NAME] = _group_name
                        print(f'Added: "{BLUET}{contact[NAME]}{ENDC}" to {BLUET}{_group_name}{ENDC}.')
                    else:
                        print(f'\nGroup: {BLUET}{_group_name}{ENDC} Does not exist.\n'
                                'Cannot add a contact to a group that does not exist.')                        
            return _contacts_info
#-------------------------------------------------------------------------------------------------------------------------------------------        
        def __change_group(self, 
            _contacts_info: list[list[str]] , 
            _group_name: str,
            _new_group_name: str
            ) ->  list[list[str]]:

            if _group_name is None:
                print(f'\nYou must enter the {BLUET}group name{ENDC} you are changing from to change groups.')  
            if _new_group_name is None:
                print(f'\nYou must enter the {BLUET}new group name{ENDC} you are changing to.')     
            else:
                for contact in _contacts_info:
                    if contact[GROUP_NAME] == _group_name:
                        contact[GROUP_NAME] = _new_group_name
                
                print(f'\nGroup: {BLUET}{_group_name}{ENDC} changed to '
                      f'Group: {BLUET}{_new_group_name}{ENDC}')

            return _contacts_info
#-------------------------------------------------------------------------------------------------------------------------------------------
        def __handle_odd_man_out(self, 
            _contacts_info: list[list[str]],  
            _members_to_remove: list[str],
            _group_name: str) -> tuple[bool|None, list[str] | None]:
            """
            Groups not allowed to have one memeber. ask user to Decide the action to take if one will be left.
            If the user selects yes, then the names of all group members are returned as all_group_contacts so 
            they can all be removed. If No then all_group_contactst is returned with both members set to None 
            to abort the  delete. If there is not a problem with the odd man out, the delete goes on as normal
            """
                 
            total_members_being_removed:  int  = len(_members_to_remove)
            total_members_in_group:       int  = 0
            delete_all:                   bool = False   # assume will be a normal delete with no odd man out
            all_group_contacts:      list[str] = []
            
            
            for contact in _contacts_info:
                if contact[GROUP_NAME] == _group_name:
                    total_members_in_group += 1
                    all_group_contacts.append(contact[NAME])
                    
            # odd man out detected
            if (total_members_in_group - total_members_being_removed) == 1:
                if warn_or_continue(f'{YELLT}This action will leave only one member in Group{ENDC}: {BLUET}{_group_name}{ENDC}.'
                                   f'\n{YELLT}All members of Group{ENDC}: {BLUET}{_group_name}{ENDC} {YELLT}will be '
                                   f'removed if you continue...{ENDC}\n'):
                     delete_all = True
                else:
                    # Abort the delete
                    delete_all = None
                    all_group_contacts = None      
            else:
                 # normal delete, no odd man out
                 all_group_contacts = None
                 
            return (delete_all, all_group_contacts)
#-------------------------------------------------------------------------------------------------------------------------------------------
# DRIVER CODE TO TEST CLASS
if __name__ == "__main__":
    pass
  
    