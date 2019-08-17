#!/bin/bash
FILE_TO_DEPLOY=$1
FOUND=false
REGEX="CIRCUITPY$"
BASE_DIR=""
for f in /media/paul/*; do
    if [[ -d $f  ]]; then
        if [[ $f =~ $REGEX ]]; then
            FOUND=true
            BASE_DIR=$f
            break
        fi
        # $f is a directory
        echo $f
    fi
done

if [[ $FOUND == "true" ]]; then
    cp $FILE_TO_DEPLOY $BASE_DIR/main.py
else
    echo "No gemma found"
fi