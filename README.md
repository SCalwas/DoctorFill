# Doctor Fill

Doctor Fill is the primary care physician for the AWS SDK Docs team.

To keep SDK docs healthy and happy, Doctor Fill employs a two-pronged approach.

* The DoctorFill GitHub App can be installed on any GitHub repo. Whenever a push
occurs to a repo that has the app installed, Doctor Fill sends a notification.
* The Doctor Fill web application receives the notifications and performs whatever
operations it deems appropriate, within commonly accepted medical practices, of
course.

For development purposes, the DoctorFill GitHub App is installed on the GitHub
repo SCalwas/github_app_poc. A push to the repo triggers the sending of a 
notification. If the Doctor Fill web application is running, it can receive and
process the event.

## Doctor Fill Dissected

Doctor Fill comprises the following files.

* app.py - The main Doctor Fill module. It receives notifications from GitHub,
verifies the received information, and prescribes appropriate operations.
* requirements.txt - Initialization file used to install Python package 
dependencies.
* smeeio_url.txt - Contains a URL address. This address acts as an intermediary
between the DoctorFill GitHub App and the Doctor Fill web application. This
address receives the GitHub notification and passes it along to the web app.
Using an intermediary eliminates having to expose your computer to the internet
in order to receive notifications directly.
* README.md - The file you are reading now.
* .gitignore - Self-evident.

In addition, the following files are provided to dev contributors, but are
not part of the repository.

* github_app_credentials - A text file that contains credentials necessary to
run the GitHub App and web application. No modifications ever need to be made
to the contents of this file.
* doctorfill.2018-11-21.private-key.pem - Private key text file. No modifications
ever need to be made to the contents of this file.

## Doctor Fill setup to perform before every session

To prevent exposing your computer to the internet, the DoctorFill GitHub App
sends its notifications to an intermediate URL destination. The intermediate 
destination then passes them to the Doctor Fill web application. Every time 
you start a new dev session, you must set up this intermediary.

The intermediate URL is stored in the smeeio_url.txt file. Copy the URL address.
At a terminal prompt, paste the URL into the following command.

```
smee -u <smeeUrlAddress>
```

The intermediary will run and wait for notifications from GitHub. It requires
no user interaction to perform its duties. Just run it and leave it alone. To
terminate the intermediary, enter Ctrl-C.

If you want, you can optionally monitor in your browser the notifications and 
payloads that the intermediary receives from GitHub. To do so, paste the 
intermediary URL address into your browser. The loaded webpage is updated 
dynamically whenever it receives a notification.

## Adding functionality to Doctor Fill

When the Doctor Fill web application receives notification that a push has occurred 
on the github_app_poc repository, it cycles through each new file that was added to
the repo as part of the push. For each new file, Doctor Fill loads the file's 
contents and can pass the contents to a linter-type function. The file contents are
passed as a string.

To have your function called, insert the appropriate code statement around line 130
of the app.py source file. The location with a sample function call is shown below.

```python
### Pass to linter ###
# updated = add_your_function_here(contents_str)
```

Your function can perform any exploratory and surgical operations it desires. If it 
changes the file's contents, it should return True, otherwise False. If the file is 
changed, Doctor Fill will commit the modified file back to the repo. Don't forget 
to pull the modified file(s) to your local repo afterward.


## One-time Doctor Fill setup

The DoctorFill GitHub App is already installed on the SCalwas/github_app_poc repo.
No further setup of the GitHub App needs to occur.

Before running the Doctor Fill web application for the first time, perform the
following one-time setup operations.

* Clone the SCalwas/DoctorFill repository.
* From Amazon WorkDocs, copy the required shared files (github_app_credentials and
doctorfill.2018-11-21.private-key.pem). Store them in the DoctorFill repo directory.
The .gitignore file will prevent them from ever being added to the repository.
* Install Node.js. This is required only to get the npm package manager.
* Install the intermediary smee client by running the command shown below. The 
installed app must be run at the start of every session as described in an earlier
section. Note: The following command only installs the client. To run the client, 
execute the command described earlier.
```
npm install --global smee-client
```
* Install Python 3.
* If you use Python virtual environments (recommended), create one for the Doctor
Fill directory and activate it before installing the library dependencies in the
next step.
* Use pip to install the Doctor Fill library dependencies. The appropriate command
line is shown below.
```
pip install -r requirements.txt
```

To verify that everything is set up correctly, run the intermediary smee client as 
described in an earlier section. Then run the Doctor Fill app.py from a command 
line or IDE/debugger. If configuring an IDE/debugger, Doctor Fill is a Flask app 
and it must monitor port 3000. (The default port for Flask apps is 5000.)

Upon startup, Doctor Fill should perform its initialization and then begin
waiting for notifications from GitHub. As Doctor Fill proceeds, it logs 
informational messages to the console.

When Doctor Fill is waiting for notifications, go to the SCalwas/github_app_poc
repo and create a new issue. Use any issue name and description. After the issue is
created, Doctor Fill should automatically add the "enhancement" label to it. If the
label appears shortly after creating the issue, the dev environment is working
correctly.
