# import mouseinfo
import os
import pyautogui
import pytesseract
import re
import signal
import sys
import time
from enum import Enum
from PIL import ImageGrab, ImageEnhance
from difflib import SequenceMatcher
from pynput import keyboard

import setup
from setup import get_user_options, get_line_count, initialize_logger, validate_file

use_image_gen_end_condition = True
is_list_end = False
current_count = -1
desired_count = -1
friend_name = ""
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
pyautogui.PAUSE = 1
script_paused = False


class ImageType(Enum):
    Square = 1
    Rectangle = 2
    LongRectangle = 3


coordinates = {
    "friendCount": {
        "english": (125, 110, 146.15, 130),
        "japanese": (85.5, 110, 106.5, 130),
        "chinese": (65.5, 110, 86.65, 130)
    },
    "friendCode": (175, 70, 270, 95),
    "getLastFriend": (90, 350, 175, 410),
    "goToFriend": (150, 200),
    "removeFriend": (150, 410),
    "confirmDeleteFriend": (200, 370),
    "clickOutOfProfile": (140, 510),
    "betweenFriendSpace": (135, 235)

}


def get_resize_resolution(image_type):
    selected_language = setup.selected_language
    if image_type == ImageType.Square:
        return 200, 200
    elif image_type == ImageType.Rectangle:
        return 400, 100
    elif image_type == ImageType.LongRectangle:
        return 600, 300
    else:
        return 0, 0


def convert_screenshot_to_string(ss_name, ss_coordinates, image_type, psm=7):
    logger = setup.logger
    resize_resolution = get_resize_resolution(image_type)
    screenshot = ImageGrab.grab(bbox=ss_coordinates).resize(resize_resolution)
    enhanced_screenshot = ImageEnhance.Contrast(screenshot).enhance(3)
    parsed_text = pytesseract.image_to_string(enhanced_screenshot, lang='eng', config=f'--psm {psm}')

    if setup.is_debug_mode:
        screenshot.save(ss_name + '.png')
        enhanced_screenshot.save(ss_name + "_enhanced.png")
        logger.info(f"parsed text: {parsed_text}")
        logger.info(
            f"level of confidence: {pytesseract.image_to_data(enhanced_screenshot, config=f'--psm {psm}', output_type='dict')['conf']}")
    return parsed_text


def is_vip_friend(file_path, friend_code):
    logger = setup.logger
    with open(file_path, 'r') as file:
        for line in file:
            friend_code_from_file = re.sub(r"\D", "", line)
            similarity_score = SequenceMatcher(None, friend_code, friend_code_from_file).ratio() * 100
            if setup.is_debug_mode:
                logger.debug(f"{friend_code} and {friend_code_from_file} are {similarity_score}% similar")

            if similarity_score > 60:
                logger.info(f"{friend_code} and {friend_code_from_file} are {similarity_score}% similar, they"
                            " are a vip")
                return True
    logger.info("they are not a vip, the similarity scores were not high enough.")
    return False


def delete_friend():
    setup.logger.info("deleting friend...")
    pyautogui.click(coordinates["removeFriend"])
    time.sleep(3)
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
    global is_list_end
    if num_vip_friends % 3 == 0:
        is_list_end = is_end_of_list()
        if is_list_end:
            return
        else:
            pyautogui.moveTo(coordinates["betweenFriendSpace"])
            pyautogui.dragTo(y=coordinates["betweenFriendSpace"][1] - 173, duration=1)
            coordinates["goToFriend"] = (150, coordinates["goToFriend"][1] - 200)  # moving back to first slot

    else:
        coordinates["goToFriend"] = (150, coordinates["goToFriend"][1] + 100)


def is_end_of_list():
    global friend_name
    last_friend_name = re.sub("[^0-9a-zA-Z]+", "", convert_screenshot_to_string("lastFriendName",
                                                                                coordinates["getLastFriend"],
                                                                                ImageType.LongRectangle, psm=11))
    similarity_score = SequenceMatcher(None, friend_name, last_friend_name).ratio() * 100

    if last_friend_name == "":
        return False
    friend_name = last_friend_name

    if similarity_score > 75:
        if setup.is_debug_mode:
            setup.logger.info(
                f"the friend names are {similarity_score}% similar, you've reached the end of the list.")
        return True
    else:
        if setup.is_debug_mode:
            setup.logger.info(f"the friend names are {similarity_score}% similar, you still have a ways to go!")
        return False


def get_current_count():
    global current_count
    current_count_string = (
        re.sub(r"\D", "",
               convert_screenshot_to_string("friendCount", coordinates["friendCount"][setup.selected_language],
                                            ImageType.Square)))
    current_count = int(current_count_string) if current_count_string.isdecimal() else -1

    if current_count == -1:
        setup.logger.error("the current count could not be found. Make sure you are in the Friends screen and see "
                           "'number of friends' at the top")
        sys.exit(-1)


def check_and_delete_friends():
    global is_list_end, current_count, desired_count
    use_image_gen = setup.use_image_gen_end_condition
    logger = setup.logger
    num_vip_friends = 0
    if not use_image_gen:
        get_current_count()
        desired_count = get_line_count("vip_ids.txt")
    retry_attempts = 0
    while not is_list_end:
        if use_image_gen and is_list_end or not use_image_gen and current_count <= desired_count:
            break
        while script_paused:
            time.sleep(5)
        (x, y) = pyautogui.position()
        pyautogui.click(coordinates["goToFriend"])
        fc = re.sub(r"\D", "",
                    convert_screenshot_to_string("friendCode", coordinates["friendCode"], ImageType.Rectangle))

        if fc == "" or len(fc) < 4 and retry_attempts > 5:
            logger.error("could not accurately determine the friend code. Exiting...")
            sys.exit(-1)
        elif fc == "" or len(fc) < 4:
            retry_attempts += 1
            logger.error("could not accurately determine the friend code, retrying...")
            continue

        if setup.is_debug_mode:
            logger.debug(fc)

        if is_vip_friend("vip_ids.txt", fc):
            pyautogui.click(coordinates["clickOutOfProfile"])
            num_vip_friends += 1
            go_to_next_friend(num_vip_friends)
        else:
            delete_friend()
            current_count -= 1

        pyautogui.moveTo(x, y)

    if not use_image_gen:
        logger.info(f"current count: {current_count}\n desired count: {desired_count}")
    logger.info("the script has finished running.")


if __name__ == '__main__':
    # mouseinfo.MouseInfoWindow()
    listener = keyboard.Listener(on_press=on_press)
    listener.start()
    try:
        get_user_options()
        validate_file()
        initialize_logger()
        check_and_delete_friends()
    except KeyboardInterrupt:
        setup.logger.error("There was a keyboard interrupt. Exiting...")
        sys.exit()
    except Exception as e:
        setup.logger.error(e)

