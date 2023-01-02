# zorkdemo

[![Python build and test](https://github.com/bcorfman/zorkdemo/actions/workflows/build-test.yml/badge.svg)](https://github.com/bcorfman/zorkdemo/actions/workflows/build-test.yml)
[![Open in Codespaces](https://github.com/codespaces/badge.svg)](https://github.com/codespaces/new?hide_repo_select=true&ref=main&repo=338102781&machine=standardLinux32gb&devcontainer_path=.devcontainer%2Fdevcontainer.json&location=EastUs)

Runs on Linux, Windows or Mac.

A (much simplified) port of a famous adventure game to help teach my daughter how to program in Python.

Two easy ways to launch the console project:

1. Click on the Open with GitHub Codespaces badge above to launch the project in a browser or on your desktop inside Visual Studio Code, then type `poetry run python zorkdemo.py` in the terminal window.
2. Download one of the binary releases and run the file on your system.

NOTE: the MacOS version does not have code signing built into it yet (that's next on my list!). To run it, you will need to set the binary as executable with `chmod 755` or similar, and after trying to run it once, go through System Preferences: Security and Privacy: General and "Allow the program to run anyway".

## Web (Hug) version

* Install [Python](https://www.python.org) 3.8.1 or higher
* Install [Poetry](https://python-poetry.org)
* At a command prompt in the project directory, type `poetry install` to set up dependencies

Next. set the flask application environment variables:

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
