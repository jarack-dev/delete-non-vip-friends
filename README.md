##
instructions:
- download/install python 3.0+ (this script was made using python 3.9)
- downlad/install tesseract from here: [Tesseract Github Link](https://github.com/UB-Mannheim/tesseract/wiki) 
- Note the file path teseract was installed under (for me that was `C:\Program Files\Tesseract-OCR\tesseract.exe`)
- replace line 12 in the script with the path your own version was installed under
- make a list of ids you dont want deleted, named vip_ids.txt and put it in 
  the same directory as this script
- Open your main instance, click on the pokemon tcg app
- go to the "Social" tab on the bottom tabs and click on friends
- open the ptcgpb bot, select your primary monitor and click "arrange windows"
- ***MAKE SURE YOUR MAIN INSTANCE IS ON YOUR PRIMARY MONITOR, OTHERWISE IT WILL NOT WORK

- open up a terminal window and run the following commands in the same directory the script is in: 
- `pip install -r requirements.txt`
- `python main.py`


Note: this script takes control of your mouse, so you will not be able to use it while it is running

Hotkeys supported:
- q: quit the script at any time
- p: pause the script after next one is finished
- r: resume the script (only works while paused)
