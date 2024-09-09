#!/bin/bash
# set -x

CHUNK_CSV_FILES_DIR="../csv/chunks/"

declare -a servers=(
  "local"
  "3.27.245.146" #nig_1
  "3.107.78.96" #nig_2
  "3.27.254.12" #nig_3
  "52.62.105.138" #nig_4
  "13.239.24.153" #nig_5
  "3.106.59.36" #nig_6
  "3.27.206.78" #nig_7
  "3.106.54.4" #nig_8
  "3.106.114.50" #nig_9
)
server_index=0

for file in "$CHUNK_CSV_FILES_DIR"*.csv; do
  server=${servers[$server_index]}
  
  if [[ "$server" == "local" ]]; then
    echo "Copying $file to chunk_to_process directory on $server..."
    mkdir -p ../csv/chunk_to_process/
    cp $file ../csv/chunk_to_process/
    echo "Copied $file to chunk_to_process directory on $server..."
  else
    echo "Uploading $file to $server:$REMOTE_DIR"
    sftp ubuntu@"$server" <<EOF
mkdir UG
mkdir UG/tiki
mkdir UG/tiki/csv
mkdir UG/tiki/csv/chunk_to_process
cd UG/tiki/csv/chunk_to_process
put "$file"
exit
EOF
  echo "Uploaded $file to $server"  
  fi
  server_index=$((server_index + 1))
done