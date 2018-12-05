# Doctor Fill Web Application

Doctor Fill is accepting new patients.

DoctorFill is a GitHub App that is installed on the SCalwas/github_app_poc
repository. Whenever a push occurs on the repo, the app sends a notification
to a configured URL. The Doctor Fill web application can receive the 
notifications and perform whatever operations it deems appropriate, within
commonly accepted medical practices, of course.

## Setup to perform for every session

To prevent exposing your computer to the internet, the DoctorFill GitHub app
sends its notifications to an intermediate URL destination. The intermediate 
destination then passes them to the Doctor Fill web application. Every time 
you start a new dev session, you must set up this intermediary.

The intermediate URL is stored in the smeeio_url.txt file. Copy the URL address
and enter it on the following command line.

```
smee -u <smeeURL>
```

Optionally, go to the same URL in your browser. From the browser, you'll be able
to monitor the notifications and payloads sent from GitHub.

## Adding functionality to Doctor Fill

When Doctor Fill receives notification that a push has occurred on the 
github_app_poc repository, it cycles through each new file that was added to the
repo in the push's commits. For each new file, Doctor Fill loads the file's 
contents and can pass the contents of type 'bytes' to a linter-type function. 

Insert a call to your function at line 130 of the app.py source file. Your function
can perform any exploratory and surgical operations it desires. If it changes 
the file's contents, it should return True, otherwise False. If the file is 
changed, Doctor Fill commits the modified file back to the repo. Afterward, don't 
forget to pull the changed file to your local repo.


## One-time setup

Before running the Doctor Fill web application for the first time, perform the
following one-time setup operations.

* Clone the SCalwas/DoctorFill repository.
* From Amazon Docs, copy the necessary shared files. Store them in the DoctorFile
repo directory. The .gitignore file will not add them to the repository.
* Install Node.js
* Install the smee client that is run for every session.
```
npm install --global smee-client
```
* Install Python 3
* Run pip to install Doctor Fill library dependencies.
```
pip install -r requirements.txt
```
