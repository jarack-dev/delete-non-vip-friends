import os
import signal
import sys
import time
import pytesseract
import pyautogui
import re
from pynput import keyboard
from difflib import SequenceMatcher

debug = True
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
pyautogui.PAUSE = 1
script_paused = False
coordinates = {
    "friendCount": (125, 110, 20, 15),
    "friendCode": (175, 75, 95, 20),
    "goToFriend": (150, 200),
    "removeFriend": (150, 410),
    "confirmDeleteFriend": (200, 370),
    "clickOutOfProfile": (140, 510),
    "betweenFriendSpace": (135, 235),
}


def convert_screenshot_to_string(ss_coordinates):
    screenshot = pyautogui.screenshot(region=ss_coordinates)
    screenshot.save('screenshot.png')
    return pytesseract.image_to_string(screenshot, lang='eng', config='--psm 7')


def is_vip_friend(filePath, friend_code):
    with open(filePath, 'r') as file:
        for line in file:
            friend_code_from_file = re.sub('[^\d\.]', "", line)
            similarity_score = SequenceMatcher(None, friend_code, friend_code_from_file).ratio()
            if debug:
                print(f"{friend_code} and {friend_code_from_file} are {similarity_score * 100}% similar")

            if similarity_score > 0.6:
                print(f"{friend_code} and {friend_code_from_file} are {similarity_score * 100}% similar, they are a vip")
                return True
    print("they are not a vip")
    return False


def get_line_count(filePath):
    with open(filePath, 'r') as fp:
        lines = len(fp.readlines())
        return lines


def delete_friend():
    print("deleting friend")
    pyautogui.click(coordinates["removeFriend"])
    pyautogui.click(coordinates["confirmDeleteFriend"])
    pyautogui.click(coordinates["clickOutOfProfile"])


def on_press(key):
    global script_paused
    try:
        print(key.char)
        # If key pressed is a special key like shift key.char throws an exception
        if key.char == "q":
            print("quit hotkey was detected, quitting...")
            os.kill(os.getpid(), signal.SIGINT)
        if key.char == "r":
            script_paused = False
            print("script is resuming...")
        if key.char == "p":
            script_paused = True
            print("script is pausing...")
    except AttributeError:
        pass


def go_to_next_friend(num_vip_friends):
    if num_vip_friends % 3 == 0:
        pyautogui.moveTo(coordinates["betweenFriendSpace"])
        pyautogui.dragTo(y=coordinates["betweenFriendSpace"][1] - 180, duration=1)
    else:
        coordinates["goToFriend"] = (150, coordinates["goToFriend"][1] + 100)


def check_and_delete_friends():
    num_vip_friends = 0
    current_count_string = (re.sub('[^\d\.]', "", convert_screenshot_to_string(coordinates["friendCount"])))
    current_count = int(current_count_string) if current_count_string.isdecimal() else -1
    desired_count = get_line_count("vip_ids.txt")

    if current_count == -1:
        sys.exit(-1)

    while current_count >= desired_count:
        while script_paused:
            time.sleep(5)
        pyautogui.click(coordinates["goToFriend"])
        fc = re.sub("[^\d\.]", "", convert_screenshot_to_string(coordinates["friendCode"]))
        if fc == "":
            continue
        print(fc)
        if is_vip_friend("vip_ids.txt", fc):
            pyautogui.click(coordinates["clickOutOfProfile"])
            num_vip_friends += 1
            go_to_next_friend(num_vip_friends)
        else:
            delete_friend()
            current_count -= 1


if __name__ == '__main__':
    # mouseinfo.MouseInfoWindow()
    listener = keyboard.Listener(on_press=on_press)
    listener.start()
    try:
        check_and_delete_friends()
    except KeyboardInterrupt:
        sys.exit()
