# SpecMap
Version2 of hypermap

!!! .venv Installation START !!!
- Installation an .venv creation on windows enter the following 5 command in your terminal:
>>> Remove-Item -Recurse -Force .venv
>>> python -m venv .venv
>>> .\.venv\Scripts\Activate.ps1
>>> python -m pip install --upgrade pip
>>> pip install -r requirements.txt

- then select the virtual environment
if u get the tcl error:     self.tk = _tkinter.create(screenName, baseName, className, interactive, wantobjects, useTk, sync, use)
              ~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
_tkinter.TclError: Can't find a usable init.tcl in the following directories: [...] This probably means that Tcl wasn't installed properly.
Fix: 
place the tcl installation in the path of your python installation in the .venv dir 
(u might the tcl folder from C:\Users\username\AppData\Local\Programs\Python\Python313)

then start a terminal and run the following commands:
>>> $projectdir = (Get-Location).Path
>>> $env:TCL_LIBRARY = "$projectdir\.venv\tcl\tcl8.6"
>>> $env:TK_LIBRARY  = "$projectdir\.venv\tcl\tk8.6"
this 

!!! .venv Installation END !!!

run mainN.py with all necessary modules in a folder ... worla
(the N in mainN.py is dependent on the version, the higher, the newer the version)

Setup on Github: 
Note: the main branche ist protected. For changes create new patch that contains changes. Then create pull request. After review, merge into main branch. Then create new tag with version number
Get access to the repository by invitation as a collaborator. 

github clone repository that a colaborator grated me access to edit it locally e. g. in visual studio code (advise from chatgpt, but checked and works):
To clone a GitHub repository that a collaborator has granted you access to and edit it locally in Visual Studio Code, follow these steps:

Step 1: Set Up Git (if not already done)
Install Git:

Download and install Git from the official website: git-scm.com.
Follow the installation prompts to complete the setup.
Configure Git:

Open a terminal and configure your Git username and email:
bash
Code kopieren
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

Step 2: Clone the Repository
Open GitHub:

Go to GitHub and log in to your account.
Find the Repository:

Navigate to the repository you want to clone (this should be one you have access to).
Copy the Repository URL:

Click on the green "Code" button in the repository page.
Choose the URL under "HTTPS" or "SSH" (if you have set up SSH keys).
Clone the Repository:

Open a terminal or command prompt.
Navigate to the directory where you want to clone the repository.
Run the following command, replacing REPO_URL with the URL you copied:
bash
Code kopieren
git clone REPO_URL
Example:
bash
Code kopieren
git clone https://github.com/username/repo-name.git
This will download the repository to your local machine.

Step 3: Open the Repository in Visual Studio Code
Launch Visual Studio Code:

Open Visual Studio Code on your computer.
Open the Cloned Repository:

In Visual Studio Code, go to File > Open Folder....
Navigate to the directory where you cloned the repository and select it.
Start Editing:

Now you can start editing the files in the repository.
Use the Source Control feature in VS Code (accessible via the Git icon on the left sidebar) to see changes, stage them, and commit.

Step 4: Commit and Push Changes
Stage Changes:

After making changes, go to the Source Control panel in VS Code.
Stage the changes by clicking the + icon next to the file names.
Commit Changes:

Add a commit message in the text box and click the checkmark icon to commit.
Push Changes:

To push your changes to the remote repository, click on the three dots in the Source Control panel, then choose Push.
That's it! You've successfully cloned a GitHub repository, edited it locally, and pushed changes back to GitHub using Visual Studio Code.

Python: 
install python 3.12 and the packages
numpy, pandas, matplotlib, scipy using pip install

Igor: 

See Igor Program folder and the Readme.txt file in the folder
