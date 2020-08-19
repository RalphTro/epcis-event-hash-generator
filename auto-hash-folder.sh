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


WHATCH_DIR=${1%/}

PATH_TO_MAIN=${2:-"epcis_event_hash_generator"}
PATH_TO_MAIN=${PATH_TO_MAIN%/}

inotifywait -m $WHATCH_DIR -e create -e moved_to |
    while read dir action file; do
        file=$(realpath $WHATCH_DIR/$file)
        #echo "file=$file"
        filename=$(basename -- "$file")
        #echo "filename=$filename"
        extension="${filename##*.}"
        #echo "extension=$extension"
        filename="${filename%.*}"

        if [[ "$extension" == "json" ]] || [[ "$extension" == "xml" ]]; then
            echo -e "[...]\t Hashing $filename"
            if python3 ${PATH_TO_MAIN}/main.py -b $file; then
                out_file_path=$(realpath $WHATCH_DIR/${filename}.hashes)
                cat $out_file_path
                echo -e "[OK]\t Hashes stored in ${filename}.hashes"

                if [[ "$POST_BINARY_URL" != "" ]]; then
                    echo -e "[...]\t Posting binary hashes to $POST_BINARY_URL"
                    EXIT_STATUS=0
                    echo >post.log
                    while read -r line; do
                        echo -e "\nPosting $line\n" >>post.log
                        python3 -c "import binascii; import sys; sys.stdout.buffer.write(binascii.unhexlify(\"${line:14:64}\"));" |
                            curl -v --data-binary "@-" --header "Content-Type: application/octet-stream" --header "X-Auth-Token: $POST_X_AUTH" "$POST_BINARY_URL" >>post.log 2>&1 ||
                            EXIT_STATUS=$?
                    done <$out_file_path
                    cat post.log
                    if [[ "$EXIT_STATUS" == "0" ]]; then
                        echo -e "[done]\t posted."
                    else
                        echo -e "[ERR]\t some hash posting failed."
                    fi
                fi

            else
                echo -e "[ERR]\t Error Hashing $filename"
            fi
        fi

    done
