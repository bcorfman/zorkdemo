# zorkdemo

[![Python build and test](https://github.com/bcorfman/zorkdemo/actions/workflows/build-test.yml/badge.svg)](https://github.com/bcorfman/zorkdemo/actions/workflows/build-test.yml)

Runs on Linux, Windows or Mac.

A (much simplified) port of a famous adventure game to help teach my daughter how to program in Python.

Two ways to launch the project:

1. Download the source code, and, from a console window, type `python main.py` to start the game -- provided you have Python 3.7 or higher installed on your system.
2. Download one of the binary releases and run the file on your system.

NOTE: the MacOS version does not have code signing built into it yet (that's next on my list!). To run it, you will need to set the binary as executable with `chmod 755` or similar, and after trying to run it once, go through System Preferences: Security and Privacy: General and "Allow the program to run anyway".

## Web (Hug) version

In a virtual environment (preferably), install the requirements from the `requirements.txt` file (i.e. `pip install -r requirements.txt`).

Set the flask application environment variables:

The easiest option is to create a `.env` file in the root of the project with the contents:

```config
SECRET_KEY="<some random key>"
```

alternatively, you can manually set your environment variables for your terminal session but you'll have to remember to do that for every new session.

```sh
EXPORT SECRET_KEY="<put something random here>"
```

### Running the development web server

In the root of the project, run:

```sh
hug -m web.app
```

Navigate in your browser to:

[http://localhost:8000/](http://localhost:8000/)

Have Fun!

If you want to restart delete your `sid` cookie from your browser and refresh the page.

**NOTE:** future versions should provide a link to an endpoint to achieve something like this.

Or, you could delete your session record from the Sqlite database.

## Web TODO Items

- make endsession actually work
- provide link to endsession
- alignment between input and output for seamless experience
- figure out how to handle quit/exit
- wsgi file for hooking this up to a real web server and hosting
