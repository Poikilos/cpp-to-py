# cpp-to-py
This project intends to convert C++ code to Python using ply by creating an abstract syntax tree (AST).

This program requires Python 3.


## Setup
```
# python3 -m pip install ply
python3 -m pip uninstall -y ply
# ^ "PLY is no longer maintained as pip-installable package. Although no
#   new features are planned, it continues to be maintained and
#   modernized. If you want to use the latest version, you need to check
#   it out from the PLY GitHub page." -<https://www.dabeaz.com/ply/>
REPOS=$HOME/Downloads/git/dabeaz
mkdir -p $REPOS
# wget -O $HOME/Downlaods/ply.zip https://github.com/dabeaz/ply/archive/refs/heads/master.zip
REPO=$REPOS/ply
if [ ! -d $REPO ]; then
    git clone https://github.com/dabeaz/ply.git $REPO
fi
cd $REPO
if [ $? -ne 0 ]; then
    echo "Error: 'cd $REPO' failed."
    exit 1
fi
git pull
python3 ./install.py --user
# meld ~/.local/lib/python3.7/site-packages/ply/ ~/git/cpp-to-py/cpp-to-py.py
# ^
# meld $REPO/example/cpp/cpp.py ~/git/cpp-to-py/cpp-to-py.py
```


## Developer Notes

