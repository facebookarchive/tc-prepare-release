# tc-bumper

Bump version of TorchCraft automagically. You probably want to use this only if
you are core developer.

*WARNING:* if you are not careful you might lose work. Use it at your own risk.

## Installation

* Install python 2 or python 3
* `$ git clone git@github.com:TorchCraft/tc-bumper`

## Usage

```
$ cd tc-bumper

# First off, visualise the options in case there's anything you need
$ python tc-bumper -h

# Now you can happily run the tool
# It automatically makes a backup of the directory and stashes any dirt
$ python tc-bumper $OLD_VERSION $NEW_VERSION $PATH_TO_TORCHCRAFT -b -s

# e.g.
$ ./tc-bumper 1.2-1 1.3-1 ../TorchCraft -b -s
```
