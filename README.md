# tc-prepare-release: TorchCraft Release Helper

Bump version of TorchCraft automagically.

There are two tools, `tc-bumper` and `tc-make-release`.

* `tc-bumper`

  1. creates a `new_release` branch (trying very hard);
  2. replaces the version in certain files such as
     `$TORHCRAFT_PATH/CMakeLists.txt` and `$TORCHCRAFT_PATH/quick_setup.sh`;
  3. commits changes and pushes the new branch to whatever remote is assigned
     to `origin` in `$TORCHCRAFT_PATH`.

* `tc-make-release`

  1. copies the release files in the correct order / tree structure;
  2. zips everything up into one binary that you can upload on GitHub.


---

**WARNING:** like with all automatic tools, if you are not careful you might lose
work. You probably want to use this only if you are core developer.

---


## Installation

* Install python 2 or python 3;
* `$ git clone git@github.com:TorchCraft/tc-prepare-release`.


## Usage

* Set the git head in `$TORCHCRAFT_PATH` to `develop`.

* Create release:

```bash
$ cd tc-prepare-release

# First off, visualise the options in case there's anything you need.

$ python tc-bumper -h

# Now you can happily run the tool.
# With these flags it automatically makes a backup of the directory and 
# stashes any dirt.

$ python tc-bumper $OLD_VERSION $NEW_VERSION $TORHCRAFT_PATH -b -s

# e.g.
# python tc-bumper 1.2-1 1.3-1 ../TorchCraft -b -s
```

* Create zip:
  - Compile solution on Windows and copy `BWEnv.exe` and `BWEnv.dll` to `tc-bumper/out/`;
  - Run `python tc-make-release.py $NEW_VERSION $TORCHCRAFT_PATH`.
