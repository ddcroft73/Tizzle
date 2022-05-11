# Constants.py

from os.path import(
     dirname as os_dirname,
     realpath as os_realpath,
     join as os_join
)

REDT:  str =  '\033[31m'
YELLT: str = '\033[33m'
YELLIT: str = '\033[33;3m'
BLUET: str = '\033[34m'
ENDC:  str = '\033[m' 
GRNT:  str = '\033[92m'
VIT:   str = '\033[35m'
TURT: str = '\033[96m'
GRYT: str = '\033[90m'

LINE_BREAK: str = 'BREAK'

# Absolute paths to all files used:
PROG_NAME:       str = 'tizz.py'
BAT_DIR :        str = 'batch'
SETTINGS_DIR:    str = 'settings'
DB_DIR:          str = 'db' 
SRC_DIR:         str = 'src'
PROG_DIR:        str = os_dirname(os_realpath(__file__))                               # == ./src
MAIN_DIR:        str = '\\'.join(PROG_DIR.split('\\'))[:-len(SRC_DIR)-1]               # == The parent(main) directory of the entire application.
DB:              str = os_join(MAIN_DIR, DB_DIR,       "message_db.json")
SETTINGS_FILE:   str = os_join(MAIN_DIR, SETTINGS_DIR, "settings.json")
CONTACTS_DB:     str = os_join(MAIN_DIR, DB_DIR,       "contacts.json")

# Access to the data in the json database 
# All are not used, but defined just in case
DEFAULT_CONTACT: int = 0

ID:              int = 0
MESSAGE:         int = 1
DESTINATION:     int = 2
SEND_TIME_DATE:  int = 3 
END_DATE:        int = 4 
CREATED:         int = 5
FREQUENCY:       int = 6
STATUS:          int = 7

# access to contact information
NAME:            int = 0
PHONE_NUMBER:    int = 1
PROVIDER:        int = 2   
GROUP_NAME:      int = 3
MSG_LIST:        int = 4

SUCCESS:         int = 0
CONTACT:         int = 1
GROUP:           int = 2


# Edit for the location of responder files.
RESPONDER_DIR:   str = r'C:\projects\python\Responder'
RESPONDER_PROG:  str = 'main.py'
RESPONDER_LOG:   str = os_join(RESPONDER_DIR, 'responder.log')
RESPONDER:       str = os_join(RESPONDER_DIR, RESPONDER_PROG)       