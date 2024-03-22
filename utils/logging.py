import traceback
import sys
import platform
import os

os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
import torch
from colorama import Fore
from colorama import Style
from datetime import datetime

os.system("color")  # Add colors to Terminal output

# * Format Custom System Messages for Terminal


def template(
    *, message_type="", color_of_type=Fore.BLUE, content="", dependency="", args=""
):
    now = datetime.now()
    dt_string = now.strftime("%d-%m-%Y %H:%M:%S")
    date_time = f"{Style.BRIGHT}{dt_string}{Style.RESET_ALL}"
    print(
        f"{date_time} {Style.BRIGHT}{color_of_type}{message_type}{Style.RESET_ALL} {Fore.MAGENTA}{dependency}{Style.RESET_ALL} {content}"
    )


def warning(warning, dependency="", *args):
    template(
        message_type="WARNING  ",
        color_of_type=Fore.YELLOW,
        content=warning,
        dependency=dependency,
    )


def error(error, dependency="", *args):
    template(
        message_type="ERROR    ",
        color_of_type=Fore.RED,
        content=f"{error}\n\n{Fore.RED}{traceback.format_exc()}",
        dependency=dependency,
    )


def info(info, dependency="", *args):
    template(
        message_type="INFO     ",
        color_of_type=Fore.BLUE,
        content=info,
        dependency=dependency,
    )


def system(system_info, dependency="", *args):
    template(
        message_type="SYSTEM  ",
        color_of_type=Fore.GREEN,
        content=system_info,
        dependency=dependency,
    )


def system_info(dependency=f"Python", *args):
    system_info = f"\nUsing Python {sys.version}\n{platform.system()} {platform.release()}\n{platform.version()}\n{platform.machine()}\nNumber of CPU threads: {torch.get_num_threads()}"
    template(
        message_type="SYSTEM   ",
        color_of_type=Fore.GREEN,
        content=system_info,
        dependency=dependency,
    )
