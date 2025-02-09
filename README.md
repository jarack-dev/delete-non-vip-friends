## instructions:
1. downlad/install tesseract from here: [Tesseract Github Link](https://github.com/UB-Mannheim/tesseract/wiki). Note the file path teseract was installed under (for me that was `C:\Program Files\Tesseract-OCR\tesseract.exe`). If you're planning on running the exe file, it must be installed under the same path. 

### Running the Exe File:
2. Make sure tesseract is installed to `C:\Program Files\Tesseract-OCR\tesseract.exe`, the exe will not work if it's in any other directory.
3. Add ids to vip_ids.txt, one per line, and put the file in the same directory as the deleteNonVipFriends.exe.
4. Open your main instance, and open the app.
5. go to the "Social" tab on the bottom tabs and click on friends.
6. open the bot, select your primary monitor and click "arrange windows".

### Running the Python Script: 
1. download/install python 3.0+ (this script was made using python 3.9).
3. replace [this line](https://github.com/jarack-dev/delete-non-vip-friends/blob/main/main.py#L14) in the script with the path your own version was installed under.
4. Add ids to vip_ids.txt, one per line.
5. open up a terminal window and run the following commands in the same directory the script is in: 
- `pip install -r requirements.txt`
- `python main.py`
6. Open your main instance, and open the app.
7. go to the "Social" tab on the bottom tabs and click on friends.
8. open the bot, select your primary monitor and click "arrange windows".
  
***MAKE SURE YOUR MAIN INSTANCE IS ON YOUR PRIMARY MONITOR, OTHERWISE IT WILL NOT WORK*
Note: this script takes control of your mouse, so you will not be able to use it while it is running

Hotkeys supported:
- q: quit the script at any time
- p: pause the script after next one is finished
- r: resume the script (only works while paused)
