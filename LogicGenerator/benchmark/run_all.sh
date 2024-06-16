#! /usr/bin/bash

echo run all python-files in this folder
for py_file in $(find . -name '*.py' | sort)
do
    echo $py_file
    python3 $py_file
done
