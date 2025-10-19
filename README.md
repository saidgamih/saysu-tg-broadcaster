# About
This is an automation python app that can send messages to all groups a user is belongs to in telegram via a predifined messages in a csv file (if you have new setup ideas feel free to submit a PR).

(!) Be aware that any misuse of the telegram API can cause the supension of your account, so be responsible and use that only when it's needed.

# Installation and setup :
* Install python in your machine if not installed.
* Extract files inside a folder and run a terminal from it.
* Setup a python virtual environment by running *python -m venv venv*
* Get inside your python virtual environment by running *.\\venv\\Scripts\\activate*
* Install dependencies by running *pip install -r .\\requirments.txt*
* Run the script using the command python client\_win.py

# Configuration :
When running the app for the first time you need to configure you telegram `API ID` and `API Hash`. 
You can get that from your telegram dev tools (https://my.telegram.org/apps).

<img width="602" height="534" alt="image" src="https://github.com/user-attachments/assets/e83c4dd1-5b11-4f18-bede-88e198e4cf29" />

When clicking on Start for the fisrt time the script will try connect to your telegram and a token will be sent to you, so you can provide it the app via a dialog window.

<img width="293" height="102" alt="image" src="https://github.com/user-attachments/assets/316826f2-100a-4682-b4a1-15e7da7fb15c" />

After that the app will generate config and session file in the same directory as the script.

Then reclick on the Start button to start sending messages to all your groups.

# Disclaimer
I'm not responsible for any misuse of this app, as the tools I used are public and meant to be used responsibly.

