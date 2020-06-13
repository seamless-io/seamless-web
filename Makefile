# The program used as the shell is taken from the variable `SHELL'.  If
# this variable is not set in your makefile, the program `/bin/sh' is
# used as the shell.
# https://stackoverflow.com/questions/589276/how-can-i-use-bash-syntax-in-makefile-targets
SHELL := /bin/bash

watch:
	rm -rf client/dist
	pushd client && npm install && npm start
