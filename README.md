# TwoPasswords

[![Pypi](https://img.shields.io/pypi/v/pyvault.svg)](https://pypi.org/project/twopasswords)
[![MIT licensed](https://img.shields.io/badge/license-MIT-green.svg)](https://raw.githubusercontent.com/gennadis/twopasswords/main/LICENSE)

TwoPasswords is a simple Python password manager, that uses Face Recognition as a second factor.
It allows you to securely save account credentials with a simple TUI interface.

## Features
- Account credentials stored locally in an encrypted SQLite database with [SQLCipher](https://www.zetetic.net/sqlcipher/)
- Passwords can be passed to Clipboard
- Passwords can be generated in [XKCD style](https://xkcd.com/936/)
- Import and Export in JSON


## Basic Usage
To start using TwoPasswords, you have to register your face and enter your new Master Password.

## Installation notes
1. TwoPasswords requires `cmake` to be installed on your machine.
```bash
pip3 install cmake
```

2. TwoPasswords requires `sqlcipher` to be installed on your machine.

On MacOS, you can install it with [brew](https://brew.sh/):
```bash
brew install sqlcipher
pip3 install sqlcipher3==0.4.5

# If you are getting an error "Failed to build sqlcipher3", you would need to fix the build flags:
SQLCIPHER_PATH="$(brew --cellar sqlcipher)/$(brew list --versions sqlcipher | tr ' ' '\n' | tail -1)"
C_INCLUDE_PATH=$SQLCIPHER_PATH/include LIBRARY_PATH=$SQLCIPHER_PATH/lib pip3 install sqlcipher3==0.4.5
```

3. Also you need to install latest ffmpeg library for a latest OpenCV version
```bash
brew install ffmpeg
```


### Installing via PyPI

```bash
pip3 install twopasswords

# Run setup
twopasswords
```

### Installing via cloning this project

```bash
# Clone project
git clone https://github.com/gennadis/twopasswords.git 
cd twopasswords

# Installation
python3 setup.py install

# Run setup
twopasswords
```