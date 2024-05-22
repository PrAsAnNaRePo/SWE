import os
import sys
import base64
from colorama import Fore, Style
from rich.markdown import Markdown
from rich import print as Print

def assistant_message(msg):
    Print(Markdown(f"{Fore.YELLOW}{Style.BRIGHT}🤖 {Fore.YELLOW}{msg}{Style.RESET_ALL}"))

def internal_monologue(msg):
    Print(f"{Fore.LIGHTBLACK_EX} {msg}{Style.RESET_ALL}")

def token_usages_message(msg):
    Print(f"{Fore.LIGHTMAGENTA_EX} {msg} {Style.RESET_ALL}")

def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')

def clear_line():
    if os.name == "nt":
        console.print("\033[A\033[K", end="")
    else:
        sys.stdout.write("\033[2K\033[G")
        sys.stdout.flush()