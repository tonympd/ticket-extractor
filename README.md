# ticket-extractor
This is a modified version of the ppdg-extractor to support the following:
 - Ticketmaster
 - Axs

## Contributors
- @Tony 


## Setup ##

1) Install the newest version of Python: https://www.python.org/downloads/

2) Open command prompt (cmd) and navigate to this folder. Install the dependencies by running the following commands:
	
	```bash
	 pip3 install -r requirements.txt
    ```
    
3) Rename config.sample.py to config.py and edit the following variables:
	
	a) Change IMAP_USERNAME to your gmail account
	
	b) Change IMAP_PASSWORD to your gmail password
	
	c) Create a gmail label for the cards you would like to extract and change FOLDER to this label. This label will serve as the processing folder for your cards. When you would like to extract a card, label it with this label, run the extractor, and then move the card to another label. The program can only see cards that reside in this label.
	
	d) Change FROM_EMAILS to any list of email you want to check the FROM address of.  This is nice if you have forwarded emails or for multiple types of cards.
	
	e) **Note:** When logging in for the first time, gmail may block access. You will need to follow the steps in the email to follow to enable less secure applications.  (https://myaccount.google.com/lesssecureapps)
	
4) Windows Users: Double click on MasterExtractor.bat to run the program. 

    Alternatively you can run master-extractor.py for a python IDE.  PyCharm Recommended (https://www.jetbrains.com/pycharm/)
 
    In order to access the cards, open the .csv file with your notepad program of choice. Notepad++ Recommended (https://notepad-plus-plus.org/download/v7.5.3.html).