# Setup

Following are instructions to configure the local environment to support development.
If you are not already using Windows Subsystem for Linux, now would be a really 
great time to install it and start using.

Assumption also that you are using vscode as your ide.  

Recommended vscode extensions to support development:

* python - microsofts vscode python add on
* autoDocstring - autogenerate docstrings for methods
* wsl - allows you to run vscode from wsl easily

## Install dependencies

### Check your python versions

Project is setup to use python 3.11 or higher.  Make sure this is installed and 
available at your command prompt.

you can verify by running:

`python --version`

If you don't have a version of python >= 3.11, use pyenv to easily allow you to
have multiple versions of python installed in harmony with one another.

### Install poetry

This is the one example where you will want to install globally.

```shell
# verify your version
python --version 

# install poetry 
python -m pip install poetry
```

### Install Project Dependencies

```shell
cd backend
poetry install
```

Poetry will create a `.venv` folder in your project that contains a virtualenv.
In order to activate your virtualenv run:

```shell
cd backend
. .venv/bin/activate
```

OR

`
