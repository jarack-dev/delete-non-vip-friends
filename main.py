# import mouseinfo
import os
import signal
import sys
import time
import pytesseract
import pyautogui
import re
from PIL import ImageGrab, ImageEnhance
from pynput import keyboard
from difflib import SequenceMatcher
import importlib
import setup
from setup import get_user_language, get_line_count, initialize_logger, validate_file

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
pyautogui.PAUSE = 1
script_paused = False

coordinates = {
    "friendCount": {
        "english": (125, 110, 146.15, 130),
        "japanese": (85.5, 110, 105, 130),
        "chinese": ()
    },
    "friendCode": (175, 70, 270, 95),
    "goToFriend": (150, 200),
    "removeFriend": (150, 410),
    "confirmDeleteFriend": (200, 370),
    "clickOutOfProfile": (140, 510),
    "betweenFriendSpace": (135, 235),
}


def get_resize_resolution(is_square):
    selected_language = setup.selected_language
    if selected_language == "english":
        return (200, 200) if is_square else (400, 100)
    elif selected_language == "japanese":
        return (200, 200) if is_square else (400, 100)
    elif selected_language == "chinese":
        return (200, 200) if is_square else (400, 100)


def convert_screenshot_to_string(ss_name, ss_coordinates, is_square, psm=7):
    logger = setup.logger
    resize_resolution = get_resize_resolution(is_square)
    screenshot = ImageGrab.grab(bbox=ss_coordinates).resize(resize_resolution)
    enhanced_screenshot = ImageEnhance.Contrast(screenshot).enhance(3)
    parsed_text = pytesseract.image_to_string(enhanced_screenshot, lang='eng', config=f'--psm {psm}')

    if setup.is_debug_mode:
        screenshot.save(ss_name + '.png')
        enhanced_screenshot.save(ss_name + "_enhanced.png")
        logger.info(f"parsed text: {parsed_text}")
        logger.info(f"level of confidence: {pytesseract.image_to_data(enhanced_screenshot, lang='eng', config=f'--psm {psm}', output_type='dict')['conf']}")
    return parsed_text


def is_vip_friend(filePath, friend_code):
    logger = setup.logger
    with open(filePath, 'r') as file:
        for line in file:
            friend_code_from_file = re.sub(r"\D", "", line)
            similarity_score = SequenceMatcher(None, friend_code, friend_code_from_file).ratio()
            if setup.is_debug_mode:
                setup.logger.debug(f"{friend_code} and {friend_code_from_file} are {similarity_score * 100}% similar")

            if similarity_score > 0.6:
                logger.info(f"{friend_code} and {friend_code_from_file} are {similarity_score * 100}% similar, they"
                            " are a vip")
                return True
    setup.logger.info("they are not a vip, the similarity scores were not high enough.")
    return False


def delete_friend():
    setup.logger.info("deleting friend...")
    pyautogui.click(coordinates["removeFriend"])
    pyautogui.click(coordinates["confirmDeleteFriend"])
    pyautogui.click(coordinates["clickOutOfProfile"])


def on_press(key):
    global script_paused
    logger = setup.logger
    try:
        # If key pressed is a special key like shift key.char throws an exception
        if key.char == "q":
            logger.info("quit hotkey was detected, quitting...")
            os.kill(os.getpid(), signal.SIGINT)
        if key.char == "r":
            script_paused = False
            logger.info("script is resuming...")
        if key.char == "p":
            script_paused = True
            logger.info("script is pausing...")
    except AttributeError:
        pass


def go_to_next_friend(num_vip_friends):
    if num_vip_friends % 3 == 0:
        pyautogui.moveTo(coordinates["betweenFriendSpace"])
        pyautogui.dragTo(y=coordinates["betweenFriendSpace"][1] - 170, duration=1)
        coordinates["goToFriend"] = (150, coordinates["goToFriend"][1] - 200)  # moving back to first slot
    else:
        coordinates["goToFriend"] = (150, coordinates["goToFriend"][1] + 100)


def check_and_delete_friends():
    logger = setup.logger
    num_vip_friends = 0
    current_count_string = (
        re.sub(r"\D", "",
               convert_screenshot_to_string("friendCount", coordinates["friendCount"][setup.selected_language], True)))
    current_count = int(current_count_string) if current_count_string.isdecimal() else -1
    desired_count = get_line_count("vip_ids.txt")

    if current_count == -1:
        logger.error("the current count could not be found. Make sure you are in the Friends screen and see "
                     "'number of friends' at the top")
        sys.exit(-1)

    while current_count > desired_count:
        while script_paused:
            time.sleep(5)
        (x, y) = pyautogui.position()
        pyautogui.click(coordinates["goToFriend"])
        pyautogui.moveTo(x, y)
        fc = re.sub(r"\D", "", convert_screenshot_to_string("friendCode", coordinates["friendCode"], False))
        index = 0
        while fc == "" or len(fc) < 4:
            if index == 50:
                logger.error("could not accurately determine the friend code. Exiting...")
                sys.exit(-1)
            index += 1
            psm = 6 if index % 2 == 0 else 7
            fc = re.sub(r"\D", "",
                        convert_screenshot_to_string("friendCode", coordinates["friendCode"], False, psm))
        if setup.is_debug_mode:
            logger.debug(fc)
        if is_vip_friend("vip_ids.txt", fc):
            pyautogui.click(coordinates["clickOutOfProfile"])
            num_vip_friends += 1
            go_to_next_friend(num_vip_friends)
            pyautogui.moveTo(x, y)
        else:
            delete_friend()
            current_count -= 1
            pyautogui.moveTo(x, y)
        pyautogui.moveTo(x, y)
    logger.info(f"current count: {current_count}\n desired count: {desired_count}")
    logger.info("the script has finished running.")


if __name__ == '__main__':
    # mouseinfo.MouseInfoWindow()
    listener = keyboard.Listener(on_press=on_press)
    listener.start()
    try:
        get_user_language()
        validate_file()
        initialize_logger()
        importlib.reload(setup)
        check_and_delete_friends()
    except KeyboardInterrupt:
        setup.logger.error("There was a keyboard interrupt. Exiting...")
        sys.exit()
