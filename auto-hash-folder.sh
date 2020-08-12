#!/bin/bash

USAGE_MSG="
This script whatches a folder for files with .json or .xml file ending appearing.
As soon as a new file is found, the epcis event hash generator is run in batch mode
in order to produce a sibbling file with the hashes of the events.

usage: $0 FOLDER_TO_WATCH [PATH_TO_MAIN=""]
"

if [ ! -d "$1" ]; then
    echo "$USAGE_MSG"
    exit 1
fi

PATH_TO_MAIN=${2:-""}

inotifywait -m $1 -e create -e moved_to |
    while read dir action file; do
        file=$(realpath $1/$file)
        #echo "file=$file"
        filename=$(basename -- "$file")
        #echo "filename=$filename"
        extension="${filename##*.}"
        #echo "extension=$extension"
        filename="${filename%.*}"

        if [[ "$extension" == "json" ]] || [[ "$extension" == "xml" ]]; then
            echo -e "[...]\t Hashing $filename"
            if python3 ${PATH_TO_MAIN}main.py -b $file; then
                cat $(realpath $1/${filename}.hashes)
                echo -e "[OK]\t Hashes stored in ${filename}.hashes"
            else
                echo -e "[ERR]\t Error Hashing $filename"
            fi
        fi

    done
