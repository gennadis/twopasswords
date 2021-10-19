**Installation notes:**

# ffmpeg for a latest OpenCV version
1. brew install ffmpeg

# SQLCipher
2. brew install sqlcipher
3. pip install sqlcipher3==0.4.5
4. if "Failed to build sqlcipher3": SQLCIPHER_PATH="$(brew --cellar sqlcipher)/$(brew list --versions sqlcipher | tr ' ' '\n' | tail -1)" C_INCLUDE_PATH=$SQLCIPHER_PATH/include LIBRARY_PATH=$SQLCIPHER_PATH/lib pip3 install sqlcipher3==0.4.5

# Black PEP8
pip install black
pip uninstall regex
pip install regex==2021.9.30
