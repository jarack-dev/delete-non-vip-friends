import logging
import sys
import tkinter as tk
from tkinter import ttk

import sv_ttk
from tktooltip import ToolTip

logger = logging.getLogger("delete_non_vip_friends")
supported_languages = "english", "japanese", "chinese"
selected_language = ""
is_debug_mode = False
use_image_gen_end_condition = False
id_file = "vip_ids.txt"


def initialize_logger():
    global logger
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s: %(message)s")
    error_log = logging.FileHandler("error.log")
    debug_log = logging.FileHandler("debug.log")
    error_log.setFormatter(formatter)
    debug_log.setFormatter(formatter)
    debug_log.setLevel(logging.DEBUG)
    error_log.setLevel(logging.ERROR)
    logger.addHandler(error_log)
    logger.addHandler(debug_log)


def get_line_count(file_path):
    with open(file_path, 'r') as fp:
        lines = len(fp.readlines())
        return lines


def validate_file():
    global id_file
    with open(id_file, 'r') as file:
        for line in file:
            line = line.strip().replace("-", "")  # allowing hyphens
            if line and not line.isdigit():
                logger.error("the id file was not formatted correctly, please make sure it only contains ids (hyphens "
                             "are okay)")
                sys.exit()


def get_user_options():
    root = tk.Tk()
    root.eval('tk::PlaceWindow . center')
    root.title("Remove Non-Vip Friends")
    root.geometry('400x250')
    text = tk.Label(root, text="Select a Language", pady=10)
    text.pack()

    def set_language(_event):
        global selected_language
        input_language = language_select.get()
        if input_language != "":
            selected_language = input_language
            submit_button.state(["!disabled"])

    language_select = ttk.Combobox(root, state="readonly", values=supported_languages)
    language_select.bind("<<ComboboxSelected>>", set_language)
    language_select.pack()

    debug_checkbox = ttk.Checkbutton(text="Debug Mode")
    debug_checkbox.pack(pady=10)
    debug_checkbox.state(['!alternate'])

    image_gen_end_condition_checkbox = ttk.Checkbutton(text="(Experimental) Delete Till End")
    image_gen_end_condition_checkbox.pack(pady=10)
    image_gen_end_condition_checkbox.state(['!alternate'])

    tooltip = ToolTip(image_gen_end_condition_checkbox, msg="Usually the script will stop when the number of friends matches the amount of people "
                                 "in id file. This option will take a screenshot every time it scrolls, and it will "
                                 "determine its the end of the list if the two screenshots are similar enough")

    frame = tk.Frame(root)
    frame.pack(padx=10, pady=10, expand=True)

    def get_selected_option():
        global is_debug_mode, use_image_gen_end_condition
        is_debug_mode = debug_checkbox.instate(["selected"])
        use_image_gen_end_condition = image_gen_end_condition_checkbox.instate(["selected"])
        root.destroy()

    cancel_button = ttk.Button(frame, text="Cancel", command=sys.exit)
    submit_button = ttk.Button(frame, text="Ok", command=get_selected_option)
    submit_button.state(["disabled"])
    cancel_button.pack(side=tk.LEFT, padx=10)
    submit_button.pack(side=tk.RIGHT, padx=10)
    sv_ttk.set_theme("dark")
    root.mainloop()