### Related projects
- [Cpp2PythonConverter](https://github.com/ivonamilutinovic/Cpp2PythonConverter): not tried yet
  - archived in 2019; has only 2 commits; has only a lex an ypp file and no documentation in the readme
- [Cpp2Python_translator](https://github.com/GianlucaPorcelli/Cpp2Python_translator): not tried yet
  "The present work aims to translate a program understandable by a c++ compiler into a sequence of equivalent instructions (where possible) written in python language."
  - uses an Abstract Syntax Tree (AST)
- seasnake: only works with C, apparently (and only on Ubuntu 14.04 and 16.04)
- [cpp2python](https://github.com/andreikop/cpp2python) by andreikop leaves major artifacts listed below (These issues, plus requiring ANSI style via `astyle --style=ansi`, indicate it isn't a true lexer):
  - `if path.isEmpty()) qFatal("Cannot determine settings storage location":` (incorrect no-brace case scoping)
  - `QDir d{path` (incorrect constructor syntax)
  - `def` (Python keywords shouldn't be allowed as variable names)
- [cpp2python](https://github.com/asadretdinov/cpp2python) by asadretdinov: not tested (Russian, requires C++ to use)
- [CPP_TO_PYTHON](https://github.com/RamGopalPandey/CPP_TO_PYTHON)
  - It requires that all statements have curly braces and no leading spaces (which indicate it is not a true parser).
- [cpp_to_python](https://github.com/YoshikazuArimitsu/cpp_to_python) appears to be in the planning stages.

#### Not applicable
- [CLion_CPP2Python](https://github.com/mhyttsten/CLion_CPP2Python) and similar projects appear to just allow calling compiled C++ modules.

### More Lexers and Parsers (unused)
- [CodeTokenizer](https://github.com/poikilos/CodeTokenizer) makes you do everything beyong tokenizing manually.

### outputinspector conversion
(of nodeps [standard C++] branch to Python)
```
cd ~/git/outputinspector-nodeps
PATH=$PATH:/usr/include
# ^ stat.h etc
PATH=$PATH:/usr/include/c++/8
# ^ vector.h etc
export PATH
# ^ doesn't fix:
cat > /dev/null <<END
Couldn't find 'string'
Couldn't find 'vector'
Couldn't find 'map'
Couldn't find 'algorithm'
Couldn't find 'cctype'
Couldn't find 'locale'
Couldn't find 'map'
Couldn't find 'vector'
Couldn't find 'list'
Couldn't find 'cstddef'
Couldn't find 'iostream'
Couldn't find 'vector'
Couldn't find 'iosfwd'
Couldn't find 'string'
Couldn't find 'cassert'
Couldn't find 'sys/types.h'
Couldn't find 'sys/stat.h'
Couldn't find 'regex'
Couldn't find 'algorithm'
Couldn't find 'functional'
END
python3 ~/git/cpp-to-py/cpp-to-py.py mainwindow.cpp
```

### PLY
License: A 3-clause BSD license is in the readme: <https://raw.githubusercontent.com/dabeaz/ply/master/README.md>
- with the conflicting phrase "All rights reserved":
  [The license copyright line contradicts the BSD 3-clause license below it. #252](https://github.com/dabeaz/ply/issues/252)

#### Choosing PLY
PLY is purely Python so it doesn't require bison and flex like pybison does, which may help it work better under Kivy on mobile platforms.
```
# python3 -m pip uninstall -y antlr4-python3-runtime
# python3 -m pip uninstall -y pybison
# python3 -c "import bison"
# ^ check if install worked
```
PLY issues noted by [pybison](https://pypi.org/project/pybison/): 'usage of 'named groups' regular expressions in the lexer creates a hard limit of 100 tokens"; pure python (slower); SLR not LALR.

#### PLY Examples
~/.local/lib/python3.7/site-packages/ply/cpp.py

From <https://www.dabeaz.com/ply/>:
- [cppheaderparser](http://sourceforge.net/projects/cppheaderparser/). A C++ header parser.
- [ZXBasic](http://www.zxbasic.net/). A cross compiler translates BASIC into Z80 assembler.
- [ ] [ Add your project here by sending email to "dave" at "dabeaz.com" ]

#### PLY issues
- <https://github.com/dabeaz/ply/issues>

### First-time repo setup
(already done in repo--not part of installation)
```
mkdir -p ~/Downloads/git/dabeaz && cd ~/Downloads/git/dabeaz && git clone https://github.com/dabeaz/ply.git
# install ply via its install.py (not setup.py--see setup.md)
cd ~/git/cpp-to-py && cp ~/Downloads/git/dabeaz/ply/example/cpp.py ./
# ^ examples are not in ~/.local/lib/python3.7/site-packages/ply unless using the OLD unmaintained version from pip!
# meld ~/Downloads/git/dabeaz/ply/example/cpp/cpp.py ~/git/cpp-to-py/cpp-to-py.py
```

### Regenerate the parser(s)
UNUSED
(Fix [ANTLR runtime and generated code versions disagree: 4.9.2!=4.8 #1](https://github.com/poikilos/CodeTokenizer/issues/1)).
- Complete the "Setup" section.
- Change `REPO_PATH` in the first line of shell commands below.
```
REPO_PATH=~/git/CodeTokenizer
# See <https://www.cs.upc.edu/~padro/CL/practica/install.html>
sudo apt-get install antlr4 -t buster-backports
# ^ also installs: libantlr3-runtime-java libantlr4-runtime-java libjsonp-java libstringtemplate4-java libtreelayout-java
cd $REPO_PATH/tokenizer/grammars/CPP
# antlr4 -Dlanguage=python3 CPP14.g4
# ^ -Dlanguage=: The default is java.
# ^ "error(31):  ANTLR cannot generate python3 code as of version 4.7.2"
#   so:
mkdir ~/Downloads
wget -O ~/Downloads/antlr-4.9.2-complete.jar https://www.antlr.org/download/antlr-4.9.2-complete.jar
java -jar ~/Downloads/antlr-4.9.2-complete.jar -Dlanguage=python3 CPP14.g4
# ^ "error(31):  ANTLR cannot generate python3 code as of version 4.7.2"
# The solution is to fix the case (capitalize "Python"):
java -jar ~/Downloads/antlr-4.9.2-complete.jar -Dlanguage=Python3 CPP14.g4
# ^ creates a parser with bad syntax: [invalid syntax "throw" in CPP14Parser.py #2](https://github.com/poikilos/CodeTokenizer/issues/2)
# so try:
java -jar ~/Downloads/antlr-4.9.2-complete.jar -Dlanguage=Python3 CPP14Lexer.g4
java -jar ~/Downloads/antlr-4.9.2-complete.jar -Dlanguage=Python3 CPP14Parser.g4

```

### Parsing C++ Using Python
- Grammars are at <https://github.com/antlr/grammars-v4>
  (See wget commands under "First-time repo setup"
  - It also has Lua:
    ```
mkdir -p antlr/grammars-v4/lua
cd antlr/grammars-v4/lua
wget -O Lua.g4 https://raw.githubusercontent.com/antlr/grammars-v4/master/lua/Lua.g4
```



