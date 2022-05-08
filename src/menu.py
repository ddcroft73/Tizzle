# OOD Menu

# User runs program and is displayed with a 4 choice menu
# WHen user enters a Nimber the menu choice is redered
# 
# I wnat the command to be in the list\dicct so that it is esxcuted directly   

# display a menu from a list, 
from typing import Callable


class Menu():
    choice: str|None = None
    '''
      Display one of 2 menus depending on
    '''

    def __init__(self, menu_one: list[str], menu_two: list[str], id: str):
        self.menu_one = menu_one[:]
        self.menu_two = menu_two[:]
        self.id = id

    def __display_menu(self, id: str) -> None:
        # print the menu
        pass
     

if __name__ == "__main__":

    _msg = 'This is a message to be used as a test... nigga.'

    def insert_stop_message(msg_id_: str, freq_: str) -> str:
        '''
        Decides if a message needs to be flagged with a stop message
        and appends if needed.
        '''
        new_message: str
        break_message: str = f'\n\nReply "Stop {msg_id_}" to disable this text.'
        
        if ('EVERY' in freq_ or freq_ in ['DAILY', 'WEEKLY', 'MONTHLY']):
            new_message = _msg + break_message
        else: new_message = _msg    

        return new_message

    _msg =  insert_stop_message('m0123', 'DAILY')   
    print(_msg)

   # menu = Menu()
    