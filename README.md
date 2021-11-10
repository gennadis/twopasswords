# Installation notes:

### ffmpeg for a latest OpenCV version
`brew install ffmpeg`

### SQLCipher
- brew install sqlcipher
- pip install sqlcipher3==0.4.5
- if "Failed to build sqlcipher3": 
1. SQLCIPHER_PATH="$(brew --cellar sqlcipher)/$(brew list --versions sqlcipher | tr ' ' '\n' | tail -1)" 
2. C_INCLUDE_PATH=$SQLCIPHER_PATH/include LIBRARY_PATH=$SQLCIPHER_PATH/lib pip3 install sqlcipher3==0.4.5


### For black auto-PEP8
- pip install black
- pip uninstall regex
- pip install regex==2021.9.30
