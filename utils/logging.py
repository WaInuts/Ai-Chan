import traceback
import sys
from colorama import Fore
from colorama import Style
from datetime import datetime

# * Format Custom System Messages for Terminal
now = datetime.now()
dt_string = now.strftime("%d-%m-%Y %H:%M:%S")
date_time = f"{Style.BRIGHT}{dt_string}{Style.RESET_ALL}"

def error(error, dependency="", *args):
    print(f"{date_time} {Fore.RED}ERROR:{Style.RESET_ALL} {Fore.MAGENTA}{dependency}{Style.RESET_ALL} {error}\n\n{Fore.RED}{traceback.format_exc()}")

def info(info, dependency="", *args):
    print(f"{date_time} {Fore.BLUE}INFO:{Style.RESET_ALL} {Fore.MAGENTA}{dependency}{Style.RESET_ALL} {info}")