# zorkdemo
Runs on Linux, Windows or Mac.

A (much simplified) port of a famous adventure game to help teach my daughter how to program in Python.

Two ways to launch the project:
1. Download the source code, and, from a console window, type `python main.py` to start the game -- provided you have Python 3.6 or higher installed on your system.
2. Download one of the binary releases and run the file on your system. 

NOTE: the MacOS version does not have code signing built into it yet (that's next on my list!). To run it, you will need to set the binary as executable with `chmod 755` or similar, and after trying to run it once, go through System Preferences: Security and Privacy: General and "Allow the program to run anyway".

## Web (Flask) version

In a virtual environment (preferably), install the requirements from the `requirements.txt` file.

Set the flask application environment variables:

### Option 1

The easier option is to create a `.flaskenv` file in the root of the project with the contents:

```config
FLASK_APP=web.app
SECRET_KEY="<some random key>"
```

### Option 2

export variables in your current terminal session:

```sh
EXPORT FLASK_APP=web.app
EXPORT SECRET_KEY="<put something random here>"
```

### Setting up the DB for the very first use

**NOTE:** this is necessary before running the software for the first time.

In the root of the project, run:

```sh
flask create-tables
```

### Running the development web server
In the root of the project, run:

```sh
flask run
```

Navigate in your browser to:

http://localhost:5000/

Have Fun!

If you want to restart, manually navigate to:

http://localhost:5000/endsession

This will terminate the session and restart a new session.

**NOTE:** future versions should provide a link to this endpoint on the actual page.

Alternatively, you can delete the session cookie from your browser.

Or, you could delete your session record from the Sqlite database.
