#! /bin/bash

find . -name '*.py' -exec autopep8 -aaaai {} \;
