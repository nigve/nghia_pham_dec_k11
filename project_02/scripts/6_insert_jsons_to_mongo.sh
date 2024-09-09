#!/bin/bash
# set -x

RAW_DATA_DIR="./raw_data/jsons"
RAW_DATA_FROM_OTHER_SERVER_DIR="./raw_data_from_other_servers/"

filter_json() {
    file=$1
    jq -c '{id, name, url_key, price, description, images}' "$file"
}

# file_inserted=0
# for file in "$RAW_DATA_DIR"/*.json; do
#     if filter_json $file | mongoimport --db tiki --collection products; then
#         file_inserted=$((file_inserted + 1))
#         echo "$file_inserted file(s) inserted to mongo from $RAW_DATA_DIR"
#     else  
#         echo "Error: Failed to import $file"
#         exit 1
#     fi    
# done    

for subdir in "$RAW_DATA_FROM_OTHER_SERVER_DIR"*/; do
    if [ -d "$subdir" ]; then
        file_inserted=0
        for file in "$subdir"/jsons/*.json; do
            if filter_json "$file" | mongoimport --db tiki --collection products; then
                file_inserted=$((file_inserted + 1))
                echo "$file_inserted file(s) inserted to mongo from $subdir"
            else  
                echo "Error: Failed to import $file"
                exit 1
            fi    
        done
    fi    
done